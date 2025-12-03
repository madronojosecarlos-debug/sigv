import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../services/api'
import { DatosMapa } from '../types'
import { Link } from 'react-router-dom'

export default function Mapa() {
  const { data: datosMapa, isLoading } = useQuery({
    queryKey: ['mapa'],
    queryFn: dashboardApi.getMapa,
    refetchInterval: 30000,
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mapa de Instalaciones</h1>
        <p className="text-gray-500">Vista en tiempo real de la ubicación de vehículos</p>
      </div>

      {/* Mapa visual */}
      <div className="bg-white rounded-xl shadow p-6">
        <div className="relative bg-gray-100 rounded-lg" style={{ height: '500px' }}>
          {/* Representación visual del plano en L */}
          <svg viewBox="0 0 600 500" className="w-full h-full">
            {/* Fondo */}
            <rect x="0" y="0" width="600" height="500" fill="#f3f4f6" />

            {/* Parcela 15 (parte inferior izquierda de la L) */}
            <rect x="50" y="250" width="200" height="200" fill="#e5e7eb" stroke="#9ca3af" strokeWidth="2" rx="4" />
            <text x="150" y="350" textAnchor="middle" className="text-sm" fill="#6b7280">Parcela 15</text>

            {/* Parcela 14 (parte superior de la L) */}
            <rect x="150" y="50" width="200" height="200" fill="#e5e7eb" stroke="#9ca3af" strokeWidth="2" rx="4" />
            <text x="250" y="150" textAnchor="middle" className="text-sm" fill="#6b7280">Parcela 14</text>

            {/* Entrada principal */}
            <rect x="50" y="450" width="100" height="30" fill="#fecaca" stroke="#f87171" strokeWidth="2" rx="4" />
            <text x="100" y="468" textAnchor="middle" fontSize="10" fill="#991b1b">Entrada</text>

            {/* Taller */}
            <rect x="400" y="150" width="150" height="200" fill="#fef3c7" stroke="#fbbf24" strokeWidth="2" rx="4" />
            <text x="475" y="250" textAnchor="middle" className="text-sm" fill="#92400e">Taller</text>

            {/* Cámaras LPR */}
            <circle cx="60" cy="445" r="8" fill="#ef4444" />
            <text x="60" y="435" textAnchor="middle" fontSize="8" fill="#991b1b">LPR-1</text>

            <circle cx="140" cy="445" r="8" fill="#ef4444" />
            <text x="140" y="435" textAnchor="middle" fontSize="8" fill="#991b1b">LPR-2</text>

            {/* Cámaras Overview */}
            <circle cx="70" cy="430" r="5" fill="#3b82f6" />
            <circle cx="230" cy="430" r="5" fill="#3b82f6" />
            <circle cx="150" cy="250" r="5" fill="#3b82f6" />
            <circle cx="330" cy="150" r="5" fill="#3b82f6" />
            <circle cx="330" cy="70" r="5" fill="#3b82f6" />
            <circle cx="170" cy="100" r="5" fill="#3b82f6" />
          </svg>

          {/* Leyenda */}
          <div className="absolute top-4 right-4 bg-white rounded-lg shadow p-3 text-xs space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span>Cámara LPR</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span>Cámara Overview</span>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de zonas con vehículos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {datosMapa?.map((zona: DatosMapa) => (
          <div
            key={zona.id}
            className="bg-white rounded-xl shadow p-6"
            style={{ borderLeft: `4px solid ${zona.color}` }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">{zona.nombre}</h3>
              <span className="text-2xl font-bold" style={{ color: zona.color }}>
                {zona.cantidad_vehiculos}
              </span>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto">
              {zona.vehiculos.map((v) => (
                <Link
                  key={v.id}
                  to={`/vehiculos/${v.id}`}
                  className="block p-2 hover:bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{v.matricula}</span>
                    <div className="flex gap-1">
                      {v.etiquetas.slice(0, 2).map((e, i) => (
                        <span
                          key={i}
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: e.color }}
                          title={e.nombre}
                        />
                      ))}
                    </div>
                  </div>
                  <p className="text-xs text-gray-500">
                    {v.marca} {v.modelo}
                  </p>
                </Link>
              ))}
              {zona.vehiculos.length === 0 && (
                <p className="text-sm text-gray-400">Sin vehículos</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
