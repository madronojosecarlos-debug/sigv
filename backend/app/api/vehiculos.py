"""
Endpoints de Gestión de Vehículos
- CRUD de vehículos
- Búsqueda avanzada
- Asignación de etiquetas
- Campos personalizados
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.vehiculo import Vehiculo, CampoPersonalizado, ValorCampoPersonalizado
from ..models.etiqueta import Etiqueta, VehiculoEtiqueta
from ..models.zona import Zona
from ..models.usuario import Usuario
from .auth import get_current_user

router = APIRouter()


# Schemas
class VehiculoCreate(BaseModel):
    matricula: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    año: Optional[int] = None
    vin: Optional[str] = None
    cliente_nombre: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_email: Optional[str] = None
    notas: Optional[str] = None
    campos_personalizados: Optional[Dict[str, Any]] = None  # {campo_id: valor}


class VehiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    color: Optional[str] = None
    año: Optional[int] = None
    vin: Optional[str] = None
    cliente_nombre: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_email: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None
    campos_personalizados: Optional[Dict[str, Any]] = None


class EtiquetaAsignar(BaseModel):
    etiqueta_id: int


class VehiculoResponse(BaseModel):
    id: int
    matricula: str
    marca: Optional[str]
    modelo: Optional[str]
    color: Optional[str]
    año: Optional[int]
    vin: Optional[str]
    cliente_nombre: Optional[str]
    cliente_telefono: Optional[str]
    cliente_email: Optional[str]
    notas: Optional[str]
    activo: bool
    en_instalaciones: bool
    zona_actual: Optional[dict]
    etiquetas: List[dict]
    campos_personalizados: Dict[str, Any]
    fecha_primera_entrada: Optional[datetime]
    fecha_ultima_entrada: Optional[datetime]
    fecha_ultimo_movimiento: Optional[datetime]
    fecha_creacion: Optional[datetime]

    class Config:
        from_attributes = True


# Funciones auxiliares
def vehiculo_to_response(vehiculo: Vehiculo, db: Session) -> VehiculoResponse:
    """Convertir modelo a respuesta"""
    # Obtener etiquetas activas
    etiquetas_activas = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.vehiculo_id == vehiculo.id,
        VehiculoEtiqueta.activa == True
    ).all()

    etiquetas = []
    for ve in etiquetas_activas:
        etiqueta = db.query(Etiqueta).filter(Etiqueta.id == ve.etiqueta_id).first()
        if etiqueta:
            etiquetas.append({
                "id": etiqueta.id,
                "nombre": etiqueta.nombre,
                "color": etiqueta.color,
                "fecha_asignacion": ve.fecha_asignacion
            })

    # Obtener campos personalizados
    campos = {}
    for valor in vehiculo.campos_personalizados:
        campo = db.query(CampoPersonalizado).filter(CampoPersonalizado.id == valor.campo_id).first()
        if campo:
            campos[campo.nombre] = {
                "etiqueta": campo.etiqueta,
                "valor": valor.valor,
                "tipo": campo.tipo
            }

    # Zona actual
    zona = None
    if vehiculo.zona_actual:
        zona = {
            "id": vehiculo.zona_actual.id,
            "nombre": vehiculo.zona_actual.nombre,
            "codigo": vehiculo.zona_actual.codigo
        }

    return VehiculoResponse(
        id=vehiculo.id,
        matricula=vehiculo.matricula,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        color=vehiculo.color,
        año=vehiculo.año,
        vin=vehiculo.vin,
        cliente_nombre=vehiculo.cliente_nombre,
        cliente_telefono=vehiculo.cliente_telefono,
        cliente_email=vehiculo.cliente_email,
        notas=vehiculo.notas,
        activo=vehiculo.activo,
        en_instalaciones=vehiculo.en_instalaciones,
        zona_actual=zona,
        etiquetas=etiquetas,
        campos_personalizados=campos,
        fecha_primera_entrada=vehiculo.fecha_primera_entrada,
        fecha_ultima_entrada=vehiculo.fecha_ultima_entrada,
        fecha_ultimo_movimiento=vehiculo.fecha_ultimo_movimiento,
        fecha_creacion=vehiculo.fecha_creacion
    )


# Endpoints
@router.get("/", response_model=List[VehiculoResponse])
async def listar_vehiculos(
    buscar: Optional[str] = None,
    en_instalaciones: Optional[bool] = None,
    activo: Optional[bool] = True,
    zona_id: Optional[int] = None,
    etiqueta_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar vehículos con filtros"""
    query = db.query(Vehiculo)

    if activo is not None:
        query = query.filter(Vehiculo.activo == activo)

    if en_instalaciones is not None:
        query = query.filter(Vehiculo.en_instalaciones == en_instalaciones)

    if zona_id is not None:
        query = query.filter(Vehiculo.zona_actual_id == zona_id)

    if buscar:
        query = query.filter(
            or_(
                Vehiculo.matricula.ilike(f"%{buscar}%"),
                Vehiculo.marca.ilike(f"%{buscar}%"),
                Vehiculo.modelo.ilike(f"%{buscar}%"),
                Vehiculo.cliente_nombre.ilike(f"%{buscar}%")
            )
        )

    if etiqueta_id is not None:
        # Filtrar por etiqueta
        vehiculo_ids = db.query(VehiculoEtiqueta.vehiculo_id).filter(
            VehiculoEtiqueta.etiqueta_id == etiqueta_id,
            VehiculoEtiqueta.activa == True
        ).subquery()
        query = query.filter(Vehiculo.id.in_(vehiculo_ids))

    vehiculos = query.order_by(Vehiculo.fecha_ultimo_movimiento.desc()).offset(skip).limit(limit).all()

    return [vehiculo_to_response(v, db) for v in vehiculos]


