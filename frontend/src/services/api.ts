import axios from 'axios'

const API_URL = '/api'

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir token de autenticación
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const { data } = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },
  me: async () => {
    const { data } = await api.get('/auth/me')
    return data
  },
}

// Dashboard
export const dashboardApi = {
  getEstadisticas: async () => {
    const { data } = await api.get('/dashboard/estadisticas')
    return data
  },
  getMapa: async () => {
    const { data } = await api.get('/dashboard/mapa')
    return data
  },
  getVehiculosInactivos: async (dias = 20) => {
    const { data } = await api.get(`/dashboard/vehiculos-inactivos?dias=${dias}`)
    return data
  },
  getVehiculosEsperandoPiezas: async () => {
    const { data } = await api.get('/dashboard/vehiculos-esperando-piezas')
    return data
  },
  getVehiculosPorTiempoEstancia: async () => {
    const { data } = await api.get('/dashboard/vehiculos-por-tiempo-estancia')
    return data
  },
  getActividadReciente: async () => {
    const { data } = await api.get('/dashboard/actividad-reciente')
    return data
  },
}

// Vehículos
export const vehiculosApi = {
  listar: async (params?: Record<string, unknown>) => {
    const { data } = await api.get('/vehiculos/', { params })
    return data
  },
  buscar: async (matricula: string) => {
    const { data } = await api.get(`/vehiculos/buscar/${matricula}`)
    return data
  },
  obtener: async (id: number) => {
    const { data } = await api.get(`/vehiculos/${id}`)
    return data
  },
  crear: async (vehiculo: Record<string, unknown>) => {
    const { data } = await api.post('/vehiculos/', vehiculo)
    return data
  },
  actualizar: async (id: number, vehiculo: Record<string, unknown>) => {
    const { data } = await api.put(`/vehiculos/${id}`, vehiculo)
    return data
  },
  asignarEtiqueta: async (vehiculoId: number, etiquetaId: number) => {
    const { data } = await api.post(`/vehiculos/${vehiculoId}/etiquetas`, { etiqueta_id: etiquetaId })
    return data
  },
  quitarEtiqueta: async (vehiculoId: number, etiquetaId: number) => {
    const { data } = await api.delete(`/vehiculos/${vehiculoId}/etiquetas/${etiquetaId}`)
    return data
  },
  getHistorial: async (id: number) => {
    const { data } = await api.get(`/vehiculos/${id}/historial`)
    return data
  },
}

// Etiquetas
export const etiquetasApi = {
  listar: async (activo = true) => {
    const { data } = await api.get('/etiquetas/', { params: { activo } })
    return data
  },
  obtener: async (id: number) => {
    const { data } = await api.get(`/etiquetas/${id}`)
    return data
  },
  crear: async (etiqueta: Record<string, unknown>) => {
    const { data } = await api.post('/etiquetas/', etiqueta)
    return data
  },
  actualizar: async (id: number, etiqueta: Record<string, unknown>) => {
    const { data } = await api.put(`/etiquetas/${id}`, etiqueta)
    return data
  },
  eliminar: async (id: number) => {
    const { data } = await api.delete(`/etiquetas/${id}`)
    return data
  },
}

// Zonas y Cámaras
export const zonasApi = {
  listar: async () => {
    const { data } = await api.get('/zonas/')
    return data
  },
  obtener: async (id: number) => {
    const { data } = await api.get(`/zonas/${id}`)
    return data
  },
  crear: async (zona: Record<string, unknown>) => {
    const { data } = await api.post('/zonas/', zona)
    return data
  },
  actualizar: async (id: number, zona: Record<string, unknown>) => {
    const { data } = await api.put(`/zonas/${id}`, zona)
    return data
  },
  listarCamaras: async () => {
    const { data } = await api.get('/zonas/camaras/')
    return data
  },
  crearCamara: async (camara: Record<string, unknown>) => {
    const { data } = await api.post('/zonas/camaras/', camara)
    return data
  },
}

// Movimientos
export const movimientosApi = {
  registrarLPR: async (deteccion: { matricula: string; camara_codigo: string; confianza?: number }) => {
    const { data } = await api.post('/movimientos/lpr/detectar', deteccion)
    return data
  },
  registrarManual: async (movimiento: Record<string, unknown>) => {
    const { data } = await api.post('/movimientos/manual', movimiento)
    return data
  },
  listarPorVehiculo: async (vehiculoId: number) => {
    const { data } = await api.get(`/movimientos/vehiculo/${vehiculoId}`)
    return data
  },
  listarRecientes: async () => {
    const { data } = await api.get('/movimientos/recientes')
    return data
  },
}

// Alertas
export const alertasApi = {
  listar: async (params?: Record<string, unknown>) => {
    const { data } = await api.get('/alertas/', { params })
    return data
  },
  contador: async () => {
    const { data } = await api.get('/alertas/contador')
    return data
  },
  marcarLeida: async (id: number) => {
    const { data } = await api.post(`/alertas/${id}/leer`)
    return data
  },
  resolver: async (id: number, notas?: string) => {
    const { data } = await api.post(`/alertas/${id}/resolver`, { notas })
    return data
  },
  generarInactividad: async () => {
    const { data } = await api.post('/alertas/generar-inactividad')
    return data
  },
}

// Usuarios
export const usuariosApi = {
  listar: async (params?: Record<string, unknown>) => {
    const { data } = await api.get('/usuarios/', { params })
    return data
  },
  obtener: async (id: number) => {
    const { data } = await api.get(`/usuarios/${id}`)
    return data
  },
  crear: async (usuario: Record<string, unknown>) => {
    const { data } = await api.post('/usuarios/', usuario)
    return data
  },
  actualizar: async (id: number, usuario: Record<string, unknown>) => {
    const { data } = await api.put(`/usuarios/${id}`, usuario)
    return data
  },
  eliminar: async (id: number) => {
    const { data } = await api.delete(`/usuarios/${id}`)
    return data
  },
}

// Campos personalizados
export const camposApi = {
  listar: async () => {
    const { data } = await api.get('/campos/')
    return data
  },
  crear: async (campo: Record<string, unknown>) => {
    const { data } = await api.post('/campos/', campo)
    return data
  },
  actualizar: async (id: number, campo: Record<string, unknown>) => {
    const { data } = await api.put(`/campos/${id}`, campo)
    return data
  },
  eliminar: async (id: number) => {
    const { data } = await api.delete(`/campos/${id}`)
    return data
  },
  inicializarPredefinidos: async () => {
    const { data } = await api.post('/campos/inicializar-predefinidos')
    return data
  },
}

export default api
