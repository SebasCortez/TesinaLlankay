<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-inner">
        <h1>Centro de Solicitudes</h1>
        <p>Gestiona tus servicios contratados y los trabajos solicitados por tus clientes</p>

        <!-- TABS DE SOLICITUDES -->
        <div v-if="auth.esTrabajador" class="sol-tabs">
          <button
            :class="['sol-tab-btn', tabActiva === 'enviadas' ? 'activo' : '']"
            @click="cambiarTab('enviadas')"
          >
            📤 Servicios que he solicitado ({{ totalEnviadas }})
          </button>
          <button
            :class="['sol-tab-btn', tabActiva === 'recibidas' ? 'activo' : '']"
            @click="cambiarTab('recibidas')"
          >
            📥 Trabajos recibidos de clientes ({{ totalRecibidas }})
          </button>
        </div>
      </div>
    </div>

    <div class="contenedor">
      <div v-if="cargando" class="estado">
        <div class="spinner"></div>
        <p>Cargando solicitudes...</p>
      </div>

      <div v-else-if="solicitudes.length === 0" class="estado">
        <div style="font-size:48px;margin-bottom:16px">📋</div>
        <h3>No hay solicitudes en esta sección</h3>
        <p v-if="tabActiva === 'enviadas'">Busca un técnico en Cusco y envía tu primera solicitud de servicio.</p>
        <p v-else>Aún no has recibido solicitudes de clientes. Asegúrate de estar disponible en tu perfil.</p>
        <router-link v-if="tabActiva === 'enviadas'" to="/buscar" class="btn-primary" style="margin-top:16px">
          Buscar técnicos en el mapa
        </router-link>
      </div>

      <div v-else class="lista">
        <div v-for="s in solicitudes" :key="s.id" class="solicitud-card card">
          <div class="sol-header">
            <div class="sol-persona">
              <div class="sol-avatar">
                <span v-if="tabActiva === 'enviadas'">
                  {{ s.trabajador.usuario.first_name?.[0] || 'T' }}{{ s.trabajador.usuario.last_name?.[0] || '' }}
                </span>
                <span v-else>
                  {{ s.cliente.first_name?.[0] || 'C' }}{{ s.cliente.last_name?.[0] || '' }}
                </span>
              </div>
              <div>
                <div class="sol-nombre" v-if="tabActiva === 'enviadas'">
                  {{ s.trabajador.usuario.first_name }} {{ s.trabajador.usuario.last_name }}
                  <span class="rep-badge">⭐ {{ s.trabajador.calificacion_promedio.toFixed(1) }} ({{ s.trabajador.num_calificaciones }})</span>
                </div>
                <div class="sol-nombre" v-else>
                  {{ s.cliente.first_name }} {{ s.cliente.last_name }}
                  <span v-if="s.cliente.reputacion_promedio" class="rep-badge">⭐ {{ s.cliente.reputacion_promedio }} ({{ s.cliente.num_calificaciones }} reseñas)</span>
                  <span v-else class="rep-badge rep-nuevo">⭐ Nuevo cliente</span>
                </div>
                <div class="sol-sub" v-if="tabActiva === 'enviadas'">
                  {{ s.trabajador.oficio }} ({{ s.trabajador.categoria }})
                </div>
                <div class="sol-sub" v-else>
                  📞 {{ s.cliente.celular || 'Sin celular' }} · 📍 {{ s.cliente.distrito || 'Cusco' }}
                </div>
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
              <span class="sol-label">Descripción del Problema</span>
              <p>{{ s.descripcion_problema }}</p>
            </div>
            <div class="sol-campo">
              <span class="sol-label">Dirección del Servicio</span>
              <p>📍 {{ s.direccion }}</p>
            </div>

            <!-- TARJETA DE COTIZACIÓN / PRESUPUESTO -->
            <div class="cotizacion-card" v-if="s.precio_acordado || editandoPresupuesto === s.id">
              <div class="cotizacion-header">
                <span class="cotizacion-title">💰 Presupuesto & Cotización</span>
                <button
                  v-if="tabActiva === 'recibidas' && editandoPresupuesto !== s.id"
                  class="btn-text-sm"
                  @click="iniciarEdicionPresupuesto(s)"
                >
                  ✏️ Modificar
                </button>
              </div>

              <!-- Vista de lectura -->
              <div v-if="editandoPresupuesto !== s.id" class="cotizacion-val-row">
                <div class="cotizacion-monto">
                  S/ {{ Number(s.precio_acordado).toFixed(2) }}
                </div>
                <div class="cotizacion-pago-badge" :class="`pago-${s.metodo_pago?.toLowerCase()}`">
                  {{ getMetodoPagoIcono(s.metodo_pago) }} {{ s.metodo_pago || 'Efectivo' }}
                </div>
              </div>

              <!-- Formulario de edición (Técnico) -->
              <div v-else class="cotizacion-form">
                <div class="cotizacion-inputs">
                  <div class="input-monto-wrap">
                    <span class="prefix">S/</span>
                    <input
                      v-model="formPresupuesto.precio"
                      class="form-input"
                      type="number"
                      step="5"
                      min="0"
                      placeholder="Monto acordado"
                    />
                  </div>
                  <select v-model="formPresupuesto.metodo" class="form-select">
                    <option value="Yape">💜 Yape</option>
                    <option value="Plin">💙 Plin</option>
                    <option value="Efectivo">💵 Efectivo</option>
                    <option value="Transferencia">🏦 Transferencia</option>
                  </select>
                </div>
                <div class="cotizacion-actions">
                  <button class="btn-secondary btn-sm" @click="editandoPresupuesto = null">Cancelar</button>
                  <button class="btn-primary btn-sm" @click="guardarPresupuesto(s.id)">Guardar cotización</button>
                </div>
              </div>
            </div>

            <!-- Botón para añadir presupuesto si es técnico y no tiene -->
            <div v-else-if="tabActiva === 'recibidas' && !s.precio_acordado" class="add-cotizacion-box">
              <button class="btn-secondary btn-sm" @click="iniciarEdicionPresupuesto(s)">
                ➕ Añadir presupuesto / precio acordado
              </button>
            </div>

            <div v-if="s.motivo_rechazo" class="sol-campo">
              <span class="sol-label">Motivo de Rechazo</span>
              <p class="txt-red">{{ s.motivo_rechazo }}</p>
            </div>
          </div>

          <div class="sol-footer">
            <span class="sol-fecha">Solicitado el: {{ formatFecha(s.fecha_solicitud) }}</span>

            <!-- ACCIONES PARA EL TÉCNICO (TRABAJOS RECIBIDOS) -->
            <div v-if="tabActiva === 'recibidas'" class="sol-acciones">
              <div v-if="s.estado === 'pendiente'" style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="btn-primary" @click="cambiarEstado(s.id, 'aceptado')" :disabled="procesando === s.id">
                  ✅ Aceptar trabajo
                </button>
                <div style="display:flex;gap:6px">
                  <input v-model="motivos[s.id]" class="form-input" style="width:190px;padding:8px 12px;font-size:13px;"
                    placeholder="Motivo de rechazo..." />
                  <button class="btn-danger" @click="cambiarEstado(s.id, 'rechazado', motivos[s.id])"
                    :disabled="procesando === s.id">
                    ❌ Rechazar
                  </button>
                </div>
              </div>
              <button v-if="s.estado === 'aceptado'" class="btn-primary" style="background:#7C3AED"
                @click="cambiarEstado(s.id, 'en_progreso')" :disabled="procesando === s.id">
                🔧 Marcar en progreso
              </button>
              <button v-if="s.estado === 'en_progreso'" class="btn-primary" @click="cambiarEstado(s.id, 'completado')"
                :disabled="procesando === s.id">
                ✔ Marcar completado
              </button>
              <div v-if="s.estado === 'completado'">
                <span v-if="s.ha_calificado_cliente" class="badge badge-green">
                  ✔ Calificaste al cliente
                </span>
                <button v-else class="btn-primary btn-sm btn-calificar" @click="abrirModalCalificar(s, 'cliente')">
                  ⭐ Calificar al cliente
                </button>
              </div>
            </div>

            <!-- ACCIONES PARA EL CLIENTE (SERVICIOS SOLICITADOS) -->
            <div v-if="tabActiva === 'enviadas' && s.estado === 'completado'">
              <span v-if="s.ha_calificado_trabajador" class="badge badge-green">
                ✔ Calificaste al técnico
              </span>
              <button v-else class="btn-primary btn-sm btn-calificar" @click="abrirModalCalificar(s, 'trabajador')">
                ⭐ Calificar atención del técnico
              </button>
            </div>
          </div>

          <div v-if="mensajes[s.id]"
            :class="['alert', mensajes[s.id]?.tipo === 'exito' ? 'alert-success' : 'alert-error']"
            style="margin:0 24px 18px">
            {{ mensajes[s.id]?.texto }}
          </div>

        </div>
      </div>
    </div>

    <!-- MODAL DE CALIFICACIÓN BIDIRECCIONAL -->
    <div v-if="modalCalificarAbierto" class="modal-overlay" @click.self="cerrarModalCalificar">
      <div class="modal-card card">
        <div class="modal-header">
          <h3>
            <span v-if="tipoCalificacion === 'cliente'">⭐ Calificar al Cliente</span>
            <span v-else>⭐ Calificar al Técnico</span>
          </h3>
          <button class="btn-modal-close" @click="cerrarModalCalificar">✕</button>
        </div>

        <div class="modal-body">
          <p class="modal-target-desc">
            <strong v-if="tipoCalificacion === 'cliente'">
              Cliente: {{ solicitudACalificar?.cliente.first_name }} {{ solicitudACalificar?.cliente.last_name }}
            </strong>
            <strong v-else>
              Técnico: {{ solicitudACalificar?.trabajador.usuario.first_name }} {{ solicitudACalificar?.trabajador.usuario.last_name }} ({{ solicitudACalificar?.trabajador.oficio }})
            </strong>
          </p>

          <!-- SELECCIÓN DE ESTRELLAS -->
          <div class="rating-stars-wrap">
            <label class="rating-label">Puntuación:</label>
            <div class="stars-selector">
              <button
                v-for="estrella in 5"
                :key="estrella"
                type="button"
                :class="['star-btn', estrella <= formCalificacion.puntuacion ? 'active' : '']"
                @click="formCalificacion.puntuacion = estrella"
              >
                ★
              </button>
              <span class="stars-val-text">{{ formCalificacion.puntuacion }} de 5 estrellas</span>
            </div>
          </div>

          <!-- COMENTARIO -->
          <div class="form-group" style="margin-top:16px;">
            <label class="form-label">
              <span v-if="tipoCalificacion === 'cliente'">Comentario sobre el trato, puntualidad y cumplimiento del pago:</span>
              <span v-else>Comentario sobre la calidad del servicio técnico recibido:</span>
            </label>
            <textarea
              v-model="formCalificacion.comentario"
              class="form-textarea"
              rows="3"
              placeholder="Escribe tu opinión sincera..."
            ></textarea>
          </div>

          <div v-if="errorCalificacion" class="alert alert-error" style="margin-top:12px">
            {{ errorCalificacion }}
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="cerrarModalCalificar" :disabled="guardandoCalificacion">
            Cancelar
          </button>
          <button class="btn-primary" @click="enviarCalificacion" :disabled="guardandoCalificacion">
            <span v-if="!guardandoCalificacion">Enviar Calificación ➔</span>
            <span v-else>Guardando...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../services/api'
