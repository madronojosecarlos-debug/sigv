"""
Sistema de Etiquetas de Proceso
- Totalmente personalizable (crear, editar, eliminar)
- Colores personalizables
- Un vehículo puede tener múltiples etiquetas
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Etiqueta(Base):
    """
    Etiquetas de proceso personalizables.
    Ejemplos: "Recepción", "Esperando piezas", "En reparación", "Listo"
    """
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#3498db")  # Color hexadecimal
    descripcion = Column(String(255))
    icono = Column(String(50))  # Nombre del icono (opcional)
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)  # Para ordenar en la interfaz

    # Si es una etiqueta "especial" del sistema
    es_sistema = Column(Boolean, default=False)  # Ej: "Entregado" no se puede borrar

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    vehiculos = relationship("VehiculoEtiqueta", back_populates="etiqueta", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Etiqueta {self.nombre}>"


class VehiculoEtiqueta(Base):
    """
    Relación muchos a muchos entre vehículos y etiquetas.
    Guarda historial de cuándo se asignó cada etiqueta.
    """
    __tablename__ = "vehiculo_etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    etiqueta_id = Column(Integer, ForeignKey("etiquetas.id"), nullable=False)
    activa = Column(Boolean, default=True)  # False = etiqueta removida pero guardamos historial

    # Quién asignó la etiqueta
    asignado_por_id = Column(Integer, ForeignKey("usuarios.id"))

    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_remocion = Column(DateTime(timezone=True))  # Cuando se quitó

    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="etiquetas")
    etiqueta = relationship("Etiqueta", back_populates="vehiculos")

    def __repr__(self):
        return f"<VehiculoEtiqueta vehiculo={self.vehiculo_id} etiqueta={self.etiqueta_id}>"
