"""
Endpoints de Campos Personalizados
- Permite añadir/quitar campos dinámicos a los vehículos
- CRUD completo
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.vehiculo import CampoPersonalizado, ValorCampoPersonalizado
from ..models.usuario import Usuario
from .auth import get_current_user, get_current_admin

router = APIRouter()


# Schemas
class CampoCreate(BaseModel):
    nombre: str  # Identificador único (sin espacios, minúsculas)
    etiqueta: str  # Nombre visible "Número de Orden"
    tipo: str = "texto"  # texto, numero, fecha, booleano, seleccion
    opciones: Optional[List[str]] = None  # Para tipo seleccion
    obligatorio: bool = False
    orden: int = 0


class CampoUpdate(BaseModel):
    etiqueta: Optional[str] = None
    tipo: Optional[str] = None
    opciones: Optional[List[str]] = None
    obligatorio: Optional[bool] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class CampoResponse(BaseModel):
    id: int
    nombre: str
    etiqueta: str
    tipo: str
    opciones: Optional[List[str]]
    obligatorio: bool
    activo: bool
    orden: int

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[CampoResponse])
async def listar_campos(
    activo: Optional[bool] = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todos los campos personalizados"""
    query = db.query(CampoPersonalizado)

    if activo is not None:
        query = query.filter(CampoPersonalizado.activo == activo)

    campos = query.order_by(CampoPersonalizado.orden, CampoPersonalizado.etiqueta).all()

    return [
        CampoResponse(
            id=c.id,
            nombre=c.nombre,
            etiqueta=c.etiqueta,
            tipo=c.tipo,
            opciones=c.opciones,
            obligatorio=c.obligatorio,
            activo=c.activo,
            orden=c.orden
        )
        for c in campos
    ]


@router.get("/{campo_id}", response_model=CampoResponse)
async def obtener_campo(
    campo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un campo por ID"""
    campo = db.query(CampoPersonalizado).filter(CampoPersonalizado.id == campo_id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")

    return CampoResponse(
        id=campo.id,
        nombre=campo.nombre,
        etiqueta=campo.etiqueta,
        tipo=campo.tipo,
        opciones=campo.opciones,
        obligatorio=campo.obligatorio,
        activo=campo.activo,
        orden=campo.orden
    )


@router.post("/", response_model=CampoResponse, status_code=status.HTTP_201_CREATED)
async def crear_campo(
    campo_data: CampoCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear un nuevo campo personalizado (solo admin)"""
    # Normalizar nombre
    nombre = campo_data.nombre.lower().replace(" ", "_").replace("-", "_")

    # Verificar nombre único
    if db.query(CampoPersonalizado).filter(CampoPersonalizado.nombre == nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un campo con este nombre"
        )

    # Validar tipo
    tipos_validos = ["texto", "numero", "fecha", "booleano", "seleccion"]
    if campo_data.tipo not in tipos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Opciones: {', '.join(tipos_validos)}"
        )

    # Si es selección, debe tener opciones
    if campo_data.tipo == "seleccion" and not campo_data.opciones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los campos de tipo 'seleccion' requieren opciones"
        )

    nuevo_campo = CampoPersonalizado(
        nombre=nombre,
        etiqueta=campo_data.etiqueta,
        tipo=campo_data.tipo,
        opciones=campo_data.opciones,
        obligatorio=campo_data.obligatorio,
        orden=campo_data.orden
    )

    db.add(nuevo_campo)
    db.commit()
    db.refresh(nuevo_campo)

    return CampoResponse(
        id=nuevo_campo.id,
        nombre=nuevo_campo.nombre,
        etiqueta=nuevo_campo.etiqueta,
        tipo=nuevo_campo.tipo,
        opciones=nuevo_campo.opciones,
        obligatorio=nuevo_campo.obligatorio,
        activo=nuevo_campo.activo,
        orden=nuevo_campo.orden
    )


