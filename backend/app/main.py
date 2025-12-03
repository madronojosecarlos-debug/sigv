"""
SIGV - Sistema Inteligente de Gestión de Vehículos
API Principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .api import auth, usuarios, vehiculos, etiquetas, zonas, movimientos, alertas, dashboard, campos_personalizados

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="SIGV API",
    description="Sistema Inteligente de Gestión de Vehículos - Centro de Automóvil Pedro Madroño",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "Bienvenido a SIGV API",
        "version": "1.0.0",
        "cliente": "Centro de Automóvil Pedro Madroño",
        "documentacion": "/docs"
    }


@app.get("/health")
async def health_check():
    """Verificar que el servidor está funcionando"""
    return {"status": "ok"}


# Registrar routers de la API
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(vehiculos.router, prefix="/api/vehiculos", tags=["Vehículos"])
app.include_router(etiquetas.router, prefix="/api/etiquetas", tags=["Etiquetas"])
app.include_router(zonas.router, prefix="/api/zonas", tags=["Zonas"])
app.include_router(movimientos.router, prefix="/api/movimientos", tags=["Movimientos"])
app.include_router(alertas.router, prefix="/api/alertas", tags=["Alertas"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(campos_personalizados.router, prefix="/api/campos", tags=["Campos Personalizados"])
