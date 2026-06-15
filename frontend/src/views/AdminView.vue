<template>
  <div class="contenedor">
    <h2>Panel de administración</h2>
    <p class="sub">Solicitudes de registro de técnicos pendientes de aprobación</p>

    <div v-if="cargando" class="estado">Cargando solicitudes...</div>
    <div v-else-if="pendientes.length === 0" class="estado">No hay solicitudes pendientes</div>

    <div class="lista">
      <div v-for="t in pendientes" :key="t.id" class="solicitud">
        <div class="solicitud-top">
          <div class="avatar" :style="{ background: getColor(t.id) }">
            {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
          </div>
          <div class="solicitud-info">
            <div class="nombre">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
            <div class="detalle">{{ t.oficio }} · {{ t.categoria }}</div>
            <div class="detalle">{{ t.usuario.distrito }} · {{ t.experiencia }}</div>
            <div class="detalle">📱 {{ t.usuario.celular }}</div>
            <div class="detalle">📧 {{ t.usuario.email }}</div>
            <div v-if="t.descripcion" class="descripcion">{{ t.descripcion }}</div>
            <div class="fecha">Solicitud: {{ formatFecha(t.fecha_solicitud) }}</div>
          </div>
        </div>

        <div class="solicitud-acciones">
          <button class="btn-aprobar" @click="aprobar(t.id)" :disabled="procesando === t.id">
            ✅ Aprobar
          </button>
          <div class="rechazo-form">
            <input v-model="motivos[t.id]" placeholder="Motivo de rechazo (opcional)" />
            <button class="btn-rechazar" @click="rechazar(t.id)" :disabled="procesando === t.id">
              ❌ Rechazar
            </button>
          </div>
        </div>

        <div v-if="mensajes[t.id]" :class="['msg', mensajes[t.id].tipo]">
          {{ mensajes[t.id].texto }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const pendientes = ref<any[]>([])
const cargando = ref(false)
const procesando = ref<number | null>(null)
const motivos = ref<any>({})
const mensajes = ref<any>({})

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

async function cargarPendientes() {
  cargando.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/trabajadores/pendientes/')
    pendientes.value = res.data
  } finally {
    cargando.value = false
  }
}

async function aprobar(id: number) {
  procesando.value = id
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/trabajadores/${id}/aprobar/`)
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    setTimeout(() => cargarPendientes(), 1500)
  } catch (e) {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al aprobar' }
  } finally {
    procesando.value = null
  }
}

async function rechazar(id: number) {
  procesando.value = id
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/trabajadores/${id}/rechazar/`, {
      motivo: motivos.value[id] || 'Sin motivo especificado'
    })
    mensajes.value[id] = { tipo: 'error', texto: res.data.mensaje }
    setTimeout(() => cargarPendientes(), 1500)
  } catch (e) {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al rechazar' }
  } finally {
    procesando.value = null
  }
}

onMounted(() => cargarPendientes())
</script>

<style scoped>
.contenedor { max-width: 800px; margin: 40px auto; padding: 0 24px; }
h2 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.sub { font-size: 14px; color: #888; margin-bottom: 24px; }
.estado { text-align: center; padding: 48px; color: #888; }
.lista { display: flex; flex-direction: column; gap: 16px; }
.solicitud { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; }
.solicitud-top { display: flex; gap: 16px; margin-bottom: 16px; }
.avatar {
  width: 52px; height: 52px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; flex-shrink: 0;
}
.nombre { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.detalle { font-size: 13px; color: #666; margin-top: 2px; }
.descripcion { font-size: 13px; color: #888; font-style: italic; margin-top: 6px; background: #f8f7f4; padding: 8px; border-radius: 6px; }
.fecha { font-size: 11px; color: #aaa; margin-top: 6px; }
.solicitud-acciones { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; padding-top: 14px; border-top: 1px solid #f0eeea; }
.btn-aprobar {
  padding: 9px 20px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-aprobar:disabled { background: #aaa; cursor: not-allowed; }
.rechazo-form { display: flex; gap: 8px; flex: 1; }
.rechazo-form input {
  flex: 1; padding: 9px 12px;
  border: 1px solid #ccc; border-radius: 8px; font-size: 13px; outline: none;
}
.rechazo-form input:focus { border-color: #e24b4a; }
.btn-rechazar {
  padding: 9px 16px; background: #e24b4a; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-rechazar:disabled { background: #aaa; cursor: not-allowed; }
.msg { padding: 8px 12px; border-radius: 8px; font-size: 13px; margin-top: 10px; }
.msg.exito { background: #e1f5ee; color: #0f6e56; }
.msg.error { background: #fde8e8; color: #c0392b; }
</style>