import type { Solicitud, EstadoSolicitud } from '../types'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const solicitudes = ref<Solicitud[]>([])
const cargando = ref(false)
const procesando = ref<number | null>(null)
const motivos = ref<Record<number, string>>({})
const mensajes = ref<Record<number, { tipo: 'exito' | 'error'; texto: string }>>({})

const editandoPresupuesto = ref<number | null>(null)
const formPresupuesto = ref<{ precio: number | string; metodo: string }>({ precio: '', metodo: 'Yape' })

// Estado de Calificación Bidireccional
const modalCalificarAbierto = ref(false)
const solicitudACalificar = ref<Solicitud | null>(null)
const tipoCalificacion = ref<'cliente' | 'trabajador'>('cliente')
const formCalificacion = ref<{ puntuacion: number; comentario: string }>({ puntuacion: 5, comentario: '' })
const guardandoCalificacion = ref(false)
const errorCalificacion = ref<string | null>(null)

const tabActiva = ref<'enviadas' | 'recibidas'>(auth.enModoTrabajador ? 'recibidas' : 'enviadas')
const totalEnviadas = ref(0)
const totalRecibidas = ref(0)

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

function getMetodoPagoIcono(metodo?: string) {
  switch (metodo) {
    case 'Yape': return '💜'
    case 'Plin': return '💙'
    case 'Transferencia': return '🏦'
    default: return '💵'
  }
}

