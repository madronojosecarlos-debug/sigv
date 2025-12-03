"""
Modelo de Usuarios y Roles
- Administradores: gestionan etiquetas, usuarios, configuración
- Trabajadores: usan el sistema, actualizan estados
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class Rol(enum.Enum):
    ADMINISTRADOR = "administrador"
    ASESOR = "asesor"  # Asesor de servicios
    MECANICO = "mecanico"  # Trabajador de taller


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(150))
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(Rol), default=Rol.MECANICO, nullable=False)
    activo = Column(Boolean, default=True)
    telefono = Column(String(20))

    # Auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    ultimo_acceso = Column(DateTime(timezone=True))

    # Relaciones
    movimientos_registrados = relationship("Movimiento", back_populates="registrado_por")

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol.value})>"
