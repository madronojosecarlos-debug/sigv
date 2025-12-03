import { Outlet, Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import { alertasApi } from '../services/api'
import {
  LayoutDashboard,
  Car,
  Map,
  Tags,
  Bell,
  Users,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/vehiculos', icon: Car, label: 'Vehículos' },
  { path: '/mapa', icon: Map, label: 'Mapa' },
  { path: '/etiquetas', icon: Tags, label: 'Etiquetas' },
  { path: '/alertas', icon: Bell, label: 'Alertas' },
  { path: '/usuarios', icon: Users, label: 'Usuarios', adminOnly: true },
  { path: '/configuracion', icon: Settings, label: 'Configuración', adminOnly: true },
]

export default function Layout() {
  const location = useLocation()
  const { usuario, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const { data: contadorAlertas } = useQuery({
    queryKey: ['alertas-contador'],
    queryFn: alertasApi.contador,
    refetchInterval: 30000, // Actualizar cada 30 segundos
  })

  const isAdmin = usuario?.rol === 'administrador'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar móvil */}
      <div
        className={clsx(
          'fixed inset-0 z-40 lg:hidden',
          sidebarOpen ? 'block' : 'hidden'
        )}
      >
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75"
          onClick={() => setSidebarOpen(false)}
        />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
          <div className="flex h-16 items-center justify-between px-4 border-b">
            <span className="text-xl font-bold text-primary-600">SIGV</span>
            <button onClick={() => setSidebarOpen(false)}>
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 px-2 py-4 space-y-1">
            {menuItems
              .filter((item) => !item.adminOnly || isAdmin)
              .map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={clsx(
                    'flex items-center px-3 py-2 rounded-lg text-sm font-medium',
                    location.pathname === item.path
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.label}
                  {item.path === '/alertas' && contadorAlertas?.no_leidas > 0 && (
                    <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {contadorAlertas.no_leidas}
                    </span>
                  )}
                </Link>
              ))}
          </nav>
        </div>
      </div>

      {/* Sidebar desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r">
          <div className="flex h-16 items-center px-6 border-b">
            <span className="text-xl font-bold text-primary-600">SIGV</span>
          </div>
          <nav className="flex-1 px-3 py-4 space-y-1">
            {menuItems
              .filter((item) => !item.adminOnly || isAdmin)
              .map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={clsx(
                    'flex items-center px-3 py-2 rounded-lg text-sm font-medium',
                    location.pathname === item.path
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.label}
                  {item.path === '/alertas' && contadorAlertas?.no_leidas > 0 && (
                    <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {contadorAlertas.no_leidas}
                    </span>
                  )}
                </Link>
              ))}
          </nav>
          <div className="p-4 border-t">
            <div className="flex items-center">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {usuario?.nombre}
                </p>
                <p className="text-xs text-gray-500 truncate">{usuario?.rol}</p>
              </div>
              <button
                onClick={logout}
                className="ml-2 p-2 text-gray-400 hover:text-gray-600"
                title="Cerrar sesión"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="lg:pl-64">
        {/* Header móvil */}
        <div className="sticky top-0 z-30 flex h-16 items-center bg-white border-b px-4 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-500 hover:text-gray-600"
          >
            <Menu className="h-6 w-6" />
          </button>
          <span className="ml-4 text-lg font-semibold text-primary-600">SIGV</span>
        </div>

        {/* Contenido */}
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
