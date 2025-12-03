import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usuariosApi } from '../services/api'
import { Usuario } from '../types'
import { Plus, Edit2, Trash2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function Usuarios() {
  const queryClient = useQueryClient()
  const [mostrarModal, setMostrarModal] = useState(false)
  const [editando, setEditando] = useState<Usuario | null>(null)
  const [form, setForm] = useState({
    email: '', nombre: '', apellidos: '', password: '', rol: 'mecanico', telefono: ''
  })

  const { data: usuarios, isLoading } = useQuery({
    queryKey: ['usuarios'],
    queryFn: () => usuariosApi.listar(),
  })

  const crearMutation = useMutation({
    mutationFn: usuariosApi.crear,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      cerrarModal()
      toast.success('Usuario creado')
    },
    onError: () => toast.error('Error al crear usuario'),
  })

  const actualizarMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      usuariosApi.actualizar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      cerrarModal()
      toast.success('Usuario actualizado')
    },
  })

  const eliminarMutation = useMutation({
    mutationFn: usuariosApi.eliminar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
      toast.success('Usuario desactivado')
    },
  })

  const cerrarModal = () => {
    setMostrarModal(false)
    setEditando(null)
    setForm({ email: '', nombre: '', apellidos: '', password: '', rol: 'mecanico', telefono: '' })
  }

  const abrirEditar = (usuario: Usuario) => {
    setEditando(usuario)
    setForm({
      email: usuario.email,
      nombre: usuario.nombre,
      apellidos: usuario.apellidos || '',
      password: '',
      rol: usuario.rol,
      telefono: usuario.telefono || ''
    })
    setMostrarModal(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editando) {
      const { password, ...data } = form
      actualizarMutation.mutate({ id: editando.id, data })
    } else {
      crearMutation.mutate(form)
    }
  }

  const roles = { administrador: 'Administrador', asesor: 'Asesor', mecanico: 'Mecánico' }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Usuarios</h1>
          <p className="text-gray-500">Gestión de usuarios del sistema</p>
        </div>
        <button
          onClick={() => setMostrarModal(true)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nuevo Usuario
        </button>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios?.map((usuario: Usuario) => (
              <tr key={usuario.id}>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{usuario.nombre} {usuario.apellidos}</div>
                  <div className="text-sm text-gray-500">{usuario.email}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={clsx('px-2 py-1 text-xs rounded-full',
                    usuario.rol === 'administrador' ? 'bg-purple-100 text-purple-800' :
                    usuario.rol === 'asesor' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  )}>
                    {roles[usuario.rol]}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={clsx('px-2 py-1 text-xs rounded-full',
                    usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  )}>
                    {usuario.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button onClick={() => abrirEditar(usuario)} className="p-1 hover:bg-gray-100 rounded">
                      <Edit2 className="h-4 w-4 text-gray-400" />
                    </button>
                    {usuario.activo && (
                      <button
                        onClick={() => { if (confirm('¿Desactivar este usuario?')) eliminarMutation.mutate(usuario.id) }}
                        className="p-1 hover:bg-gray-100 rounded"
                      >
                        <Trash2 className="h-4 w-4 text-gray-400" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {mostrarModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={cerrarModal} />
            <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">{editando ? 'Editar Usuario' : 'Nuevo Usuario'}</h2>
                <button onClick={cerrarModal}><X className="h-6 w-6 text-gray-400" /></button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input type="email" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg" required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                    <input type="text" value={form.nombre} onChange={(e) => setForm({...form, nombre: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
                    <input type="text" value={form.apellidos} onChange={(e) => setForm({...form, apellidos: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg" />
                  </div>
                </div>
                {!editando && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                    <input type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg" required={!editando} />
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
                  <select value={form.rol} onChange={(e) => setForm({...form, rol: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg">
                    <option value="mecanico">Mecánico</option>
                    <option value="asesor">Asesor</option>
                    <option value="administrador">Administrador</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                  <input type="tel" value={form.telefono} onChange={(e) => setForm({...form, telefono: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg" />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={cerrarModal} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancelar</button>
                  <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
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