@router.get("/buscar/{matricula}", response_model=VehiculoResponse)
async def buscar_por_matricula(
    matricula: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar vehículo por matrícula exacta"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.matricula == matricula.upper()).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return vehiculo_to_response(vehiculo, db)


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(
    vehiculo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un vehículo por ID"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return vehiculo_to_response(vehiculo, db)


@router.post("/", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
async def crear_vehiculo(
    vehiculo_data: VehiculoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo vehículo"""
    # Normalizar matrícula
    matricula = vehiculo_data.matricula.upper().replace(" ", "").replace("-", "")

    # Verificar si ya existe
    existente = db.query(Vehiculo).filter(Vehiculo.matricula == matricula).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un vehículo con esta matrícula"
        )

    nuevo_vehiculo = Vehiculo(
        matricula=matricula,
        marca=vehiculo_data.marca,
        modelo=vehiculo_data.modelo,
        color=vehiculo_data.color,
        año=vehiculo_data.año,
        vin=vehiculo_data.vin,
        cliente_nombre=vehiculo_data.cliente_nombre,
        cliente_telefono=vehiculo_data.cliente_telefono,
        cliente_email=vehiculo_data.cliente_email,
        notas=vehiculo_data.notas
    )

    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    # Guardar campos personalizados
    if vehiculo_data.campos_personalizados:
        for campo_id, valor in vehiculo_data.campos_personalizados.items():
            nuevo_valor = ValorCampoPersonalizado(
                vehiculo_id=nuevo_vehiculo.id,
                campo_id=int(campo_id),
                valor=str(valor)
            )
            db.add(nuevo_valor)
        db.commit()
        db.refresh(nuevo_vehiculo)

    return vehiculo_to_response(nuevo_vehiculo, db)


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
async def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo_data: VehiculoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un vehículo"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # Actualizar campos base
    if vehiculo_data.marca is not None:
        vehiculo.marca = vehiculo_data.marca
    if vehiculo_data.modelo is not None:
        vehiculo.modelo = vehiculo_data.modelo
    if vehiculo_data.color is not None:
        vehiculo.color = vehiculo_data.color
    if vehiculo_data.año is not None:
        vehiculo.año = vehiculo_data.año
    if vehiculo_data.vin is not None:
        vehiculo.vin = vehiculo_data.vin
    if vehiculo_data.cliente_nombre is not None:
        vehiculo.cliente_nombre = vehiculo_data.cliente_nombre
    if vehiculo_data.cliente_telefono is not None:
        vehiculo.cliente_telefono = vehiculo_data.cliente_telefono
    if vehiculo_data.cliente_email is not None:
        vehiculo.cliente_email = vehiculo_data.cliente_email
    if vehiculo_data.notas is not None:
        vehiculo.notas = vehiculo_data.notas
    if vehiculo_data.activo is not None:
        vehiculo.activo = vehiculo_data.activo

    # Actualizar campos personalizados
    if vehiculo_data.campos_personalizados:
        for campo_id, valor in vehiculo_data.campos_personalizados.items():
            # Buscar si existe
            valor_existente = db.query(ValorCampoPersonalizado).filter(
                ValorCampoPersonalizado.vehiculo_id == vehiculo_id,
                ValorCampoPersonalizado.campo_id == int(campo_id)
            ).first()

            if valor_existente:
                valor_existente.valor = str(valor)
            else:
                nuevo_valor = ValorCampoPersonalizado(
                    vehiculo_id=vehiculo_id,
                    campo_id=int(campo_id),
                    valor=str(valor)
                )
                db.add(nuevo_valor)

    db.commit()
    db.refresh(vehiculo)

    return vehiculo_to_response(vehiculo, db)


@router.post("/{vehiculo_id}/etiquetas")
async def asignar_etiqueta(
    vehiculo_id: int,
    etiqueta_data: EtiquetaAsignar,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asignar una etiqueta a un vehículo"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    etiqueta = db.query(Etiqueta).filter(Etiqueta.id == etiqueta_data.etiqueta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    # Verificar si ya está asignada
    existente = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.vehiculo_id == vehiculo_id,
        VehiculoEtiqueta.etiqueta_id == etiqueta_data.etiqueta_id,
        VehiculoEtiqueta.activa == True
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta etiqueta ya está asignada al vehículo"
        )

    nueva_asignacion = VehiculoEtiqueta(
        vehiculo_id=vehiculo_id,
        etiqueta_id=etiqueta_data.etiqueta_id,
        asignado_por_id=current_user.id
    )

    db.add(nueva_asignacion)
    db.commit()

    return {"mensaje": f"Etiqueta '{etiqueta.nombre}' asignada al vehículo {vehiculo.matricula}"}


@router.delete("/{vehiculo_id}/etiquetas/{etiqueta_id}")
async def quitar_etiqueta(
    vehiculo_id: int,
    etiqueta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quitar una etiqueta de un vehículo"""
    asignacion = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.vehiculo_id == vehiculo_id,
        VehiculoEtiqueta.etiqueta_id == etiqueta_id,
        VehiculoEtiqueta.activa == True
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Etiqueta no asignada a este vehículo")

    asignacion.activa = False
    asignacion.fecha_remocion = datetime.utcnow()
    db.commit()

    return {"mensaje": "Etiqueta removida correctamente"}


@router.get("/{vehiculo_id}/historial")
async def historial_vehiculo(
    vehiculo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener historial completo de un vehículo (movimientos y etiquetas)"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # Historial de etiquetas
    etiquetas_historial = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.vehiculo_id == vehiculo_id
    ).order_by(VehiculoEtiqueta.fecha_asignacion.desc()).all()

    historial_etiquetas = []
    for ve in etiquetas_historial:
        etiqueta = db.query(Etiqueta).filter(Etiqueta.id == ve.etiqueta_id).first()
        if etiqueta:
            historial_etiquetas.append({
                "etiqueta": etiqueta.nombre,
                "color": etiqueta.color,
                "activa": ve.activa,
                "fecha_asignacion": ve.fecha_asignacion,
                "fecha_remocion": ve.fecha_remocion
            })

    return {
        "vehiculo": {
            "id": vehiculo.id,
            "matricula": vehiculo.matricula
        },
        "historial_etiquetas": historial_etiquetas,
        "movimientos": []  # Se llenará desde el endpoint de movimientos
    }
