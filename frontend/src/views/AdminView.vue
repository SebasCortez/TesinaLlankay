<template>
  <div class="admin">
    <div class="admin-sidebar">
      <div class="sidebar-title">Panel Admin</div>
      <button :class="['sidebar-btn', seccion === 'dashboard' ? 'active' : '']" @click="seccion = 'dashboard'">📊
        Dashboard</button>
      <button :class="['sidebar-btn', seccion === 'pendientes' ? 'active' : '']" @click="seccion = 'pendientes'">⏳ Solicitudes
        pendientes <span v-if="pendientes.length" class="badge">{{ pendientes.length }}</span></button>
      <button :class="['sidebar-btn', seccion === 'trabajadores' ? 'active' : '']" @click="seccion = 'trabajadores'">👷
        Trabajadores</button>
      <button :class="['sidebar-btn', seccion === 'clientes' ? 'active' : '']" @click="seccion = 'clientes'">👥
        Clientes</button>
      <button :class="['sidebar-btn', seccion === 'solicitudes' ? 'active' : '']" @click="seccion = 'solicitudes'">📋 Todas las
        solicitudes</button>
    </div>

    <div class="admin-content">

      <!-- DASHBOARD -->
      <div v-if="seccion === 'dashboard'">
        <h2>Dashboard</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-num">{{ stats.total_clientes }}</div>
            <div class="stat-label">Clientes registrados</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ stats.total_trabajadores }}</div>
            <div class="stat-label">Trabajadores aprobados</div>
          </div>
          <div class="stat-card amber">
            <div class="stat-num">{{ stats.pendientes_aprobacion }}</div>
            <div class="stat-label">Pendientes de aprobación</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ stats.total_solicitudes }}</div>
            <div class="stat-label">Solicitudes totales</div>
          </div>
          <div class="stat-card green">
            <div class="stat-num">{{ stats.solicitudes_completadas }}</div>
            <div class="stat-label">Servicios completados</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ stats.total_calificaciones }}</div>
            <div class="stat-label">Calificaciones</div>
          </div>
        </div>
      </div>

      <!-- PENDIENTES -->
      <div v-if="seccion === 'pendientes'">
        <h2>Solicitudes de registro pendientes</h2>
        <div v-if="pendientes.length === 0" class="estado">No hay solicitudes pendientes</div>
        <div class="lista">
          <div v-for="t in pendientes" :key="t.id" class="item-card">
            <div class="item-top">
              <div class="avatar" :style="{ background: getColor(t.id) }">
                {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
              </div>
              <div class="item-info">
                <div class="nombre">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="detalle">{{ t.oficio }} · {{ t.categoria }}</div>
                <div class="detalle">📍 {{ t.usuario.distrito }} · {{ t.experiencia }}</div>
                <div class="detalle">📱 {{ t.usuario.celular }} · 📧 {{ t.usuario.email }}</div>
                <div v-if="t.descripcion" class="descripcion">{{ t.descripcion }}</div>
                <div class="fecha">{{ formatFecha(t.fecha_solicitud) }}</div>
              </div>
            </div>
            <div class="item-acciones">
              <button class="btn-verde" @click="aprobar(t.id)" :disabled="procesando === t.id">✅ Aprobar</button>
              <div style="display:flex;gap:8px;flex:1">
                <input v-model="motivos[t.id]" placeholder="Motivo de rechazo (opcional)" class="input-sm" />
                <button class="btn-rojo" @click="rechazar(t.id)" :disabled="procesando === t.id">❌ Rechazar</button>
              </div>
            </div>
            <div v-if="mensajes[t.id]" :class="['msg', mensajes[t.id].tipo]">{{ mensajes[t.id].texto }}</div>
          </div>
        </div>
      </div>

      <!-- TRABAJADORES -->
      <div v-if="seccion === 'trabajadores'">
        <h2>Trabajadores</h2>
        <div class="tabla">
          <div class="tabla-header">
            <span>Nombre</span><span>Oficio</span><span>Categoría</span><span>Estado</span><span>Calif.</span><span>Servicios</span>
          </div>
          <div v-for="t in trabajadores" :key="t.id" class="tabla-fila">
            <span>{{ t.usuario.first_name }} {{ t.usuario.last_name }}</span>
            <span>{{ t.oficio }}</span>
            <span>{{ t.categoria }}</span>
            <span :class="['badge-estado', t.estado]">{{ t.estado }}</span>
            <span>⭐ {{ t.calificacion_promedio.toFixed(1) }}</span>
            <span>{{ t.num_calificaciones }}</span>
          </div>
        </div>
      </div>

      <!-- CLIENTES -->
      <div v-if="seccion === 'clientes'">
        <h2>Clientes</h2>
        <div class="tabla">
          <div class="tabla-header">
            <span>Nombre</span><span>Usuario</span><span>Correo</span><span>Celular</span><span>Distrito</span>
          </div>
          <div v-for="c in clientes" :key="c.id" class="tabla-fila">
            <span>{{ c.first_name }} {{ c.last_name }}</span>
            <span>{{ c.username }}</span>
            <span>{{ c.email }}</span>
            <span>{{ c.celular }}</span>
            <span>{{ c.distrito }}</span>
          </div>
        </div>
      </div>

      <!-- TODAS LAS SOLICITUDES -->
      <div v-if="seccion === 'solicitudes'">
        <h2>Todas las solicitudes</h2>
        <div class="tabla">
          <div class="tabla-header">
            <span>Cliente</span><span>Técnico</span><span>Problema</span><span>Estado</span><span>Fecha</span>
          </div>
          <div v-for="s in todasSolicitudes" :key="s.id" class="tabla-fila">
            <span>{{ s.cliente.first_name }} {{ s.cliente.last_name }}</span>
            <span>{{ s.trabajador.usuario.first_name }} {{ s.trabajador.usuario.last_name }}</span>
            <span class="truncar">{{ s.descripcion_problema }}</span>
            <span :class="['badge-estado', s.estado]">{{ s.estado }}</span>
            <span>{{ formatFecha(s.fecha_solicitud) }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const seccion = ref('dashboard')
const pendientes = ref<any[]>([])
const trabajadores = ref<any[]>([])
const clientes = ref<any[]>([])
const todasSolicitudes = ref<any[]>([])
const procesando = ref<number | null>(null)
const motivos = ref<any>({})
const mensajes = ref<any>({})

const stats = ref({
  total_clientes: 0,
  total_trabajadores: 0,
  pendientes_aprobacion: 0,
  total_solicitudes: 0,
  solicitudes_completadas: 0,
  total_calificaciones: 0,
})

function getIniciales(nombre: string, apellido: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}
function getColor(id: number) {
  const colores = ['#c8eed9', '#d4edba', '#fde8c8', '#d6e8f8', '#f8d6e8', '#e8d6f8']
  return colores[id % colores.length]
}
function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function cargarTodo() {
  const [resPend, resTrab, resSol] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/trabajadores/pendientes/'),
    axios.get('http://127.0.0.1:8000/api/admin/trabajadores/'),
    axios.get('http://127.0.0.1:8000/api/admin/solicitudes/'),
  ])
  pendientes.value = resPend.data
  trabajadores.value = resTrab.data
  todasSolicitudes.value = resSol.data

  const resClientes = await axios.get('http://127.0.0.1:8000/api/admin/clientes/')
  clientes.value = resClientes.data

  stats.value = {
    total_clientes: clientes.value.length,
    total_trabajadores: trabajadores.value.filter((t: any) => t.estado === 'aprobado').length,
    pendientes_aprobacion: pendientes.value.length,
    total_solicitudes: todasSolicitudes.value.length,
    solicitudes_completadas: todasSolicitudes.value.filter((s: any) => s.estado === 'completado').length,
    total_calificaciones: trabajadores.value.reduce((acc: number, t: any) => acc + t.num_calificaciones, 0),
  }
}

