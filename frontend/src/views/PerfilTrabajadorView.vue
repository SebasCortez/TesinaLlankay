<template>
  <div class="page" v-if="trabajador">
    <div class="perfil-header">
      <div class="perfil-header-inner">
        <div class="perfil-avatar" :style="{ background: getColor(trabajador.id) }">
          {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
        </div>
        <div class="perfil-info">
          <h1>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h1>
          <p class="perfil-oficio">{{ trabajador.oficio }}</p>
          <div class="perfil-meta">
            <span class="badge badge-blue">{{ trabajador.categoria }}</span>
            <span class="badge badge-gray">📍 {{ trabajador.usuario.distrito }}, Cusco</span>
            <span class="badge badge-gray">⏱ {{ trabajador.experiencia }}</span>
            <span :class="['badge', trabajador.disponible ? 'badge-green' : 'badge-gray']">
              {{ trabajador.disponible ? '● Disponible' : '● Ocupado' }}
            </span>
          </div>
        </div>
        <div class="perfil-rating">
          <div class="rating-num">{{ trabajador.calificacion_promedio.toFixed(1) }}</div>
          <div class="rating-stars">
            <span v-for="n in 5" :key="n">{{ n <= Math.round(trabajador.calificacion_promedio) ? '⭐' : '☆' }}</span>
          </div>
          <div class="rating-count">{{ trabajador.num_calificaciones }} calificaciones</div>
        </div>
      </div>
    </div>

    <div class="perfil-body">
      <div class="perfil-main">

        <!-- Descripción -->
        <div class="card seccion" v-if="trabajador.descripcion">
          <h3>Sobre mí</h3>
          <p class="descripcion-txt">{{ trabajador.descripcion }}</p>
        </div>

        <!-- Contacto -->
        <div class="card seccion">
          <h3>Información de contacto</h3>
          <div class="contact-grid">
            <div class="contact-item">
              <span class="contact-icon">📱</span>
              <div>
                <div class="contact-label">Celular</div>
                <div class="contact-val">{{ trabajador.usuario.celular }}</div>
              </div>
            </div>
            <div class="contact-item">
              <span class="contact-icon">📧</span>
              <div>
                <div class="contact-label">Correo</div>
                <div class="contact-val">{{ trabajador.usuario.email }}</div>
              </div>
            </div>
          </div>
          <router-link v-if="auth.esCliente" :to="`/trabajador/${trabajador.id}/solicitar`" class="btn-primary"
            style="width:100%;justify-content:center;margin-top:16px;padding:12px">
            📩 Solicitar servicio
          </router-link>
          <div v-if="!auth.estaAutenticado" class="aviso-login">
            <router-link to="/login">Inicia sesión</router-link> para solicitar este servicio
          </div>
        </div>

        <!-- Calificaciones -->
        <div class="card seccion">
          <h3>Calificaciones ({{ calificaciones.length }})</h3>

          <!-- Formulario -->
          <div v-if="auth.esCliente" class="form-cal">
            <p class="form-cal-title">Deja tu calificación</p>
            <div class="stars-input">
              <span v-for="n in 5" :key="n" @click="nuevaCal.puntuacion = n" @mouseover="hover = n"
                @mouseleave="hover = 0"
                :class="['star-btn', n <= (hover || nuevaCal.puntuacion) ? 'activa' : '']">★</span>
              <span class="star-label" v-if="nuevaCal.puntuacion">{{ starLabels[nuevaCal.puntuacion - 1] }}</span>
            </div>
            <textarea v-model="nuevaCal.comentario" class="form-textarea"
              placeholder="Cuéntanos tu experiencia con este técnico..." rows="3" style="margin-top:10px"></textarea>
            <div v-if="errorCal" class="alert alert-error" style="margin-top:10px">{{ errorCal }}</div>
            <div v-if="exitoCal" class="alert alert-success" style="margin-top:10px">{{ exitoCal }}</div>
            <button class="btn-primary" style="margin-top:12px" @click="calificar" :disabled="cargandoCal">
              {{ cargandoCal ? 'Enviando...' : 'Enviar calificación' }}
            </button>
          </div>

          <div v-if="!auth.estaAutenticado" class="aviso-login">
            <router-link to="/login">Inicia sesión</router-link> como cliente para dejar una calificación
          </div>

          <div v-if="calificaciones.length === 0" class="sin-cal">
            <div style="font-size:32px;margin-bottom:8px">⭐</div>
            <p>Aún no hay calificaciones para este técnico</p>
          </div>

          <div v-for="c in calificaciones" :key="c.id" class="review-item">
            <div class="review-header">
              <div class="review-avatar">{{ c.cliente.first_name[0] }}{{ c.cliente.last_name[0] }}</div>
              <div>
                <div class="review-name">{{ c.cliente.first_name }} {{ c.cliente.last_name }}</div>
                <div class="review-date">{{ formatFecha(c.fecha) }}</div>
              </div>
              <div class="review-stars">
                <span v-for="n in 5" :key="n">{{ n <= c.puntuacion ? '⭐' : '☆' }}</span>
              </div>
            </div>
            <p v-if="c.comentario" class="review-comment">{{ c.comentario }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="estado-carga">
    <div class="spinner"></div>
    <p>Cargando perfil...</p>
  </div>
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
const hover = ref(0)
const nuevaCal = ref({ puntuacion: 0, comentario: '' })
const starLabels = ['Malo', 'Regular', 'Bueno', 'Muy bueno', 'Excelente']

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return colores[id % colores.length]
}
function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function cargarDatos() {
  const id = route.params.id
  const [r1, r2] = await Promise.all([
    axios.get(`http://127.0.0.1:8000/api/trabajadores/${id}/`),
    axios.get(`http://127.0.0.1:8000/api/calificaciones/${id}/`)
  ])
  trabajador.value = r1.data
  calificaciones.value = r2.data
}

async function calificar() {
  if (nuevaCal.value.puntuacion === 0) return errorCal.value = 'Selecciona una puntuación'
  errorCal.value = ''
  cargandoCal.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/calificaciones/', {
      trabajador: route.params.id,
      puntuacion: nuevaCal.value.puntuacion,
      comentario: nuevaCal.value.comentario,
    })
    exitoCal.value = '✅ ¡Calificación enviada exitosamente!'
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
.page {
  min-height: calc(100vh - 64px);
}

