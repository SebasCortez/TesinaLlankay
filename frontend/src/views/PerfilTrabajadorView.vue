<template>
  <div class="contenedor" v-if="trabajador">
    <div class="layout">
      <div class="sidebar">
        <div class="avatar-big" :style="{ background: getColor(trabajador.id) }">
          {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
        </div>
        <h2>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h2>
        <p class="oficio">{{ trabajador.oficio }}</p>
        <div class="estrellas">
          <span v-for="n in 5" :key="n">{{ n <= Math.round(trabajador.calificacion_promedio) ? '⭐' : '☆' }}</span>
          <span class="cal-num">{{ trabajador.calificacion_promedio.toFixed(1) }} ({{ trabajador.num_calificaciones }} calif.)</span>
        </div>
        <div class="info">
          <div>📍 {{ trabajador.usuario.distrito }}, Cusco</div>
          <div>📱 {{ trabajador.usuario.celular }}</div>
          <div>🏷 {{ trabajador.categoria }}</div>
          <div>⏱ {{ trabajador.experiencia }}</div>
          <div>✅ Verificado</div>
          <router-link
            v-if="auth.esCliente"
            :to="`/trabajador/${trabajador.id}/solicitar`"
            class="btn-solicitar"
            >
            📩 Solicitar servicio
          </router-link>
        </div>
        <div v-if="trabajador.descripcion" class="descripcion">
          {{ trabajador.descripcion }}
        </div>
      </div>

      <div class="main">
        <div class="calificaciones-seccion">
          <h3>Calificaciones ({{ calificaciones.length }})</h3>

          <!-- Formulario de calificación -->
          <div v-if="auth.esCliente" class="form-cal">
            <p class="form-title">Deja tu calificación</p>
            <div class="estrellas-input">
              <span
                v-for="n in 5" :key="n"
                @click="nuevaCal.puntuacion = n"
                :class="['estrella', n <= nuevaCal.puntuacion ? 'activa' : '']"
              >★</span>
            </div>
            <textarea v-model="nuevaCal.comentario" placeholder="Escribe tu comentario..." rows="3"></textarea>
            <div v-if="errorCal" class="error">{{ errorCal }}</div>
            <div v-if="exitoCal" class="exito">{{ exitoCal }}</div>
            <button class="btn-verde" @click="calificar" :disabled="cargandoCal">
              {{ cargandoCal ? 'Enviando...' : 'Enviar calificación' }}
            </button>
          </div>

          <div v-if="!auth.esCliente && !auth.estaAutenticado" class="aviso">
            <router-link to="/login">Inicia sesión</router-link> como cliente para dejar una calificación
          </div>

          <div v-if="calificaciones.length === 0" class="sin-cal">Aún no hay calificaciones</div>

          <div v-for="c in calificaciones" :key="c.id" class="review">
            <div class="review-top">
              <strong>{{ c.cliente.first_name }} {{ c.cliente.last_name }}</strong>
              <div class="estrellas">
                <span v-for="n in 5" :key="n">{{ n <= c.puntuacion ? '⭐' : '☆' }}</span>
              </div>
              <span class="fecha">{{ formatFecha(c.fecha) }}</span>
            </div>
            <p v-if="c.comentario" class="comentario">{{ c.comentario }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="estado">Cargando...</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()
const trabajador = ref<any>(null)
const calificaciones = ref<any[]>([])
const errorCal = ref('')
const exitoCal = ref('')
const cargandoCal = ref(false)
const nuevaCal = ref({ puntuacion: 0, comentario: '' })

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#c8eed9','#d4edba','#fde8c8','#d6e8f8','#f8d6e8','#e8d6f8']
  return colores[id % colores.length]
}
function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', { year:'numeric', month:'long', day:'numeric' })
}

