<template>
  <div class="page-center">
    <div class="card">
      <h2>Registro de cliente</h2>
      <div class="campo">
        <label>Nombre</label>
        <input v-model="form.first_name" type="text" placeholder="Tu nombre" />
      </div>
      <div class="campo">
        <label>Apellido</label>
        <input v-model="form.last_name" type="text" placeholder="Tu apellido" />
      </div>
      <div class="campo">
        <label>Usuario</label>
        <input v-model="form.username" type="text" placeholder="Nombre de usuario" />
      </div>
      <div class="campo">
        <label>Correo</label>
        <input v-model="form.email" type="email" placeholder="tucorreo@gmail.com" />
      </div>
      <div class="campo">
        <label>Celular</label>
        <input v-model="form.celular" type="tel" placeholder="+51 984 000 000" />
      </div>
      <div class="campo">
        <label>Distrito</label>
        <select v-model="form.distrito">
          <option value="">Selecciona tu distrito</option>
          <option v-for="d in distritos" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
      <div class="campo">
        <label>Contraseña</label>
        <input v-model="form.password" type="password" placeholder="Mínimo 8 caracteres" />
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="exito" class="exito">{{ exito }}</div>
      <button class="btn-verde" @click="registrar" :disabled="cargando">
        {{ cargando ? 'Registrando...' : 'Crear cuenta' }}
      </button>
      <p class="link">¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const error = ref('')
const exito = ref('')
const cargando = ref(false)

const distritos = ['Cusco Centro','San Blas','San Sebastián','San Jerónimo','Santiago','Wanchaq','Poroy','Belén']

const form = ref({
  first_name: '', last_name: '', username: '',
  email: '', celular: '', distrito: '', password: '',
  rol: 'cliente'
})

async function registrar() {
  error.value = ''
  if (!form.value.first_name || !form.value.username || !form.value.password)
    return error.value = 'Completa todos los campos obligatorios'
  if (form.value.password.length < 8)
    return error.value = 'La contraseña debe tener al menos 8 caracteres'
  cargando.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/usuarios/registro/', form.value)
    exito.value = '¡Cuenta creada! Redirigiendo...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e: any) {
    error.value = e.response?.data?.username?.[0] || 'Error al registrar, intenta de nuevo'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.page-center {
  min-height: calc(100vh - 56px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.card {
  background: #fff; border: 1px solid #e0e0e0;
  border-radius: 16px; padding: 32px;
  width: 440px; max-width: 100%;
}
h2 { font-size: 20px; font-weight: 700; margin-bottom: 24px; }
.campo { margin-bottom: 14px; }
.campo label { display: block; font-size: 12px; font-weight: 600; color: #555; margin-bottom: 5px; }
.campo input, .campo select {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ccc; border-radius: 8px; font-size: 14px; outline: none;
}
.campo input:focus, .campo select:focus { border-color: #1D9E75; }
.btn-verde {
  width: 100%; padding: 11px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
  cursor: pointer; margin-top: 8px;
}
.btn-verde:disabled { background: #aaa; cursor: not-allowed; }
.error { background: #fde8e8; color: #c0392b; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.exito { background: #e1f5ee; color: #0f6e56; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.link { font-size: 13px; color: #666; margin-top: 16px; text-align: center; }
.link a { color: #1D9E75; }
</style>