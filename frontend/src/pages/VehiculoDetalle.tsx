import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vehiculosApi, etiquetasApi, movimientosApi, zonasApi } from '../services/api'
import { ArrowLeft, Plus, X, MapPin, Clock } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function VehiculoDetalle() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const [mostrarAsignarEtiqueta, setMostrarAsignarEtiqueta] = useState(false)
  const [mostrarMovimiento, setMostrarMovimiento] = useState(false)

  const { data: vehiculo, isLoading } = useQuery({
    queryKey: ['vehiculo', id],
    queryFn: () => vehiculosApi.obtener(Number(id)),
  })

  const { data: movimientos } = useQuery({
    queryKey: ['movimientos', id],
    queryFn: () => movimientosApi.listarPorVehiculo(Number(id)),
  })

  const { data: etiquetas } = useQuery({
    queryKey: ['etiquetas'],
    queryFn: () => etiquetasApi.listar(),
  })

  const { data: zonas } = useQuery({
    queryKey: ['zonas'],
    queryFn: zonasApi.listar,
  })

  const asignarEtiquetaMutation = useMutation({
    mutationFn: (etiquetaId: number) => vehiculosApi.asignarEtiqueta(Number(id), etiquetaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculo', id] })
      setMostrarAsignarEtiqueta(false)
      toast.success('Etiqueta asignada')
    },
  })

  const quitarEtiquetaMutation = useMutation({
    mutationFn: (etiquetaId: number) => vehiculosApi.quitarEtiqueta(Number(id), etiquetaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculo', id] })
      toast.success('Etiqueta removida')
    },
  })

  const registrarMovimientoMutation = useMutation({
    mutationFn: (data: { tipo: string; zona_destino_id?: number }) =>
      movimientosApi.registrarManual({ vehiculo_id: Number(id), ...data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculo', id] })
      queryClient.invalidateQueries({ queryKey: ['movimientos', id] })
      setMostrarMovimiento(false)
      toast.success('Movimiento registrado')
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!vehiculo) {
    return <div className="text-center py-12">Vehículo no encontrado</div>
  }

  const etiquetasDisponibles = etiquetas?.filter(
    (e: { id: number }) => !vehiculo.etiquetas?.find((ve: { id: number }) => ve.id === e.id)
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/vehiculos" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{vehiculo.matricula}</h1>
          <p className="text-gray-500">
            {vehiculo.marca} {vehiculo.modelo} {vehiculo.color && `- ${vehiculo.color}`}
          </p>
        </div>
        <span
          className={`ml-auto px-3 py-1 rounded-full text-sm ${
            vehiculo.en_instalaciones ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}
        >
          {vehiculo.en_instalaciones ? 'En instalaciones' : 'Fuera'}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Info principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Datos del vehículo */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Información del Vehículo</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Cliente</p>
                <p className="font-medium">{vehiculo.cliente_nombre || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Teléfono</p>
                <p className="font-medium">{vehiculo.cliente_telefono || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">VIN</p>
                <p className="font-medium">{vehiculo.vin || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Año</p>
                <p className="font-medium">{vehiculo.año || '-'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-500">Notas</p>
                <p className="font-medium">{vehiculo.notas || '-'}</p>
              </div>
            </div>
          </div>

          {/* Etiquetas */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Etiquetas</h2>
              <button
                onClick={() => setMostrarAsignarEtiqueta(true)}
                className="text-primary-600 hover:text-primary-700"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {vehiculo.etiquetas?.map((etiqueta: { id: number; nombre: string; color: string }) => (
                <span
                  key={etiqueta.id}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm text-white"
                  style={{ backgroundColor: etiqueta.color }}
                >
                  {etiqueta.nombre}
                  <button
                    onClick={() => quitarEtiquetaMutation.mutate(etiqueta.id)}
                    className="ml-2 hover:opacity-75"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
              {(!vehiculo.etiquetas || vehiculo.etiquetas.length === 0) && (
                <p className="text-gray-400 text-sm">Sin etiquetas asignadas</p>
              )}
            </div>
          </div>

          {/* Historial de movimientos */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Historial de Movimientos</h2>
              <button
                onClick={() => setMostrarMovimiento(true)}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Registrar movimiento
              </button>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {movimientos?.map((mov: { id: number; tipo: string; zona_destino?: { nombre: string }; fecha_hora: string; manual: boolean }) => (
                <div key={mov.id} className="flex items-start gap-3 text-sm">
                  <div
                    className={`w-2 h-2 mt-2 rounded-full ${
                      mov.tipo === 'entrada'
                        ? 'bg-green-500'
                        : mov.tipo === 'salida'
                        ? 'bg-orange-500'
                        : 'bg-blue-500'
                    }`}
                  />
                  <div>
                    <p className="font-medium capitalize">{mov.tipo.replace('_', ' ')}</p>
                    {mov.zona_destino && (
                      <p className="text-gray-500">→ {mov.zona_destino.nombre}</p>
                    )}
                    <p className="text-gray-400 text-xs">
                      {format(new Date(mov.fecha_hora), "d MMM yyyy, HH:mm", { locale: es })}
                      {mov.manual && ' (manual)'}
                    </p>
                  </div>
                </div>
              ))}
              {(!movimientos || movimientos.length === 0) && (
                <p className="text-gray-400 text-sm">Sin movimientos registrados</p>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Ubicación */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="h-5 w-5 text-gray-400" />
              <h2 className="text-lg font-semibold">Ubicación</h2>
            </div>
            <p className="text-gray-900 font-medium">
              {vehiculo.zona_actual?.nombre || 'No ubicado'}
            </p>
          </div>

          {/* Tiempos */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <Clock className="h-5 w-5 text-gray-400" />
              <h2 className="text-lg font-semibold">Tiempos</h2>
            </div>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-500">Primera entrada</p>
                <p className="font-medium">
                  {vehiculo.fecha_primera_entrada
                    ? format(new Date(vehiculo.fecha_primera_entrada), "d MMM yyyy", { locale: es })
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Última entrada</p>
                <p className="font-medium">
                  {vehiculo.fecha_ultima_entrada
                    ? format(new Date(vehiculo.fecha_ultima_entrada), "d MMM yyyy, HH:mm", { locale: es })
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Último movimiento</p>
                <p className="font-medium">
                  {vehiculo.fecha_ultimo_movimiento
                    ? format(new Date(vehiculo.fecha_ultimo_movimiento), "d MMM yyyy, HH:mm", { locale: es })
                    : '-'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal asignar etiqueta */}
      {mostrarAsignarEtiqueta && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setMostrarAsignarEtiqueta(false)} />
            <div className="relative bg-white rounded-xl shadow-xl max-w-sm w-full p-6">
              <h2 className="text-lg font-semibold mb-4">Asignar Etiqueta</h2>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {etiquetasDisponibles?.map((etiqueta: { id: number; nombre: string; color: string }) => (
                  <button
                    key={etiqueta.id}
                    onClick={() => asignarEtiquetaMutation.mutate(etiqueta.id)}
                    className="w-full flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg"
                  >
                    <span
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: etiqueta.color }}
                    />
                    <span>{etiqueta.nombre}</span>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setMostrarAsignarEtiqueta(false)}
                className="mt-4 w-full py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal registrar movimiento */}
      {mostrarMovimiento && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setMostrarMovimiento(false)} />
            <div className="relative bg-white rounded-xl shadow-xl max-w-sm w-full p-6">
              <h2 className="text-lg font-semibold mb-4">Registrar Movimiento</h2>
              <div className="space-y-3">
                <button
                  onClick={() => registrarMovimientoMutation.mutate({ tipo: 'entrada', zona_destino_id: zonas?.[0]?.id })}
                  className="w-full p-3 text-left hover:bg-green-50 rounded-lg border border-green-200"
                >
                  <span className="font-medium text-green-700">Entrada</span>
                  <p className="text-sm text-gray-500">Registrar entrada a instalaciones</p>
                </button>
                <button
                  onClick={() => registrarMovimientoMutation.mutate({ tipo: 'salida' })}
                  className="w-full p-3 text-left hover:bg-orange-50 rounded-lg border border-orange-200"
                >
                  <span className="font-medium text-orange-700">Salida</span>
                  <p className="text-sm text-gray-500">Registrar salida de instalaciones</p>
                </button>
              </div>
              <button
                onClick={() => setMostrarMovimiento(false)}
                className="mt-4 w-full py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