@router.put("/{campo_id}", response_model=CampoResponse)
async def actualizar_campo(
    campo_id: int,
    campo_data: CampoUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar un campo personalizado (solo admin)"""
    campo = db.query(CampoPersonalizado).filter(CampoPersonalizado.id == campo_id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")

    if campo_data.etiqueta is not None:
        campo.etiqueta = campo_data.etiqueta

    if campo_data.tipo is not None:
        tipos_validos = ["texto", "numero", "fecha", "booleano", "seleccion"]
        if campo_data.tipo not in tipos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Opciones: {', '.join(tipos_validos)}"
            )
        campo.tipo = campo_data.tipo

    if campo_data.opciones is not None:
        campo.opciones = campo_data.opciones

    if campo_data.obligatorio is not None:
        campo.obligatorio = campo_data.obligatorio

    if campo_data.orden is not None:
        campo.orden = campo_data.orden

    if campo_data.activo is not None:
        campo.activo = campo_data.activo

    db.commit()
    db.refresh(campo)

    return CampoResponse(
        id=campo.id,
        nombre=campo.nombre,
        etiqueta=campo.etiqueta,
        tipo=campo.tipo,
        opciones=campo.opciones,
        obligatorio=campo.obligatorio,
        activo=campo.activo,
        orden=campo.orden
    )


@router.delete("/{campo_id}")
async def eliminar_campo(
    campo_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Desactivar un campo personalizado (solo admin)"""
    campo = db.query(CampoPersonalizado).filter(CampoPersonalizado.id == campo_id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")

    campo.activo = False
    db.commit()

    return {"mensaje": f"Campo '{campo.etiqueta}' desactivado correctamente"}


# Campos predefinidos sugeridos
@router.post("/inicializar-predefinidos")
async def inicializar_campos_predefinidos(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear campos predefinidos comunes para un taller"""
    campos_predefinidos = [
        {
            "nombre": "numero_orden",
            "etiqueta": "Número de Orden",
            "tipo": "texto",
            "orden": 1
        },
        {
            "nombre": "compania_seguros",
            "etiqueta": "Compañía de Seguros",
            "tipo": "texto",
            "orden": 2
        },
        {
            "nombre": "numero_siniestro",
            "etiqueta": "Número de Siniestro",
            "tipo": "texto",
            "orden": 3
        },
        {
            "nombre": "perito_asignado",
            "etiqueta": "Perito Asignado",
            "tipo": "texto",
            "orden": 4
        },
        {
            "nombre": "fecha_cita_perito",
            "etiqueta": "Fecha Cita Perito",
            "tipo": "fecha",
            "orden": 5
        },
        {
            "nombre": "presupuesto",
            "etiqueta": "Presupuesto (€)",
            "tipo": "numero",
            "orden": 6
        },
        {
            "nombre": "vehiculo_cortesia",
            "etiqueta": "Vehículo de Cortesía",
            "tipo": "booleano",
            "orden": 7
        },
        {
            "nombre": "tipo_reparacion",
            "etiqueta": "Tipo de Reparación",
            "tipo": "seleccion",
            "opciones": ["Chapa y pintura", "Mecánica", "Electricidad", "ITV", "Mantenimiento", "Otro"],
            "orden": 8
        },
        {
            "nombre": "kilometraje",
            "etiqueta": "Kilometraje",
            "tipo": "numero",
            "orden": 9
        },
        {
            "nombre": "fecha_estimada_entrega",
            "etiqueta": "Fecha Estimada de Entrega",
            "tipo": "fecha",
            "orden": 10
        }
    ]

    creados = 0
    existentes = 0

    for campo_data in campos_predefinidos:
        existente = db.query(CampoPersonalizado).filter(
            CampoPersonalizado.nombre == campo_data["nombre"]
        ).first()

        if existente:
            existentes += 1
            continue

        nuevo_campo = CampoPersonalizado(**campo_data)
        db.add(nuevo_campo)
        creados += 1

    db.commit()

    return {
        "mensaje": f"Campos predefinidos procesados",
        "creados": creados,
        "ya_existentes": existentes
    }
