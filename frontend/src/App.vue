<template>
  <div id="app" @click="cerrarDropdownSiClicFuera">
    <!-- NAVBAR PRINCIPAL -->
    <nav class="navbar">
      <router-link to="/" class="logo" @click="menuMovilAbierto = false">
        <div class="logo-icon">🔧</div>
        <div class="logo-text-wrap">
          <span class="logo-text">Llankay</span>
          <span class="logo-badge">Cusco</span>
        </div>
      </router-link>

      <!-- ENLACES ESCRITORIO -->
      <div class="nav-links hide-on-mobile">
        <!-- MODO DUAL SWITCHER (SI ES TÉCNICO) -->
        <div v-if="auth.esTrabajador" class="modo-switch">
          <button
            :class="['btn-modo', auth.modoActual === 'cliente' ? 'activo' : '']"
            @click="auth.cambiarModo('cliente')"
            title="Actuar como cliente y contratar servicios"
          >
            🛒 Modo Cliente
          </button>
          <button
            :class="['btn-modo', auth.modoActual === 'trabajador' ? 'activo' : '']"
            @click="auth.cambiarModo('trabajador')"
            title="Actuar como técnico y recibir trabajos"
          >
            ⚡ Modo Técnico
          </button>
        </div>

        <!-- BOTÓN CONVERTIRSE EN TÉCNICO (SI SOLO ES CLIENTE) -->
        <router-link
          v-if="auth.estaAutenticado && !auth.esTrabajador && !auth.esAdmin"
          to="/registro-trabajador"
          class="btn-ofrecer"
        >
          💼 Ofrecer servicios
        </router-link>

        <!-- ENLACES DE NAVEGACIÓN -->
        <router-link to="/buscar" class="nav-link">
          <span>🔍</span> Buscar técnicos
        </router-link>

        <router-link to="/contacto" class="nav-link">
          <span>✉️</span> Contacto
        </router-link>

        <router-link v-if="auth.estaAutenticado && !auth.esAdmin" to="/solicitudes" class="nav-link">
          <span>📋</span> {{ auth.enModoTrabajador ? 'Trabajos recibidos' : 'Mis solicitudes' }}
        </router-link>

        <router-link v-if="auth.esAdmin" to="/admin" class="nav-link admin-link">
          ⚡ Panel Admin
        </router-link>

        <!-- CAMPANA DE NOTIFICACIONES (SI ESTÁ AUTENTICADO) -->
        <div v-if="auth.estaAutenticado" class="notif-wrapper" ref="notifWrapperRef">
          <button class="btn-notif" @click.stop="toggleNotificaciones" title="Notificaciones" aria-label="Notificaciones">
            <span>🔔</span>
            <span v-if="noLeidasCount > 0" class="notif-badge">{{ noLeidasCount > 9 ? '9+' : noLeidasCount }}</span>
          </button>

          <!-- DROPDOWN DE NOTIFICACIONES -->
          <div v-if="mostrarNotificaciones" class="notif-dropdown card" @click.stop>
            <div class="notif-dropdown-header">
              <div class="notif-header-title">
                <span>🔔 Notificaciones</span>
                <span v-if="noLeidasCount > 0" class="notif-count-pill">{{ noLeidasCount }} nuevas</span>
              </div>
              <button v-if="noLeidasCount > 0" class="btn-marcar-todas" @click="marcarTodasLeidas">
                Marcar todas leídas
              </button>
            </div>

            <div v-if="cargandoNotifs" class="notif-loading">
              <div class="spinner-sm"></div>
              <span>Cargando notificaciones...</span>
            </div>

            <div v-else-if="notificaciones.length === 0" class="notif-empty">
              <span>✨</span>
              <p>No tienes notificaciones por el momento</p>
            </div>

            <div v-else class="notif-list">
              <div
                v-for="n in notificaciones"
                :key="n.id"
                :class="['notif-item', !n.leida ? 'no-leida' : '']"
                @click="abrirNotificacion(n)"
              >
                <div class="notif-item-icon">
                  {{ getNotifIcono(n.tipo) }}
                </div>
                <div class="notif-item-content">
                  <div class="notif-item-title">{{ n.titulo }}</div>
                  <div class="notif-item-msg">{{ n.mensaje }}</div>
                  <div class="notif-item-time">{{ formatTiempoRelativo(n.fecha_creacion) }}</div>
                </div>
                <span v-if="!n.leida" class="notif-unread-dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- TEMA CLARO / OSCURO -->
        <button class="btn-theme" @click="theme.toggle()" :title="theme.dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'" aria-label="Cambiar tema">
          <span>{{ theme.dark ? '☀️' : '🌙' }}</span>
        </button>

        <template v-if="!auth.estaAutenticado">
          <router-link to="/login" class="nav-link">Iniciar sesión</router-link>
          <router-link to="/registro-cliente" class="btn-primary">Registrarse</router-link>
        </template>
        <template v-else>
          <router-link to="/mi-perfil" class="nav-link perfil-link">
            <span class="nav-avatar">{{ auth.usuario?.first_name?.[0] || 'U' }}{{ auth.usuario?.last_name?.[0] || '' }}</span>
            <span class="nav-user-name">{{ auth.usuario?.first_name }}</span>
          </router-link>
          <button class="btn-logout" @click="cerrarSesion" title="Cerrar sesión">
            Salir ➔
          </button>
        </template>
      </div>

      <!-- CONTROLES MÓVILES (Campana + Tema + Menú Hamburguesa) -->
      <div class="nav-mobile-controls show-on-mobile">
        <button class="btn-theme-mobile" @click="theme.toggle()" :title="theme.dark ? 'Modo claro' : 'Modo oscuro'">
          <span>{{ theme.dark ? '☀️' : '🌙' }}</span>
        </button>

        <button 
          v-if="auth.estaAutenticado" 
          class="btn-notif-mobile" 
          @click.stop="toggleNotificaciones"
          title="Notificaciones"
        >
          <span>🔔</span>
          <span v-if="noLeidasCount > 0" class="notif-badge-mobile">{{ noLeidasCount > 9 ? '9+' : noLeidasCount }}</span>
        </button>

        <button 
          class="btn-hamburger" 
          @click="menuMovilAbierto = !menuMovilAbierto" 
          :aria-expanded="menuMovilAbierto"
          aria-label="Abrir menú de navegación"
        >
          <span>{{ menuMovilAbierto ? '✕' : '☰' }}</span>
        </button>
      </div>
    </nav>

    <!-- MENÚ MÓVIL DESPLEGABLE (DRAWER) -->
    <div v-if="menuMovilAbierto" class="mobile-drawer-overlay" @click="menuMovilAbierto = false">
      <div class="mobile-drawer card" @click.stop>
        <div class="drawer-header">
          <div class="drawer-user" v-if="auth.estaAutenticado">
            <div class="drawer-avatar">
              {{ auth.usuario?.first_name?.[0] || 'U' }}{{ auth.usuario?.last_name?.[0] || '' }}
            </div>
            <div>
              <strong>{{ auth.usuario?.first_name }} {{ auth.usuario?.last_name }}</strong>
              <span class="drawer-user-role">@{{ auth.usuario?.username }} · {{ auth.esTrabajador ? 'Técnico' : 'Cliente' }}</span>
            </div>
          </div>
          <div v-else class="drawer-guest">
            <strong>Bienvenido a TécniCusco</strong>
            <span>Servicios técnicos en Cusco</span>
          </div>
          <button class="btn-drawer-close" @click="menuMovilAbierto = false">✕</button>
        </div>

        <!-- MODO DUAL EN MÓVIL -->
        <div v-if="auth.esTrabajador" class="drawer-modo-switch">
          <button
            :class="['btn-modo-mob', auth.modoActual === 'cliente' ? 'activo' : '']"
            @click="auth.cambiarModo('cliente')"
          >
            🛒 Modo Cliente
          </button>
          <button
            :class="['btn-modo-mob', auth.modoActual === 'trabajador' ? 'activo' : '']"
            @click="auth.cambiarModo('trabajador')"
          >
            ⚡ Modo Técnico
          </button>
        </div>

        <!-- ENLACES DEL MENÚ MÓVIL -->
        <div class="drawer-links">
          <router-link to="/" class="drawer-link" @click="menuMovilAbierto = false">
            <span>🏠</span> Inicio
          </router-link>
          <router-link to="/buscar" class="drawer-link" @click="menuMovilAbierto = false">
            <span>🔍</span> Buscar Técnicos y Mapa
          </router-link>
          <router-link to="/contacto" class="drawer-link" @click="menuMovilAbierto = false">
            <span>📍</span> Contacto y Sede Cusco
          </router-link>

          <template v-if="auth.estaAutenticado">
            <router-link to="/solicitudes" class="drawer-link" @click="menuMovilAbierto = false">
              <span>📋</span> {{ auth.enModoTrabajador ? 'Trabajos recibidos' : 'Mis solicitudes' }}
            </router-link>
            <router-link to="/mi-perfil" class="drawer-link" @click="menuMovilAbierto = false">
              <span>👤</span> Mi Perfil y Cuenta
            </router-link>
            <router-link v-if="auth.esAdmin" to="/admin" class="drawer-link drawer-admin" @click="menuMovilAbierto = false">
              <span>⚡</span> Panel de Administración
            </router-link>
          </template>
        </div>

        <hr class="divider">

        <!-- LEGAL Y ACCIONES INFERIORES EN MÓVIL -->
        <div class="drawer-footer">
          <div class="drawer-legal-links">
            <router-link to="/politica-privacidad" @click="menuMovilAbierto = false">Privacidad</router-link> ·
            <router-link to="/terminos-condiciones" @click="menuMovilAbierto = false">Términos</router-link>
          </div>

          <template v-if="!auth.estaAutenticado">
            <router-link to="/login" class="btn-secondary drawer-btn-auth" @click="menuMovilAbierto = false">
              Iniciar sesión
            </router-link>
            <router-link to="/registro-cliente" class="btn-primary drawer-btn-auth" @click="menuMovilAbierto = false">
              Registrarme como Cliente
            </router-link>
            <router-link to="/registro-trabajador" class="btn-ofrecer-mob" @click="menuMovilAbierto = false">
              💼 Registrarme como Técnico
            </router-link>
          </template>
          <template v-else>
            <button class="btn-danger drawer-btn-auth" @click="cerrarSesionMobile">
              Cerrar sesión
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- CONTENIDO DE LA PÁGINA -->
    <main class="app-main-content">
      <router-view />
    </main>

    <!-- FOOTER GLOBAL -->
    <AppFooter @configurar-cookies="abrirCookiesModal" />

    <!-- BANNER DE COOKIES -->
    <CookieBanner ref="cookieBannerRef" />

    <!-- ASISTENTE CHATBOT IA (GROQ LLAMA 3.3 70B) -->
    <ChatbotIA />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
