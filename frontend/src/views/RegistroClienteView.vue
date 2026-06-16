<template>
  <div class="page-center">
    <div class="card registro-card">
      <div class="registro-header">
        <div class="registro-icon">👤</div>
        <h2>Crear cuenta de cliente</h2>
        <p>Encuentra y contrata técnicos verificados en Cusco</p>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Nombre</label>
          <input v-model="form.first_name" class="form-input" type="text" placeholder="Tu nombre" />
        </div>
        <div class="form-group">
          <label class="form-label">Apellido</label>
          <input v-model="form.last_name" class="form-input" type="text" placeholder="Tu apellido" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Nombre de usuario</label>
        <input v-model="form.username" class="form-input" type="text" placeholder="Ej: juan_perez" />
      </div>
      <div class="form-group">
        <label class="form-label">Correo electrónico</label>
        <input v-model="form.email" class="form-input" type="email" placeholder="tucorreo@gmail.com" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Celular</label>
          <input v-model="form.celular" class="form-input" type="tel" placeholder="+51 984 000 000" />
        </div>
        <div class="form-group">
          <label class="form-label">Distrito</label>
          <select v-model="form.distrito" class="form-select">
            <option value="">Selecciona</option>
            <option v-for="d in distritos" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Contraseña</label>
        <input v-model="form.password" class="form-input" type="password" placeholder="Mínimo 8 caracteres" />
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="exito" class="alert alert-success">{{ exito }}</div>

      <button class="btn-primary" style="width:100%;justify-content:center;padding:12px" @click="registrar"
        :disabled="cargando">
        {{ cargando ? 'Creando cuenta...' : 'Crear cuenta' }}
      </button>

      <hr class="divider">
      <p class="registro-footer">
        ¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link> ·
        ¿Eres técnico? <router-link to="/registro-trabajador">Regístrate aquí</router-link>
      </p>
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
const distritos = ['Cusco Centro', 'San Blas', 'San Sebastián', 'San Jerónimo', 'Santiago', 'Wanchaq', 'Poroy', 'Belén']
const form = ref({ first_name: '', last_name: '', username: '', email: '', celular: '', distrito: '', password: '', rol: 'cliente' })

async function registrar() {
  error.value = ''
  if (!form.value.first_name || !form.value.username || !form.value.password)
    return error.value = 'Completa los campos obligatorios'
  if (form.value.password.length < 8)
    return error.value = 'La contraseña debe tener al menos 8 caracteres'
  cargando.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/usuarios/registro/', form.value)
    exito.value = '✅ ¡Cuenta creada! Redirigiendo...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e: any) {
    error.value = e.response?.data?.username?.[0] || 'Error al registrar'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.registro-card {
  padding: 40px;
  width: 480px;
  max-width: 100%;
}

.registro-header {
  text-align: center;
  margin-bottom: 28px;
}

.registro-icon {
  width: 52px;
  height: 52px;
  background: var(--primary-light);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin: 0 auto 14px;
}

.registro-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.registro-header p {
  font-size: 14px;
  color: var(--text2);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.registro-footer {
  font-size: 13px;
  color: var(--text2);
  text-align: center;
}

.registro-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}
</style>