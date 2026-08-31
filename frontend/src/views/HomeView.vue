<template>
  <div class="home">
    <!-- HERO SECTION -->
    <div class="hero-wrapper">
      <div class="hero-ambient-glow"></div>
      <div class="hero">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>📍 Plataforma Oficial · Cusco, Perú</span>
          </div>
          <h1>Encuentra técnicos <span class="gradient-text">verificados</span> cerca de ti</h1>
          <p>Conecta al instante con electricistas, gasfiteros, carpinteros y especialistas calificados por vecinos de Cusco con geolocalización en tiempo real.</p>
          <div class="hero-btns">
            <router-link to="/buscar" class="btn-primary hero-btn-main">
              <span>🔍</span> Explorar técnicos en mapa
            </router-link>
            <router-link to="/registro-trabajador" class="btn-secondary hero-btn-sub">
              <span>👷</span> Registrarme como técnico
            </router-link>
          </div>
        </div>

        <!-- HERO VISUAL: RUEDA VERTICAL CILÍNDRICA ULTRA-SMOOTH -->
        <div class="hero-visual">
          <div class="wheel-header">
            <div class="wheel-status">
              <span class="live-pulse"></span>
              <span class="wheel-status-text">Técnicos destacados en Cusco</span>
            </div>
            <div class="wheel-controls">
              <button class="btn-wheel-nav" @click="rotarArriba" title="Técnico anterior">▲</button>
              <button class="btn-wheel-nav" @click="rotarAbajo" title="Siguiente técnico">▼</button>
            </div>
          </div>

          <!-- CONTENEDOR RUEDA VERTICAL CON MÁSCARA GRADIENTE (Pausable en hover) -->
          <div 
            class="wheel-container"
            @mouseenter="pausarRueda"
            @mouseleave="reanudarRueda"
          >
            <div 
              class="wheel-track"
              :style="{
                transform: `translateY(-${offsetY}px)`,
                transition: conTransicion ? 'transform 0.65s cubic-bezier(0.16, 1, 0.3, 1)' : 'none'
              }"
            >
              <router-link 
                v-for="(t, index) in listaCilindro" 
                :key="'cil-' + t.id + '-' + index"
                :to="`/trabajador/${t.id}`" 
                :class="[
                  'hero-card', 'card', 'wheel-card',
                  esCardCentro(index) ? 'card-destacada' : 'card-lateral'
                ]"
              >
                <div class="hc-avatar-wrap">
                  <img v-if="t.foto_url" :src="t.foto_url" :alt="'Foto de ' + t.nombre" class="hc-avatar-img" />
                  <div v-else class="hc-avatar" :style="{ background: t.avatarGradient }">
                    {{ t.iniciales }}
                  </div>
                </div>

                <div class="hc-info">
                  <div class="hc-top-row">
                    <span class="hc-name">{{ t.nombre }}</span>
                    <span class="hc-rating">⭐ {{ t.calificacion.toFixed(1) }}</span>
                  </div>
                  <div class="hc-job">{{ t.oficio }}</div>
                  <div class="hc-sub">
                    <span class="hc-distrito">📍 {{ t.distrito }}</span>
                    <span class="hc-cat-pill">{{ t.categoria }}</span>
                  </div>
                </div>

                <div class="hc-action">
                  <span class="badge badge-green hc-badge">
                    <span class="live-dot"></span> Disponible
                  </span>
                  <span class="hc-ver-btn">Ver perfil ➔</span>
                </div>
              </router-link>
            </div>

            <!-- FADES DE BORDE PARA EFECTO CILINDRO 3D -->
            <div class="wheel-fade-top"></div>
            <div class="wheel-fade-bottom"></div>
          </div>

          <div class="wheel-hint">
            <span>💡 Rotación en vivo · Pasa el mouse para pausar o haz clic para ver perfil.</span>
          </div>

          <div class="hero-stats card">
            <div class="hs">
              <span class="hs-num">50+</span>
              <span class="hs-label">Técnicos Activos</span>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
              <span class="hs-num">4.9 ⭐</span>
              <span class="hs-label">Satisfacción</span>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
              <span class="hs-num">500+</span>
              <span class="hs-label">Servicios</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CATEGORIAS -->
    <div class="categorias-section">
      <div class="section-header">
        <span class="section-subtitle">ESPECIALIDADES</span>
        <h2>¿Qué servicio necesitas hoy?</h2>
        <p>Selecciona una categoría para ver técnicos disponibles en tu distrito</p>
      </div>

      <div class="categorias-grid">
        <router-link v-for="cat in categorias" :key="cat.nombre" :to="`/buscar?categoria=${cat.nombre}`" class="cat-card card">
          <div class="cat-icon-wrap">{{ cat.icon }}</div>
          <div class="cat-nombre">{{ cat.nombre }}</div>
          <span class="cat-arrow">➔</span>
        </router-link>
      </div>
    </div>

    <!-- COMO FUNCIONA -->
    <div class="como-section">
      <div class="section-header">
        <span class="section-subtitle">PROCESO SIMPLE</span>
        <h2>¿Cómo funciona Llankay?</h2>
        <p>Todo el flujo de contratación diseñado para ser rápido, seguro y transparente</p>
      </div>

      <div class="pasos-grid">
        <div class="paso-card card" v-for="paso in pasos" :key="paso.num">
          <div class="paso-top">
            <div class="paso-icon">{{ paso.icon }}</div>
            <div class="paso-num">{{ paso.num }}</div>
          </div>
          <h3>{{ paso.titulo }}</h3>
          <p>{{ paso.desc }}</p>
        </div>
      </div>
    </div>

    <!-- CTA BANNER -->
    <div class="cta-wrapper">
      <div class="cta-card card">
        <div class="cta-glow"></div>
        <div class="cta-content">
          <h2>¿Eres técnico o profesional independiente en Cusco?</h2>
          <p>Únete gratis a nuestra red de confianza, recibe solicitudes directas y haz crecer tu reputación laboral.</p>
          <router-link to="/registro-trabajador" class="btn-primary btn-cta">
            Registrarme como técnico ahora ➔
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../services/api'
import type { Trabajador } from '../types'

