import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { etiquetasApi } from '../services/api'
import { Etiqueta } from '../types'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'

export default function Etiquetas() {
  const queryClient = useQueryClient()
  const { usuario } = useAuthStore()
  const isAdmin = usuario?.rol === 'administrador'
  const [mostrarModal, setMostrarModal] = useState(false)
  const [editando, setEditando] = useState<Etiqueta | null>(null)
  const [form, setForm] = useState({ nombre: '', color: '#3498db', descripcion: '' })

  const { data: etiquetas, isLoading } = useQuery({
    queryKey: ['etiquetas-todas'],
    queryFn: () => etiquetasApi.listar(undefined),
  })

  const crearMutation = useMutation({
    mutationFn: etiquetasApi.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['etiquetas'] })
      cerrarModal()
      toast.success('Etiqueta creada')
    },
  })

  const actualizarMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      etiquetasApi.actualizar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['etiquetas'] })
      cerrarModal()
      toast.success('Etiqueta actualizada')
    },
  })

  const eliminarMutation = useMutation({
    mutationFn: etiquetasApi.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['etiquetas'] })
      toast.success('Etiqueta eliminada')
    },
  })

  const cerrarModal = () => {
    setMostrarModal(false)
    setEditando(null)
    setForm({ nombre: '', color: '#3498db', descripcion: '' })
  }

  const abrirEditar = (etiqueta: Etiqueta) => {
    setEditando(etiqueta)
    setForm({ nombre: etiqueta.nombre, color: etiqueta.color, descripcion: etiqueta.descripcion || '' })
    setMostrarModal(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editando) {
      actualizarMutation.mutate({ id: editando.id, data: form })
    } else {
      crearMutation.mutate(form)
    }
  }

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
          <h1 className="text-2xl font-bold text-gray-900">Etiquetas</h1>
          <p className="text-gray-500">Gestión de etiquetas de proceso</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setMostrarModal(true)}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Nueva Etiqueta
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
          {etiquetas?.map((etiqueta: Etiqueta) => (
            <div
              key={etiqueta.id}
              className="border rounded-lg p-4"
              style={{ borderLeftWidth: '4px', borderLeftColor: etiqueta.color }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: etiqueta.color }}
                    />
                    <h3 className="font-semibold">{etiqueta.nombre}</h3>
                  </div>
                  {etiqueta.descripcion && (
                    <p className="text-sm text-gray-500 mt-1">{etiqueta.descripcion}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-2">
                    {etiqueta.cantidad_vehiculos || 0} vehículos
                  </p>
                </div>
                {isAdmin && !etiqueta.es_sistema && (
                  <div className="flex gap-1">
                    <button
                      onClick={() => abrirEditar(etiqueta)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Edit2 className="h-4 w-4 text-gray-400" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm('¿Eliminar esta etiqueta?')) {
                          eliminarMutation.mutate(etiqueta.id)
                        }
                      }}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Trash2 className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {mostrarModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={cerrarModal} />
            <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  {editando ? 'Editar Etiqueta' : 'Nueva Etiqueta'}
                </h2>
                <button onClick={cerrarModal}>
                  <X className="h-6 w-6 text-gray-400" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                  <input
                    type="text"
                    value={form.nombre}
                    onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                  <div className="flex items-center gap-3">
                    <input
                      type="color"
                      value={form.color}
                      onChange={(e) => setForm({ ...form, color: e.target.value })}
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={form.color}
                      onChange={(e) => setForm({ ...form, color: e.target.value })}
                      className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={form.descripcion}
                    onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    rows={2}
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={cerrarModal}
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    {editando ? 'Guardar' : 'Crear'}
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