import api from './services/api'
import type { Notificacion } from './types'
import AppFooter from './components/AppFooter.vue'
import CookieBanner from './components/CookieBanner.vue'
import ChatbotIA from './components/ChatbotIA.vue'

const theme = useThemeStore()
const auth = useAuthStore()
const router = useRouter()

const notificaciones = ref<Notificacion[]>([])
const noLeidasCount = ref(0)
const mostrarNotificaciones = ref(false)
const cargandoNotifs = ref(false)
const notifWrapperRef = ref<HTMLElement | null>(null)
const cookieBannerRef = ref<any>(null)
const menuMovilAbierto = ref(false)
let notifInterval: number | null = null

function getNotifIcono(tipo: string) {
  switch (tipo) {
    case 'solicitud_nueva': return '🛠️'
    case 'solicitud_aceptada': return '✅'
    case 'solicitud_en_progreso': return '🔧'
    case 'solicitud_completada': return '🎉'
    case 'solicitud_rechazada': return '❌'
    case 'calificacion_recibida': return '⭐'
    default: return '🔔'
  }
}

function formatTiempoRelativo(fechaStr: string) {
  const fecha = new Date(fechaStr)
  const ahora = new Date()
  const diffSegundos = Math.floor((ahora.getTime() - fecha.getTime()) / 1000)

  if (diffSegundos < 60) return 'Hace un momento'
  const minutos = Math.floor(diffSegundos / 60)
  if (minutos < 60) return `Hace ${minutos} min`
  const horas = Math.floor(minutos / 60)
  if (horas < 24) return `Hace ${horas} h`
  const dias = Math.floor(horas / 24)
  return `Hace ${dias} d`
}

