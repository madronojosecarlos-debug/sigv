"""
Endpoints de Gestión de Zonas y Cámaras
- CRUD de zonas (Campa, Taller, etc.)
- CRUD de cámaras
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.zona import Zona, Camara
from ..models.vehiculo import Vehiculo
from ..models.usuario import Usuario
from .auth import get_current_user, get_current_admin

router = APIRouter()


# Schemas
class ZonaCreate(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    tipo: str = "campa"  # entrada, campa, taller
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    ancho: Optional[float] = None
    alto: Optional[float] = None
    color: str = "#95a5a6"


class ZonaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    ancho: Optional[float] = None
    alto: Optional[float] = None
    color: Optional[str] = None
    activo: Optional[bool] = None


class ZonaResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    descripcion: Optional[str]
    tipo: str
    pos_x: Optional[float]
    pos_y: Optional[float]
    ancho: Optional[float]
    alto: Optional[float]
    color: str
    activo: bool
    cantidad_vehiculos: int = 0
    camaras: List[dict] = []

    class Config:
        from_attributes = True


class CamaraCreate(BaseModel):
    nombre: str
    codigo: str
    tipo: str  # lpr, vigilancia
    zona_id: Optional[int] = None
    ip: Optional[str] = None
    puerto: Optional[int] = None
    url_stream: Optional[str] = None
    direccion: Optional[str] = None  # entrada, salida, ambos
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    angulo: Optional[float] = None


class CamaraUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    zona_id: Optional[int] = None
    ip: Optional[str] = None
    puerto: Optional[int] = None
    url_stream: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    angulo: Optional[float] = None


class CamaraResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    tipo: str
    zona_id: Optional[int]
    zona_nombre: Optional[str] = None
    ip: Optional[str]
    puerto: Optional[int]
    url_stream: Optional[str]
    direccion: Optional[str]
    activo: bool
    online: bool
    pos_x: Optional[float]
    pos_y: Optional[float]
    angulo: Optional[float]

    class Config:
        from_attributes = True


# Endpoints de Zonas
@router.get("/", response_model=List[ZonaResponse])
async def listar_zonas(
    activo: Optional[bool] = True,
    tipo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todas las zonas"""
    query = db.query(Zona)

    if activo is not None:
        query = query.filter(Zona.activo == activo)

    if tipo:
        query = query.filter(Zona.tipo == tipo)

    zonas = query.order_by(Zona.orden, Zona.nombre).all()

    result = []
    for zona in zonas:
        # Contar vehículos en esta zona
        cantidad = db.query(Vehiculo).filter(
            Vehiculo.zona_actual_id == zona.id,
            Vehiculo.en_instalaciones == True
        ).count()

        # Obtener cámaras
        camaras = db.query(Camara).filter(Camara.zona_id == zona.id).all()
        camaras_list = [{"id": c.id, "codigo": c.codigo, "tipo": c.tipo, "online": c.online} for c in camaras]

        result.append(ZonaResponse(
            id=zona.id,
            nombre=zona.nombre,
            codigo=zona.codigo,
            descripcion=zona.descripcion,
            tipo=zona.tipo,
            pos_x=zona.pos_x,
            pos_y=zona.pos_y,
            ancho=zona.ancho,
            alto=zona.alto,
            color=zona.color,
            activo=zona.activo,
            cantidad_vehiculos=cantidad,
            camaras=camaras_list
        ))

    return result


