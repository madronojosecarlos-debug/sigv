"""
Endpoints de Alertas
- Listado de alertas
- Marcar como leída/resuelta
- Generación automática de alertas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database import get_db
from ..config import settings
from ..models.alerta import Alerta, TipoAlerta
from ..models.vehiculo import Vehiculo
from ..models.movimiento import Movimiento
from ..models.usuario import Usuario
from .auth import get_current_user

router = APIRouter()


# Schemas
class AlertaResponse(BaseModel):
    id: int
    tipo: str
    vehiculo_id: Optional[int]
    vehiculo_matricula: Optional[str]
    titulo: str
    mensaje: Optional[str]
    prioridad: str
    leida: bool
    resuelta: bool
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime]

    class Config:
        from_attributes = True


class ResolverAlerta(BaseModel):
    notas: Optional[str] = None


# Funciones auxiliares
def generar_alertas_inactividad(db: Session):
    """
    Genera alertas para vehículos que llevan más de X días sin movimiento.
    Se ejecuta periódicamente.
    """
    dias_limite = settings.ALERTA_INACTIVIDAD_DIAS
    fecha_limite = datetime.utcnow() - timedelta(days=dias_limite)

    # Buscar vehículos inactivos
    vehiculos_inactivos = db.query(Vehiculo).filter(
        Vehiculo.en_instalaciones == True,
        Vehiculo.fecha_ultimo_movimiento < fecha_limite
    ).all()

    alertas_creadas = 0
    for vehiculo in vehiculos_inactivos:
        # Verificar si ya existe una alerta de inactividad no resuelta
        alerta_existente = db.query(Alerta).filter(
            Alerta.vehiculo_id == vehiculo.id,
            Alerta.tipo == TipoAlerta.INACTIVIDAD,
            Alerta.resuelta == False
        ).first()

        if not alerta_existente:
            dias_inactivo = (datetime.utcnow() - vehiculo.fecha_ultimo_movimiento).days

            alerta = Alerta(
                tipo=TipoAlerta.INACTIVIDAD,
                vehiculo_id=vehiculo.id,
                titulo=f"Vehículo inactivo: {vehiculo.matricula}",
                mensaje=f"El vehículo {vehiculo.matricula} lleva {dias_inactivo} días sin movimiento. "
                        f"Último movimiento: {vehiculo.fecha_ultimo_movimiento.strftime('%d/%m/%Y %H:%M')}",
                prioridad="alta"
            )
            db.add(alerta)
            alertas_creadas += 1

    if alertas_creadas > 0:
        db.commit()

    return alertas_creadas


# Endpoints
@router.get("/", response_model=List[AlertaResponse])
async def listar_alertas(
    tipo: Optional[str] = None,
    leida: Optional[bool] = None,
    resuelta: Optional[bool] = False,
    prioridad: Optional[str] = None,
    vehiculo_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar alertas con filtros"""
    query = db.query(Alerta)

    if tipo:
        query = query.filter(Alerta.tipo == TipoAlerta(tipo))

    if leida is not None:
        query = query.filter(Alerta.leida == leida)

    if resuelta is not None:
        query = query.filter(Alerta.resuelta == resuelta)

    if prioridad:
        query = query.filter(Alerta.prioridad == prioridad)

    if vehiculo_id:
        query = query.filter(Alerta.vehiculo_id == vehiculo_id)

    alertas = query.order_by(desc(Alerta.fecha_creacion)).offset(skip).limit(limit).all()

    result = []
    for alerta in alertas:
        vehiculo_matricula = None
        if alerta.vehiculo_id:
            vehiculo = db.query(Vehiculo).filter(Vehiculo.id == alerta.vehiculo_id).first()
            if vehiculo:
                vehiculo_matricula = vehiculo.matricula

        result.append(AlertaResponse(
            id=alerta.id,
            tipo=alerta.tipo.value,
            vehiculo_id=alerta.vehiculo_id,
            vehiculo_matricula=vehiculo_matricula,
            titulo=alerta.titulo,
            mensaje=alerta.mensaje,
            prioridad=alerta.prioridad,
            leida=alerta.leida,
            resuelta=alerta.resuelta,
            fecha_creacion=alerta.fecha_creacion,
            fecha_resolucion=alerta.fecha_resolucion
        ))

    return result