async function cargarNotificaciones() {
  if (!auth.estaAutenticado) return
  try {
    const res = await api.get<{ no_leidas: number; notificaciones: Notificacion[] }>('/notificaciones/')
    notificaciones.value = res.data.notificaciones
    noLeidasCount.value = res.data.no_leidas
  } catch {
    // Silencioso en caso de error de red
  }
}

async function toggleNotificaciones() {
  mostrarNotificaciones.value = !mostrarNotificaciones.value
  if (mostrarNotificaciones.value) {
    cargandoNotifs.value = true
    await cargarNotificaciones()
    cargandoNotifs.value = false
  }
}

async function abrirNotificacion(n: Notificacion) {
  if (!n.leida) {
    try {
      await api.patch(`/notificaciones/${n.id}/leer/`)
      n.leida = true
      if (noLeidasCount.value > 0) noLeidasCount.value--
    } catch {}
  }
  mostrarNotificaciones.value = false
  if (n.enlace) {
    router.push(n.enlace)
  }
}

async function marcarTodasLeidas() {
  try {
    await api.post('/notificaciones/marcar-todas-leidas/')
    notificaciones.value.forEach(n => n.leida = true)
    noLeidasCount.value = 0
  } catch {}
}

function cerrarDropdownSiClicFuera(event: MouseEvent) {
  if (mostrarNotificaciones.value && notifWrapperRef.value && !notifWrapperRef.value.contains(event.target as Node)) {
    mostrarNotificaciones.value = false
  }
}

