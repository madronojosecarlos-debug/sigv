import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Vehiculos from './pages/Vehiculos'
import VehiculoDetalle from './pages/VehiculoDetalle'
import Mapa from './pages/Mapa'
import Etiquetas from './pages/Etiquetas'
import Alertas from './pages/Alertas'
import Usuarios from './pages/Usuarios'
import Configuracion from './pages/Configuracion'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="vehiculos" element={<Vehiculos />} />
          <Route path="vehiculos/:id" element={<VehiculoDetalle />} />
          <Route path="mapa" element={<Mapa />} />
          <Route path="etiquetas" element={<Etiquetas />} />
          <Route path="alertas" element={<Alertas />} />
          <Route path="usuarios" element={<Usuarios />} />
          <Route path="configuracion" element={<Configuracion />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
