import { defineStore } from 'pinia'
import api from '../services/api'
import type { Usuario, LoginResponse } from '../types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    usuario: (JSON.parse(localStorage.getItem('usuario') || 'null') as Usuario | null),
    token: (localStorage.getItem('token') || null) as string | null,
    refreshToken: (localStorage.getItem('refreshToken') || null) as string | null,
    modoActual: ((localStorage.getItem('modoActual') as 'cliente' | 'trabajador' | null) || 'cliente') as 'cliente' | 'trabajador',
  }),

  getters: {
    estaAutenticado: (state) => !!state.token,
    esAdmin: (state) => state.usuario?.rol === 'admin',
    esCliente: (state) => state.usuario?.rol === 'cliente',
    esTrabajador: (state) => state.usuario?.rol === 'trabajador',
    enModoTrabajador: (state) => state.usuario?.rol === 'trabajador' && state.modoActual === 'trabajador',
    enModoCliente: (state) => state.modoActual === 'cliente',
  },

  actions: {
    async login(username: string, password: string, captchaKey?: string, captchaValue?: string): Promise<LoginResponse> {
      const payload: Record<string, string> = { username, password }
      if (captchaKey && captchaValue) {
        payload.captcha_key = captchaKey
        payload.captcha_value = captchaValue
      }
      const res = await api.post<LoginResponse>('/usuarios/login/', payload)
      this.token = res.data.access
      this.refreshToken = res.data.refresh
      this.usuario = res.data.usuario

      // Si es trabajador, puede iniciar en modo técnico o cliente
      if (res.data.usuario.rol === 'trabajador' && !localStorage.getItem('modoActual')) {
        this.modoActual = 'trabajador'
        localStorage.setItem('modoActual', 'trabajador')
      }

      localStorage.setItem('token', res.data.access)
      localStorage.setItem('refreshToken', res.data.refresh)
      localStorage.setItem('usuario', JSON.stringify(res.data.usuario))
      return res.data
    },

    async loginConGoogle(credential: string): Promise<LoginResponse> {
      const res = await api.post<LoginResponse>('/usuarios/google-login/', { credential })
      this.token = res.data.access
      this.refreshToken = res.data.refresh
      this.usuario = res.data.usuario

      localStorage.setItem('token', res.data.access)
      localStorage.setItem('refreshToken', res.data.refresh)
      localStorage.setItem('usuario', JSON.stringify(res.data.usuario))
      return res.data
    },

    cambiarModo(modo: 'cliente' | 'trabajador') {
      this.modoActual = modo
      localStorage.setItem('modoActual', modo)
    },

    logout() {
      this.token = null
      this.refreshToken = null
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('usuario')
      localStorage.removeItem('modoActual')
    },

    actualizarUsuarioLocal(nuevoUsuario: Partial<Usuario>) {
      if (this.usuario) {
        this.usuario = { ...this.usuario, ...nuevoUsuario }
        localStorage.setItem('usuario', JSON.stringify(this.usuario))
      }
    }
  }
})