function cerrarSesion() {
  auth.logout()
  mostrarNotificaciones.value = false
  notificaciones.value = []
  noLeidasCount.value = 0
  router.push('/')
}

function cerrarSesionMobile() {
  menuMovilAbierto.value = false
  cerrarSesion()
}

function abrirCookiesModal() {
  cookieBannerRef.value?.abrirConfiguracion()
}

watch(() => auth.estaAutenticado, (isAuth) => {
  if (isAuth) {
    cargarNotificaciones()
  } else {
    notificaciones.value = []
    noLeidasCount.value = 0
  }
})

onMounted(() => {
  if (auth.estaAutenticado) {
    cargarNotificaciones()
    notifInterval = window.setInterval(cargarNotificaciones, 25000)
  }
})

onUnmounted(() => {
  if (notifInterval) clearInterval(notifInterval)
})
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main-content {
  flex: 1;
}

.navbar {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 16px;
    height: 62px;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: -0.5px;
}

.logo-icon {
  width: 38px;
  height: 38px;
  background: var(--primary-gradient);
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 4px 12px var(--primary-glow);
  color: #fff;
  transition: transform 0.2s ease;
}

.logo:hover .logo-icon {
  transform: rotate(-10deg) scale(1.05);
}

.logo-text-wrap {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.logo-badge {
  font-size: 10px;
  font-weight: 700;
  background: var(--primary-light);
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* CONMUTADOR DE MODO DUAL */
.modo-switch {
  display: flex;
  align-items: center;
  background: var(--surface-subtle);
  padding: 3px;
  border-radius: 24px;
  border: 1px solid var(--border);
  margin-right: 6px;
}

.btn-modo {
  padding: 5px 12px;
  border: none;
  border-radius: 20px;
  background: transparent;
  color: var(--text2);
  font-size: 12.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-modo:hover {
  color: var(--text);
}

.btn-modo.activo {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.btn-ofrecer {
  padding: 6px 12px;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px dashed var(--primary);
  border-radius: 20px;
  font-size: 12.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  text-decoration: none;
  transition: all 0.2s ease;
  margin-right: 4px;
}

.btn-ofrecer:hover {
  background: var(--primary);
  color: #fff;
  transform: translateY(-1px);
}

/* NOTIFICACIONES CAMPANA & DROPDOWN */
.notif-wrapper {
  position: relative;
}

.btn-notif {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-notif:hover {
  background: var(--surface-subtle);
  transform: scale(1.05);
}

.notif-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #EF4444;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  padding: 1px 5px;
  border-radius: 10px;
  border: 2px solid var(--surface);
}

.notif-dropdown {
  position: absolute;
  top: 48px;
  right: 0;
  width: 360px;
  max-width: 90vw;
  max-height: 480px;
  overflow-y: auto;
  padding: 0;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  z-index: 200;
  animation: fadeIn 0.2s ease-out;
}

.notif-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-subtle);
}

.notif-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.notif-count-pill {
  font-size: 11px;
  font-weight: 700;
  background: var(--primary-light);
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 10px;
}

.btn-marcar-todas {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
}

.notif-loading {
  padding: 24px;
  text-align: center;
  color: var(--text2);
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.notif-empty {
  padding: 32px 20px;
  text-align: center;
  color: var(--text2);
}

.notif-empty span {
  font-size: 28px;
  display: block;
  margin-bottom: 8px;
}

.notif-list {
  display: flex;
  flex-direction: column;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s ease;
  position: relative;
}

.notif-item:hover {
  background: var(--surface-subtle);
}

.notif-item.no-leida {
  background: rgba(37, 99, 235, 0.04);
}

.notif-item-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notif-item-content {
  flex: 1;
}

.notif-item-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 2px;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.notif-item-msg {
  font-size: 12.5px;
  color: var(--text2);
  line-height: 1.4;
  margin-bottom: 4px;
}

.notif-item-time {
  font-size: 11px;
  color: var(--text3);
}

.notif-unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
  margin-top: 6px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--text2);
  font-size: 14px;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: var(--surface-subtle);
  color: var(--text);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-logout {
  padding: 8px 14px;
  background: transparent;
  border: 1.5px solid var(--border2);
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text2);
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  border-color: var(--red);
  color: var(--red);
  background: var(--red-light);
}

.btn-theme {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-theme:hover {
  background: var(--surface-subtle);
  transform: rotate(15deg) scale(1.05);
}

/* ======================================================== */
/* CONTROLES Y MENÚ MÓVIL                                  */
/* ======================================================== */
.nav-mobile-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-hamburger,
.btn-theme-mobile,
.btn-notif-mobile {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.btn-notif-mobile {
  position: relative;
  font-size: 15px;
}

.notif-badge-mobile {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #EF4444;
  color: #fff;
  font-size: 9px;
  font-weight: 800;
  padding: 1px 4px;
  border-radius: 8px;
}

/* DRAWER MÓVIL */
.mobile-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 990;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease-out;
}

.mobile-drawer {
  width: 320px;
  max-width: 85vw;
  height: 100vh;
  background: var(--surface);
  border-left: 1px solid var(--border);
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  animation: slideLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border-radius: 0;
}

@keyframes slideLeft {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.drawer-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.drawer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 800;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-user strong {
  display: block;
  font-size: 14px;
  color: var(--text);
}

.drawer-user-role {
  font-size: 12px;
  color: var(--text2);
}

.drawer-guest strong {
  display: block;
  font-size: 14.5px;
  color: var(--text);
}

.drawer-guest span {
  font-size: 12px;
  color: var(--text2);
}

.btn-drawer-close {
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 14px;
  cursor: pointer;
  color: var(--text2);
}

.drawer-modo-switch {
  display: flex;
  background: var(--surface-subtle);
  padding: 4px;
  border-radius: 20px;
  border: 1px solid var(--border);
  margin-bottom: 18px;
}

.btn-modo-mob {
  flex: 1;
  padding: 7px;
  border: none;
  border-radius: 16px;
  background: transparent;
  color: var(--text2);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.btn-modo-mob.activo {
  background: var(--primary-gradient);
  color: #fff;
}

.drawer-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--text);
  font-weight: 600;
  font-size: 14px;
  transition: background 0.15s ease;
}

.drawer-link:hover,
.drawer-link.router-link-active {
  background: var(--primary-light);
  color: var(--primary);
}

.drawer-admin {
  color: var(--amber) !important;
}

.drawer-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drawer-legal-links {
  font-size: 12px;
  color: var(--text3);
  text-align: center;
  margin-bottom: 6px;
}

.drawer-legal-links a {
  color: var(--text2);
  text-decoration: none;
}

.drawer-btn-auth {
  width: 100%;
  justify-content: center;
  padding: 11px;
}

.btn-ofrecer-mob {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 11px;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px dashed var(--primary);
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-weight: 700;
  font-size: 13.5px;
}
</style>