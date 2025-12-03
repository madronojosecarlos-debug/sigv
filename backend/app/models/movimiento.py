"""
Registro de Movimientos de Vehículos
- Cada vez que una cámara detecta una matrícula se registra
- Permite tracking completo del vehículo
- Calcula tiempos de estancia y movimientos entre zonas
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class TipoMovimiento(enum.Enum):
    ENTRADA = "entrada"  # Entra a las instalaciones
    SALIDA = "salida"  # Sale de las instalaciones
    CAMBIO_ZONA = "cambio_zona"  # Se mueve entre zonas internas
    DETECCION = "deteccion"  # Detectado por cámara (sin cambio de zona)


class Movimiento(Base):
    """
    Registro de cada movimiento/detección de un vehículo.
    Es el corazón del sistema de tracking.
    """
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    tipo = Column(Enum(TipoMovimiento), nullable=False)

    # Zonas involucradas
    zona_origen_id = Column(Integer, ForeignKey("zonas.id"))  # De dónde viene
    zona_destino_id = Column(Integer, ForeignKey("zonas.id"))  # A dónde va

    # Cámara que detectó el movimiento
    camara_id = Column(Integer, ForeignKey("camaras.id"))

    # Datos de la detección LPR
    matricula_detectada = Column(String(20))  # Lo que leyó la cámara
    confianza = Column(Float)  # % de confianza de la lectura (0-100)
    imagen_url = Column(String(500))  # Captura del momento

    # Tiempo
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Si fue registrado manualmente
    manual = Column(Boolean, default=False)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"))

    # Notas
    notas = Column(Text)

    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="movimientos")
    zona_origen = relationship("Zona", foreign_keys=[zona_origen_id], back_populates="movimientos_origen")
    zona_destino = relationship("Zona", foreign_keys=[zona_destino_id], back_populates="movimientos_destino")
    registrado_por = relationship("Usuario", back_populates="movimientos_registrados")

    def __repr__(self):
        return f"<Movimiento {self.tipo.value} vehiculo={self.vehiculo_id} {self.fecha_hora}>"
