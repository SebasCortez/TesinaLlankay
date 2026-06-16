<template>
  <div class="page-center">
    <div class="card solicitud-card" v-if="trabajador">
      <div class="sol-header">
        <div class="sol-avatar" :style="{ background: getColor(trabajador.id) }">
          {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
        </div>
        <div>
          <h2>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h2>
          <p class="sol-oficio">{{ trabajador.oficio }} · {{ trabajador.categoria }}</p>
        </div>
      </div>

      <hr class="divider">

      <h3>Nueva solicitud de servicio</h3>
      <p class="sol-desc">Describe tu problema con detalle para que el técnico pueda prepararse mejor.</p>

      <div class="form-group">
        <label class="form-label">Mensaje al técnico</label>
        <textarea v-model="form.mensaje" class="form-textarea"
          placeholder="Ej: Hola, necesito ayuda con una instalación eléctrica..." rows="2"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Descripción del problema</label>
        <textarea v-model="form.descripcion_problema" class="form-textarea"
          placeholder="Describe el problema con detalle: ¿qué pasó?, ¿desde cuándo?, ¿qué has intentado?"
          rows="4"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Dirección donde se realizará el servicio</label>
        <input v-model="form.direccion" class="form-input" type="text"
          placeholder="Ej: Calle Saphi 123, San Blas, Cusco" />
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="exito" class="alert alert-success">{{ exito }}</div>

      <div class="sol-btns">
        <router-link :to="`/trabajador/${trabajador.id}`" class="btn-secondary">← Volver</router-link>
        <button class="btn-primary" @click="enviar" :disabled="cargando">
          {{ cargando ? 'Enviando...' : '📩 Enviar solicitud' }}
        </button>
      </div>
    </div>
    <div v-else class="estado-carga">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const trabajador = ref<any>(null)
const error = ref('')
const exito = ref('')
const cargando = ref(false)
const form = ref({ mensaje: '', descripcion_problema: '', direccion: '' })

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return colores[id % colores.length]
}

async function cargarTrabajador() {
  const res = await axios.get(`http://127.0.0.1:8000/api/trabajadores/${route.params.id}/`)
  trabajador.value = res.data
}

async function enviar() {
  error.value = ''
  if (!form.value.mensaje || !form.value.descripcion_problema || !form.value.direccion)
    return error.value = 'Completa todos los campos'
  if (!auth.esCliente)
    return error.value = 'Solo clientes pueden enviar solicitudes'
  cargando.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/solicitudes/crear/', {
      trabajador: route.params.id,
      ...form.value
    })
    exito.value = '✅ Solicitud enviada correctamente. El técnico te contactará pronto.'
    setTimeout(() => router.push('/solicitudes'), 2000)
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Error al enviar solicitud'
  } finally {
    cargando.value = false
  }
}

onMounted(() => cargarTrabajador())
</script>

<style scoped>
.solicitud-card {
  padding: 32px;
  width: 540px;
  max-width: 100%;
}

.sol-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.sol-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

h2 {
  font-size: 18px;
  font-weight: 700;
}

.sol-oficio {
  font-size: 13px;
  color: var(--primary);
  font-weight: 500;
  margin-top: 2px;
}

h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 6px;
}

.sol-desc {
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 20px;
}

.sol-btns {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 8px;
}

.estado-carga {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text2);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>