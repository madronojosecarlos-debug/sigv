"""
Configuración del sistema SIGV
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql://sigv_user:password@localhost:5432/sigv_db"

    # Seguridad
    SECRET_KEY: str = "cambiar_esta_clave_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Alertas
    ALERTA_INACTIVIDAD_DIAS: int = 20
    TIEMPO_ENTREGA_MINUTOS: int = 60  # 1 hora

    class Config:
        env_file = ".env"


settings = Settings()
