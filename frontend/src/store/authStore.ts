import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Usuario } from '../types'

interface AuthState {
  usuario: Usuario | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, usuario: Usuario) => void
  logout: () => void
  updateUsuario: (usuario: Usuario) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      usuario: null,
      token: null,
      isAuthenticated: false,

      login: (token: string, usuario: Usuario) => {
        localStorage.setItem('token', token)
        set({ token, usuario, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('token')
        set({ token: null, usuario: null, isAuthenticated: false })
      },

      updateUsuario: (usuario: Usuario) => {
        set({ usuario })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        usuario: state.usuario,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