.perfil-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 32px;
}

.perfil-header-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.perfil-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 700;
  flex-shrink: 0;
  border: 3px solid var(--border);
}

.perfil-info {
  flex: 1;
}

.perfil-info h1 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.perfil-oficio {
  color: var(--primary);
  font-weight: 500;
  font-size: 15px;
  margin-bottom: 10px;
}

.perfil-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.perfil-rating {
  text-align: center;
  padding: 16px 24px;
  background: var(--bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.rating-num {
  font-size: 36px;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}

.rating-stars {
  font-size: 16px;
  margin: 4px 0;
}

.rating-count {
  font-size: 12px;
  color: var(--text2);
}

.perfil-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 32px;
}

.perfil-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.seccion {
  padding: 24px;
}

.seccion h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text);
}

.descripcion-txt {
  font-size: 14px;
  color: var(--text2);
  line-height: 1.7;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.contact-icon {
  font-size: 20px;
}

.contact-label {
  font-size: 11px;
  color: var(--text2);
  font-weight: 500;
}

.contact-val {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.aviso-login {
  font-size: 13px;
  color: var(--text2);
  margin-top: 12px;
}

.aviso-login a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.form-cal {
  background: var(--bg);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid var(--border);
}

.form-cal-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.stars-input {
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-btn {
  font-size: 32px;
  cursor: pointer;
  color: var(--border2);
  transition: color 0.1s;
  line-height: 1;
}

.star-btn.activa {
  color: #F59E0B;
}

.star-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text2);
  margin-left: 4px;
}

.sin-cal {
  text-align: center;
  padding: 32px;
  color: var(--text2);
  font-size: 14px;
}

.review-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.review-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.review-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.review-name {
  font-size: 13px;
  font-weight: 600;
}

.review-date {
  font-size: 11px;
  color: var(--text3);
  margin-top: 1px;
}

.review-stars {
  margin-left: auto;
  font-size: 13px;
}

.review-comment {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.6;
  padding-left: 48px;
}

.estado-carga {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  color: var(--text2);
  gap: 16px;
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