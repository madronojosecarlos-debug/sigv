"""
Sistema de Alertas
- Alerta de inactividad: vehículo > 20 días sin movimiento
- Alerta de entrega: vehículo > 1 hora entre zonas (se considera entregado)
- Alertas personalizables en el futuro
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class TipoAlerta(enum.Enum):
    INACTIVIDAD = "inactividad"  # Vehículo sin movimiento > X días
    POSIBLE_ENTREGA = "posible_entrega"  # Vehículo > 1 hora entre zonas
    ENTRADA_NO_REGISTRADA = "entrada_no_registrada"  # Matrícula no reconocida
    SALIDA_SIN_AUTORIZACION = "salida_sin_autorizacion"  # Vehículo sale sin etiqueta "Listo"
    PERSONALIZADA = "personalizada"  # Alertas definidas por el usuario


class Alerta(Base):
    """
    Alertas del sistema.
    Se generan automáticamente según las reglas configuradas.
    """
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoAlerta), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=True)  # Puede ser alerta general

    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text)
    prioridad = Column(String(20), default="media")  # baja, media, alta, critica

    # Estado de la alerta
    leida = Column(Boolean, default=False)
    resuelta = Column(Boolean, default=False)
    fecha_lectura = Column(DateTime(timezone=True))
    fecha_resolucion = Column(DateTime(timezone=True))
    resuelta_por_id = Column(Integer, ForeignKey("usuarios.id"))
    notas_resolucion = Column(Text)

    # Auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="alertas")

    def __repr__(self):
        return f"<Alerta {self.tipo.value} vehiculo={self.vehiculo_id}>"
