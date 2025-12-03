"""
Endpoints de Movimientos de Vehículos
- Registro de detecciones LPR
- Registro manual de movimientos
- Historial de movimientos
- Lógica de entrada/salida y cambio de zonas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database import get_db
from ..config import settings
from ..models.movimiento import Movimiento, TipoMovimiento
from ..models.vehiculo import Vehiculo
from ..models.zona import Zona, Camara
from ..models.alerta import Alerta, TipoAlerta
from ..models.usuario import Usuario
from .auth import get_current_user

router = APIRouter()


# Schemas
class DeteccionLPR(BaseModel):
    """Datos que envía una cámara LPR al detectar una matrícula"""
    matricula: str
    camara_codigo: str
    confianza: Optional[float] = None
    imagen_url: Optional[str] = None


class MovimientoManual(BaseModel):
    """Registro manual de movimiento"""
    vehiculo_id: int
    tipo: str  # entrada, salida, cambio_zona
    zona_destino_id: Optional[int] = None
    notas: Optional[str] = None


class MovimientoResponse(BaseModel):
    id: int
    vehiculo_id: int
    matricula: str
    tipo: str
    zona_origen: Optional[dict]
    zona_destino: Optional[dict]
    camara: Optional[dict]
    confianza: Optional[float]
    fecha_hora: datetime
    manual: bool
    registrado_por: Optional[str]
    notas: Optional[str]

    class Config:
        from_attributes = True


# Funciones auxiliares
def procesar_deteccion(
    matricula: str,
    camara: Camara,
    db: Session,
    confianza: float = None,
    imagen_url: str = None
) -> dict:
    """
    Procesa una detección de matrícula y actualiza el estado del vehículo.
    Retorna información sobre la acción realizada.
    """
    matricula_norm = matricula.upper().replace(" ", "").replace("-", "")

    # Buscar o crear vehículo
    vehiculo = db.query(Vehiculo).filter(Vehiculo.matricula == matricula_norm).first()
    vehiculo_nuevo = False

    if not vehiculo:
        # Crear vehículo nuevo
        vehiculo = Vehiculo(matricula=matricula_norm)
        db.add(vehiculo)
        db.flush()
        vehiculo_nuevo = True

        # Crear alerta de matrícula no registrada
        alerta = Alerta(
            tipo=TipoAlerta.ENTRADA_NO_REGISTRADA,
            vehiculo_id=vehiculo.id,
            titulo=f"Matrícula no registrada: {matricula_norm}",
            mensaje=f"Se ha detectado la matrícula {matricula_norm} que no estaba en el sistema. "
                    f"Detectada por cámara {camara.codigo}.",
            prioridad="media"
        )
        db.add(alerta)

    # Determinar tipo de movimiento basado en la cámara y estado actual
    zona_origen_id = vehiculo.zona_actual_id
    zona_destino_id = camara.zona_id
    tipo_movimiento = TipoMovimiento.DETECCION

    if camara.tipo == "lpr":
        if camara.direccion == "entrada" or (camara.direccion == "ambos" and not vehiculo.en_instalaciones):
            # Es una entrada
            tipo_movimiento = TipoMovimiento.ENTRADA
            vehiculo.en_instalaciones = True
            vehiculo.fecha_ultima_entrada = datetime.utcnow()
            if not vehiculo.fecha_primera_entrada:
                vehiculo.fecha_primera_entrada = datetime.utcnow()

        elif camara.direccion == "salida" or (camara.direccion == "ambos" and vehiculo.en_instalaciones):
            # Es una salida
            tipo_movimiento = TipoMovimiento.SALIDA
            vehiculo.en_instalaciones = False
            vehiculo.fecha_ultima_salida = datetime.utcnow()

        elif zona_origen_id != zona_destino_id:
            # Cambio de zona
            tipo_movimiento = TipoMovimiento.CAMBIO_ZONA

    # Actualizar zona y tiempo
    vehiculo.zona_actual_id = zona_destino_id
    vehiculo.fecha_ultimo_movimiento = datetime.utcnow()

    # Registrar movimiento
    movimiento = Movimiento(
        vehiculo_id=vehiculo.id,
        tipo=tipo_movimiento,
        zona_origen_id=zona_origen_id,
        zona_destino_id=zona_destino_id,
        camara_id=camara.id,
        matricula_detectada=matricula_norm,
        confianza=confianza,
        imagen_url=imagen_url
    )
    db.add(movimiento)
    db.commit()

    return {
        "accion": tipo_movimiento.value,
        "vehiculo_id": vehiculo.id,
        "matricula": matricula_norm,
        "vehiculo_nuevo": vehiculo_nuevo,
        "zona_destino": camara.zona.nombre if camara.zona else None
    }


def verificar_posible_entrega(vehiculo_id: int, db: Session):
    """
    Verifica si un vehículo debe marcarse como entregado.
    Si lleva más de 1 hora sin ser detectado después de salir de una zona, se considera entregado.
    """
    tiempo_limite = settings.TIEMPO_ENTREGA_MINUTOS

    # Obtener último movimiento
    ultimo_movimiento = db.query(Movimiento).filter(
        Movimiento.vehiculo_id == vehiculo_id
    ).order_by(desc(Movimiento.fecha_hora)).first()

    if not ultimo_movimiento:
        return

    # Si fue una salida hace más de X minutos
    if ultimo_movimiento.tipo == TipoMovimiento.SALIDA:
        tiempo_desde_salida = datetime.utcnow() - ultimo_movimiento.fecha_hora
        if tiempo_desde_salida > timedelta(minutes=tiempo_limite):
            # Marcar como posible entrega
            vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
            if vehiculo and vehiculo.en_instalaciones:
                vehiculo.en_instalaciones = False

                # Crear alerta
                alerta = Alerta(
                    tipo=TipoAlerta.POSIBLE_ENTREGA,
                    vehiculo_id=vehiculo_id,
                    titulo=f"Posible entrega: {vehiculo.matricula}",
                    mensaje=f"El vehículo {vehiculo.matricula} no ha sido detectado en más de "
                            f"{tiempo_limite} minutos desde su última salida. Se considera entregado.",
                    prioridad="baja"
                )
                db.add(alerta)
                db.commit()


# Endpoints
@router.post("/lpr/detectar")
async def registrar_deteccion_lpr(
    deteccion: DeteccionLPR,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recibir detecciones de las cámaras LPR.
    Este endpoint será llamado por las cámaras/software LPR.
    """
    # Buscar cámara
    camara = db.query(Camara).filter(Camara.codigo == deteccion.camara_codigo.upper()).first()
    if not camara:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cámara {deteccion.camara_codigo} no encontrada"
        )

    if not camara.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cámara desactivada"
        )

    # Procesar detección
    resultado = procesar_deteccion(
        matricula=deteccion.matricula,
        camara=camara,
        db=db,
        confianza=deteccion.confianza,
        imagen_url=deteccion.imagen_url
    )

    return {
        "mensaje": "Detección registrada",
        "resultado": resultado
    }


