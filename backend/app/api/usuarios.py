"""
Endpoints de Gestión de Usuarios
- CRUD de usuarios
- Solo administradores pueden crear/editar/eliminar
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..database import get_db
from ..models.usuario import Usuario, Rol
from .auth import get_current_user, get_current_admin, get_password_hash

router = APIRouter()


# Schemas
class UsuarioCreate(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: Optional[str] = None
    password: str
    rol: str = "mecanico"  # administrador, asesor, mecanico
    telefono: Optional[str] = None


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    rol: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellidos: Optional[str]
    rol: str
    telefono: Optional[str]
    activo: bool
    fecha_creacion: Optional[datetime]
    ultimo_acceso: Optional[datetime]

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    activo: Optional[bool] = None,
    rol: Optional[str] = None,
    buscar: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (filtrable)"""
    query = db.query(Usuario)

    if activo is not None:
        query = query.filter(Usuario.activo == activo)

    if rol:
        query = query.filter(Usuario.rol == Rol(rol))

    if buscar:
        query = query.filter(
            (Usuario.nombre.ilike(f"%{buscar}%")) |
            (Usuario.apellidos.ilike(f"%{buscar}%")) |
            (Usuario.email.ilike(f"%{buscar}%"))
        )

    usuarios = query.offset(skip).limit(limit).all()

    return [
        UsuarioResponse(
            id=u.id,
            email=u.email,
            nombre=u.nombre,
            apellidos=u.apellidos,
            rol=u.rol.value,
            telefono=u.telefono,
            activo=u.activo,
            fecha_creacion=u.fecha_creacion,
            ultimo_acceso=u.ultimo_acceso
        )
        for u in usuarios
    ]


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un usuario por ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        rol=usuario.rol.value,
        telefono=usuario.telefono,
        activo=usuario.activo,
        fecha_creacion=usuario.fecha_creacion,
        ultimo_acceso=usuario.ultimo_acceso
    )


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    usuario_data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear un nuevo usuario (solo admin)"""
    # Verificar que el email no existe
    if db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )

    # Validar rol
    try:
        rol = Rol(usuario_data.rol)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Opciones: administrador, asesor, mecanico"
        )

    # Crear usuario
    nuevo_usuario = Usuario(
        email=usuario_data.email,
        nombre=usuario_data.nombre,
        apellidos=usuario_data.apellidos,
        password_hash=get_password_hash(usuario_data.password),
        rol=rol,
        telefono=usuario_data.telefono
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return UsuarioResponse(
        id=nuevo_usuario.id,
        email=nuevo_usuario.email,
        nombre=nuevo_usuario.nombre,
        apellidos=nuevo_usuario.apellidos,
        rol=nuevo_usuario.rol.value,
        telefono=nuevo_usuario.telefono,
        activo=nuevo_usuario.activo,
        fecha_creacion=nuevo_usuario.fecha_creacion,
        ultimo_acceso=nuevo_usuario.ultimo_acceso
    )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar un usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar campos
    if usuario_data.email is not None:
        # Verificar que el email no existe
        if db.query(Usuario).filter(Usuario.email == usuario_data.email, Usuario.id != usuario_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email"
            )
        usuario.email = usuario_data.email

    if usuario_data.nombre is not None:
        usuario.nombre = usuario_data.nombre

    if usuario_data.apellidos is not None:
        usuario.apellidos = usuario_data.apellidos

    if usuario_data.rol is not None:
        try:
            usuario.rol = Rol(usuario_data.rol)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol inválido"
            )

    if usuario_data.telefono is not None:
        usuario.telefono = usuario_data.telefono

    if usuario_data.activo is not None:
        usuario.activo = usuario_data.activo

    db.commit()
    db.refresh(usuario)

    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        rol=usuario.rol.value,
        telefono=usuario.telefono,
        activo=usuario.activo,
        fecha_creacion=usuario.fecha_creacion,
        ultimo_acceso=usuario.ultimo_acceso
    )


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Desactivar un usuario (solo admin) - No se elimina, solo se desactiva"""
    if usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivarte a ti mismo"
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    db.commit()

    return {"mensaje": f"Usuario {usuario.nombre} desactivado correctamente"}


@router.post("/{usuario_id}/resetear-password")
async def resetear_password(
    usuario_id: int,
    nuevo_password: str,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Resetear contraseña de un usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.password_hash = get_password_hash(nuevo_password)
    db.commit()

    return {"mensaje": f"Contraseña de {usuario.nombre} reseteada correctamente"}