interface TecnicoRueda {
  id: number
  nombre: string
  oficio: string
  categoria: string
  distrito: string
  calificacion: number
  foto_url?: string | null
  iniciales: string
  avatarGradient: string
}

const listaGradientes: readonly string[] = [
  'linear-gradient(135deg, #3B82F6, #1D4ED8)',
  'linear-gradient(135deg, #10B981, #059669)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #8B5CF6, #6D28D9)',
  'linear-gradient(135deg, #EC4899, #BE185D)',
  'linear-gradient(135deg, #14B8A6, #0F766E)',
  'linear-gradient(135deg, #F97316, #C2410C)'
]

function getGradiente(idx: number): string {
  return listaGradientes[idx % listaGradientes.length] ?? 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
}

// Lista de técnicos inicial / fallback con perfiles reales en Cusco
const listaTecnicos = ref<TecnicoRueda[]>([
  {
    id: 1,
    nombre: 'Carlos Huanca Quispe',
    oficio: '⚡ Electricista Industrial y Residencial',
    categoria: 'Electricidad',
    distrito: 'San Sebastián',
    calificacion: 4.9,
    iniciales: 'CH',
    avatarGradient: getGradiente(0)
  },
  {
    id: 2,
    nombre: 'Miguel Quispe Mamani',
    oficio: '💧 Gasfitero y Termas Solares',
    categoria: 'Gasfitería',
    distrito: 'Wanchaq',
    calificacion: 4.8,
    iniciales: 'MQ',
    avatarGradient: getGradiente(1)
  },
  {
    id: 3,
    nombre: 'Rosa Pumaccahua Flores',
    oficio: '🪚 Carpintería Fina y Muebles',
    categoria: 'Carpintería',
    distrito: 'Cusco',
    calificacion: 5.0,
    iniciales: 'RP',
    avatarGradient: getGradiente(2)
  },
  {
    id: 4,
    nombre: 'Jorge Alarcón Vargas',
    oficio: '🔑 Cerrajería 24h y Puertas Blindadas',
    categoria: 'Cerrajería',
    distrito: 'Santiago',
    calificacion: 4.9,
    iniciales: 'JA',
    avatarGradient: getGradiente(3)
  },
  {
    id: 5,
    nombre: 'Walter Condori Estrada',
    oficio: '🧱 Maestro de Albañilería y Estructuras',
    categoria: 'Albañilería y Construcción',
    distrito: 'San Jerónimo',
    calificacion: 4.8,
    iniciales: 'WC',
    avatarGradient: getGradiente(4)
  },
  {
    id: 6,
    nombre: 'Elena Ticona Morales',
    oficio: '🎨 Pintura y Acabados de Interiores',
    categoria: 'Pintura',
    distrito: 'Wanchaq',
    calificacion: 4.9,
    iniciales: 'ET',
    avatarGradient: getGradiente(5)
  },
  {
    id: 7,
    nombre: 'David Sotomayor Peña',
    oficio: '🏗️ Instalador de Drywall y Techos',
    categoria: 'Drywall y Cielorraso',
    distrito: 'San Sebastián',
    calificacion: 4.9,
    iniciales: 'DS',
    avatarGradient: getGradiente(6)
  }
])

