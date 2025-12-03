# SIGV - Sistema Inteligente de Gestión de Vehículos

## Centro de Automóvil Pedro Madroño

---

## Requisitos Previos

### Software necesario:
- **Python 3.10+** - Para el backend
- **Node.js 18+** - Para el frontend
- **PostgreSQL 14+** - Base de datos

---

## Instalación Paso a Paso

### 1. Instalar PostgreSQL

Descarga e instala PostgreSQL desde: https://www.postgresql.org/download/windows/

Después de instalarlo, crea la base de datos:

```sql
-- Ejecutar en pgAdmin o psql
CREATE DATABASE sigv_db;
CREATE USER sigv_user WITH PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE sigv_db TO sigv_user;
```

### 2. Configurar el Backend

```bash
# Ir a la carpeta del backend
cd "C:\Users\josec\Desktop\Claude Code\SIGV\backend"

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar y configurar variables de entorno
copy .env.example .env
# Editar .env con tu configuración de base de datos
```

Edita el archivo `.env` con tus datos:
```
DATABASE_URL=postgresql://sigv_user:tu_password_seguro@localhost:5432/sigv_db
SECRET_KEY=una_clave_secreta_muy_larga_y_segura
```

### 3. Inicializar la Base de Datos

```bash
# Con el entorno virtual activado
python init_database.py
```

Esto creará:
- Usuario admin: `admin@sigv.local` / `admin123`
- Etiquetas predefinidas
- Zonas del plano en L
- Cámaras de ejemplo

### 4. Ejecutar el Backend

```bash
python run.py
```

El servidor estará en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 5. Configurar el Frontend

```bash
# En otra terminal, ir a la carpeta del frontend
cd "C:\Users\josec\Desktop\Claude Code\SIGV\frontend"

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

El frontend estará en: http://localhost:3000

---

## Uso del Sistema

### Acceder al Panel
1. Abre http://localhost:3000
2. Inicia sesión con: `admin@sigv.local` / `admin123`

### Simulador de Cámaras LPR

Para probar el sistema sin cámaras físicas:

```bash
cd "C:\Users\josec\Desktop\Claude Code\SIGV\lpr-simulator"

# Modo interactivo (escribir matrículas manualmente)
python simulator.py

# Modo automático (genera detecciones aleatorias)
python simulator.py --modo auto --intervalo 30 --cantidad 10

# Modo escenario (simula un día típico)
python simulator.py --modo escenario
```

---

## Estructura del Proyecto

```
SIGV/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/       # Endpoints
│   │   ├── models/    # Modelos de BD
│   │   └── services/  # Lógica de negocio
│   └── requirements.txt
├── frontend/          # React + Tailwind
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
└── lpr-simulator/     # Simulador de cámaras
```

---

## Funcionalidades Implementadas

### Dashboard
- Contadores de vehículos en instalaciones
- Entradas/salidas del día
- Vehículos por zona y etiqueta
- Listado de vehículos inactivos (+20 días)
- Vehículos esperando piezas

### Vehículos
- Listado con búsqueda y filtros
- Detalle con historial de movimientos
- Asignación de etiquetas
- Campos personalizados

### Mapa
- Vista del plano en L
- Vehículos por zona en tiempo real

### Etiquetas
- Crear/editar/eliminar etiquetas
- Colores personalizables

### Alertas
- Inactividad > 20 días
- Posible entrega (> 1 hora sin detectar)
- Matrículas no registradas

### Usuarios
- Roles: Administrador, Asesor, Mecánico
- Gestión de usuarios

---

## Próximos Pasos

1. **Comprar hardware** (cuando el software esté probado)
   - 2x Cámaras LPR Safire
   - 1x Cámara vigilancia adicional
   - 1x Servidor dedicado
   - 1x Switch PoE

2. **Configurar cámaras reales**
   - Actualizar IPs en el sistema
   - Configurar streaming RTSP

3. **Integración LPR real**
   - Conectar software LPR de las cámaras
   - Configurar webhooks para enviar detecciones

---

## Soporte

Cualquier duda sobre el funcionamiento del sistema, consulta la documentación de la API en http://localhost:8000/docs