function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString('es-PE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function cambiarTab(tab: 'enviadas' | 'recibidas') {
  tabActiva.value = tab
  cargarSolicitudes()
}

function iniciarEdicionPresupuesto(s: Solicitud) {
  formPresupuesto.value = {
    precio: s.precio_acordado || '',
    metodo: s.metodo_pago || 'Yape'
  }
  editandoPresupuesto.value = s.id
}

async function guardarPresupuesto(id: number) {
  const data = formPresupuesto.value
  if (!data || !data.precio) return
  procesando.value = id
  try {
    const res = await api.patch<{ mensaje: string; solicitud: Solicitud }>(`/solicitudes/${id}/estado/`, {
      precio_acordado: parseFloat(String(data.precio)),
      metodo_pago: data.metodo
    })
    const idx = solicitudes.value.findIndex(s => s.id === id)
    if (idx !== -1) {
      solicitudes.value[idx] = res.data.solicitud
    }
    editandoPresupuesto.value = null
    mensajes.value[id] = { tipo: 'exito', texto: '✅ Cotización actualizada correctamente.' }
    setTimeout(() => delete mensajes.value[id], 3000)
  } catch {
    mensajes.value[id] = { tipo: 'error', texto: 'Error al actualizar cotización.' }
  } finally {
    procesando.value = null
  }
}

