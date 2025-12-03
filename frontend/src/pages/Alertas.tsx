import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertasApi } from '../services/api'
import { Alerta } from '../types'
import { Bell, Check, Eye, AlertTriangle, Clock, Car } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'
import clsx from 'clsx'

const iconosPorTipo = {
  inactividad: Clock,
  posible_entrega: Car,
  entrada_no_registrada: AlertTriangle,
  salida_sin_autorizacion: AlertTriangle,
  personalizada: Bell,
}

const coloresPrioridad = {
  baja: 'bg-gray-100 text-gray-800',
  media: 'bg-yellow-100 text-yellow-800',
  alta: 'bg-orange-100 text-orange-800',
  critica: 'bg-red-100 text-red-800',
}

export default function Alertas() {
  const queryClient = useQueryClient()

  const { data: alertas, isLoading } = useQuery({
    queryKey: ['alertas'],
    queryFn: () => alertasApi.listar({ resuelta: false }),
    refetchInterval: 30000,
  })

  const { data: contador } = useQuery({
    queryKey: ['alertas-contador'],
    queryFn: alertasApi.contador,
  })

  const marcarLeidaMutation = useMutation({
    mutationFn: alertasApi.marcarLeida,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertas'] })
      queryClient.invalidateQueries({ queryKey: ['alertas-contador'] })
    },
  })

  const resolverMutation = useMutation({
    mutationFn: (id: number) => alertasApi.resolver(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertas'] })
      queryClient.invalidateQueries({ queryKey: ['alertas-contador'] })
      toast.success('Alerta resuelta')
    },
  })

  const generarInactividadMutation = useMutation({
    mutationFn: alertasApi.generarInactividad,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['alertas'] })
      toast.success(data.mensaje)
    },
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alertas</h1>
          <p className="text-gray-500">
            {contador?.no_leidas || 0} sin leer de {contador?.total || 0} pendientes
          </p>
        </div>
        <button
          onClick={() => generarInactividadMutation.mutate()}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          Verificar inactividad
        </button>
      </div>

      {/* Resumen por tipo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{contador?.por_tipo?.inactividad || 0}</p>
              <p className="text-xs text-gray-500">Inactividad</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Car className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{contador?.por_tipo?.posible_entrega || 0}</p>
              <p className="text-xs text-gray-500">Posible entrega</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{contador?.por_tipo?.entrada_no_registrada || 0}</p>
              <p className="text-xs text-gray-500">No registrada</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Bell className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{contador?.total || 0}</p>
              <p className="text-xs text-gray-500">Total pendientes</p>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de alertas */}
      <div className="bg-white rounded-xl shadow">
        {alertas?.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No hay alertas pendientes</p>
          </div>
        ) : (
          <div className="divide-y">
            {alertas?.map((alerta: Alerta) => {
              const Icono = iconosPorTipo[alerta.tipo] || Bell
              return (
                <div
                  key={alerta.id}
                  className={clsx('p-4 hover:bg-gray-50', !alerta.leida && 'bg-blue-50')}
                >
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Icono className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-gray-900">{alerta.titulo}</h3>
                        <span
                          className={clsx(
                            'px-2 py-0.5 text-xs rounded-full',
                            coloresPrioridad[alerta.prioridad]
                          )}
                        >
                          {alerta.prioridad}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">{alerta.mensaje}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>
                          {format(new Date(alerta.fecha_creacion), "d MMM yyyy, HH:mm", { locale: es })}
                        </span>
                        {alerta.vehiculo_matricula && (
                          <Link
                            to={`/vehiculos/${alerta.vehiculo_id}`}
                            className="text-primary-600 hover:underline"
                          >
                            {alerta.vehiculo_matricula}
                          </Link>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!alerta.leida && (
                        <button
                          onClick={() => marcarLeidaMutation.mutate(alerta.id)}
                          className="p-2 hover:bg-gray-100 rounded-lg"
                          title="Marcar como leída"
                        >
                          <Eye className="h-4 w-4 text-gray-400" />
                        </button>
                      )}
                      <button
                        onClick={() => resolverMutation.mutate(alerta.id)}
                        className="p-2 hover:bg-green-100 rounded-lg"
                        title="Resolver"
                      >
                        <Check className="h-4 w-4 text-green-600" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
