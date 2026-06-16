<template>
  <div class="admin">
    <div class="admin-sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🔧</div>
        <div>
          <div class="sidebar-brand-name">TécniCusco</div>
          <div class="sidebar-brand-sub">Panel de administración</div>
        </div>
      </div>

      <div class="sidebar-menu">
        <button :class="['menu-btn', seccion === 'dashboard' ? 'active' : '']" @click="seccion = 'dashboard'">
          <span class="menu-icon">📊</span> Dashboard
        </button>
        <button :class="['menu-btn', seccion === 'pendientes' ? 'active' : '']" @click="seccion = 'pendientes'">
          <span class="menu-icon">⏳</span> Pendientes
          <span v-if="pendientes.length" class="menu-badge">{{ pendientes.length }}</span>
        </button>
        <button :class="['menu-btn', seccion === 'trabajadores' ? 'active' : '']" @click="seccion = 'trabajadores'">
          <span class="menu-icon">👷</span> Trabajadores
        </button>
        <button :class="['menu-btn', seccion === 'clientes' ? 'active' : '']" @click="seccion = 'clientes'">
          <span class="menu-icon">👥</span> Clientes
        </button>
        <button :class="['menu-btn', seccion === 'solicitudes' ? 'active' : '']" @click="seccion = 'solicitudes'">
          <span class="menu-icon">📋</span> Solicitudes
        </button>
      </div>
    </div>

    <div class="admin-main">

      <!-- DASHBOARD -->
      <div v-if="seccion === 'dashboard'">
        <div class="admin-page-header">
          <h2>Dashboard</h2>
          <p>Resumen general de la plataforma</p>
        </div>
        <div class="stats-grid">
          <div class="stat-card card">
            <div class="stat-icon" style="background:#DBEAFE;color:#1D4ED8">👥</div>
            <div class="stat-num">{{ stats.total_clientes }}</div>
            <div class="stat-label">Clientes</div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon" style="background:#D1FAE5;color:#065F46">👷</div>
            <div class="stat-num">{{ stats.total_trabajadores }}</div>
            <div class="stat-label">Técnicos aprobados</div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon" style="background:#FEF3C7;color:#92400E">⏳</div>
            <div class="stat-num">{{ stats.pendientes_aprobacion }}</div>
            <div class="stat-label">Pendientes</div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon" style="background:#EDE9FE;color:#5B21B6">📋</div>
            <div class="stat-num">{{ stats.total_solicitudes }}</div>
            <div class="stat-label">Solicitudes totales</div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon" style="background:#D1FAE5;color:#065F46">✔</div>
            <div class="stat-num">{{ stats.solicitudes_completadas }}</div>
            <div class="stat-label">Servicios completados</div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon" style="background:#FEE2E2;color:#991B1B">⭐</div>
            <div class="stat-num">{{ stats.total_calificaciones }}</div>
            <div class="stat-label">Calificaciones</div>
          </div>
        </div>

        <div class="dashboard-bottom">
          <div class="card recent-section">
            <h3>Últimas solicitudes</h3>
            <div v-for="s in todasSolicitudes.slice(0, 5)" :key="s.id" class="recent-item">
              <div class="recent-info">
                <div class="recent-name">{{ s.cliente.first_name }} → {{ s.trabajador.usuario.first_name }}</div>
                <div class="recent-sub">{{ s.descripcion_problema.substring(0, 60) }}...</div>
              </div>
              <span :class="['badge', estadoBadge[s.estado]]">{{ estadoTexto[s.estado] }}</span>
            </div>
          </div>
          <div class="card recent-section">
            <h3>Solicitudes pendientes de aprobación</h3>
            <div v-if="pendientes.length === 0" class="empty-state">✅ No hay solicitudes pendientes</div>
            <div v-for="t in pendientes.slice(0, 5)" :key="t.id" class="recent-item">
              <div class="recent-info">
                <div class="recent-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="recent-sub">{{ t.oficio }} · {{ t.categoria }}</div>
              </div>
              <button class="btn-primary" style="padding:6px 12px;font-size:12px"
                @click="aprobar(t.id)">Aprobar</button>
            </div>
          </div>
        </div>
      </div>

      <!-- PENDIENTES -->
      <div v-if="seccion === 'pendientes'">
        <div class="admin-page-header">
          <h2>Solicitudes pendientes</h2>
          <p>Revisa y aprueba o rechaza las solicitudes de registro de técnicos</p>
        </div>
        <div v-if="pendientes.length === 0" class="empty-full">
          <div style="font-size:48px;margin-bottom:16px">✅</div>
          <h3>No hay solicitudes pendientes</h3>
        </div>
        <div class="lista">
          <div v-for="t in pendientes" :key="t.id" class="card item-card">
            <div class="item-top">
              <div class="item-avatar" :style="{ background: getColor(t.id) }">
                {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
              </div>
              <div class="item-info">
                <div class="item-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="item-meta">{{ t.oficio }} · {{ t.categoria }} · {{ t.experiencia }}</div>
                <div class="item-meta">📍 {{ t.usuario.distrito }} · 📱 {{ t.usuario.celular }} · 📧 {{ t.usuario.email
                  }}</div>
                <div v-if="t.descripcion" class="item-desc">{{ t.descripcion }}</div>
                <div class="item-fecha">Solicitud: {{ formatFecha(t.fecha_solicitud) }}</div>
              </div>
            </div>
            <div class="item-acciones">
              <button class="btn-primary" @click="aprobar(t.id)" :disabled="procesando === t.id">✅ Aprobar</button>
              <input v-model="motivos[t.id]" class="form-input" style="flex:1;padding:9px 12px"
                placeholder="Motivo de rechazo (opcional)" />
              <button class="btn-danger" @click="rechazar(t.id)" :disabled="procesando === t.id">❌ Rechazar</button>
            </div>
            <div v-if="mensajes[t.id]"
              :class="['alert', mensajes[t.id].tipo === 'exito' ? 'alert-success' : 'alert-error']"
              style="margin:12px 0 0">
              {{ mensajes[t.id].texto }}
            </div>
          </div>
        </div>
      </div>

      <!-- TRABAJADORES -->
      <div v-if="seccion === 'trabajadores'">
        <div class="admin-page-header">
          <h2>Trabajadores</h2>
          <p>{{ trabajadores.length }} técnicos registrados en la plataforma</p>
        </div>
        <div class="card tabla-card">
          <div class="tabla-header">
            <span>Técnico</span>
            <span>Oficio</span>
            <span>Categoría</span>
            <span>Estado</span>
            <span>Calificación</span>
            <span>Servicios</span>
          </div>
          <div v-for="t in trabajadores" :key="t.id" class="tabla-fila">
            <div class="tabla-persona">
              <div class="tabla-avatar" :style="{ background: getColor(t.id) }">{{ getIniciales(t.usuario.first_name,
                t.usuario.last_name) }}</div>
              <div>
                <div class="tabla-nombre">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="tabla-sub">{{ t.usuario.distrito }}</div>
              </div>
            </div>
            <span class="tabla-txt">{{ t.oficio }}</span>
            <span class="badge badge-blue">{{ t.categoria }}</span>
            <span :class="['badge', estadoBadgeT[t.estado]]">{{ t.estado }}</span>
            <span class="tabla-txt">⭐ {{ t.calificacion_promedio.toFixed(1) }}</span>
            <span class="tabla-txt">{{ t.num_calificaciones }}</span>
          </div>
        </div>
      </div>

      <!-- CLIENTES -->
      <div v-if="seccion === 'clientes'">
        <div class="admin-page-header">
          <h2>Clientes</h2>
          <p>{{ clientes.length }} clientes registrados en la plataforma</p>
        </div>
        <div class="card tabla-card">
          <div class="tabla-header tabla-header-5">
            <span>Cliente</span>
            <span>Usuario</span>
            <span>Correo</span>
            <span>Celular</span>
            <span>Distrito</span>
          </div>
          <div v-for="c in clientes" :key="c.id" class="tabla-fila tabla-fila-5">
            <div class="tabla-persona">
              <div class="tabla-avatar" style="background:#DBEAFE;color:#1D4ED8">{{ c.first_name?.[0] }}{{
                c.last_name?.[0] }}</div>
              <div>
                <div class="tabla-nombre">{{ c.first_name }} {{ c.last_name }}</div>
              </div>
            </div>
            <span class="tabla-txt">@{{ c.username }}</span>
            <span class="tabla-txt">{{ c.email || '—' }}</span>
            <span class="tabla-txt">{{ c.celular || '—' }}</span>
            <span class="tabla-txt">{{ c.distrito || '—' }}</span>
          </div>
        </div>
      </div>

      <!-- SOLICITUDES -->
      <div v-if="seccion === 'solicitudes'">
        <div class="admin-page-header">
          <h2>Todas las solicitudes</h2>
          <p>{{ todasSolicitudes.length }} solicitudes en total</p>
        </div>
        <div class="card tabla-card">
          <div class="tabla-header tabla-header-5">
            <span>Cliente</span>
            <span>Técnico</span>
            <span>Problema</span>
            <span>Estado</span>
            <span>Fecha</span>
          </div>
          <div v-for="s in todasSolicitudes" :key="s.id" class="tabla-fila tabla-fila-5">
            <span class="tabla-txt">{{ s.cliente.first_name }} {{ s.cliente.last_name }}</span>
            <span class="tabla-txt">{{ s.trabajador.usuario.first_name }} {{ s.trabajador.usuario.last_name }}</span>
            <span class="tabla-txt truncar">{{ s.descripcion_problema }}</span>
            <span :class="['badge', estadoBadge[s.estado]]">{{ estadoTexto[s.estado] }}</span>
            <span class="tabla-txt">{{ formatFecha(s.fecha_solicitud) }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const seccion = ref('dashboard')
const pendientes = ref<any[]>([])
const trabajadores = ref<any[]>([])
const clientes = ref<any[]>([])
const todasSolicitudes = ref<any[]>([])
const procesando = ref<number | null>(null)
const motivos = ref<any>({})
const mensajes = ref<any>({})

const stats = ref({ total_clientes: 0, total_trabajadores: 0, pendientes_aprobacion: 0, total_solicitudes: 0, solicitudes_completadas: 0, total_calificaciones: 0 })

const estadoTexto: any = { pendiente: '⏳ Pendiente', aceptado: '✅ Aceptado', en_progreso: '🔧 En progreso', completado: '✔ Completado', rechazado: '❌ Rechazado' }
const estadoBadge: any = { pendiente: 'badge-amber', aceptado: 'badge-green', en_progreso: 'badge-blue', completado: 'badge-green', rechazado: 'badge-red' }
const estadoBadgeT: any = { aprobado: 'badge-green', pendiente: 'badge-amber', rechazado: 'badge-red' }

function getIniciales(n: string, a: string) { return (n?.[0] || '') + (a?.[0] || '') }
function getColor(id: number) {
  const c = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return c[id % c.length]
}
function formatFecha(f: string) {
  return new Date(f).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function cargarTodo() {
  const [r1, r2, r3, r4] = await Promise.all([
    axios.get('http://127.0.0.1:8000/api/trabajadores/pendientes/'),
    axios.get('http://127.0.0.1:8000/api/admin/trabajadores/'),
    axios.get('http://127.0.0.1:8000/api/admin/solicitudes/'),
    axios.get('http://127.0.0.1:8000/api/admin/clientes/'),
  ])
  pendientes.value = r1.data
  trabajadores.value = r2.data
  todasSolicitudes.value = r3.data
  clientes.value = r4.data
  stats.value = {
    total_clientes: r4.data.length,
    total_trabajadores: r2.data.filter((t: any) => t.estado === 'aprobado').length,
    pendientes_aprobacion: r1.data.length,
    total_solicitudes: r3.data.length,
    solicitudes_completadas: r3.data.filter((s: any) => s.estado === 'completado').length,
    total_calificaciones: r2.data.reduce((a: number, t: any) => a + t.num_calificaciones, 0),
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
    const res = await axios.post(`http://127.0.0.1:8000/api/trabajadores/${id}/rechazar/`, { motivo: motivos.value[id] || 'Sin motivo' })
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
  min-height: calc(100vh - 64px);
}

.admin-sidebar {
  width: 240px;
  background: #0F172A;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-brand-icon {
  width: 36px;
  height: 36px;
  background: var(--primary);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.sidebar-brand-name {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.sidebar-brand-sub {
  font-size: 11px;
  color: #64748B;
  margin-top: 1px;
}

.sidebar-menu {
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: all 0.15s;
}

.menu-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.menu-btn.active {
  background: rgba(37, 99, 235, 0.2);
  color: #93C5FD;
}

.menu-icon {
  font-size: 16px;
}

.menu-badge {
  margin-left: auto;
  background: #EF4444;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 10px;
}

.admin-main {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg);
}

.admin-page-header {
  margin-bottom: 24px;
}

.admin-page-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
}

.admin-page-header p {
  font-size: 14px;
  color: var(--text2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
}

.stat-label {
  font-size: 12px;
  color: var(--text2);
}

.dashboard-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.recent-section {
  padding: 20px;
}

.recent-section h3 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 16px;
}

.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-name {
  font-size: 13px;
  font-weight: 600;
}

.recent-sub {
  font-size: 12px;
  color: var(--text2);
  margin-top: 2px;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text2);
  font-size: 13px;
}

.empty-full {
  text-align: center;
  padding: 64px;
  color: var(--text2);
}

.empty-full h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.lista {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.item-card {
  padding: 20px;
}

.item-top {
  display: flex;
  gap: 14px;
  margin-bottom: 16px;
}

.item-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.item-name {
  font-size: 15px;
  font-weight: 700;
}

.item-meta {
  font-size: 12px;
  color: var(--text2);
  margin-top: 3px;
}

.item-desc {
  font-size: 12px;
  color: var(--text2);
  font-style: italic;
  margin-top: 6px;
  background: var(--bg);
  padding: 6px 10px;
  border-radius: 6px;
}

.item-fecha {
  font-size: 11px;
  color: var(--text3);
  margin-top: 6px;
}

.item-acciones {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}

.tabla-card {
  overflow: hidden;
}

.tabla-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr 1fr;
  padding: 12px 20px;
  background: var(--bg);
  font-size: 11px;
  font-weight: 600;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
  gap: 12px;
}

.tabla-header-5 {
  grid-template-columns: 2fr 1fr 2fr 1fr 1fr;
}

.tabla-fila {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr 1fr;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  gap: 12px;
  align-items: center;
}

.tabla-fila-5 {
  grid-template-columns: 2fr 1fr 2fr 1fr 1fr;
}

.tabla-fila:last-child {
  border-bottom: none;
}

.tabla-fila:hover {
  background: var(--bg);
}

.tabla-persona {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tabla-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.tabla-nombre {
  font-size: 13px;
  font-weight: 600;
}

.tabla-sub {
  font-size: 11px;
  color: var(--text2);
}

.tabla-txt {
  font-size: 13px;
  color: var(--text2);
}

.truncar {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>