// ALTURA DE CADA TARJETA + GAP
const CARD_SLOT_HEIGHT = 92 // 80px altura + 12px gap

// Triplicar lista para deslizamiento infinito continuo
const listaCilindro = computed<TecnicoRueda[]>(() => {
  if (listaTecnicos.value.length === 0) return []
  return [...listaTecnicos.value, ...listaTecnicos.value, ...listaTecnicos.value]
})

// Iniciar en el set central
const indiceOffset = ref(listaTecnicos.value.length)
const conTransicion = ref(true)
const offsetY = computed(() => indiceOffset.value * CARD_SLOT_HEIGHT)

let timerRueda: any = null
const pausado = ref(false)

function esCardCentro(index: number): boolean {
  return index === indiceOffset.value + 1
}

function rotarAbajo() {
  const N = listaTecnicos.value.length
  if (N === 0) return

  conTransicion.value = true
  indiceOffset.value++

  // Cuando sobrepasa el segundo bloque, resetear sin salto
  if (indiceOffset.value >= N * 2) {
    setTimeout(() => {
      conTransicion.value = false
      indiceOffset.value = N
      nextTick(() => {
        requestAnimationFrame(() => {
          conTransicion.value = true
        })
      })
    }, 650)
  }
}

function rotarArriba() {
  const N = listaTecnicos.value.length
  if (N === 0) return

  conTransicion.value = true
  indiceOffset.value--

  if (indiceOffset.value < N) {
    setTimeout(() => {
      conTransicion.value = false
      indiceOffset.value = N * 2 - 1
      nextTick(() => {
        requestAnimationFrame(() => {
          conTransicion.value = true
        })
      })
    }, 650)
  }
}

function pausarRueda() {
  pausado.value = true
  if (timerRueda) clearInterval(timerRueda)
}

function reanudarRueda() {
  pausado.value = false
  iniciarRotacion()
}

function iniciarRotacion() {
  if (timerRueda) clearInterval(timerRueda)
  timerRueda = setInterval(() => {
    if (!pausado.value) {
      rotarAbajo()
    }
  }, 2800)
}

async function cargarTecnicosReales() {
  try {
    const res = await api.get<Trabajador[]>('/trabajadores/')
    if (res.data && res.data.length >= 3) {
      listaTecnicos.value = res.data.map((t, idx): TecnicoRueda => {
        const nombre = `${t.usuario.first_name} ${t.usuario.last_name}`.trim()
        const ini = ((t.usuario.first_name?.[0] || '') + (t.usuario.last_name?.[0] || '')).toUpperCase() || 'TC'
        return {
          id: t.id,
          nombre: nombre || 'Técnico Profesional',
          oficio: t.oficio || t.categoria,
          categoria: t.categoria,
          distrito: t.usuario.distrito || 'Cusco',
          calificacion: t.calificacion_promedio > 0 ? t.calificacion_promedio : 4.8,
          foto_url: t.foto_url,
          iniciales: ini,
          avatarGradient: getGradiente(idx)
        }
      })
      indiceOffset.value = listaTecnicos.value.length
    }
  } catch (e) {
    console.log('Usando técnicos de vitrina local en Cusco:', e)
  }
}

onMounted(() => {
  cargarTecnicosReales()
  iniciarRotacion()
})

onUnmounted(() => {
  if (timerRueda) clearInterval(timerRueda)
})

