import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../services/api'
import { Car, LogIn, LogOut, AlertTriangle, Clock, Package } from 'lucide-react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function Dashboard() {
  const { data: estadisticas, isLoading } = useQuery({
    queryKey: ['estadisticas'],
    queryFn: dashboardApi.getEstadisticas,
    refetchInterval: 30000,
  })

  const { data: actividadReciente } = useQuery({
    queryKey: ['actividad-reciente'],
    queryFn: dashboardApi.getActividadReciente,
    refetchInterval: 15000,
  })

  const { data: vehiculosInactivos } = useQuery({
    queryKey: ['vehiculos-inactivos'],
    queryFn: () => dashboardApi.getVehiculosInactivos(20),
  })

  const { data: esperandoPiezas } = useQuery({
    queryKey: ['esperando-piezas'],
    queryFn: dashboardApi.getVehiculosEsperandoPiezas,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Título */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Resumen del estado de las instalaciones</p>
      </div>

      {/* Cards principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Car className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">En instalaciones</p>
              <p className="text-2xl font-bold">{estadisticas?.vehiculos?.en_instalaciones || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <LogIn className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Entradas hoy</p>
              <p className="text-2xl font-bold">{estadisticas?.movimientos_hoy?.entradas || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 rounded-lg">
              <LogOut className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Salidas hoy</p>
              <p className="text-2xl font-bold">{estadisticas?.movimientos_hoy?.salidas || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Alertas pendientes</p>
              <p className="text-2xl font-bold">{estadisticas?.alertas?.pendientes || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Vehículos por zona */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Vehículos por Zona</h2>
          <div className="space-y-3">
            {estadisticas?.vehiculos_por_zona?.map((zona: { zona_id: number; zona_nombre: string; zona_color: string; cantidad: number }) => (
              <div key={zona.zona_id} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-full mr-3"
                    style={{ backgroundColor: zona.zona_color }}
                  />
                  <span className="text-gray-700">{zona.zona_nombre}</span>
                </div>
                <span className="font-semibold">{zona.cantidad}</span>
              </div>
            ))}
            {(!estadisticas?.vehiculos_por_zona || estadisticas.vehiculos_por_zona.length === 0) && (
              <p className="text-gray-400 text-sm">No hay zonas configuradas</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Vehículos por Etiqueta</h2>
          <div className="space-y-3">
            {estadisticas?.vehiculos_por_etiqueta?.slice(0, 8).map((etiqueta: { etiqueta_id: number; etiqueta_nombre: string; etiqueta_color: string; cantidad: number }) => (
              <div key={etiqueta.etiqueta_id} className="flex items-center justify-between">
                <div className="flex items-center">
                  <span
                    className="px-2 py-1 text-xs rounded-full text-white mr-3"
                    style={{ backgroundColor: etiqueta.etiqueta_color }}
                  >
                    {etiqueta.etiqueta_nombre}
                  </span>
                </div>
                <span className="font-semibold">{etiqueta.cantidad}</span>
              </div>
            ))}
            {(!estadisticas?.vehiculos_por_etiqueta || estadisticas.vehiculos_por_etiqueta.length === 0) && (
              <p className="text-gray-400 text-sm">No hay etiquetas con vehículos</p>
            )}
          </div>
        </div>
      </div>

      {/* Listados prioritarios */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Actividad reciente */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Actividad Reciente</h2>
            <Clock className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {actividadReciente?.map((mov: { id: number; tipo: string; matricula: string; fecha_hora: string }) => (
              <div key={mov.id} className="flex items-center text-sm">
                <span
                  className={`w-2 h-2 rounded-full mr-2 ${
                    mov.tipo === 'entrada' ? 'bg-green-500' : 'bg-orange-500'
                  }`}
                />
                <span className="font-medium">{mov.matricula}</span>
                <span className="text-gray-400 ml-2">
                  {format(new Date(mov.fecha_hora), 'HH:mm', { locale: es })}
                </span>
              </div>
            ))}
            {(!actividadReciente || actividadReciente.length === 0) && (
              <p className="text-gray-400 text-sm">Sin actividad reciente</p>
            )}
          </div>
        </div>

        {/* Esperando piezas */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Esperando Piezas</h2>
            <Package className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {esperandoPiezas?.map((v: { id: number; matricula: string; dias_esperando: number; cliente_nombre?: string }) => (
              <Link
                key={v.id}
                to={`/vehiculos/${v.id}`}
                className="block hover:bg-gray-50 -mx-2 px-2 py-1 rounded"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{v.matricula}</span>
                  <span className="text-xs text-red-500">{v.dias_esperando} días</span>
                </div>
                {v.cliente_nombre && (
                  <p className="text-xs text-gray-400">{v.cliente_nombre}</p>
                )}
              </Link>
            ))}
            {(!esperandoPiezas || esperandoPiezas.length === 0) && (
              <p className="text-gray-400 text-sm">No hay vehículos esperando piezas</p>
            )}
          </div>
        </div>

        {/* Vehículos inactivos */}
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Inactivos +20 días</h2>
            <AlertTriangle className="h-5 w-5 text-red-400" />
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {vehiculosInactivos?.map((v: { id: number; matricula: string; dias_inactivo: number; zona_actual?: string }) => (
              <Link
                key={v.id}
                to={`/vehiculos/${v.id}`}
                className="block hover:bg-gray-50 -mx-2 px-2 py-1 rounded"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{v.matricula}</span>
                  <span className="text-xs text-red-500">{v.dias_inactivo} días</span>
                </div>
                {v.zona_actual && (
                  <p className="text-xs text-gray-400">{v.zona_actual}</p>
                )}
              </Link>
            ))}
            {(!vehiculosInactivos || vehiculosInactivos.length === 0) && (
              <p className="text-gray-400 text-sm">No hay vehículos inactivos</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