@router.get("/contador")
async def contar_alertas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener contadores de alertas"""
    total = db.query(Alerta).filter(Alerta.resuelta == False).count()
    no_leidas = db.query(Alerta).filter(Alerta.leida == False, Alerta.resuelta == False).count()

    por_prioridad = {
        "critica": db.query(Alerta).filter(Alerta.prioridad == "critica", Alerta.resuelta == False).count(),
        "alta": db.query(Alerta).filter(Alerta.prioridad == "alta", Alerta.resuelta == False).count(),
        "media": db.query(Alerta).filter(Alerta.prioridad == "media", Alerta.resuelta == False).count(),
        "baja": db.query(Alerta).filter(Alerta.prioridad == "baja", Alerta.resuelta == False).count()
    }

    por_tipo = {
        "inactividad": db.query(Alerta).filter(Alerta.tipo == TipoAlerta.INACTIVIDAD, Alerta.resuelta == False).count(),
        "posible_entrega": db.query(Alerta).filter(Alerta.tipo == TipoAlerta.POSIBLE_ENTREGA, Alerta.resuelta == False).count(),
        "entrada_no_registrada": db.query(Alerta).filter(Alerta.tipo == TipoAlerta.ENTRADA_NO_REGISTRADA, Alerta.resuelta == False).count()
    }

    return {
        "total": total,
        "no_leidas": no_leidas,
        "por_prioridad": por_prioridad,
        "por_tipo": por_tipo
    }


@router.get("/{alerta_id}", response_model=AlertaResponse)
async def obtener_alerta(
    alerta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una alerta por ID"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    vehiculo_matricula = None
    if alerta.vehiculo_id:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == alerta.vehiculo_id).first()
        if vehiculo:
            vehiculo_matricula = vehiculo.matricula

    return AlertaResponse(
        id=alerta.id,
        tipo=alerta.tipo.value,
        vehiculo_id=alerta.vehiculo_id,
        vehiculo_matricula=vehiculo_matricula,
        titulo=alerta.titulo,
        mensaje=alerta.mensaje,
        prioridad=alerta.prioridad,
        leida=alerta.leida,
        resuelta=alerta.resuelta,
        fecha_creacion=alerta.fecha_creacion,
        fecha_resolucion=alerta.fecha_resolucion
    )


@router.post("/{alerta_id}/leer")
async def marcar_leida(
    alerta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar una alerta como leída"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    alerta.leida = True
    alerta.fecha_lectura = datetime.utcnow()
    db.commit()

    return {"mensaje": "Alerta marcada como leída"}


@router.post("/{alerta_id}/resolver")
async def resolver_alerta(
    alerta_id: int,
    datos: ResolverAlerta,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolver una alerta"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    alerta.resuelta = True
    alerta.fecha_resolucion = datetime.utcnow()
    alerta.resuelta_por_id = current_user.id
    alerta.notas_resolucion = datos.notas
    db.commit()

    return {"mensaje": "Alerta resuelta"}


@router.post("/generar-inactividad")
async def ejecutar_alertas_inactividad(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ejecutar manualmente la generación de alertas de inactividad"""
    alertas_creadas = generar_alertas_inactividad(db)
    return {"mensaje": f"Se generaron {alertas_creadas} alertas de inactividad"}


@router.post("/marcar-todas-leidas")
async def marcar_todas_leidas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar todas las alertas como leídas"""
    db.query(Alerta).filter(Alerta.leida == False).update({
        Alerta.leida: True,
        Alerta.fecha_lectura: datetime.utcnow()
    })
    db.commit()

    return {"mensaje": "Todas las alertas marcadas como leídas"}