const categorias = [
  { icon: '⚡', nombre: 'Electricidad' },
  { icon: '💧', nombre: 'Gasfitería' },
  { icon: '🪚', nombre: 'Carpintería' },
  { icon: '🔑', nombre: 'Cerrajería' },
  { icon: '🎨', nombre: 'Pintura' },
  { icon: '🧱', nombre: 'Albañilería y Construcción' },
  { icon: '🏗️', nombre: 'Drywall y Cielorraso' },
  { icon: '🔥', nombre: 'Soldadura y Estructuras Metálicas' },
  { icon: '📻', nombre: 'Reparación de Electrodomésticos' },
  { icon: '☀️', nombre: 'Termas Solares y Calefacción' },
  { icon: '❄️', nombre: 'Refrigeración y Climatización' },
  { icon: '🪟', nombre: 'Vidriería y Aluminios' },
  { icon: '🌿', nombre: 'Jardinería y Áreas Verdes' },
  { icon: '💻', nombre: 'Mantenimiento de Cómputo y Redes' },
  { icon: '🧹', nombre: 'Limpieza y Desinfección' },
]

const pasos = [
  { num: '01', icon: '📍', titulo: 'Ubica o filtra', desc: 'Encuentra técnicos cercanos a tu ubicación en mapa satelital o por especialidad.' },
  { num: '02', icon: '📋', titulo: 'Envía tu solicitud', desc: 'Describe la avería o trabajo con dirección para coordinar de inmediato.' },
  { num: '03', icon: '🔧', titulo: 'Servicio garantizado', desc: 'El técnico acepta la solicitud, te contacta y realiza el trabajo acordado.' },
  { num: '04', icon: '⭐', titulo: 'Calificación verificada', desc: 'Evalúa la puntualidad y calidad del servicio para apoyar a la comunidad.' },
]
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* HERO */
.hero-wrapper {
  position: relative;
  overflow: hidden;
  padding: 60px 24px 80px;
}

.hero-ambient-glow {
  position: absolute;
  top: -100px;
  right: -50px;
  width: 550px;
  height: 550px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.08) 50%, transparent 70%);
  filter: blur(50px);
  pointer-events: none;
  z-index: 0;
}

.hero {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 56px;
  max-width: 1180px;
  margin: 0 auto;
  align-items: center;
  position: relative;
  z-index: 1;
}

@media (max-width: 960px) {
  .hero {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  .hero-btns {
    justify-content: center;
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 9999px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  margin-bottom: 24px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: var(--primary);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--primary);
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.03em;
  margin-bottom: 20px;
}

.gradient-text {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-content p {
  font-size: 17px;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 32px;
  max-width: 520px;
}

.hero-btns {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-btn-main {
  padding: 13px 28px;
  font-size: 15px;
}

.hero-btn-sub {
  padding: 13px 24px;
  font-size: 15px;
}

/* ======================================================== */
/* RUEDA VERTICAL CILÍNDRICA ULTRA-SMOOTH                  */
/* ======================================================== */
.hero-visual {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.wheel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6px;
}

.wheel-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-pulse {
  width: 8px;
  height: 8px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse-green 1.8s infinite;
}

@keyframes pulse-green {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.wheel-status-text {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.wheel-controls {
  display: flex;
  gap: 6px;
}

.btn-wheel-nav {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-wheel-nav:hover {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
  transform: scale(1.08);
}

.wheel-container {
  position: relative;
  height: 276px; /* Exactamente 3 slots de 92px */
  overflow: hidden;
  border-radius: var(--radius-lg);
  padding: 0 4px;
}

.wheel-track {
  display: flex;
  flex-direction: column;
  gap: 12px;
  will-change: transform;
}

.wheel-card {
  height: 80px;
  padding: 12px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  border: 1px solid var(--border);
  box-sizing: border-box;
  flex-shrink: 0;
  transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), 
              opacity 0.65s cubic-bezier(0.16, 1, 0.3, 1), 
              border-color 0.4s ease, 
              box-shadow 0.4s ease;
}

/* Tarjeta central destacada */
.card-destacada {
  opacity: 1 !important;
  transform: scale(1.02) !important;
  border-color: var(--primary) !important;
  box-shadow: 0 10px 28px var(--primary-glow) !important;
  background: var(--surface) !important;
  z-index: 3;
}

/* Tarjetas superior e inferior en la rueda */
.card-lateral {
  opacity: 0.72;
  transform: scale(0.96);
  background: var(--surface-subtle);
  border-color: var(--border);
  z-index: 1;
}

.wheel-card:hover {
  transform: scale(1.035) !important;
  border-color: var(--primary) !important;
  box-shadow: 0 12px 32px var(--primary-glow) !important;
  opacity: 1 !important;
  z-index: 10 !important;
}

/* Fades de borde para efecto 3D infinito */
.wheel-fade-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: linear-gradient(to bottom, var(--bg) 0%, transparent 100%);
  pointer-events: none;
  z-index: 4;
}

.wheel-fade-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: linear-gradient(to top, var(--bg) 0%, transparent 100%);
  pointer-events: none;
  z-index: 4;
}

.hc-avatar-wrap {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
}

.hc-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hc-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.hc-info {
  flex: 1;
  min-width: 0;
}

.hc-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.hc-name {
  font-size: 15px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hc-rating {
  font-size: 12px;
  font-weight: 700;
  color: #F59E0B;
  white-space: nowrap;
}

.hc-job {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--primary);
  margin: 1px 0 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hc-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--text2);
}

.hc-cat-pill {
  background: var(--surface-subtle);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
  font-size: 10.5px;
}

.hc-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.hc-badge {
  font-size: 11px;
  padding: 3px 8px;
}

.hc-ver-btn {
  font-size: 11px;
  font-weight: 700;
  color: var(--primary);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s ease;
}

.wheel-card:hover .hc-ver-btn {
  opacity: 1;
  transform: translateX(0);
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #10B981;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 6px #10B981;
}

.wheel-hint {
  text-align: center;
  font-size: 11.5px;
  color: var(--text3);
  margin-top: -2px;
}

.hero-stats {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: var(--surface-glass);
}

.hs {
  text-align: center;
}

.hs-num {
  display: block;
  font-size: 20px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
}

.hs-label {
  font-size: 12px;
  color: var(--text2);
  font-weight: 500;
}

.hs-div {
  width: 1px;
  height: 36px;
  background: var(--border);
}

/* SECCIONES HEADER */
.section-header {
  text-align: center;
  max-width: 650px;
  margin: 0 auto 36px;
}

.section-subtitle {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--primary);
  text-transform: uppercase;
  margin-bottom: 8px;
  display: block;
}

.section-header h2 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 10px;
}

