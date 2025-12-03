"""
Modelo de Vehículos con campos personalizables
- Campos base obligatorios (matrícula)
- Campos personalizados dinámicos (añadir/quitar según necesidad)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Vehiculo(Base):
    """
    Vehículo principal con campos base.
    Los campos adicionales se guardan en ValorCampoPersonalizado.
    """
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20), unique=True, index=True, nullable=False)

    # Campos base comunes (pueden dejarse vacíos)
    marca = Column(String(50))
    modelo = Column(String(50))
    color = Column(String(30))
    año = Column(Integer)
    vin = Column(String(50))  # Número de bastidor

    # Cliente
    cliente_nombre = Column(String(150))
    cliente_telefono = Column(String(20))
    cliente_email = Column(String(255))

    # Estado general
    activo = Column(Boolean, default=True)  # False = entregado/dado de baja
    en_instalaciones = Column(Boolean, default=False)  # True = está dentro

    # Ubicación actual
    zona_actual_id = Column(Integer, ForeignKey("zonas.id"), nullable=True)

    # Notas generales
    notas = Column(Text)

    # Auditoría
    fecha_primera_entrada = Column(DateTime(timezone=True))
    fecha_ultima_entrada = Column(DateTime(timezone=True))
    fecha_ultima_salida = Column(DateTime(timezone=True))
    fecha_ultimo_movimiento = Column(DateTime(timezone=True))
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    zona_actual = relationship("Zona", back_populates="vehiculos")
    etiquetas = relationship("VehiculoEtiqueta", back_populates="vehiculo", cascade="all, delete-orphan")
    movimientos = relationship("Movimiento", back_populates="vehiculo", cascade="all, delete-orphan")
    campos_personalizados = relationship("ValorCampoPersonalizado", back_populates="vehiculo", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="vehiculo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehiculo {self.matricula}>"


class CampoPersonalizado(Base):
    """
    Definición de campos personalizados.
    Permite añadir campos nuevos sin modificar la estructura de la BD.
    Ejemplo: "Número de orden", "Compañía de seguros", "Perito asignado"
    """
    __tablename__ = "campos_personalizados"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)  # Ej: "numero_orden"
    etiqueta = Column(String(100), nullable=False)  # Ej: "Número de Orden"
    tipo = Column(String(20), default="texto")  # texto, numero, fecha, booleano, seleccion
    opciones = Column(JSON)  # Para tipo "seleccion": ["opcion1", "opcion2"]
    obligatorio = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)  # Para ordenar en formularios

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    valores = relationship("ValorCampoPersonalizado", back_populates="campo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CampoPersonalizado {self.nombre}>"


class ValorCampoPersonalizado(Base):
    """
    Valores de campos personalizados por vehículo.
    Estructura EAV (Entity-Attribute-Value) para máxima flexibilidad.
    """
    __tablename__ = "valores_campos_personalizados"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    campo_id = Column(Integer, ForeignKey("campos_personalizados.id"), nullable=False)
    valor = Column(Text)  # Guardamos todo como texto, convertimos según el tipo

    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="campos_personalizados")
    campo = relationship("CampoPersonalizado", back_populates="valores")

    def __repr__(self):
        return f"<ValorCampo vehiculo={self.vehiculo_id} campo={self.campo_id}>"
