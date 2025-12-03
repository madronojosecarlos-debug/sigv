import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { zonasApi, camposApi } from '../services/api'
import { Zona, CampoPersonalizado } from '../types'
import { Settings, MapPin, Database, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function Configuracion() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<'zonas' | 'campos'>('zonas')

  const { data: zonas } = useQuery({
    queryKey: ['zonas'],
    queryFn: zonasApi.listar,
  })

  const { data: campos } = useQuery({
    queryKey: ['campos'],
    queryFn: camposApi.listar,
  })

  const inicializarCamposMutation = useMutation({
    mutationFn: camposApi.inicializarPredefinidos,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['campos'] })
      toast.success(data.mensaje)
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="text-gray-500">Configuración del sistema SIGV</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow">
        <div className="border-b">
          <nav className="flex -mb-px">
            <button
              onClick={() => setTab('zonas')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                tab === 'zonas'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <MapPin className="h-4 w-4 inline mr-2" />
              Zonas y Cámaras
            </button>
            <button
              onClick={() => setTab('campos')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                tab === 'campos'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Database className="h-4 w-4 inline mr-2" />
              Campos Personalizados
            </button>
          </nav>
        </div>

        <div className="p-6">
          {tab === 'zonas' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Zonas Configuradas</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {zonas?.map((zona: Zona) => (
                  <div
                    key={zona.id}
                    className="border rounded-lg p-4"
                    style={{ borderLeftWidth: '4px', borderLeftColor: zona.color }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{zona.nombre}</h3>
                        <p className="text-sm text-gray-500">Código: {zona.codigo}</p>
                        <p className="text-sm text-gray-500">Tipo: {zona.tipo}</p>
                      </div>
                      <span className="text-2xl font-bold" style={{ color: zona.color }}>
                        {zona.cantidad_vehiculos || 0}
                      </span>
                    </div>
                    {zona.camaras && zona.camaras.length > 0 && (
                      <div className="mt-3 pt-3 border-t">
                        <p className="text-xs text-gray-500 mb-2">Cámaras:</p>
                        <div className="flex flex-wrap gap-2">
                          {zona.camaras.map((cam) => (
                            <span
                              key={cam.id}
                              className={`px-2 py-1 text-xs rounded ${
                                cam.online ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {cam.codigo} ({cam.tipo})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === 'campos' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Campos Personalizados</h2>
                <button
                  onClick={() => inicializarCamposMutation.mutate()}
                  className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Inicializar Predefinidos
                </button>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                Estos campos se pueden añadir a cualquier vehículo para guardar información adicional.
              </p>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campo</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Obligatorio</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {campos?.map((campo: CampoPersonalizado) => (
                      <tr key={campo.id}>
                        <td className="px-4 py-3">
                          <div className="font-medium">{campo.etiqueta}</div>
                          <div className="text-xs text-gray-400">{campo.nombre}</div>
                        </td>
                        <td className="px-4 py-3 text-sm capitalize">{campo.tipo}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            campo.obligatorio ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'
                          }`}>
                            {campo.obligatorio ? 'Sí' : 'No'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            campo.activo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                          }`}>
                            {campo.activo ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {(!campos || campos.length === 0) && (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                          No hay campos personalizados. Haz clic en "Inicializar Predefinidos" para crear los campos comunes.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info del sistema */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex items-center gap-3 mb-4">
          <Settings className="h-5 w-5 text-gray-400" />
          <h2 className="text-lg font-semibold">Información del Sistema</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Versión</p>
            <p className="font-medium">1.0.0</p>
          </div>
          <div>
            <p className="text-gray-500">Cliente</p>
            <p className="font-medium">Centro de Automóvil Pedro Madroño</p>
          </div>
          <div>
            <p className="text-gray-500">Alerta Inactividad</p>
            <p className="font-medium">20 días</p>
          </div>
          <div>
            <p className="text-gray-500">Tiempo Entrega</p>
            <p className="font-medium">60 minutos</p>
          </div>
        </div>
      </div>
    </div>
  )
}
