<template>
  <div class="page">
    <div class="filtros">
      <input v-model="busqueda" @input="buscar" placeholder="Buscar por oficio o nombre..." />
      <select v-model="categoria" @change="buscar">
        <option value="">Todas las categorías</option>
        <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
      </select>
      <button class="btn-ubicacion" @click="usarUbicacion" :disabled="buscandoUbicacion">
        {{ buscandoUbicacion ? '📍 Buscando...' : '📍 Cerca de mí' }}
      </button>
      <button v-if="usandoUbicacion" class="btn-limpiar" @click="limpiarUbicacion">✕ Quitar filtro</button>
    </div>

    <div v-if="usandoUbicacion" class="aviso-ubicacion">
      📍 Mostrando técnicos en un radio de 5 km
    </div>

    <div class="contenedor">
      <div v-if="cargando" class="estado">Buscando técnicos...</div>
      <div v-else-if="tecnicos.length === 0" class="estado">No se encontraron técnicos</div>

      <div class="grid">
        <div v-for="t in tecnicos" :key="t.id" class="card">
          <div class="card-top">
            <div class="avatar" :style="{ background: getColor(t.id) }">
              {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
            </div>
            <div>
              <div class="nombre">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
              <div class="oficio">{{ t.oficio }}</div>
            </div>
            <span :class="['estado-badge', t.disponible ? 'verde' : 'gris']">
              {{ t.disponible ? 'Disponible' : 'Ocupado' }}
            </span>
          </div>

          <div class="estrellas">
            <span v-for="n in 5" :key="n">{{ n <= Math.round(t.calificacion_promedio) ? '⭐' : '☆' }}</span>
            <span class="cal-num">{{ t.calificacion_promedio.toFixed(1) }} ({{ t.num_calificaciones }})</span>
          </div>

          <div class="tags">
            <span class="tag">{{ t.categoria }}</span>
            <span class="tag gris" v-if="t.distancia_km !== null">📍 {{ t.distancia_km }} km</span>
            <span class="tag gris">{{ t.usuario.distrito }}</span>
          </div>

          <div class="card-btns">
            <router-link :to="`/trabajador/${t.id}`" class="btn-verde">Ver perfil</router-link>
          </div>
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

const categorias = ['Electricidad','Gasfitería','Carpintería','Cerrajería','Pintura']

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}

function getColor(id: number) {
  const colores = ['#c8eed9','#d4edba','#fde8c8','#d6e8f8','#f8d6e8','#e8d6f8']
  return colores[id % colores.length]
}

async function buscar() {
  cargando.value = true
  try {
    const params: any = {}
    if (busqueda.value) params.busqueda = busqueda.value
    if (categoria.value) params.categoria = categoria.value
    if (latitud.value && longitud.value) {
      params.lat = latitud.value
      params.lon = longitud.value
    }
    const res = await axios.get('http://127.0.0.1:8000/api/trabajadores/', { params })
    tecnicos.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function usarUbicacion() {
  if (!navigator.geolocation)
    return alert('Tu navegador no soporta geolocalización')
  buscandoUbicacion.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      latitud.value = pos.coords.latitude
      longitud.value = pos.coords.longitude
      usandoUbicacion.value = true
      buscandoUbicacion.value = false
      buscar()
    },
    () => {
      alert('No se pudo obtener tu ubicación')
      buscandoUbicacion.value = false
    }
  )
}

function limpiarUbicacion() {
  latitud.value = null
  longitud.value = null
  usandoUbicacion.value = false
  buscar()
}

onMounted(() => buscar())
</script>

<style scoped>
.page { min-height: calc(100vh - 56px); }
.filtros {
  background: #fff; border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
}
.filtros input {
  flex: 1; min-width: 200px; padding: 9px 12px;
  border: 1px solid #ccc; border-radius: 8px; font-size: 14px; outline: none;
}
.filtros input:focus { border-color: #1D9E75; }
.filtros select {
  padding: 9px 12px; border: 1px solid #ccc;
  border-radius: 8px; font-size: 14px; background: #fff; cursor: pointer;
}
.btn-ubicacion {
  padding: 9px 16px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-ubicacion:disabled { background: #aaa; cursor: not-allowed; }
.btn-limpiar {
  padding: 9px 12px; background: transparent;
  border: 1px solid #ccc; border-radius: 8px; font-size: 13px; cursor: pointer;
}
.aviso-ubicacion {
  background: #e1f5ee; color: #0f6e56;
  padding: 10px 24px; font-size: 13px; font-weight: 500;
}
.contenedor { max-width: 1100px; margin: 0 auto; padding: 24px; }
.estado { text-align: center; padding: 48px; color: #888; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap: 14px; }
.card {
  background: #fff; border: 1px solid #e0e0e0;
  border-radius: 12px; padding: 16px;
  transition: box-shadow 0.2s, transform 0.2s;
}
.card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-2px); }
.card-top { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.avatar {
  width: 42px; height: 42px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; flex-shrink: 0;
}
.nombre { font-size: 14px; font-weight: 600; }
.oficio { font-size: 12px; color: #666; }
.estado-badge { margin-left: auto; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 12px; white-space: nowrap; }
.verde { background: #e1f5ee; color: #0f6e56; }
.gris { background: #f0eeea; color: #888; }
.estrellas { font-size: 13px; display: flex; align-items: center; gap: 2px; margin-bottom: 8px; }
.cal-num { font-size: 11px; color: #888; margin-left: 4px; }
.tags { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.tag { font-size: 11px; font-weight: 500; padding: 3px 8px; border-radius: 10px; background: #e1f5ee; color: #0f6e56; }
.tag.gris { background: #f0eeea; color: #666; }
.card-btns { padding-top: 12px; border-top: 1px solid #f0eeea; }
.btn-verde {
  display: block; text-align: center;
  padding: 8px; background: #1D9E75; color: #fff;
  border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 600;
}
.btn-verde:hover { background: #0f6e56; }
</style>