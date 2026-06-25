import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Cargar token si existe
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

import { useThemeStore } from './stores/theme'
const theme = useThemeStore()
theme.init()

import { registerSW } from 'virtual:pwa-register'

registerSW({ immediate: true })

app.mount('#app')   