function abrirModalCalificar(s: Solicitud, tipo: 'cliente' | 'trabajador') {
  solicitudACalificar.value = s
  tipoCalificacion.value = tipo
  formCalificacion.value = { puntuacion: 5, comentario: '' }
  errorCalificacion.value = null
  modalCalificarAbierto.value = true
}

function cerrarModalCalificar() {
  modalCalificarAbierto.value = false
  solicitudACalificar.value = null
  errorCalificacion.value = null
}

async function enviarCalificacion() {
  if (!solicitudACalificar.value) return
  guardandoCalificacion.value = true
  errorCalificacion.value = null

  try {
    const s = solicitudACalificar.value
    if (tipoCalificacion.value === 'cliente') {
      await api.post('/calificaciones/cliente/', {
        cliente: s.cliente.id,
        solicitud: s.id,
        puntuacion: formCalificacion.value.puntuacion,
        comentario: formCalificacion.value.comentario
      })
      s.ha_calificado_cliente = true
      mensajes.value[s.id] = { tipo: 'exito', texto: '⭐ Calificación al cliente registrada correctamente.' }
    } else {
      await api.post('/calificaciones/', {
        trabajador: s.trabajador.id,
        solicitud: s.id,
        puntuacion: formCalificacion.value.puntuacion,
        comentario: formCalificacion.value.comentario
      })
      s.ha_calificado_trabajador = true
      mensajes.value[s.id] = { tipo: 'exito', texto: '⭐ Calificación al técnico registrada correctamente.' }
    }

    cerrarModalCalificar()
    setTimeout(() => delete mensajes.value[s.id], 4000)
  } catch (e: any) {
    errorCalificacion.value = e.response?.data?.error || 'No se pudo registrar la calificación.'
  } finally {
    guardandoCalificacion.value = false
  }
}


async function cargarContadores() {
  if (!auth.esTrabajador) return
  try {
    const [resEnv, resRec] = await Promise.all([
      api.get<Solicitud[]>('/solicitudes/?tipo=enviadas'),
      api.get<Solicitud[]>('/solicitudes/?tipo=recibidas')
    ])
    totalEnviadas.value = resEnv.data.length
    totalRecibidas.value = resRec.data.length
  } catch (e) {
    console.error('Error al cargar contadores:', e)
  }
}

async function cargarSolicitudes() {
  cargando.value = true
  try {
    const res = await api.get<Solicitud[]>(`/solicitudes/?tipo=${tabActiva.value}`)
    solicitudes.value = res.data
    if (tabActiva.value === 'enviadas') totalEnviadas.value = res.data.length
    else totalRecibidas.value = res.data.length
  } catch (err) {
    console.error('Error al cargar solicitudes:', err)
  } finally {
    cargando.value = false
  }
}

async function cambiarEstado(id: number, nuevoEstado: EstadoSolicitud, motivo?: string) {
  procesando.value = id
  mensajes.value[id] = { tipo: 'exito', texto: '' }
  try {
    await api.patch(`/solicitudes/${id}/estado/`, {
      estado: nuevoEstado,
      motivo_rechazo: motivo || ''
    })
    mensajes.value[id] = { tipo: 'exito', texto: `✅ Solicitud actualizada a: ${nuevoEstado}` }
    await cargarSolicitudes()
    await cargarContadores()
    setTimeout(() => delete mensajes.value[id], 3000)
  } catch (e: any) {
    mensajes.value[id] = { tipo: 'error', texto: e.response?.data?.error || 'Error al cambiar estado' }
  } finally {
    procesando.value = null
  }
}

watch(() => auth.modoActual, (nuevoModo) => {
  if (auth.esTrabajador) {
    tabActiva.value = nuevoModo === 'trabajador' ? 'recibidas' : 'enviadas'
    cargarSolicitudes()
  }
})

