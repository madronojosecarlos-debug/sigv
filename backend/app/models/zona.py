"""
Zonas y Cámaras
- Zonas: Campa, Taller, Entrada Principal, etc.
- Cámaras: LPR y de vigilancia asociadas a cada zona
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Zona(Base):
    """
    Zonas físicas de las instalaciones.
    Fase 1: Entrada Principal, Campa (Parcela 14, Parcela 15)
    Fase 2: Taller (diferentes áreas)
    """
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)  # Ej: "CAMPA_14", "TALLER_1"
    descripcion = Column(String(255))
    tipo = Column(String(50))  # "entrada", "campa", "taller"

    # Para el mapa interactivo (coordenadas relativas)
    pos_x = Column(Float)  # Posición X en el mapa
    pos_y = Column(Float)  # Posición Y en el mapa
    ancho = Column(Float)  # Ancho de la zona en el mapa
    alto = Column(Float)  # Alto de la zona en el mapa
    color = Column(String(7), default="#95a5a6")  # Color en el mapa

    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    vehiculos = relationship("Vehiculo", back_populates="zona_actual")
    camaras = relationship("Camara", back_populates="zona")
    movimientos_origen = relationship("Movimiento", foreign_keys="Movimiento.zona_origen_id", back_populates="zona_origen")
    movimientos_destino = relationship("Movimiento", foreign_keys="Movimiento.zona_destino_id", back_populates="zona_destino")

    def __repr__(self):
        return f"<Zona {self.nombre}>"


class Camara(Base):
    """
    Cámaras de vigilancia y LPR.
    Cada cámara está asociada a una zona.
    """
    __tablename__ = "camaras"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)  # Ej: "LPR-1", "OV-3"
    tipo = Column(String(20), nullable=False)  # "lpr" o "vigilancia"
    zona_id = Column(Integer, ForeignKey("zonas.id"))

    # Configuración de conexión
    ip = Column(String(50))
    puerto = Column(Integer)
    url_stream = Column(String(500))  # URL para streaming RTSP
    usuario = Column(String(100))
    password_encriptado = Column(String(255))

    # Para cámaras LPR: dirección que vigilan
    direccion = Column(String(20))  # "entrada", "salida", "ambos"

    # Estado
    activo = Column(Boolean, default=True)
    online = Column(Boolean, default=False)
    ultimo_ping = Column(DateTime(timezone=True))

    # Posición en el mapa
    pos_x = Column(Float)
    pos_y = Column(Float)
    angulo = Column(Float)  # Dirección hacia donde apunta (grados)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    zona = relationship("Zona", back_populates="camaras")

    def __repr__(self):
        return f"<Camara {self.codigo} ({self.tipo})>"
