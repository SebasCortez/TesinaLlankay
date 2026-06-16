<template>
  <div class="page">
    <div class="search-header">
      <div class="search-inner">
        <h1>Técnicos disponibles en Cusco</h1>
        <div class="search-bar">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input v-model="busqueda" @input="buscar" class="search-input"
              placeholder="Buscar por oficio, nombre o especialidad..." />
          </div>
          <select v-model="categoria" @change="buscar" class="search-select">
            <option value="">Todas las categorías</option>
            <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
          </select>
          <button class="btn-primary" @click="usarUbicacion" :disabled="buscandoUbicacion">
            {{ buscandoUbicacion ? '📍 Buscando...' : '📍 Cerca de mí' }}
          </button>
          <button v-if="usandoUbicacion" class="btn-secondary" @click="limpiarUbicacion">✕ Quitar</button>
        </div>
        <div v-if="usandoUbicacion" class="ubicacion-aviso">
          📍 Mostrando técnicos en un radio de 5 km de tu ubicación
        </div>
      </div>
    </div>

    <div class="resultados">
      <div class="resultados-header">
        <span class="resultados-count">{{ tecnicos.length }} técnico{{ tecnicos.length !== 1 ? 's' : '' }} encontrado{{
          tecnicos.length !== 1 ? 's' : '' }}</span>
      </div>

      <div v-if="cargando" class="estado">
        <div class="spinner"></div>
        <p>Buscando técnicos...</p>
      </div>

      <div v-else-if="tecnicos.length === 0" class="estado">
        <div style="font-size:48px;margin-bottom:16px">🔍</div>
        <h3>No se encontraron técnicos</h3>
        <p>Intenta con otros términos o categorías</p>
      </div>

      <div v-else class="grid">
        <div v-for="t in tecnicos" :key="t.id" class="worker-card card">
          <div class="wc-top">
            <div class="wc-avatar" :style="{ background: getColor(t.id) }">
              {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
            </div>
            <div class="wc-info">
              <div class="wc-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
              <div class="wc-job">{{ t.oficio }}</div>
            </div>
            <span :class="['badge', t.disponible ? 'badge-green' : 'badge-gray']">
              {{ t.disponible ? '● Disponible' : '● Ocupado' }}
            </span>
          </div>

          <div class="wc-stars">
            <span v-for="n in 5" :key="n" class="star">{{ n <= Math.round(t.calificacion_promedio) ? '⭐' : '☆' }}</span>
                <span class="wc-cal">{{ t.calificacion_promedio.toFixed(1) }} ({{ t.num_calificaciones }})</span>
          </div>

          <div class="wc-tags">
            <span class="badge badge-blue">{{ t.categoria }}</span>
            <span v-if="t.distancia_km !== null" class="badge badge-gray">📍 {{ t.distancia_km }} km</span>
            <span class="badge badge-gray">{{ t.usuario.distrito }}</span>
          </div>

          <router-link :to="`/trabajador/${t.id}`" class="btn-primary"
            style="width:100%;justify-content:center;margin-top:14px;padding:10px">
            Ver perfil
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const busqueda = ref('')
const categoria = ref('')
const tecnicos = ref<any[]>([])
const cargando = ref(false)
const buscandoUbicacion = ref(false)
const usandoUbicacion = ref(false)
const latitud = ref<number | null>(null)
const longitud = ref<number | null>(null)
const categorias = ['Electricidad', 'Gasfitería', 'Carpintería', 'Cerrajería', 'Pintura']

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return colores[id % colores.length]
}

async function buscar() {
  cargando.value = true
  try {
    const params: any = {}
    if (busqueda.value) params.busqueda = busqueda.value
    if (categoria.value) params.categoria = categoria.value
    if (latitud.value && longitud.value) { params.lat = latitud.value; params.lon = longitud.value }
    const res = await axios.get('http://127.0.0.1:8000/api/trabajadores/', { params })
    tecnicos.value = res.data
  } finally {
    cargando.value = false
  }
}

function usarUbicacion() {
  if (!navigator.geolocation) return alert('Tu navegador no soporta geolocalización')
  buscandoUbicacion.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => { latitud.value = pos.coords.latitude; longitud.value = pos.coords.longitude; usandoUbicacion.value = true; buscandoUbicacion.value = false; buscar() },
    () => { alert('No se pudo obtener tu ubicación'); buscandoUbicacion.value = false }
  )
}

function limpiarUbicacion() {
  latitud.value = null; longitud.value = null; usandoUbicacion.value = false; buscar()
}

onMounted(() => buscar())
</script>

<style scoped>
.search-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 32px;
}

.search-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.search-inner h1 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 16px;
}

.search-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input-wrap {
  flex: 1;
  min-width: 240px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 15px;
}

.search-input {
  width: 100%;
  padding: 10px 14px 10px 38px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.search-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-select {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-family: inherit;
  background: var(--surface);
  cursor: pointer;
  outline: none;
}

.ubicacion-aviso {
  margin-top: 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--primary);
  background: var(--primary-light);
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  display: inline-block;
}

.resultados {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 32px;
}

.resultados-header {
  margin-bottom: 20px;
}

.resultados-count {
  font-size: 14px;
  color: var(--text2);
  font-weight: 500;
}

.estado {
  text-align: center;
  padding: 64px 32px;
  color: var(--text2);
}

.estado h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.estado p {
  font-size: 14px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.worker-card {
  padding: 18px;
  transition: box-shadow 0.2s, transform 0.2s;
}

.worker-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.wc-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.wc-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}

.wc-name {
  font-size: 14px;
  font-weight: 600;
}

.wc-job {
  font-size: 12px;
  color: var(--text2);
  margin-top: 2px;
}

.wc-stars {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 10px;
}

.star {
  font-size: 13px;
}

.wc-cal {
  font-size: 12px;
  color: var(--text2);
  margin-left: 5px;
}

.wc-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>