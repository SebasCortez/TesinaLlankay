<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="logo">
        <div class="logo-icon">🔧</div>
        <span>TécniCusco</span>
      </router-link>
      <div class="nav-links">
        <router-link to="/buscar" class="nav-link">Buscar técnicos</router-link>
        <button class="btn-theme" @click="theme.toggle()" :title="theme.dark ? 'Modo claro' : 'Modo oscuro'">
          {{ theme.dark ? '☀️' : '🌙' }}
        </button>
        <template v-if="!auth.estaAutenticado">
          <router-link to="/login" class="nav-link">Iniciar sesión</router-link>
          <router-link to="/registro-cliente" class="btn-primary">Registrarse</router-link>
        </template>
        <template v-else>
          <router-link v-if="auth.esAdmin" to="/admin" class="nav-link">Panel admin</router-link>
          <router-link v-if="!auth.esAdmin" to="/solicitudes" class="nav-link">Mis solicitudes</router-link>
          <router-link to="/mi-perfil" class="nav-link">Mi perfil</router-link>
          <button class="btn-logout" @click="cerrarSesion">Salir</button>
        </template>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
const theme = useThemeStore()


const auth = useAuthStore()
const router = useRouter()

function cerrarSesion() {
  auth.logout()
  router.push('/')
}
</script>

<style>
#app {
  min-height: 100vh;
}

.navbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text);
  font-weight: 700;
  font-size: 17px;
  letter-spacing: -0.3px;
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: var(--primary);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-link {
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--text2);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s;
}

.nav-link:hover {
  background: var(--bg);
  color: var(--text);
}

.nav-link.router-link-active {
  color: var(--primary);
  background: var(--primary-light);
}

.btn-logout {
  padding: 7px 14px;
  background: transparent;
  border: 1.5px solid var(--border2);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--text2);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.btn-logout:hover {
  border-color: var(--text2);
  color: var(--text);
}
.btn-theme {
  width: 36px; height: 36px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border2);
  background: transparent;
  font-size: 16px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.btn-theme:hover { background: var(--bg); }
</style>