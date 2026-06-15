<template>
  <div class="page-center">
    <div class="card" v-if="trabajador">
      <div class="trabajador-info">
        <div class="avatar" :style="{ background: getColor(trabajador.id) }">
          {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
        </div>
        <div>
          <h2>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h2>
          <p class="oficio">{{ trabajador.oficio }} · {{ trabajador.categoria }}</p>
        </div>
      </div>

      <hr>

      <h3>Enviar solicitud de servicio</h3>

      <div class="campo">
        <label>Mensaje al técnico</label>
        <textarea v-model="form.mensaje" placeholder="Saluda al técnico y cuéntale brevemente qué necesitas..." rows="3"></textarea>
      </div>
      <div class="campo">
        <label>Descripción del problema</label>
        <textarea v-model="form.descripcion_problema" placeholder="Describe el problema con detalle: ¿qué pasó?, ¿desde cuándo?, ¿qué has intentado?" rows="4"></textarea>
      </div>
      <div class="campo">
        <label>Dirección donde se realizará el servicio</label>
        <input v-model="form.direccion" type="text" placeholder="Ej: Calle Saphi 123, San Blas, Cusco" />
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="exito" class="exito">{{ exito }}</div>

      <div class="btns">
        <router-link :to="`/trabajador/${trabajador.id}`" class="btn-outline">← Volver</router-link>
        <button class="btn-verde" @click="enviar" :disabled="cargando">
          {{ cargando ? 'Enviando...' : 'Enviar solicitud' }}
        </button>
      </div>
    </div>
    <div v-else class="estado">Cargando...</div>
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

const form = ref({
  mensaje: '',
  descripcion_problema: '',
  direccion: ''
})

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#c8eed9','#d4edba','#fde8c8','#d6e8f8','#f8d6e8','#e8d6f8']
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
    exito.value = '✅ Solicitud enviada correctamente'
    setTimeout(() => router.push('/solicitudes'), 1500)
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Error al enviar solicitud'
  } finally {
    cargando.value = false
  }
}

onMounted(() => cargarTrabajador())
</script>

<style scoped>
.page-center {
  min-height: calc(100vh - 56px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.card {
  background: #fff; border: 1px solid #e0e0e0;
  border-radius: 16px; padding: 32px;
  width: 520px; max-width: 100%;
}
.trabajador-info { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.avatar {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; flex-shrink: 0;
}
h2 { font-size: 18px; font-weight: 700; }
.oficio { font-size: 13px; color: #1D9E75; font-weight: 500; margin-top: 2px; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 16px 0; }
h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.campo { margin-bottom: 14px; }
.campo label { display: block; font-size: 12px; font-weight: 600; color: #555; margin-bottom: 5px; }
.campo input, .campo textarea {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ccc; border-radius: 8px;
  font-size: 14px; font-family: inherit; outline: none; resize: vertical;
}
.campo input:focus, .campo textarea:focus { border-color: #1D9E75; }
.btns { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
.btn-verde {
  padding: 10px 20px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn-verde:disabled { background: #aaa; cursor: not-allowed; }
.btn-outline {
  padding: 10px 20px; background: transparent;
  border: 1px solid #ccc; border-radius: 8px;
  font-size: 14px; cursor: pointer; text-decoration: none; color: #555;
  display: flex; align-items: center;
}
.error { background: #fde8e8; color: #c0392b; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.exito { background: #e1f5ee; color: #0f6e56; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.estado { text-align: center; padding: 48px; color: #888; }
</style>