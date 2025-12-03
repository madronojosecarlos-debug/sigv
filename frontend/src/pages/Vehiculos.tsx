import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { vehiculosApi, etiquetasApi, zonasApi } from '../services/api'
import { Vehiculo, Etiqueta, Zona } from '../types'
import { Search, Plus, Filter, X } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function Vehiculos() {
  const queryClient = useQueryClient()
  const [busqueda, setBusqueda] = useState('')
  const [filtroZona, setFiltroZona] = useState<number | ''>('')
  const [filtroEtiqueta, setFiltroEtiqueta] = useState<number | ''>('')
  const [filtroEnInstalaciones, setFiltroEnInstalaciones] = useState<boolean | ''>('')
  const [mostrarModal, setMostrarModal] = useState(false)
  const [nuevoVehiculo, setNuevoVehiculo] = useState({
    matricula: '',
    marca: '',
    modelo: '',
    color: '',
    cliente_nombre: '',
    cliente_telefono: '',
  })

  const { data: vehiculos, isLoading } = useQuery({
    queryKey: ['vehiculos', busqueda, filtroZona, filtroEtiqueta, filtroEnInstalaciones],
    queryFn: () =>
      vehiculosApi.listar({
        buscar: busqueda || undefined,
        zona_id: filtroZona || undefined,
        etiqueta_id: filtroEtiqueta || undefined,
        en_instalaciones: filtroEnInstalaciones === '' ? undefined : filtroEnInstalaciones,
      }),
  })

  const { data: etiquetas } = useQuery({
    queryKey: ['etiquetas'],
    queryFn: () => etiquetasApi.listar(),
  })

  const { data: zonas } = useQuery({
    queryKey: ['zonas'],
    queryFn: zonasApi.listar,
  })

  const crearVehiculoMutation = useMutation({
    mutationFn: vehiculosApi.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehiculos'] })
      setMostrarModal(false)
      setNuevoVehiculo({
        matricula: '',
        marca: '',
        modelo: '',
        color: '',
        cliente_nombre: '',
        cliente_telefono: '',
      })
      toast.success('Vehículo creado correctamente')
    },
    onError: () => {
      toast.error('Error al crear el vehículo')
    },
  })

  const handleCrear = (e: React.FormEvent) => {
    e.preventDefault()
    crearVehiculoMutation.mutate(nuevoVehiculo)
  }

  const limpiarFiltros = () => {
    setBusqueda('')
    setFiltroZona('')
    setFiltroEtiqueta('')
    setFiltroEnInstalaciones('')
  }

  const hayFiltros = busqueda || filtroZona || filtroEtiqueta || filtroEnInstalaciones !== ''

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vehículos</h1>
          <p className="text-gray-500">Gestión de vehículos en el sistema</p>
        </div>
        <button
          onClick={() => setMostrarModal(true)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nuevo Vehículo
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por matrícula, marca, modelo o cliente..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Filtro Zona */}
          <select
            value={filtroZona}
            onChange={(e) => setFiltroZona(e.target.value ? Number(e.target.value) : '')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todas las zonas</option>
            {zonas?.map((zona: Zona) => (
              <option key={zona.id} value={zona.id}>
                {zona.nombre}
              </option>
            ))}
          </select>

          {/* Filtro Etiqueta */}
          <select
            value={filtroEtiqueta}
            onChange={(e) => setFiltroEtiqueta(e.target.value ? Number(e.target.value) : '')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todas las etiquetas</option>
            {etiquetas?.map((etiqueta: Etiqueta) => (
              <option key={etiqueta.id} value={etiqueta.id}>
                {etiqueta.nombre}
              </option>
            ))}
          </select>

          {/* Filtro En instalaciones */}
          <select
            value={filtroEnInstalaciones === '' ? '' : filtroEnInstalaciones ? 'true' : 'false'}
            onChange={(e) =>
              setFiltroEnInstalaciones(e.target.value === '' ? '' : e.target.value === 'true')
            }
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todos</option>
            <option value="true">En instalaciones</option>
            <option value="false">Fuera</option>
          </select>

          {/* Limpiar filtros */}
          {hayFiltros && (
            <button
              onClick={limpiarFiltros}
              className="inline-flex items-center px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              <Filter className="h-5 w-5 mr-2" />
              Limpiar
            </button>
          )}
        </div>
      </div>

      {/* Lista de vehículos */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : vehiculos?.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No se encontraron vehículos</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehículo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cliente
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ubicación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Etiquetas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {vehiculos?.map((vehiculo: Vehiculo) => (
                  <tr key={vehiculo.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/vehiculos/${vehiculo.id}`} className="block">
                        <div className="font-medium text-gray-900">{vehiculo.matricula}</div>
                        <div className="text-sm text-gray-500">
                          {vehiculo.marca} {vehiculo.modelo}
                        </div>
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{vehiculo.cliente_nombre || '-'}</div>
                      <div className="text-sm text-gray-500">{vehiculo.cliente_telefono || ''}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {vehiculo.zona_actual?.nombre || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {vehiculo.etiquetas?.slice(0, 3).map((etiqueta) => (
                          <span
                            key={etiqueta.id}
                            className="px-2 py-0.5 text-xs rounded-full text-white"
                            style={{ backgroundColor: etiqueta.color }}
                          >
                            {etiqueta.nombre}
                          </span>
                        ))}
                        {vehiculo.etiquetas?.length > 3 && (
                          <span className="text-xs text-gray-400">
                            +{vehiculo.etiquetas.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={clsx(
                          'px-2 py-1 text-xs rounded-full',
                          vehiculo.en_instalaciones
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        )}
                      >
                        {vehiculo.en_instalaciones ? 'En instalaciones' : 'Fuera'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal crear vehículo */}
      {mostrarModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setMostrarModal(false)} />
            <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Nuevo Vehículo</h2>
                <button onClick={() => setMostrarModal(false)}>
                  <X className="h-6 w-6 text-gray-400 hover:text-gray-600" />
                </button>
              </div>

              <form onSubmit={handleCrear} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Matrícula *
                  </label>
                  <input
                    type="text"
                    value={nuevoVehiculo.matricula}
                    onChange={(e) =>
                      setNuevoVehiculo({ ...nuevoVehiculo, matricula: e.target.value.toUpperCase() })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Marca</label>
                    <input
                      type="text"
                      value={nuevoVehiculo.marca}
                      onChange={(e) =>
                        setNuevoVehiculo({ ...nuevoVehiculo, marca: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
                    <input
                      type="text"
                      value={nuevoVehiculo.modelo}
                      onChange={(e) =>
                        setNuevoVehiculo({ ...nuevoVehiculo, modelo: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                  <input
                    type="text"
                    value={nuevoVehiculo.color}
                    onChange={(e) =>
                      setNuevoVehiculo({ ...nuevoVehiculo, color: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre del cliente
                  </label>
                  <input
                    type="text"
                    value={nuevoVehiculo.cliente_nombre}
                    onChange={(e) =>
                      setNuevoVehiculo({ ...nuevoVehiculo, cliente_nombre: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono del cliente
                  </label>
                  <input
                    type="tel"
                    value={nuevoVehiculo.cliente_telefono}
                    onChange={(e) =>
                      setNuevoVehiculo({ ...nuevoVehiculo, cliente_telefono: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setMostrarModal(false)}
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={crearVehiculoMutation.isPending}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                  >
                    {crearVehiculoMutation.isPending ? 'Creando...' : 'Crear'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