onMounted(async () => {
  await cargarSolicitudes()
  await cargarContadores()
})
</script>

<style scoped>
.page {
  min-height: calc(100vh - 68px);
}

.page-header {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: 36px 24px;
}

.page-header-inner {
  max-width: 800px;
  margin: 0 auto;
}

.page-header-inner h1 {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 4px;
}

.page-header-inner p {
  font-size: 15px;
  color: var(--text2);
}

.sol-tabs {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.sol-tab-btn {
  padding: 10px 18px;
  border-radius: 12px;
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  font-size: 14px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sol-tab-btn:hover {
  background: var(--surface-subtle);
  color: var(--text);
  transform: translateY(-1px);
}

.sol-tab-btn.activo {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px var(--primary-glow);
}

.contenedor {
  max-width: 800px;
  margin: 0 auto;
  padding: 36px 24px 60px;
}

.estado {
  text-align: center;
  padding: 64px 32px;
  color: var(--text2);
}

.estado h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 6px;
}

.estado p {
  font-size: 14.5px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.lista {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.solicitud-card {
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
}

.solicitud-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.sol-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-subtle);
}

.sol-persona {
  display: flex;
  align-items: center;
  gap: 14px;
}

.sol-avatar {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.sol-nombre {
  font-size: 16px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.sol-sub {
  font-size: 13px;
  color: var(--text2);
  margin-top: 2px;
}

.sol-body {
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sol-campo {
  font-size: 14px;
}

.sol-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.sol-campo p {
  color: var(--text);
  line-height: 1.6;
}

/* COTIZACIÓN CARD */
.cotizacion-card {
  background: var(--surface-subtle);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px 20px;
}

.cotizacion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.cotizacion-title {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text2);
}

.btn-text-sm {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
}

.cotizacion-val-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.cotizacion-monto {
  font-size: 24px;
  font-weight: 800;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.cotizacion-pago-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
}

.pago-yape {
  background: rgba(116, 23, 140, 0.12);
  color: #74178C;
  border: 1px solid rgba(116, 23, 140, 0.3);
}

.pago-plin {
  background: rgba(0, 168, 232, 0.12);
  color: #0087BA;
  border: 1px solid rgba(0, 168, 232, 0.3);
}

.pago-efectivo {
  background: #D1FAE5;
  color: #065F46;
  border: 1px solid #10B981;
}

.pago-transferencia {
  background: #DBEAFE;
  color: #1E40AF;
  border: 1px solid #3B82F6;
}

.cotizacion-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cotizacion-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.input-monto-wrap {
  display: flex;
  align-items: center;
  position: relative;
}

.input-monto-wrap .prefix {
  position: absolute;
  left: 12px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text2);
}

.input-monto-wrap .form-input {
  padding-left: 36px;
}

.cotizacion-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.add-cotizacion-box {
  margin-top: 4px;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 700;
}

.txt-red {
  color: var(--red) !important;
  font-weight: 600;
}

.sol-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  flex-wrap: wrap;
  gap: 12px;
}

.sol-fecha {
  font-size: 12px;
  color: var(--text3);
}

.sol-acciones {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.rep-badge {
  font-size: 11.5px;
  font-weight: 700;
  color: #D97706;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
}

.rep-nuevo {
  color: var(--text3);
  background: var(--surface-subtle);
  border-color: var(--border);
}

.btn-calificar {
  background: linear-gradient(135deg, #F59E0B, #D97706) !important;
  color: #fff !important;
  border: none !important;
}

.btn-calificar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* MODAL DE CALIFICACIÓN */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
  animation: fadeIn 0.2s ease;
}

.modal-card {
  width: 100%;
  max-width: 500px;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1.5px solid var(--border);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  animation: scaleUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-subtle);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
  margin: 0;
}

.btn-modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--text2);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.btn-modal-close:hover {
  background: var(--border);
  color: var(--text);
}

.modal-body {
  padding: 24px;
}

.modal-target-desc {
  font-size: 14.5px;
  color: var(--text);
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px dashed var(--border);
}

.rating-stars-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rating-label {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text2);
}

.stars-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: var(--border);
  cursor: pointer;
  transition: transform 0.15s ease, color 0.15s ease;
  line-height: 1;
  padding: 0;
}

.star-btn:hover {
  transform: scale(1.2);
}

.star-btn.active {
  color: #F59E0B;
}

.stars-val-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  margin-left: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--surface-subtle);
}
</style>