@router.get("/{zona_id}", response_model=ZonaResponse)
async def obtener_zona(
    zona_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una zona por ID"""
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    cantidad = db.query(Vehiculo).filter(
        Vehiculo.zona_actual_id == zona.id,
        Vehiculo.en_instalaciones == True
    ).count()

    camaras = db.query(Camara).filter(Camara.zona_id == zona.id).all()
    camaras_list = [{"id": c.id, "codigo": c.codigo, "tipo": c.tipo, "online": c.online} for c in camaras]

    return ZonaResponse(
        id=zona.id,
        nombre=zona.nombre,
        codigo=zona.codigo,
        descripcion=zona.descripcion,
        tipo=zona.tipo,
        pos_x=zona.pos_x,
        pos_y=zona.pos_y,
        ancho=zona.ancho,
        alto=zona.alto,
        color=zona.color,
        activo=zona.activo,
        cantidad_vehiculos=cantidad,
        camaras=camaras_list
    )


@router.post("/", response_model=ZonaResponse, status_code=status.HTTP_201_CREATED)
async def crear_zona(
    zona_data: ZonaCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear una nueva zona (solo admin)"""
    # Verificar código único
    if db.query(Zona).filter(Zona.codigo == zona_data.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una zona con este código"
        )

    nueva_zona = Zona(
        nombre=zona_data.nombre,
        codigo=zona_data.codigo.upper(),
        descripcion=zona_data.descripcion,
        tipo=zona_data.tipo,
        pos_x=zona_data.pos_x,
        pos_y=zona_data.pos_y,
        ancho=zona_data.ancho,
        alto=zona_data.alto,
        color=zona_data.color
    )

    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)

    return ZonaResponse(
        id=nueva_zona.id,
        nombre=nueva_zona.nombre,
        codigo=nueva_zona.codigo,
        descripcion=nueva_zona.descripcion,
        tipo=nueva_zona.tipo,
        pos_x=nueva_zona.pos_x,
        pos_y=nueva_zona.pos_y,
        ancho=nueva_zona.ancho,
        alto=nueva_zona.alto,
        color=nueva_zona.color,
        activo=nueva_zona.activo,
        cantidad_vehiculos=0,
        camaras=[]
    )