@router.post("/manual")
async def registrar_movimiento_manual(
    movimiento_data: MovimientoManual,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar un movimiento manualmente"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == movimiento_data.vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # Validar tipo
    try:
        tipo = TipoMovimiento(movimiento_data.tipo)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimiento inválido. Opciones: entrada, salida, cambio_zona"
        )

    zona_origen_id = vehiculo.zona_actual_id
    zona_destino_id = movimiento_data.zona_destino_id

    # Actualizar vehículo según el tipo
    if tipo == TipoMovimiento.ENTRADA:
        vehiculo.en_instalaciones = True
        vehiculo.fecha_ultima_entrada = datetime.utcnow()
        if not vehiculo.fecha_primera_entrada:
            vehiculo.fecha_primera_entrada = datetime.utcnow()
        vehiculo.zona_actual_id = zona_destino_id

    elif tipo == TipoMovimiento.SALIDA:
        vehiculo.en_instalaciones = False
        vehiculo.fecha_ultima_salida = datetime.utcnow()
        zona_destino_id = None
        vehiculo.zona_actual_id = None

    elif tipo == TipoMovimiento.CAMBIO_ZONA:
        if not zona_destino_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere zona_destino_id para cambio de zona"
            )
        vehiculo.zona_actual_id = zona_destino_id

    vehiculo.fecha_ultimo_movimiento = datetime.utcnow()

    # Crear registro
    movimiento = Movimiento(
        vehiculo_id=vehiculo.id,
        tipo=tipo,
        zona_origen_id=zona_origen_id,
        zona_destino_id=zona_destino_id,
        manual=True,
        registrado_por_id=current_user.id,
        notas=movimiento_data.notas
    )

    db.add(movimiento)
    db.commit()

    return {
        "mensaje": "Movimiento registrado",
        "movimiento_id": movimiento.id
    }


