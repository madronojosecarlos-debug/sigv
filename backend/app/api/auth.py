"""
Endpoints de Autenticación
- Login
- Registro (solo admin)
- Verificar token
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..database import get_db
from ..config import settings
from ..models.usuario import Usuario, Rol

router = APIRouter()

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: dict


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# Funciones de utilidad
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credentials_exception
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    return usuario


async def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol != Rol.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


# Endpoints
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token de acceso"""
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )

    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.utcnow()
    db.commit()

    # Crear token
    access_token = create_access_token(data={"sub": usuario.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellidos": usuario.apellidos,
            "rol": usuario.rol.value
        }
    }


@router.get("/me")
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "apellidos": current_user.apellidos,
        "rol": current_user.rol.value,
        "telefono": current_user.telefono,
        "ultimo_acceso": current_user.ultimo_acceso
    }


@router.post("/cambiar-password")
async def cambiar_password(
    password_actual: str,
    password_nuevo: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    if not verify_password(password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    current_user.password_hash = get_password_hash(password_nuevo)
    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}
