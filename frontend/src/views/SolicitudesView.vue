<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-inner">
        <h1>{{ auth.esCliente ? 'Mis solicitudes' : 'Solicitudes recibidas' }}</h1>
        <p>{{ auth.esCliente ? 'Historial de servicios que has solicitado' : 'Servicios que los clientes te han solicitado' }}</p>
      </div>
    </div>

    <div class="contenedor">
      <div v-if="cargando" class="estado">
        <div class="spinner"></div>
        <p>Cargando solicitudes...</p>
      </div>

      <div v-else-if="solicitudes.length === 0" class="estado">
        <div style="font-size:48px;margin-bottom:16px">📋</div>
        <h3>No hay solicitudes aún</h3>
        <p v-if="auth.esCliente">Busca un técnico y envía tu primera solicitud</p>
        <router-link v-if="auth.esCliente" to="/buscar" class="btn-primary" style="margin-top:16px">Buscar
          técnicos</router-link>
      </div>

      <div v-else class="lista">
        <div v-for="s in solicitudes" :key="s.id" class="solicitud-card card">
          <div class="sol-header">
            <div class="sol-persona">
              <div class="sol-avatar">
                <span v-if="auth.esCliente">{{ s.trabajador.usuario.first_name[0] }}{{ s.trabajador.usuario.last_name[0]
                  }}</span>
                <span v-else>{{ s.cliente.first_name[0] }}{{ s.cliente.last_name[0] }}</span>
              </div>
              <div>
                <div class="sol-nombre" v-if="auth.esCliente">{{ s.trabajador.usuario.first_name }} {{
                  s.trabajador.usuario.last_name }}</div>
                <div class="sol-nombre" v-else>{{ s.cliente.first_name }} {{ s.cliente.last_name }}</div>
                <div class="sol-sub" v-if="auth.esCliente">{{ s.trabajador.oficio }}</div>
                <div class="sol-sub" v-else>{{ s.cliente.celular }}</div>
              </div>
            </div>
            <span :class="['badge', estadoBadge[s.estado]]">{{ estadoTexto[s.estado] }}</span>
          </div>

          <div class="sol-body">
            <div class="sol-campo">
              <span class="sol-label">Mensaje</span>
              <p>{{ s.mensaje }}</p>
            </div>
            <div class="sol-campo">
              <span class="sol-label">Problema</span>
              <p>{{ s.descripcion_problema }}</p>
            </div>
            <div class="sol-campo">
              <span class="sol-label">Dirección</span>
              <p>📍 {{ s.direccion }}</p>
            </div>
            <div v-if="s.motivo_rechazo" class="sol-campo">
              <span class="sol-label">Motivo de rechazo</span>
              <p class="txt-red">{{ s.motivo_rechazo }}</p>
            </div>
          </div>

          <div class="sol-footer">
            <span class="sol-fecha">{{ formatFecha(s.fecha_solicitud) }}</span>

            <!-- Acciones trabajador -->
            <div v-if="auth.esTrabajador" class="sol-acciones">
              <div v-if="s.estado === 'pendiente'" style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="btn-primary" @click="cambiarEstado(s.id, 'aceptado')" :disabled="procesando === s.id">✅
                  Aceptar</button>
                <div style="display:flex;gap:6px">
                  <input v-model="motivos[s.id]" class="form-input" style="width:200px;padding:8px 12px"
                    placeholder="Motivo de rechazo..." />
                  <button class="btn-danger" @click="cambiarEstado(s.id, 'rechazado', motivos[s.id])"
                    :disabled="procesando === s.id">❌ Rechazar</button>
                </div>
              </div>
              <button v-if="s.estado === 'aceptado'" class="btn-primary" style="background:#7C3AED"
                @click="cambiarEstado(s.id, 'en_progreso')" :disabled="procesando === s.id">🔧 Marcar en progreso</button>
              <button v-if="s.estado === 'en_progreso'" class="btn-primary" @click="cambiarEstado(s.id, 'completado')"
                :disabled="procesando === s.id">✔ Marcar completado</button>
            </div>

            <!-- Acciones cliente -->
            <div v-if="auth.esCliente && s.estado === 'completado'">
              <router-link :to="`/trabajador/${s.trabajador.id}`" class="btn-primary">⭐ Calificar técnico</router-link>
            </div>
          </div>

          <div v-if="mensajes[s.id]"
            :class="['alert', mensajes[s.id].tipo === 'exito' ? 'alert-success' : 'alert-error']"
            style="margin:0 20px 16px">
            {{ mensajes[s.id].texto }}
          </div>
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
const procesando = ref<number | null>(null)
const motivos = ref<any>({})
const mensajes = ref<any>({})

const estadoTexto: any = {
  pendiente: '⏳ Pendiente',
  aceptado: '✅ Aceptado',
  en_progreso: '🔧 En progreso',
  completado: '✔ Completado',
  rechazado: '❌ Rechazado'
}
const estadoBadge: any = {
  pendiente: 'badge-amber',
  aceptado: 'badge-green',
  en_progreso: 'badge-blue',
  completado: 'badge-green',
  rechazado: 'badge-red'
}

function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
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
  procesando.value = id
  try {
    const res = await axios.patch(`http://127.0.0.1:8000/api/solicitudes/${id}/estado/`, {
      estado, motivo_rechazo: motivo || ''
    })
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarSolicitudes()
  } catch (e: any) {
    mensajes.value[id] = { tipo: 'error', texto: e.response?.data?.error || 'Error al actualizar' }
  } finally {
    procesando.value = null
  }
}

onMounted(() => cargarSolicitudes())
</script>

<style scoped>
.page {
  min-height: calc(100vh - 64px);
}

.page-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 32px;
}

.page-header-inner {
  max-width: 800px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 14px;
  color: var(--text2);
}

.contenedor {
  max-width: 800px;
  margin: 0 auto;
  padding: 28px 32px;
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

.lista {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.solicitud-card {
  overflow: hidden;
}

.sol-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
}

.sol-persona {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sol-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.sol-nombre {
  font-size: 15px;
  font-weight: 600;
}

.sol-sub {
  font-size: 12px;
  color: var(--text2);
  margin-top: 2px;
}

.sol-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sol-campo {
  font-size: 13px;
}

.sol-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 3px;
}

.sol-campo p {
  color: var(--text);
  line-height: 1.55;
}

.txt-red {
  color: var(--red) !important;
}

.sol-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 10px;
}

.sol-fecha {
  font-size: 12px;
  color: var(--text3);
}

.sol-acciones {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
</style>