.section-header p {
  font-size: 15px;
  color: var(--text2);
}

/* CATEGORIAS */
.categorias-section {
  padding: 40px 24px 60px;
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
}

.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.cat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding: 24px 20px;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.cat-card:hover {
  transform: translateY(-5px);
  border-color: var(--primary);
  box-shadow: var(--shadow-glow);
}

.cat-icon-wrap {
  font-size: 36px;
  transition: transform 0.25s ease;
}

.cat-card:hover .cat-icon-wrap {
  transform: scale(1.18);
}

.cat-nombre {
  font-size: 15px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
}

.cat-arrow {
  font-size: 12px;
  color: var(--primary);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s ease;
}

.cat-card:hover .cat-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* COMO FUNCIONA */
.como-section {
  padding: 60px 24px 80px;
  background: var(--surface-subtle);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.pasos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  max-width: 1180px;
  margin: 0 auto;
}

.paso-card {
  padding: 32px 24px;
}

.paso-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.paso-icon {
  font-size: 32px;
}

.paso-num {
  font-size: 28px;
  font-weight: 900;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--primary);
  opacity: 0.3;
}

.paso-card h3 {
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 10px;
}

.paso-card p {
  font-size: 14px;
  color: var(--text2);
  line-height: 1.6;
}

/* CTA BANNER */
.cta-wrapper {
  padding: 40px 24px 80px;
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
}

.cta-card {
  position: relative;
  overflow: hidden;
  padding: 56px 40px;
  text-align: center;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.12) 0%, rgba(124, 58, 237, 0.06) 100%);
  border: 1.5px solid rgba(99, 102, 241, 0.3);
}

.cta-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  height: 250px;
  background: var(--primary-glow);
  filter: blur(60px);
  pointer-events: none;
}

.cta-content {
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
}

.cta-content h2 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 14px;
}

.cta-content p {
  font-size: 16px;
  color: var(--text2);
  line-height: 1.6;
  margin-bottom: 28px;
}

.btn-cta {
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 800;
}

@media (max-width: 640px) {
  .hero-wrapper {
    padding: 30px 16px 50px;
  }
  .hero-content h1 {
    font-size: 32px;
  }
  .wheel-container {
    height: 276px;
  }
  .wheel-card {
    padding: 10px 12px;
    height: 80px;
  }
  .cta-card {
    padding: 36px 20px;
  }
  .cta-content h2 {
    font-size: 24px;
  }
}
</style>