async function aprobar(id: number) {
  procesando.value = id
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/trabajadores/${id}/aprobar/`)
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarTodo()
  } catch {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al aprobar' }
  } finally { procesando.value = null }
}

async function rechazar(id: number) {
  procesando.value = id
  try {
    const res = await axios.post(`http://127.0.0.1:8000/api/trabajadores/${id}/rechazar/`, {
      motivo: motivos.value[id] || 'Sin motivo especificado'
    })
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarTodo()
  } catch {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al rechazar' }
  } finally { procesando.value = null }
}

onMounted(() => cargarTodo())
</script>

<style scoped>
.admin {
  display: flex;
  min-height: calc(100vh - 56px);
}

.admin-sidebar {
  width: 220px;
  background: #1A1A18;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-title {
  color: #aaa;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0 16px 16px;
}

.sidebar-btn {
  padding: 11px 16px;
  background: none;
  border: none;
  color: #ccc;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s;
}

.sidebar-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.sidebar-btn.active {
  background: rgba(29, 158, 117, 0.2);
  color: #5DCAA5;
  border-left: 3px solid #1D9E75;
}

.badge {
  background: #EF9F27;
  color: #fff;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: auto;
}

.admin-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-card.green {
  border-top: 3px solid #1D9E75;
}

.stat-card.amber {
  border-top: 3px solid #EF9F27;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #1A1A18;
}

.stat-label {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.estado {
  text-align: center;
  padding: 48px;
  color: #888;
}

.lista {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.item-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 18px;
}

.item-top {
  display: flex;
  gap: 14px;
  margin-bottom: 14px;
}

.avatar {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.nombre {
  font-size: 15px;
  font-weight: 600;
}

.detalle {
  font-size: 12px;
  color: #666;
  margin-top: 3px;
}

.descripcion {
  font-size: 12px;
  color: #888;
  font-style: italic;
  margin-top: 6px;
  background: #f8f7f4;
  padding: 6px 8px;
  border-radius: 6px;
}

.fecha {
  font-size: 11px;
  color: #aaa;
  margin-top: 6px;
}

.item-acciones {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0eeea;
}

.btn-verde {
  padding: 8px 16px;
  background: #1D9E75;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.btn-rojo {
  padding: 8px 16px;
  background: #e24b4a;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.input-sm {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}

.msg {
  padding: 8px 0;
  font-size: 13px;
}

.msg.exito {
  color: #0f6e56;
}

.msg.error {
  color: #c0392b;
}

.tabla {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.tabla-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  padding: 12px 16px;
  background: #f8f7f4;
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  gap: 8px;
}

.tabla-fila {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  padding: 12px 16px;
  border-top: 1px solid #f0eeea;
  font-size: 13px;
  gap: 8px;
  align-items: center;
}

.tabla-fila:hover {
  background: #fafaf8;
}

.badge-estado {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  display: inline-block;
}

.badge-estado.aprobado {
  background: #e1f5ee;
  color: #0f6e56;
}

.badge-estado.pendiente {
  background: #FFF8E1;
  color: #7A5800;
}

.badge-estado.rechazado {
  background: #fde8e8;
  color: #c0392b;
}

.badge-estado.completado {
  background: #e1f5ee;
  color: #0f6e56;
}

.badge-estado.en_progreso {
  background: #E6F1FB;
  color: #0C447C;
}

.truncar {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
</style>