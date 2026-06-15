<template>
  <div class="page-center">
    <div class="card">
      <h2>Iniciar sesión</h2>
      <div class="campo">
        <label>Usuario</label>
        <input v-model="form.username" type="text" placeholder="Tu nombre de usuario" />
      </div>
      <div class="campo">
        <label>Contraseña</label>
        <input v-model="form.password" type="password" placeholder="Tu contraseña" />
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <button class="btn-verde" @click="iniciarSesion" :disabled="cargando">
        {{ cargando ? 'Ingresando...' : 'Ingresar' }}
      </button>
      <p class="link">¿No tienes cuenta?
        <router-link to="/registro-cliente">Regístrate como cliente</router-link> o
        <router-link to="/registro-trabajador">como técnico</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const cargando = ref(false)
const form = ref({ username: '', password: '' })

async function iniciarSesion() {
  error.value = ''
  cargando.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    if (auth.esAdmin) router.push('/admin')
    else router.push('/buscar')
  } catch (e: any) {
    error.value = 'Usuario o contraseña incorrectos'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.page-center {
  min-height: calc(100vh - 56px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.card {
  background: #fff; border: 1px solid #e0e0e0;
  border-radius: 16px; padding: 32px;
  width: 400px; max-width: 100%;
}
h2 { font-size: 20px; font-weight: 700; margin-bottom: 24px; }
.campo { margin-bottom: 16px; }
.campo label { display: block; font-size: 12px; font-weight: 600; color: #555; margin-bottom: 5px; }
.campo input {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ccc; border-radius: 8px;
  font-size: 14px; outline: none;
}
.campo input:focus { border-color: #1D9E75; }
.btn-verde {
  width: 100%; padding: 11px;
  background: #1D9E75; color: #fff;
  border: none; border-radius: 8px;
  font-size: 14px; font-weight: 600;
  cursor: pointer; margin-top: 8px;
}
.btn-verde:disabled { background: #aaa; cursor: not-allowed; }
.error { background: #fde8e8; color: #c0392b; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.link { font-size: 13px; color: #666; margin-top: 16px; text-align: center; }
.link a { color: #1D9E75; }
</style>