@router.put("/{zona_id}", response_model=ZonaResponse)
async def actualizar_zona(
    zona_id: int,
    zona_data: ZonaUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar una zona (solo admin)"""
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    if zona_data.nombre is not None:
        zona.nombre = zona_data.nombre
    if zona_data.descripcion is not None:
        zona.descripcion = zona_data.descripcion
    if zona_data.tipo is not None:
        zona.tipo = zona_data.tipo
    if zona_data.pos_x is not None:
        zona.pos_x = zona_data.pos_x
    if zona_data.pos_y is not None:
        zona.pos_y = zona_data.pos_y
    if zona_data.ancho is not None:
        zona.ancho = zona_data.ancho
    if zona_data.alto is not None:
        zona.alto = zona_data.alto
    if zona_data.color is not None:
        zona.color = zona_data.color
    if zona_data.activo is not None:
        zona.activo = zona_data.activo

    db.commit()
    db.refresh(zona)

    cantidad = db.query(Vehiculo).filter(Vehiculo.zona_actual_id == zona.id).count()
    camaras = db.query(Camara).filter(Camara.zona_id == zona.id).all()
    camaras_list = [{"id": c.id, "codigo": c.codigo, "tipo": c.tipo, "online": c.online} for c in camaras]

    return ZonaResponse(
        id=zona.id,
        nombre=zona.nombre,
        codigo=zona.codigo,
        descripcion=zona.descripcion,
        tipo=zona.tipo,
        pos_x=zona.pos_x,
        pos_y=zona.pos_y,
        ancho=zona.ancho,
        alto=zona.alto,
        color=zona.color,
        activo=zona.activo,
        cantidad_vehiculos=cantidad,
        camaras=camaras_list
    )


# Endpoints de Cámaras
@router.get("/camaras/", response_model=List[CamaraResponse])
async def listar_camaras(
    activo: Optional[bool] = True,
    tipo: Optional[str] = None,
    zona_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todas las cámaras"""
    query = db.query(Camara)

    if activo is not None:
        query = query.filter(Camara.activo == activo)
    if tipo:
        query = query.filter(Camara.tipo == tipo)
    if zona_id:
        query = query.filter(Camara.zona_id == zona_id)

    camaras = query.all()

    result = []
    for camara in camaras:
        zona_nombre = None
        if camara.zona:
            zona_nombre = camara.zona.nombre

        result.append(CamaraResponse(
            id=camara.id,
            nombre=camara.nombre,
            codigo=camara.codigo,
            tipo=camara.tipo,
            zona_id=camara.zona_id,
            zona_nombre=zona_nombre,
            ip=camara.ip,
            puerto=camara.puerto,
            url_stream=camara.url_stream,
            direccion=camara.direccion,
            activo=camara.activo,
            online=camara.online,
            pos_x=camara.pos_x,
            pos_y=camara.pos_y,
            angulo=camara.angulo
        ))

    return result


@router.post("/camaras/", response_model=CamaraResponse, status_code=status.HTTP_201_CREATED)
async def crear_camara(
    camara_data: CamaraCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear una nueva cámara (solo admin)"""
    # Verificar código único
    if db.query(Camara).filter(Camara.codigo == camara_data.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cámara con este código"
        )

    nueva_camara = Camara(
        nombre=camara_data.nombre,
        codigo=camara_data.codigo.upper(),
        tipo=camara_data.tipo,
        zona_id=camara_data.zona_id,
        ip=camara_data.ip,
        puerto=camara_data.puerto,
        url_stream=camara_data.url_stream,
        direccion=camara_data.direccion,
        pos_x=camara_data.pos_x,
        pos_y=camara_data.pos_y,
        angulo=camara_data.angulo
    )

    db.add(nueva_camara)
    db.commit()
    db.refresh(nueva_camara)

    return CamaraResponse(
        id=nueva_camara.id,
        nombre=nueva_camara.nombre,
        codigo=nueva_camara.codigo,
        tipo=nueva_camara.tipo,
        zona_id=nueva_camara.zona_id,
        zona_nombre=None,
        ip=nueva_camara.ip,
        puerto=nueva_camara.puerto,
        url_stream=nueva_camara.url_stream,
        direccion=nueva_camara.direccion,
        activo=nueva_camara.activo,
        online=nueva_camara.online,
        pos_x=nueva_camara.pos_x,
        pos_y=nueva_camara.pos_y,
        angulo=nueva_camara.angulo
    )


@router.put("/camaras/{camara_id}", response_model=CamaraResponse)
async def actualizar_camara(
    camara_id: int,
    camara_data: CamaraUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar una cámara (solo admin)"""
    camara = db.query(Camara).filter(Camara.id == camara_id).first()
    if not camara:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    if camara_data.nombre is not None:
        camara.nombre = camara_data.nombre
    if camara_data.tipo is not None:
        camara.tipo = camara_data.tipo
    if camara_data.zona_id is not None:
        camara.zona_id = camara_data.zona_id
    if camara_data.ip is not None:
        camara.ip = camara_data.ip
    if camara_data.puerto is not None:
        camara.puerto = camara_data.puerto
    if camara_data.url_stream is not None:
        camara.url_stream = camara_data.url_stream
    if camara_data.direccion is not None:
        camara.direccion = camara_data.direccion
    if camara_data.activo is not None:
        camara.activo = camara_data.activo
    if camara_data.pos_x is not None:
        camara.pos_x = camara_data.pos_x
    if camara_data.pos_y is not None:
        camara.pos_y = camara_data.pos_y
    if camara_data.angulo is not None:
        camara.angulo = camara_data.angulo

    db.commit()
    db.refresh(camara)

    zona_nombre = None
    if camara.zona:
        zona_nombre = camara.zona.nombre

    return CamaraResponse(
        id=camara.id,
        nombre=camara.nombre,
        codigo=camara.codigo,
        tipo=camara.tipo,
        zona_id=camara.zona_id,
        zona_nombre=zona_nombre,
        ip=camara.ip,
        puerto=camara.puerto,
        url_stream=camara.url_stream,
        direccion=camara.direccion,
        activo=camara.activo,
        online=camara.online,
        pos_x=camara.pos_x,
        pos_y=camara.pos_y,
        angulo=camara.angulo
    )
