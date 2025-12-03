"""
Endpoints de Gestión de Etiquetas de Proceso
- CRUD completo de etiquetas
- Administradores crean/editan/eliminan
- Todos pueden ver y asignar
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.etiqueta import Etiqueta, VehiculoEtiqueta
from ..models.usuario import Usuario
from .auth import get_current_user, get_current_admin

router = APIRouter()


# Schemas
class EtiquetaCreate(BaseModel):
    nombre: str
    color: str = "#3498db"
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: int = 0


class EtiquetaUpdate(BaseModel):
    nombre: Optional[str] = None
    color: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class EtiquetaResponse(BaseModel):
    id: int
    nombre: str
    color: str
    descripcion: Optional[str]
    icono: Optional[str]
    activo: bool
    orden: int
    es_sistema: bool
    cantidad_vehiculos: int = 0

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[EtiquetaResponse])
async def listar_etiquetas(
    activo: Optional[bool] = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todas las etiquetas"""
    query = db.query(Etiqueta)

    if activo is not None:
        query = query.filter(Etiqueta.activo == activo)

    etiquetas = query.order_by(Etiqueta.orden, Etiqueta.nombre).all()

    result = []
    for etiqueta in etiquetas:
        # Contar vehículos con esta etiqueta activa
        cantidad = db.query(VehiculoEtiqueta).filter(
            VehiculoEtiqueta.etiqueta_id == etiqueta.id,
            VehiculoEtiqueta.activa == True
        ).count()

        result.append(EtiquetaResponse(
            id=etiqueta.id,
            nombre=etiqueta.nombre,
            color=etiqueta.color,
            descripcion=etiqueta.descripcion,
            icono=etiqueta.icono,
            activo=etiqueta.activo,
            orden=etiqueta.orden,
            es_sistema=etiqueta.es_sistema,
            cantidad_vehiculos=cantidad
        ))

    return result


@router.get("/{etiqueta_id}", response_model=EtiquetaResponse)
async def obtener_etiqueta(
    etiqueta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una etiqueta por ID"""
    etiqueta = db.query(Etiqueta).filter(Etiqueta.id == etiqueta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    cantidad = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.etiqueta_id == etiqueta.id,
        VehiculoEtiqueta.activa == True
    ).count()

    return EtiquetaResponse(
        id=etiqueta.id,
        nombre=etiqueta.nombre,
        color=etiqueta.color,
        descripcion=etiqueta.descripcion,
        icono=etiqueta.icono,
        activo=etiqueta.activo,
        orden=etiqueta.orden,
        es_sistema=etiqueta.es_sistema,
        cantidad_vehiculos=cantidad
    )


@router.post("/", response_model=EtiquetaResponse, status_code=status.HTTP_201_CREATED)
async def crear_etiqueta(
    etiqueta_data: EtiquetaCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear una nueva etiqueta (solo admin)"""
    # Verificar nombre único
    if db.query(Etiqueta).filter(Etiqueta.nombre == etiqueta_data.nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una etiqueta con este nombre"
        )

    nueva_etiqueta = Etiqueta(
        nombre=etiqueta_data.nombre,
        color=etiqueta_data.color,
        descripcion=etiqueta_data.descripcion,
        icono=etiqueta_data.icono,
        orden=etiqueta_data.orden
    )

    db.add(nueva_etiqueta)
    db.commit()
    db.refresh(nueva_etiqueta)

    return EtiquetaResponse(
        id=nueva_etiqueta.id,
        nombre=nueva_etiqueta.nombre,
        color=nueva_etiqueta.color,
        descripcion=nueva_etiqueta.descripcion,
        icono=nueva_etiqueta.icono,
        activo=nueva_etiqueta.activo,
        orden=nueva_etiqueta.orden,
        es_sistema=nueva_etiqueta.es_sistema,
        cantidad_vehiculos=0
    )


@router.put("/{etiqueta_id}", response_model=EtiquetaResponse)
async def actualizar_etiqueta(
    etiqueta_id: int,
    etiqueta_data: EtiquetaUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar una etiqueta (solo admin)"""
    etiqueta = db.query(Etiqueta).filter(Etiqueta.id == etiqueta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    if etiqueta_data.nombre is not None:
        # Verificar nombre único
        existente = db.query(Etiqueta).filter(
            Etiqueta.nombre == etiqueta_data.nombre,
            Etiqueta.id != etiqueta_id
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una etiqueta con este nombre"
            )
        etiqueta.nombre = etiqueta_data.nombre

    if etiqueta_data.color is not None:
        etiqueta.color = etiqueta_data.color

    if etiqueta_data.descripcion is not None:
        etiqueta.descripcion = etiqueta_data.descripcion

    if etiqueta_data.icono is not None:
        etiqueta.icono = etiqueta_data.icono

    if etiqueta_data.orden is not None:
        etiqueta.orden = etiqueta_data.orden

    if etiqueta_data.activo is not None:
        etiqueta.activo = etiqueta_data.activo

    db.commit()
    db.refresh(etiqueta)

    cantidad = db.query(VehiculoEtiqueta).filter(
        VehiculoEtiqueta.etiqueta_id == etiqueta.id,
        VehiculoEtiqueta.activa == True
    ).count()

    return EtiquetaResponse(
        id=etiqueta.id,
        nombre=etiqueta.nombre,
        color=etiqueta.color,
        descripcion=etiqueta.descripcion,
        icono=etiqueta.icono,
        activo=etiqueta.activo,
        orden=etiqueta.orden,
        es_sistema=etiqueta.es_sistema,
        cantidad_vehiculos=cantidad
    )


@router.delete("/{etiqueta_id}")
async def eliminar_etiqueta(
    etiqueta_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar una etiqueta (solo admin)"""
    etiqueta = db.query(Etiqueta).filter(Etiqueta.id == etiqueta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

    if etiqueta.es_sistema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden eliminar etiquetas del sistema"
        )

    # No eliminamos, solo desactivamos
    etiqueta.activo = False
    db.commit()

    return {"mensaje": f"Etiqueta '{etiqueta.nombre}' desactivada correctamente"}
