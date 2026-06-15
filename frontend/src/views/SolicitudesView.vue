<template>
  <div class="contenedor">
    <h2>{{ auth.esCliente ? 'Mis solicitudes' : 'Solicitudes recibidas' }}</h2>

    <div v-if="cargando" class="estado">Cargando...</div>
    <div v-else-if="solicitudes.length === 0" class="estado">No hay solicitudes aún</div>

    <div class="lista">
      <div v-for="s in solicitudes" :key="s.id" class="solicitud">
        <div class="solicitud-header">
          <div class="header-info">
            <div v-if="auth.esCliente">
              <div class="nombre">{{ s.trabajador.usuario.first_name }} {{ s.trabajador.usuario.last_name }}</div>
              <div class="sub">{{ s.trabajador.oficio }}</div>
            </div>
            <div v-else>
              <div class="nombre">{{ s.cliente.first_name }} {{ s.cliente.last_name }}</div>
              <div class="sub">{{ s.cliente.celular }}</div>
            </div>
          </div>
          <span :class="['estado-badge', s.estado]">{{ estadoTexto[s.estado] }}</span>
        </div>

        <div class="solicitud-body">
          <div class="campo-info">
            <span class="label">Mensaje</span>
            <p>{{ s.mensaje }}</p>
          </div>
          <div class="campo-info">
            <span class="label">Problema</span>
            <p>{{ s.descripcion_problema }}</p>
          </div>
          <div class="campo-info">
            <span class="label">Dirección</span>
            <p>📍 {{ s.direccion }}</p>
          </div>
          <div v-if="s.motivo_rechazo" class="campo-info">
            <span class="label">Motivo de rechazo</span>
            <p class="rechazo">{{ s.motivo_rechazo }}</p>
          </div>
          <div class="fecha">{{ formatFecha(s.fecha_solicitud) }}</div>
        </div>

        <!-- Acciones para trabajador -->
        <div v-if="auth.esTrabajador" class="acciones">
          <div v-if="s.estado === 'pendiente'" style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn-verde" @click="cambiarEstado(s.id, 'aceptado')">✅ Aceptar</button>
            <div style="display:flex;gap:6px;flex:1">
              <input v-model="motivos[s.id]" placeholder="Motivo de rechazo..." style="flex:1;padding:8px 10px;border:1px solid #ccc;border-radius:8px;font-size:13px;outline:none" />
              <button class="btn-rojo" @click="cambiarEstado(s.id, 'rechazado', motivos[s.id])">❌ Rechazar</button>
            </div>
          </div>
          <div v-if="s.estado === 'aceptado'">
            <button class="btn-azul" @click="cambiarEstado(s.id, 'en_progreso')">🔧 Marcar en progreso</button>
          </div>
          <div v-if="s.estado === 'en_progreso'">
            <button class="btn-verde" @click="cambiarEstado(s.id, 'completado')">✔ Marcar como completado</button>
          </div>
        </div>

        <!-- Acciones para cliente -->
        <div v-if="auth.esCliente && s.estado === 'completado'" class="acciones">
          <router-link :to="`/trabajador/${s.trabajador.id}`" class="btn-verde-link">
            ⭐ Calificar al técnico
          </router-link>
        </div>

        <div v-if="mensajes[s.id]" :class="['msg', mensajes[s.id].tipo]">
          {{ mensajes[s.id].texto }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const solicitudes = ref<any[]>([])
const cargando = ref(false)
const motivos = ref<any>({})
const mensajes = ref<any>({})

const estadoTexto: any = {
  pendiente: '⏳ Pendiente',
  aceptado: '✅ Aceptado',
  en_progreso: '🔧 En progreso',
  completado: '✔ Completado',
  rechazado: '❌ Rechazado'
}

function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', { year:'numeric', month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' })
}

async function cargarSolicitudes() {
  cargando.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/solicitudes/')
    solicitudes.value = res.data
  } finally {
    cargando.value = false
  }
}

async function cambiarEstado(id: number, estado: string, motivo?: string) {
  try {
    const res = await axios.patch(`http://127.0.0.1:8000/api/solicitudes/${id}/estado/`, {
      estado,
      motivo_rechazo: motivo || ''
    })
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarSolicitudes()
  } catch (e: any) {
    mensajes.value[id] = { tipo: 'error', texto: e.response?.data?.error || 'Error al actualizar' }
  }
}

onMounted(() => cargarSolicitudes())
</script>

<style scoped>
.contenedor { max-width: 800px; margin: 40px auto; padding: 0 24px; }
h2 { font-size: 22px; font-weight: 700; margin-bottom: 24px; }
.estado { text-align: center; padding: 48px; color: #888; }
.lista { display: flex; flex-direction: column; gap: 16px; }
.solicitud { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
.solicitud-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid #f0eeea; background: #fafaf8;
}
.nombre { font-size: 15px; font-weight: 600; }
.sub { font-size: 12px; color: #888; margin-top: 2px; }
.estado-badge {
  font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 20px;
}
.estado-badge.pendiente { background: #FFF8E1; color: #7A5800; }
.estado-badge.aceptado { background: #e1f5ee; color: #0f6e56; }
.estado-badge.en_progreso { background: #E6F1FB; color: #0C447C; }
.estado-badge.completado { background: #e1f5ee; color: #0f6e56; }
.estado-badge.rechazado { background: #fde8e8; color: #c0392b; }
.solicitud-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 10px; }
.campo-info { font-size: 13px; }
.label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; display: block; margin-bottom: 2px; }
.campo-info p { color: #333; line-height: 1.5; }
.rechazo { color: #c0392b; }
.fecha { font-size: 11px; color: #aaa; margin-top: 4px; }
.acciones { padding: 14px 20px; border-top: 1px solid #f0eeea; background: #fafaf8; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.btn-verde {
  padding: 8px 16px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-verde:hover { background: #0f6e56; }
.btn-rojo {
  padding: 8px 16px; background: #e24b4a; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-azul {
  padding: 8px 16px; background: #378ADD; color: #fff;
  border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-verde-link {
  padding: 8px 16px; background: #1D9E75; color: #fff;
  border-radius: 8px; font-size: 13px; font-weight: 600;
  text-decoration: none; display: inline-block;
}
.msg { padding: 10px 20px; font-size: 13px; }
.msg.exito { background: #e1f5ee; color: #0f6e56; }
.msg.error { background: #fde8e8; color: #c0392b; }
</style>