async function cargarDatos() {
  const id = route.params.id
  const [resTrabajador, resCal] = await Promise.all([
    axios.get(`http://127.0.0.1:8000/api/trabajadores/${id}/`),
    axios.get(`http://127.0.0.1:8000/api/calificaciones/${id}/`)
  ])
  trabajador.value = resTrabajador.data
  calificaciones.value = resCal.data
}

async function calificar() {
  if (nuevaCal.value.puntuacion === 0)
    return errorCal.value = 'Selecciona una puntuación'
  errorCal.value = ''
  cargandoCal.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/calificaciones/', {
      trabajador: route.params.id,
      puntuacion: nuevaCal.value.puntuacion,
      comentario: nuevaCal.value.comentario,
    })
    exitoCal.value = '¡Calificación enviada!'
    nuevaCal.value = { puntuacion: 0, comentario: '' }
    await cargarDatos()
  } catch (e: any) {
    errorCal.value = e.response?.data?.error || 'Error al enviar calificación'
  } finally {
    cargandoCal.value = false
  }
}

onMounted(() => cargarDatos())
</script>

<style scoped>
.contenedor { max-width: 1000px; margin: 0 auto; padding: 24px; }
.layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; align-items: start; }
.sidebar {
  background: #fff; border: 1px solid #e0e0e0;
  border-radius: 12px; padding: 24px; text-align: center;
}
.avatar-big {
  width: 80px; height: 80px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; margin: 0 auto 14px;
}
h2 { font-size: 18px; font-weight: 700; }
.oficio { color: #1D9E75; font-weight: 500; font-size: 14px; margin: 4px 0 10px; }
.estrellas { font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 2px; }
.cal-num { font-size: 12px; color: #888; margin-left: 4px; }
.info { text-align: left; margin-top: 16px; display: flex; flex-direction: column; gap: 8px; font-size: 13px; color: #555; }
.descripcion { background: #f8f7f4; border-radius: 8px; padding: 12px; margin-top: 14px; font-size: 13px; color: #555; text-align: left; line-height: 1.6; }
.main { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; }
.calificaciones-seccion h3 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
.form-cal { background: #f8f7f4; border-radius: 10px; padding: 16px; margin-bottom: 20px; }
.form-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.estrellas-input { display: flex; gap: 6px; margin-bottom: 10px; }
.estrella { font-size: 28px; cursor: pointer; color: #ddd; transition: color 0.15s; }
.estrella.activa { color: #EF9F27; }
.estrella:hover { color: #EF9F27; }
textarea {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ccc; border-radius: 8px;
  font-size: 14px; font-family: inherit; outline: none; resize: vertical;
}
textarea:focus { border-color: #1D9E75; }
.btn-verde {
  margin-top: 10px; padding: 9px 20px;
  background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-verde:disabled { background: #aaa; cursor: not-allowed; }
.aviso { font-size: 13px; color: #666; margin-bottom: 16px; }
.aviso a { color: #1D9E75; }
.sin-cal { text-align: center; padding: 24px; color: #888; font-size: 14px; }
.review { padding: 14px 0; border-bottom: 1px solid #f0eeea; }
.review:last-child { border-bottom: none; }
.review-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }
.fecha { font-size: 11px; color: #aaa; margin-left: auto; }
.comentario { font-size: 13px; color: #555; line-height: 1.6; }
.error { background: #fde8e8; color: #c0392b; padding: 8px 10px; border-radius: 8px; font-size: 13px; margin: 8px 0; }
.exito { background: #e1f5ee; color: #0f6e56; padding: 8px 10px; border-radius: 8px; font-size: 13px; margin: 8px 0; }
.estado { text-align: center; padding: 48px; color: #888; }
.btn-solicitar {
  display: block; text-align: center; margin-top: 16px;
  padding: 11px; background: #1D9E75; color: #fff;
  border-radius: 8px; text-decoration: none;
  font-size: 14px; font-weight: 600;
}
.btn-solicitar:hover { background: #0f6e56; }
</style>