@router.get("/vehiculo/{vehiculo_id}", response_model=List[MovimientoResponse])
async def listar_movimientos_vehiculo(
    vehiculo_id: int,
    limit: int = Query(50, ge=1, le=500),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de movimientos de un vehículo"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    movimientos = db.query(Movimiento).filter(
        Movimiento.vehiculo_id == vehiculo_id
    ).order_by(desc(Movimiento.fecha_hora)).limit(limit).all()

    result = []
    for mov in movimientos:
        zona_origen = None
        if mov.zona_origen:
            zona_origen = {"id": mov.zona_origen.id, "nombre": mov.zona_origen.nombre}

        zona_destino = None
        if mov.zona_destino:
            zona_destino = {"id": mov.zona_destino.id, "nombre": mov.zona_destino.nombre}

        camara_info = None
        if mov.camara_id:
            camara = db.query(Camara).filter(Camara.id == mov.camara_id).first()
            if camara:
                camara_info = {"id": camara.id, "codigo": camara.codigo}

        registrado_por = None
        if mov.registrado_por:
            registrado_por = mov.registrado_por.nombre

        result.append(MovimientoResponse(
            id=mov.id,
            vehiculo_id=mov.vehiculo_id,
            matricula=vehiculo.matricula,
            tipo=mov.tipo.value,
            zona_origen=zona_origen,
            zona_destino=zona_destino,
            camara=camara_info,
            confianza=mov.confianza,
            fecha_hora=mov.fecha_hora,
            manual=mov.manual,
            registrado_por=registrado_por,
            notas=mov.notas
        ))

    return result


@router.get("/recientes", response_model=List[MovimientoResponse])
async def listar_movimientos_recientes(
    limit: int = Query(50, ge=1, le=200),
    tipo: Optional[str] = None,
    zona_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar movimientos más recientes"""
    query = db.query(Movimiento)

    if tipo:
        query = query.filter(Movimiento.tipo == TipoMovimiento(tipo))

    if zona_id:
        query = query.filter(
            (Movimiento.zona_origen_id == zona_id) |
            (Movimiento.zona_destino_id == zona_id)
        )

    movimientos = query.order_by(desc(Movimiento.fecha_hora)).limit(limit).all()

    result = []
    for mov in movimientos:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == mov.vehiculo_id).first()

        zona_origen = None
        if mov.zona_origen:
            zona_origen = {"id": mov.zona_origen.id, "nombre": mov.zona_origen.nombre}

        zona_destino = None
        if mov.zona_destino:
            zona_destino = {"id": mov.zona_destino.id, "nombre": mov.zona_destino.nombre}

        camara_info = None
        if mov.camara_id:
            camara = db.query(Camara).filter(Camara.id == mov.camara_id).first()
            if camara:
                camara_info = {"id": camara.id, "codigo": camara.codigo}

        registrado_por = None
        if mov.registrado_por:
            registrado_por = mov.registrado_por.nombre

        result.append(MovimientoResponse(
            id=mov.id,
            vehiculo_id=mov.vehiculo_id,
            matricula=vehiculo.matricula if vehiculo else "N/A",
            tipo=mov.tipo.value,
            zona_origen=zona_origen,
            zona_destino=zona_destino,
            camara=camara_info,
            confianza=mov.confianza,
            fecha_hora=mov.fecha_hora,
            manual=mov.manual,
            registrado_por=registrado_por,
            notas=mov.notas
        ))

    return result
