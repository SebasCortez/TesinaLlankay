import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    usuario: JSON.parse(localStorage.getItem('usuario') || 'null'),
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    estaAutenticado: (state) => !!state.token,
    esAdmin: (state) => state.usuario?.rol === 'admin',
    esCliente: (state) => state.usuario?.rol === 'cliente',
    esTrabajador: (state) => state.usuario?.rol === 'trabajador',
  },

  actions: {
    async login(username: string, password: string) {
      const res = await axios.post(`${API}/usuarios/login/`, { username, password })
      this.token = res.data.access
      this.usuario = res.data.usuario
      localStorage.setItem('token', res.data.access)
      localStorage.setItem('usuario', JSON.stringify(res.data.usuario))
      axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access}`
    },

    logout() {
      this.token = null
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      delete axios.defaults.headers.common['Authorization']
    },

    cargarToken() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})