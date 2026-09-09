<template>
  <div class="admin">
    <div class="admin-sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🔧</div>
        <div>
          <div class="sidebar-brand-name">Llankay</div>
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
        <button :class="['menu-btn', seccion === 'requerimientos' ? 'active' : '']" @click="seccion = 'requerimientos'">
          <span class="menu-icon">📌</span> Oficios Solicitados
          <span v-if="requerimientosPendientes.length" class="menu-badge badge-amber-solid">{{ requerimientosPendientes.length }}</span>
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
          <div>
            <h2>Dashboard</h2>
            <p>Resumen general de la plataforma</p>
          </div>
          <div class="header-export-actions">
            <button class="btn-primary btn-sm" @click="poblarDatosDemostracion" :disabled="poblandoDemo">
              ⚡ {{ poblandoDemo ? 'Cargando datos...' : 'Poblar Técnicos Demo' }}
            </button>
            <button class="btn-secondary btn-sm" @click="exportarTecnicosCSV">
              📊 Exportar Técnicos (CSV)
            </button>
            <button class="btn-secondary btn-sm" @click="exportarSolicitudesCSV">
              📊 Exportar Solicitudes (CSV)
            </button>
            <button class="btn-secondary btn-sm" @click="exportarRequerimientosCSV">
              📌 Exportar Oficios Solicitados (CSV)
            </button>
          </div>
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
            <div class="stat-icon" style="background:#FEF3C7;color:#B45309">📌</div>
            <div class="stat-num">{{ requerimientos.length }}</div>
            <div class="stat-label">Oficios solicitados ({{ requerimientosPendientes.length }} pend.)</div>
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
        </div>

        <div class="dashboard-bottom">
          <div class="card recent-section">
            <h3>Últimos oficios no listados solicitados</h3>
            <div v-if="requerimientos.length === 0" class="empty-state">✅ No hay requerimientos registrados</div>
            <div v-for="r in requerimientos.slice(0, 4)" :key="'req-' + r.id" class="recent-item">
              <div class="recent-info">
                <div class="recent-name"><strong>{{ r.oficio_solicitado }}</strong> · {{ r.nombre_contacto }}</div>
                <div class="recent-sub">📍 {{ r.distrito }} · {{ r.celular_contacto }}</div>
              </div>
              <span :class="['badge', estadoBadgeReq[r.estado]]">{{ estadoTextoReq[r.estado] }}</span>
            </div>
          </div>

          <div class="card recent-section">
            <h3>Solicitudes pendientes de técnicos</h3>
            <div v-if="pendientes.length === 0" class="empty-state">✅ No hay técnicos pendientes de aprobación</div>
            <div v-for="t in pendientes.slice(0, 4)" :key="t.id" class="recent-item">
              <div class="recent-info">
                <div class="recent-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="recent-sub">{{ t.oficio }} ({{ t.categoria }})</div>
              </div>
              <button class="btn-primary btn-sm" @click="aprobar(t.id)">Aprobar</button>
            </div>
          </div>
        </div>
      </div>

      <!-- SECCIÓN: OFICIOS SOLICITADOS / REQUERIMIENTOS ESPECIALES -->
      <div v-if="seccion === 'requerimientos'">
        <div class="admin-page-header">
          <div>
            <h2>📌 Oficios y Especialistas Solicitados</h2>
            <p>Requerimientos de clientes registrados que no encontraron el oficio en el catálogo</p>
          </div>
          <button class="btn-secondary btn-sm" @click="exportarRequerimientosCSV">
            📊 Exportar Requerimientos (CSV)
          </button>
        </div>

        <!-- FILTROS Y BÚSQUEDA -->
        <div class="filtros-requerimientos-bar card">
          <div class="req-pills">
            <button 
              :class="['req-pill', filtroReq === 'todos' ? 'active' : '']" 
              @click="filtroReq = 'todos'"
            >
              Todos ({{ requerimientos.length }})
            </button>
            <button 
              :class="['req-pill', filtroReq === 'pendiente' ? 'active' : '']" 
              @click="filtroReq = 'pendiente'"
            >
              ⏳ Pendientes ({{ requerimientos.filter(r => r.estado === 'pendiente').length }})
            </button>
            <button 
              :class="['req-pill', filtroReq === 'contactado' ? 'active' : '']" 
              @click="filtroReq = 'contactado'"
            >
              📞 Contactados ({{ requerimientos.filter(r => r.estado === 'contactado').length }})
            </button>
            <button 
              :class="['req-pill', filtroReq === 'asignado' ? 'active' : '']" 
              @click="filtroReq = 'asignado'"
            >
              👷 Asignados ({{ requerimientos.filter(r => r.estado === 'asignado').length }})
            </button>
            <button 
              :class="['req-pill', filtroReq === 'atendido' ? 'active' : '']" 
              @click="filtroReq = 'atendido'"
            >
              ✔ Atendidos ({{ requerimientos.filter(r => r.estado === 'atendido').length }})
            </button>
          </div>

          <div class="req-search">
            <input 
              v-model="busquedaReq" 
              type="text" 
              class="form-input search-req-input" 
              placeholder="Buscar por cliente, celular, oficio o distrito..."
            />
          </div>
        </div>

        <div v-if="requerimientosFiltrados.length === 0" class="card empty-card" style="margin-top: 20px;">
          <div style="font-size: 40px; margin-bottom: 8px;">📭</div>
          <h3>No hay requerimientos en este filtro</h3>
          <p>Los pedidos registrados por clientes aparecerán aquí en tiempo real.</p>
        </div>

        <div v-else class="lista req-lista" style="margin-top: 20px;">
          <div v-for="r in requerimientosFiltrados" :key="'req-card-' + r.id" class="card req-card">
            <div class="req-card-top">
              <div class="req-cliente-info">
                <div class="req-avatar">{{ getIniciales(r.nombre_contacto) }}</div>
                <div>
                  <div class="req-nombre-row">
                    <span class="req-cliente-nombre">{{ r.nombre_contacto }}</span>
                    <span v-if="r.cliente" class="req-user-badge">@{{ r.cliente.username }}</span>
                    <span class="req-fecha">{{ formatFechaCompleta(r.fecha_creacion) }}</span>
                  </div>
                  <div class="req-sub-info">
                    <span>📍 Distrito: <strong>{{ r.distrito }}</strong></span>
                    <span>·</span>
                    <span>📞 Celular: <strong>{{ r.celular_contacto }}</strong></span>
                  </div>
                </div>
              </div>

              <div class="req-estado-control">
                <label class="req-estado-label">Estado:</label>
                <select 
                  :value="r.estado" 
                  :class="['form-select', 'req-estado-select', estadoBadgeReq[r.estado]]"
                  @change="cambiarEstadoRequerimiento(r.id, ($event.target as HTMLSelectElement).value)"
                  :disabled="guardandoReq === r.id"
                >
                  <option value="pendiente">⏳ Pendiente</option>
                  <option value="contactado">📞 Contactado</option>
                  <option value="asignado">👷 Técnico asignado</option>
                  <option value="atendido">✔ Atendido / Completado</option>
                  <option value="cancelado">❌ Cancelado</option>
                </select>
              </div>
            </div>

            <!-- DETALLE DEL OFICIO SOLICITADO -->
            <div class="req-body">
              <div class="req-oficio-badge">
                <span class="req-tag-label">Oficio requerido:</span>
                <span class="req-oficio-title">🛠️ {{ r.oficio_solicitado }}</span>
              </div>
              <p v-if="r.descripcion" class="req-descripcion-box">
                {{ r.descripcion }}
              </p>
              <p v-else class="req-sin-desc">Sin descripción adicional.</p>
            </div>

            <!-- ACCIONES DE CONTACTO Y NOTAS ADMIN -->
            <div class="req-footer">
              <div class="req-actions-btns">
                <a 
                  :href="`https://wa.me/51${r.celular_contacto.replace(/\D/g, '')}?text=Hola%20${encodeURIComponent(r.nombre_contacto)},%20te%20escribimos%20de%20Llankay%20respecto%20a%20tu%20solicitud%20para%20un%20servicio%20de%20${encodeURIComponent(r.oficio_solicitado)}%20en%20${encodeURIComponent(r.distrito)}.`" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="btn-whatsapp-sm"
                >
                  💬 Contactar por WhatsApp
                </a>
                <a :href="`tel:${r.celular_contacto}`" class="btn-secondary btn-sm">
                  📞 Llamar ({{ r.celular_contacto }})
                </a>
              </div>

              <!-- NOTAS DE SEGUIMIENTO INTERNAS DEL ADMIN -->
              <div class="req-notas-wrap">
                <input 
                  v-model="notasTemp[r.id]" 
                  type="text" 
                  class="form-input input-notas" 
                  placeholder="Nota interna (ej: Se derivó a técnico Juan en San Sebastián)..." 
                  @keydown.enter="guardarNotas(r.id)"
                />
                <button 
                  class="btn-secondary btn-sm" 
                  @click="guardarNotas(r.id)" 
                  :disabled="guardandoReq === r.id"
                >
                  Guardar nota
                </button>
              </div>
            </div>

            <div v-if="msgReq[r.id]" :class="['alert', msgReq[r.id]?.tipo === 'exito' ? 'alert-success' : 'alert-error']" style="margin-top: 10px;">
              {{ msgReq[r.id]?.texto }}
            </div>
          </div>
        </div>
      </div>

      <!-- PENDIENTES DE APROBACIÓN (TÉCNICOS) -->
      <div v-if="seccion === 'pendientes'">
        <div class="admin-page-header">
          <h2>Técnicos pendientes de validación</h2>
          <p>{{ pendientes.length }} técnicos esperando verificación</p>
        </div>
        <div v-if="pendientes.length === 0" class="card empty-card">
          <div style="font-size:44px;margin-bottom:12px">✅</div>
          <h3>¡Todo al día!</h3>
          <p>No hay técnicos pendientes de revisión en este momento.</p>
        </div>
        <div v-else class="lista">
          <div v-for="t in pendientes" :key="t.id" class="card item-card">
            <div class="item-top">
              <div class="item-avatar" :style="{ background: getColor(t.id) }">
                {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
              </div>
              <div>
                <div class="item-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                <div class="item-meta">
                  <span>@{{ t.usuario.username }}</span> ·
                  <span>📞 {{ t.usuario.celular }}</span> ·
                  <span>📍 {{ t.usuario.distrito }}</span> ·
                  <span class="badge badge-blue">{{ t.categoria }}</span>
                </div>
                <div class="item-desc"><strong>Oficio:</strong> {{ t.oficio }} — <strong>Experiencia:</strong> {{ t.experiencia }}</div>
                <div v-if="t.descripcion" class="item-desc">{{ t.descripcion }}</div>
                <div class="item-fecha">Registrado el {{ formatFecha(t.fecha_solicitud) }}</div>
              </div>
            </div>

            <div class="item-acciones">
              <button class="btn-primary btn-sm" @click="aprobar(t.id)" :disabled="procesando === t.id">
                ✔ Aprobar técnico
              </button>
              <input v-model="motivos[t.id]" class="form-input" placeholder="Motivo de rechazo (opcional)" style="flex:1;max-width:300px" />
              <button class="btn-danger btn-sm" @click="rechazar(t.id)" :disabled="procesando === t.id">
                ✖ Rechazar
              </button>
            </div>
            <div v-if="mensajes[t.id]" :class="['alert', mensajes[t.id]?.tipo === 'exito' ? 'alert-success' : 'alert-error']" style="margin-top:12px">
              {{ mensajes[t.id]?.texto }}
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
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import type { Trabajador, Usuario, Solicitud, AdminStats, EstadoSolicitud, EstadoTrabajador, RequerimientoOficio, EstadoRequerimiento } from '../types'

const seccion = ref('dashboard')
const pendientes = ref<Trabajador[]>([])
const trabajadores = ref<Trabajador[]>([])
const clientes = ref<Usuario[]>([])
const todasSolicitudes = ref<Solicitud[]>([])
const requerimientos = ref<RequerimientoOficio[]>([])
const procesando = ref<number | null>(null)
const guardandoReq = ref<number | null>(null)
const motivos = ref<Record<number, string>>({})
const mensajes = ref<Record<number, { tipo: 'exito' | 'error'; texto: string }>>({})
const msgReq = ref<Record<number, { tipo: 'exito' | 'error'; texto: string }>>({})
const notasTemp = ref<Record<number, string>>({})

const filtroReq = ref<string>('todos')
const busquedaReq = ref<string>('')
const poblandoDemo = ref(false)

async function poblarDatosDemostracion() {
  if (!confirm('¿Deseas poblar la base de datos con los 14 técnicos cusqueños de demostración y sus calificaciones?')) return
  poblandoDemo.value = true
  try {
    const res = await api.post<{ mensaje: string; total_trabajadores: number }>('/trabajadores/poblar-demo/?secret=llankay2026demo')
    alert(res.data.mensaje || '¡Datos de demostración cargados exitosamente!')
    await cargarTodo()
  } catch (err: any) {
    alert(err.response?.data?.error || 'Error al poblar datos de demostración.')
  } finally {
    poblandoDemo.value = false
  }
}

const requerimientosPendientes = computed(() => {
  return requerimientos.value.filter(r => r.estado === 'pendiente')
})

const requerimientosFiltrados = computed(() => {
  return requerimientos.value.filter(r => {
    const coincideEstado = filtroReq.value === 'todos' || r.estado === filtroReq.value
    const term = busquedaReq.value.toLowerCase().trim()
    const coincideBusqueda = !term || 
      r.nombre_contacto.toLowerCase().includes(term) ||
      r.celular_contacto.includes(term) ||
      r.oficio_solicitado.toLowerCase().includes(term) ||
      r.distrito.toLowerCase().includes(term) ||
      (r.cliente?.username && r.cliente.username.toLowerCase().includes(term))
    return coincideEstado && coincideBusqueda
  })
})

const stats = ref<AdminStats>({
  total_clientes: 0,
  total_trabajadores: 0,
  pendientes_aprobacion: 0,
  total_solicitudes: 0,
  solicitudes_completadas: 0,
  total_calificaciones: 0
})

const estadoTexto: Record<EstadoSolicitud, string> = {
  pendiente: '⏳ Pendiente',
  aceptado: '✅ Aceptado',
  en_progreso: '🔧 En progreso',
  completado: '✔ Completado',
  rechazado: '❌ Rechazado'
}
const estadoBadge: Record<EstadoSolicitud, string> = {
  pendiente: 'badge-amber',
  aceptado: 'badge-green',
  en_progreso: 'badge-blue',
  completado: 'badge-green',
  rechazado: 'badge-red'
}
const estadoBadgeT: Record<EstadoTrabajador, string> = {
  aprobado: 'badge-green',
  pendiente: 'badge-amber',
  rechazado: 'badge-red'
}

const estadoTextoReq: Record<EstadoRequerimiento, string> = {
  pendiente: '⏳ Pendiente',
  contactado: '📞 Contactado',
  asignado: '👷 Técnico asignado',
  atendido: '✔ Atendido / Completado',
  cancelado: '❌ Cancelado'
}

const estadoBadgeReq: Record<EstadoRequerimiento, string> = {
  pendiente: 'badge-amber',
  contactado: 'badge-blue',
  asignado: 'badge-purple',
  atendido: 'badge-green',
  cancelado: 'badge-gray'
}

function getIniciales(n?: string, a?: string) {
  if (!n) return 'TC'
  return (n[0] || '') + (a?.[0] || '')
}

function getColor(id: number) {
  const c = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return c[id % c.length]
}

function formatFecha(f: string) {
  return new Date(f).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatFechaCompleta(f: string) {
  return new Date(f).toLocaleDateString('es-PE', { 
    day: 'numeric', 
    month: 'short', 
    year: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

async function cargarTodo() {
  try {
    const [r1, r2, r3, r4, r5] = await Promise.all([
      api.get<Trabajador[]>('/trabajadores/pendientes/'),
      api.get<Trabajador[]>('/admin/trabajadores/'),
      api.get<Solicitud[]>('/admin/solicitudes/'),
      api.get<Usuario[]>('/admin/clientes/'),
      api.get<RequerimientoOficio[]>('/solicitudes/requerimientos/admin/'),
    ])
    pendientes.value = r1.data
    trabajadores.value = r2.data
    todasSolicitudes.value = r3.data
    clientes.value = r4.data
    requerimientos.value = r5.data

    // Inicializar notas temporales
    r5.data.forEach(r => {
      notasTemp.value[r.id] = r.notas_admin || ''
    })

    stats.value = {
      total_clientes: r4.data.length,
      total_trabajadores: r2.data.filter((t) => t.estado === 'aprobado').length,
      pendientes_aprobacion: r1.data.length,
      total_solicitudes: r3.data.length,
      solicitudes_completadas: r3.data.filter((s) => s.estado === 'completado').length,
      total_calificaciones: r2.data.reduce((a, t) => a + (t.num_calificaciones || 0), 0),
    }
  } catch (err) {
    console.error('Error al cargar datos de administración:', err)
  }
}

async function cambiarEstadoRequerimiento(id: number, nuevoEstado: string) {
  guardandoReq.value = id
  msgReq.value[id] = { tipo: 'exito', texto: 'Actualizando estado...' }
  try {
    const res = await api.patch<{ mensaje: string; requerimiento: RequerimientoOficio }>(
      `/solicitudes/requerimientos/admin/${id}/`, 
      { estado: nuevoEstado }
    )
    const idx = requerimientos.value.findIndex(r => r.id === id)
    if (idx !== -1) {
      requerimientos.value[idx] = res.data.requerimiento
    }
    msgReq.value[id] = { tipo: 'exito', texto: '✅ Estado actualizado.' }
    setTimeout(() => { delete msgReq.value[id] }, 3000)
  } catch (e: any) {
    msgReq.value[id] = { tipo: 'error', texto: e.response?.data?.error || 'Error al actualizar estado.' }
  } finally {
    guardandoReq.value = null
  }
}

async function guardarNotas(id: number) {
  guardandoReq.value = id
  try {
    const res = await api.patch<{ mensaje: string; requerimiento: RequerimientoOficio }>(
      `/solicitudes/requerimientos/admin/${id}/`, 
      { notas_admin: notasTemp.value[id] || '' }
    )
    const idx = requerimientos.value.findIndex(r => r.id === id)
    if (idx !== -1) {
      requerimientos.value[idx] = res.data.requerimiento
    }
    msgReq.value[id] = { tipo: 'exito', texto: '✅ Nota guardada.' }
    setTimeout(() => { delete msgReq.value[id] }, 3000)
  } catch (e: any) {
    msgReq.value[id] = { tipo: 'error', texto: e.response?.data?.error || 'Error al guardar nota.' }
  } finally {
    guardandoReq.value = null
  }
}

async function aprobar(id: number) {
  procesando.value = id
  try {
    const res = await api.post<{ mensaje: string }>(`/trabajadores/${id}/aprobar/`)
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarTodo()
  } catch {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al aprobar al técnico' }
  } finally {
    procesando.value = null
  }
}

async function rechazar(id: number) {
  procesando.value = id
  try {
    const res = await api.post<{ mensaje: string }>(`/trabajadores/${id}/rechazar/`, {
      motivo: motivos.value[id] || 'Sin motivo'
    })
    mensajes.value[id] = { tipo: 'exito', texto: res.data.mensaje }
    await cargarTodo()
  } catch {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al rechazar al técnico' }
  } finally {
    procesando.value = null
  }
}

function descargarCSV(nombreArchivo: string, contenidoCSV: string) {
  const blob = new Blob(['\uFEFF' + contenidoCSV], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', nombreArchivo)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function exportarTecnicosCSV() {
  const encabezados = ['ID', 'Nombre', 'Apellido', 'Usuario', 'Email', 'Celular', 'Distrito', 'Categoría', 'Oficio', 'Experiencia', 'Calificación', 'Num Reseñas', 'Disponible', 'Estado', 'Fecha Registro']
  const filas = trabajadores.value.map(t => [
    t.id,
    `"${t.usuario.first_name}"`,
    `"${t.usuario.last_name}"`,
    `"${t.usuario.username}"`,
    `"${t.usuario.email || ''}"`,
    `"${t.usuario.celular || ''}"`,
    `"${t.usuario.distrito || ''}"`,
    `"${t.categoria}"`,
    `"${t.oficio}"`,
    `"${t.experiencia}"`,
    t.calificacion_promedio,
    t.num_calificaciones,
    t.disponible ? 'Sí' : 'No',
    t.estado,
    formatFecha(t.fecha_solicitud)
  ])
  const csv = [encabezados.join(','), ...filas.map(f => f.join(','))].join('\n')
  descargarCSV(`tecnicos_llankay_${new Date().toISOString().slice(0,10)}.csv`, csv)
}

function exportarSolicitudesCSV() {
  const encabezados = ['ID', 'Cliente', 'Celular Cliente', 'Técnico', 'Oficio Técnico', 'Categoría', 'Dirección', 'Estado', 'Precio Acordado (S/)', 'Método Pago', 'Fecha Solicitud']
  const filas = todasSolicitudes.value.map(s => [
    s.id,
    `"${s.cliente.first_name} ${s.cliente.last_name}"`,
    `"${s.cliente.celular || ''}"`,
    `"${s.trabajador.usuario.first_name} ${s.trabajador.usuario.last_name}"`,
    `"${s.trabajador.oficio}"`,
    `"${s.trabajador.categoria}"`,
    `"${s.direccion}"`,
    s.estado,
    s.precio_acordado ? Number(s.precio_acordado).toFixed(2) : '0.00',
    `"${s.metodo_pago || 'Efectivo'}"`,
    formatFecha(s.fecha_solicitud)
  ])
  const csv = [encabezados.join(','), ...filas.map(f => f.join(','))].join('\n')
  descargarCSV(`solicitudes_llankay_${new Date().toISOString().slice(0,10)}.csv`, csv)
}

function exportarRequerimientosCSV() {
  const encabezados = ['ID', 'Oficio Requerido', 'Nombre Contacto', 'Celular', 'Distrito', 'Usuario Registrado', 'Estado', 'Descripción Requerimiento', 'Notas Admin', 'Fecha Registro']
  const filas = requerimientos.value.map(r => [
    r.id,
    `"${r.oficio_solicitado}"`,
    `"${r.nombre_contacto}"`,
    `"${r.celular_contacto}"`,
    `"${r.distrito}"`,
    `"${r.cliente ? r.cliente.username : 'N/A'}"`,
    r.estado,
    `"${(r.descripcion || '').replace(/"/g, '""')}"`,
    `"${(r.notas_admin || '').replace(/"/g, '""')}"`,
    formatFechaCompleta(r.fecha_creacion)
  ])
  const csv = [encabezados.join(','), ...filas.map(f => f.join(','))].join('\n')
  descargarCSV(`oficios_solicitados_llankay_${new Date().toISOString().slice(0,10)}.csv`, csv)
}

onMounted(() => cargarTodo())
</script>

<style scoped>
.header-export-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 700;
}

.admin {
  display: flex;
  min-height: calc(100vh - 68px);
}

.admin-sidebar {
  width: 250px;
  background: #090D16;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
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
  width: 38px;
  height: 38px;
  background: var(--primary-gradient);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.sidebar-brand-name {
  font-size: 15px;
  font-weight: 800;
  color: #fff;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.sidebar-brand-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.sidebar-menu {
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: all 0.2s ease;
}

.menu-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.menu-btn.active {
  background: var(--primary);
  color: #fff;
  font-weight: 700;
}

.menu-icon {
  font-size: 16px;
}

.menu-badge {
  margin-left: auto;
  background: #EF4444;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 9999px;
}

.badge-amber-solid {
  background: #F59E0B !important;
}

.badge-purple {
  background: #EDE9FE;
  color: #6D28D9;
}

.admin-main {
  flex: 1;
  padding: 36px 40px;
  overflow-y: auto;
  max-width: 1200px;
}

.admin-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.admin-page-header h2 {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 4px;
}

.admin-page-header p {
  color: var(--text2);
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 4px;
}

.stat-num {
  font-size: 28px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.stat-label {
  font-size: 12.5px;
  color: var(--text2);
  font-weight: 500;
}

.dashboard-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .dashboard-bottom {
    grid-template-columns: 1fr;
  }
}

.recent-section {
  padding: 24px;
}

.recent-section h3 {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 18px;
}

.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  gap: 12px;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-info {
  flex: 1;
  min-width: 0;
}

.recent-name {
  font-size: 13.5px;
  font-weight: 700;
}

.recent-sub {
  font-size: 12px;
  color: var(--text2);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-state {
  color: var(--text3);
  font-size: 13.5px;
  text-align: center;
  padding: 20px 0;
}

/* ======================================================== */
/* ESTILOS DE LA SECCIÓN OFICIOS SOLICITADOS               */
/* ======================================================== */
.filtros-requerimientos-bar {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.req-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.req-pill {
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface-subtle);
  color: var(--text2);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.req-pill:hover {
  background: var(--surface);
  color: var(--text);
}

.req-pill.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.req-search {
  flex: 1;
  min-width: 260px;
  max-width: 380px;
}

.search-req-input {
  height: 38px;
  font-size: 13px;
}

.req-lista {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.req-card {
  padding: 22px;
  border: 1px solid var(--border);
}

.req-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.req-cliente-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.req-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  flex-shrink: 0;
}

.req-nombre-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.req-cliente-nombre {
  font-size: 15.5px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.req-user-badge {
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
  background: var(--primary-light);
  padding: 1px 6px;
  border-radius: 4px;
}

.req-fecha {
  font-size: 12px;
  color: var(--text3);
  margin-left: 4px;
}

.req-sub-info {
  display: flex;
  gap: 8px;
  font-size: 13px;
  color: var(--text2);
  margin-top: 3px;
}

.req-estado-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.req-estado-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text2);
}

.req-estado-select {
  padding: 6px 12px;
  font-size: 12.5px;
  font-weight: 700;
  border-radius: var(--radius-sm);
}

.req-body {
  padding: 16px 0;
}

.req-oficio-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.req-tag-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
}

.req-oficio-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--primary);
}

.req-descripcion-box {
  background: var(--surface-subtle);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  font-size: 13.5px;
  color: var(--text);
  line-height: 1.55;
  margin: 0;
}

.req-sin-desc {
  font-size: 13px;
  color: var(--text3);
  font-style: italic;
  margin: 0;
}

.req-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}

.req-actions-btns {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-whatsapp-sm {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #25D366;
  color: #fff;
  text-decoration: none;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 12.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.btn-whatsapp-sm:hover {
  background: #20BA5A;
}

.req-notas-wrap {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
  max-width: 460px;
}

.input-notas {
  height: 36px;
  font-size: 12.5px;
}

/* ======================================================== */
/* ESTILOS COMUNES DE TABLAS Y TARJETAS                    */
/* ======================================================== */
.lista {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.item-card {
  padding: 24px;
}

.item-top {
  display: flex;
  gap: 16px;
  margin-bottom: 18px;
}

.item-avatar {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.item-name {
  font-size: 16px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.item-meta {
  font-size: 13px;
  color: var(--text2);
  margin-top: 3px;
}

.item-desc {
  font-size: 13px;
  color: var(--text2);
  margin-top: 8px;
  background: var(--surface-subtle);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
}

.item-fecha {
  font-size: 11.5px;
  color: var(--text3);
  margin-top: 6px;
}

.item-acciones {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.tabla-card {
  overflow: hidden;
}

.tabla-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr 1fr;
  padding: 14px 24px;
  background: var(--surface-subtle);
  font-size: 11px;
  font-weight: 700;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
  gap: 14px;
}

.tabla-header-5 {
  grid-template-columns: 2fr 1fr 2fr 1fr 1fr;
}

.tabla-fila {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr 1fr;
  padding: 14px 24px;
  border-bottom: 1px solid var(--border);
  font-size: 13.5px;
  gap: 14px;
  align-items: center;
  transition: background 0.15s ease;
}

.tabla-fila-5 {
  grid-template-columns: 2fr 1fr 2fr 1fr 1fr;
}

.tabla-fila:last-child {
  border-bottom: none;
}

.tabla-fila:hover {
  background: var(--surface-subtle);
}

.tabla-persona {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tabla-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
}

.tabla-nombre {
  font-size: 13.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.tabla-sub {
  font-size: 11.5px;
  color: var(--text3);
}

.tabla-txt {
  font-size: 13.5px;
  color: var(--text2);
}

.truncar {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>