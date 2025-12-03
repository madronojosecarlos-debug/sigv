"""
Script para inicializar la base de datos con datos de ejemplo
Ejecutar una sola vez después de crear la base de datos
"""
from app.database import SessionLocal, engine, Base
from app.services.init_db import init_all

# Crear todas las tablas
print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)

# Inicializar datos
db = SessionLocal()
try:
    init_all(db)
finally:
    db.close()
