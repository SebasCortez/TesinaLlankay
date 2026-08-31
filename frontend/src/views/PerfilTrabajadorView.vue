<template>
  <div class="page" v-if="trabajador">
    <div class="perfil-header">
      <div class="perfil-header-inner">
        <div class="perfil-avatar-wrap">
          <img 
            v-if="trabajador.foto_url" 
            :src="trabajador.foto_url" 
            class="perfil-avatar-img" 
            :alt="'Foto de perfil de ' + trabajador.usuario.first_name + ' ' + trabajador.usuario.last_name + ', ' + trabajador.oficio" 
          />
          <div v-else class="perfil-avatar" :style="{ background: getColor(trabajador.id) }">
            {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
          </div>
        </div>
        <div class="perfil-info">
          <div class="perfil-badge-top">
            <span class="badge badge-blue">{{ trabajador.categoria }}</span>
            <span :class="['badge', trabajador.disponible ? 'badge-green' : 'badge-gray']">
              {{ trabajador.disponible ? '● Disponible' : '● Ocupado' }}
            </span>
          </div>
          <h1>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h1>
          <p class="perfil-oficio">{{ trabajador.oficio }}</p>
          <div class="perfil-meta">
            <span class="meta-item">📍 {{ trabajador.usuario.distrito || 'Cusco' }}, Cusco</span>
            <span class="meta-item">⏱ {{ trabajador.experiencia }} de experiencia</span>
          </div>
        </div>
        <div class="perfil-rating card">
          <div class="rating-num">{{ trabajador.calificacion_promedio.toFixed(1) }}</div>
          <div class="rating-stars">
            <span v-for="n in 5" :key="n">{{ n <= Math.round(trabajador.calificacion_promedio) ? '⭐' : '☆' }}</span>
          </div>
          <div class="rating-count">{{ trabajador.num_calificaciones }} reseñas</div>
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
                <div class="contact-val">{{ trabajador.usuario.email || 'No especificado' }}</div>
              </div>
            </div>
          </div>

          <!-- Botones de Acción -->
          <div class="acciones-contacto">
            <a v-if="trabajador.usuario.celular"
               :href="`https://wa.me/51${trabajador.usuario.celular.replace(/\D/g, '')}?text=Hola%20${encodeURIComponent(trabajador.usuario.first_name)},%20te%20contacto%20desde%20T%C3%A9cniCusco%20para%20un%20servicio%20de%20${encodeURIComponent(trabajador.oficio)}.`"
               target="_blank"
               rel="noopener noreferrer"
               class="btn-whatsapp">
              💬 Contactar por WhatsApp
            </a>

            <router-link v-if="auth.esCliente" :to="`/trabajador/${trabajador.id}/solicitar`" class="btn-primary"
              style="width:100%;justify-content:center;padding:12px">
              📩 Solicitar servicio formal
            </router-link>
          </div>

          <div v-if="!auth.estaAutenticado" class="aviso-login">
            <router-link to="/login">Inicia sesión</router-link> para enviar una solicitud o calificar este técnico
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
            <textarea 
              v-model="nuevaCal.comentario" 
              maxlength="400"
              :class="['form-textarea', errorCal ? 'is-invalid' : '']"
              placeholder="Cuéntanos tu experiencia con este técnico..." 
              rows="3" 
              style="margin-top:10px"
              @input="errorCal = ''"
            ></textarea>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span v-if="errorCal" class="form-field-error">⚠️ {{ errorCal }}</span>
              <span v-else></span>
              <span class="form-field-hint" style="font-size: 11px; color: var(--text3)">{{ nuevaCal.comentario.length }}/400</span>
            </div>
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
import api from '../services/api'
import type { Trabajador, Calificacion } from '../types'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()
const trabajador = ref<Trabajador | null>(null)
const calificaciones = ref<Calificacion[]>([])
const errorCal = ref('')
const exitoCal = ref('')
const cargandoCal = ref(false)
const hover = ref(0)
const nuevaCal = ref({ puntuacion: 0, comentario: '' })
const starLabels = ['Malo', 'Regular', 'Bueno', 'Muy bueno', 'Excelente']

function getIniciales(nombre?: string, apellido?: string) {
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
  try {
    const [r1, r2] = await Promise.all([
      api.get<Trabajador>(`/trabajadores/${id}/`),
      api.get<Calificacion[]>(`/calificaciones/${id}/`)
    ])
    trabajador.value = r1.data
    calificaciones.value = r2.data
  } catch (error) {
    console.error('Error al cargar datos del trabajador:', error)
  }
}

async function calificar() {
  if (nuevaCal.value.puntuacion === 0) {
    errorCal.value = 'Selecciona una puntuación de 1 a 5 estrellas.'
    return
  }
  if (nuevaCal.value.comentario.trim() && nuevaCal.value.comentario.trim().length < 5) {
    errorCal.value = 'El comentario debe tener al menos 5 caracteres.'
    return
  }
  errorCal.value = ''
  cargandoCal.value = true
  try {
    await api.post('/calificaciones/', {
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
  min-height: calc(100vh - 68px);
}

.perfil-header {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: 40px 24px;
}

.perfil-header-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 28px;
  flex-wrap: wrap;
}

.perfil-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.perfil-avatar, .perfil-avatar-img {
  width: 90px;
  height: 90px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 800;
  box-shadow: var(--shadow-md);
}

.perfil-avatar-img {
  object-fit: cover;
  border: 3px solid var(--border);
}

.perfil-info {
  flex: 1;
  min-width: 260px;
}

.perfil-badge-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.perfil-info h1 {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 4px;
}

.perfil-oficio {
  color: var(--primary);
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 8px;
}

.perfil-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13.5px;
  color: var(--text2);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.perfil-rating {
  text-align: center;
  padding: 20px 28px;
  min-width: 140px;
}

.rating-num {
  font-size: 38px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
  line-height: 1;
}

.rating-stars {
  font-size: 16px;
  margin: 6px 0;
  letter-spacing: -1px;
}

.rating-count {
  font-size: 12px;
  color: var(--text2);
  font-weight: 600;
}

.perfil-body {
  max-width: 960px;
  margin: 0 auto;
  padding: 36px 24px 60px;
}

.perfil-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.seccion {
  padding: 28px;
}

.seccion h3 {
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 18px;
  color: var(--text);
}

.descripcion-txt {
  font-size: 15px;
  color: var(--text2);
  line-height: 1.7;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.contact-icon {
  font-size: 24px;
}

.contact-label {
  font-size: 11.5px;
  color: var(--text3);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.contact-val {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.aviso-login {
  font-size: 13.5px;
  color: var(--text2);
  margin-top: 14px;
  padding: 12px 16px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.aviso-login a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.acciones-contacto {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.btn-whatsapp {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #25D366;
  color: #ffffff !important;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 15px;
  padding: 13px 20px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35);
}

.btn-whatsapp:hover {
  background: #1EBE5D;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 211, 102, 0.45);
}

.form-cal {
  background: var(--surface-subtle);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--border);
}

.form-cal-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 12px;
}

.stars-input {
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-btn {
  font-size: 34px;
  cursor: pointer;
  color: var(--border2);
  transition: color 0.15s, transform 0.15s;
  line-height: 1;
}

.star-btn:hover {
  transform: scale(1.15);
}

.star-btn.activa {
  color: #F59E0B;
}

.star-label {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--amber);
  margin-left: 8px;
}

.sin-cal {
  text-align: center;
  padding: 40px;
  color: var(--text2);
  font-size: 14.5px;
}

.review-item {
  padding: 20px 0;
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
  margin-bottom: 10px;
}

.review-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  flex-shrink: 0;
}

.review-name {
  font-size: 14px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.review-date {
  font-size: 11.5px;
  color: var(--text3);
  margin-top: 1px;
}

.review-stars {
  margin-left: auto;
  font-size: 13.5px;
  letter-spacing: -1px;
}

.review-comment {
  font-size: 14px;
  color: var(--text2);
  line-height: 1.6;
  padding-left: 52px;
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
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>