// Tipos principales del sistema SIGV

export interface Usuario {
  id: number
  email: string
  nombre: string
  apellidos?: string
  rol: 'administrador' | 'asesor' | 'mecanico'
  telefono?: string
  activo: boolean
  fecha_creacion?: string
  ultimo_acceso?: string
}

export interface Etiqueta {
  id: number
  nombre: string
  color: string
  descripcion?: string
  icono?: string
  activo: boolean
  orden: number
  es_sistema: boolean
  cantidad_vehiculos?: number
}

export interface Zona {
  id: number
  nombre: string
  codigo: string
  descripcion?: string
  tipo: 'entrada' | 'campa' | 'taller'
  pos_x?: number
  pos_y?: number
  ancho?: number
  alto?: number
  color: string
  activo: boolean
  cantidad_vehiculos?: number
  camaras?: CamaraResumen[]
}

export interface CamaraResumen {
  id: number
  codigo: string
  tipo: string
  online: boolean
}

export interface Camara {
  id: number
  nombre: string
  codigo: string
  tipo: 'lpr' | 'vigilancia'
  zona_id?: number
  zona_nombre?: string
  ip?: string
  puerto?: number
  url_stream?: string
  direccion?: 'entrada' | 'salida' | 'ambos'
  activo: boolean
  online: boolean
  pos_x?: number
  pos_y?: number
  angulo?: number
}

export interface Vehiculo {
  id: number
  matricula: string
  marca?: string
  modelo?: string
  color?: string
  año?: number
  vin?: string
  cliente_nombre?: string
  cliente_telefono?: string
  cliente_email?: string
  notas?: string
  activo: boolean
  en_instalaciones: boolean
  zona_actual?: {
    id: number
    nombre: string
    codigo: string
  }
  etiquetas: VehiculoEtiqueta[]
  campos_personalizados: Record<string, CampoValor>
  fecha_primera_entrada?: string
  fecha_ultima_entrada?: string
  fecha_ultimo_movimiento?: string
  fecha_creacion?: string
}

export interface VehiculoEtiqueta {
  id: number
  nombre: string
  color: string
  fecha_asignacion?: string
}

export interface CampoValor {
  etiqueta: string
  valor: string
  tipo: string
}

export interface CampoPersonalizado {
  id: number
  nombre: string
  etiqueta: string
  tipo: 'texto' | 'numero' | 'fecha' | 'booleano' | 'seleccion'
  opciones?: string[]
  obligatorio: boolean
  activo: boolean
  orden: number
}

export interface Movimiento {
  id: number
  vehiculo_id: number
  matricula: string
  tipo: 'entrada' | 'salida' | 'cambio_zona' | 'deteccion'
  zona_origen?: { id: number; nombre: string }
  zona_destino?: { id: number; nombre: string }
  camara?: { id: number; codigo: string }
  confianza?: number
  fecha_hora: string
  manual: boolean
  registrado_por?: string
  notas?: string
}

export interface Alerta {
  id: number
  tipo: 'inactividad' | 'posible_entrega' | 'entrada_no_registrada' | 'salida_sin_autorizacion' | 'personalizada'
  vehiculo_id?: number
  vehiculo_matricula?: string
  titulo: string
  mensaje?: string
  prioridad: 'baja' | 'media' | 'alta' | 'critica'
  leida: boolean
  resuelta: boolean
  fecha_creacion: string
  fecha_resolucion?: string
}

export interface Estadisticas {
  vehiculos: {
    total: number
    en_instalaciones: number
    fuera: number
  }
  vehiculos_por_zona: Array<{
    zona_id: number
    zona_nombre: string
    zona_codigo: string
    zona_color: string
    cantidad: number
  }>
  vehiculos_por_etiqueta: Array<{
    etiqueta_id: number
    etiqueta_nombre: string
    etiqueta_color: string
    cantidad: number
  }>
  alertas: {
    pendientes: number
    no_leidas: number
  }
  movimientos_hoy: {
    entradas: number
    salidas: number
  }
}

export interface DatosMapa {
  id: number
  nombre: string
  codigo: string
  tipo: string
  pos_x?: number
  pos_y?: number
  ancho?: number
  alto?: number
  color: string
  vehiculos: Array<{
    id: number
    matricula: string
    marca?: string
    modelo?: string
    color?: string
    etiquetas: Array<{ nombre: string; color: string }>
    fecha_ultimo_movimiento?: string
  }>
  cantidad_vehiculos: number
}
