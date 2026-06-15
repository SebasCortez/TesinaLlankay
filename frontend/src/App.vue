<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="logo">🔧 TécniCusco</router-link>
      <div class="nav-links">
        <router-link to="/buscar">Buscar técnicos</router-link>
        <template v-if="auth.estaAutenticado">
          <router-link v-if="auth.esAdmin" to="/admin">Panel admin</router-link>
          <router-link to="/solicitudes">Mis solicitudes</router-link>
          <router-link to="/mi-perfil">Mi perfil</router-link>
          <button class="btn-logout" @click="cerrarSesion">Salir</button>
        </template>
        <template v-else>
          <router-link v-if="auth.esAdmin" to="/admin">Panel admin</router-link>
          <router-link to="/mi-perfil">Mi perfil</router-link>
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

const auth = useAuthStore()
const router = useRouter()

function cerrarSesion() {
  auth.logout()
  router.push('/')
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; background: #F5F4F0; color: #1A1A18; }
#app { min-height: 100vh; }
.navbar {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 32px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 100;
}
.logo { font-weight: 700; font-size: 16px; text-decoration: none; color: #1A1A18; }
.nav-links { display: flex; align-items: center; gap: 20px; }
.nav-links a { text-decoration: none; color: #555; font-size: 14px; font-weight: 500; }
.nav-links a.router-link-active { color: #1D9E75; }
.btn-nav {
  background: #1D9E75; color: #fff !important;
  padding: 7px 16px; border-radius: 8px;
}
.btn-logout {
  background: none; border: 1px solid #ccc;
  padding: 6px 14px; border-radius: 8px;
  font-size: 14px; cursor: pointer; color: #555;
}
.btn-logout:hover { border-color: #888; color: #1A1A18; }
</style>