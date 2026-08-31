<template>
  <div class="page">
    <!-- HEADER DEL PERFIL -->
    <div class="page-header">
      <div class="page-header-inner">
        <div class="perfil-top">
          <div class="perfil-avatar-wrap">
            <img v-if="auth.usuario?.foto_url || (perfil && perfil.foto_url)"
                 :src="(auth.usuario?.foto_url || perfil?.foto_url) ?? ''"
                 class="perfil-avatar-img"
                 :alt="'Foto de perfil de ' + (auth.usuario?.first_name || 'usuario') + ' ' + (auth.usuario?.last_name || '')" />

            <div v-else class="perfil-avatar">
              {{ auth.usuario?.first_name?.[0] || 'U' }}{{ auth.usuario?.last_name?.[0] || '' }}
            </div>
            <label class="foto-upload-btn" title="Cambiar foto de perfil">
              📷
              <input type="file" accept="image/jpeg,image/png,image/webp" @change="subirFotoUsuario" style="display:none" :disabled="subiendoFoto" />
            </label>
          </div>
          <div>
            <h1>{{ auth.usuario?.first_name }} {{ auth.usuario?.last_name }}</h1>
            <div class="perfil-badges">
              <span v-if="auth.usuario?.rol" :class="['badge', rolBadge[auth.usuario.rol]]">{{ rolTexto[auth.usuario.rol] }}</span>
              <span class="badge badge-subtle">@{{ auth.usuario?.username }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CONTENEDOR PRINCIPAL -->
    <div class="contenedor">
      <div v-if="mensajeGlobal" :class="['alert', tipoMensajeGlobal === 'error' ? 'alert-error' : 'alert-success']" style="margin-bottom: 24px;">
        {{ mensajeGlobal }}
      </div>

      <div class="layout">

        <!-- CARD: INFORMACIÓN PERSONAL -->
        <div class="card seccion">
          <div class="seccion-header">
            <h3>Información Personal</h3>
            <button class="btn-secondary btn-sm" @click="abrirModalPersonal">
              ✏️ Editar información
            </button>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Nombre Completo</span>
              <span class="info-val">{{ auth.usuario?.first_name }} {{ auth.usuario?.last_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Nombre de Usuario</span>
              <span class="info-val">@{{ auth.usuario?.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Correo Electrónico</span>
              <span class="info-val">{{ auth.usuario?.email || 'No especificado' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Teléfono Celular</span>
              <span class="info-val">{{ auth.usuario?.celular || 'No registrado' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Distrito de Residencia</span>
              <span class="info-val">{{ auth.usuario?.distrito || 'Cusco' }}</span>
            </div>
          </div>
        </div>

        <!-- CARD: SEGURIDAD Y CREDENCIALES -->
        <div class="card seccion">
          <div class="seccion-header">
            <div>
              <h3>Seguridad de la Cuenta</h3>
              <p class="seccion-sub">Administra tu contraseña de acceso y protección de datos</p>
            </div>
            <button class="btn-secondary btn-sm" @click="abrirModalPassword">
              🔒 Cambiar contraseña
            </button>
          </div>
        </div>

        <!-- CARD: MI REPUTACIÓN COMO CLIENTE -->
        <div class="card seccion">
          <div class="seccion-header">
            <div>
              <h3>Mi Reputación como Cliente</h3>
              <p class="seccion-sub">Calificaciones y valoraciones recibidas de técnicos que contrataste</p>
            </div>
            <div v-if="calificacionesCliente.length > 0">
              <span class="rep-score-pill">⭐ {{ calcularPromedioCliente().toFixed(1) }} / 5.0 ({{ calificacionesCliente.length }})</span>
            </div>
          </div>

          <div v-if="cargandoCalificaciones" class="califs-loading">
            <span>Cargando valoraciones recibidas...</span>
          </div>

          <div v-else-if="calificacionesCliente.length === 0" class="califs-vacio">
            <p>⭐ Aún no has recibido calificaciones de técnicos. Al completarse tus trabajos solicitados, los profesionales calificarán la puntualidad, trato y cumplimiento de pago.</p>
          </div>

          <div v-else class="califs-lista">
            <div v-for="c in calificacionesCliente" :key="c.id" class="calif-cliente-item">
              <div class="calif-cliente-top">
                <div class="calif-tecnico-info">
                  <strong>{{ c.trabajador.usuario.first_name }} {{ c.trabajador.usuario.last_name }}</strong>
                  <span class="calif-tecnico-oficio">· {{ c.trabajador.oficio }}</span>
                </div>
                <div class="calif-stars">
                  <span class="star-rating-text">⭐ {{ c.puntuacion }}/5</span>
                  <span class="calif-fecha">{{ formatFechaCorta(c.fecha) }}</span>
                </div>
              </div>
              <p v-if="c.comentario" class="calif-comentario">"{{ c.comentario }}"</p>
            </div>
          </div>
        </div>

        <!-- CARD: PERFIL TÉCNICO (SOLO TRABAJADORES) -->
        <div v-if="auth.esTrabajador && perfil" class="card seccion">
          <div class="seccion-header">
            <div>
              <h3>Mi Perfil Profesional</h3>
              <p class="seccion-sub">Información que ven los clientes al buscar servicios</p>
            </div>
            <div style="display:flex;gap:10px;align-items:center;">
              <span :class="['badge', estadoBadge[perfil.estado]]">{{ estadoTexto[perfil.estado] }}</span>
              <button class="btn-secondary btn-sm" @click="abrirModalTecnico">
                ✏️ Editar especialidad
              </button>
            </div>
          </div>

          <div v-if="perfil.estado === 'pendiente'" class="alert alert-warning" style="margin-bottom:16px;">
            ⏳ Tu cuenta está en revisión por nuestro equipo administrativo. Te notificaremos pronto.
          </div>
          <div v-if="perfil.estado === 'rechazado'" class="alert alert-error" style="margin-bottom:16px;">
            ❌ Tu solicitud fue rechazada. Motivo: <strong>{{ perfil.motivo_rechazo }}</strong>
          </div>
          <div v-if="perfil.estado === 'aprobado'" class="alert alert-success" style="margin-bottom:16px;">
            ✅ Perfil verificado. Eres visible en el mapa y directorio de Cusco.
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Especialidad / Categoría</span>
              <span class="info-val">{{ perfil.categoria }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Oficio o Título</span>
              <span class="info-val">{{ perfil.oficio }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Años de Experiencia</span>
              <span class="info-val">{{ perfil.experiencia }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Calificación Promedio</span>
              <span class="info-val">⭐ {{ perfil.calificacion_promedio.toFixed(1) }} ({{ perfil.num_calificaciones }} reseñas)</span>
            </div>
          </div>

          <div v-if="perfil.descripcion" class="item-desc-box">
            <span class="info-label">Descripción Profesional</span>
            <p>{{ perfil.descripcion }}</p>
          </div>

          <!-- Actualizar ubicación GPS -->
          <div v-if="perfil.estado === 'aprobado'" class="ubicacion-box">
            <div class="ubicacion-info">
              <div class="ubicacion-title">📍 Ubicación GPS para Clientes</div>
              <div class="ubicacion-desc">Actualiza tu posición actual para que los clientes de tu zona te encuentren más cerca.</div>
            </div>
            <button class="btn-primary" @click="actualizarUbicacion" :disabled="actualizando">
              {{ actualizando ? '📍 Obteniendo GPS...' : '📍 Actualizar mi ubicación' }}
            </button>
          </div>
        </div>

        <!-- TOGGLE DISPONIBILIDAD -->
        <div v-if="perfil && perfil.estado === 'aprobado'" class="disponibilidad-box">
          <div class="disponibilidad-info">
            <div class="disponibilidad-title">
              <span :class="['dot-estado', perfil.disponible ? 'verde' : 'gris']"></span>
              {{ perfil.disponible ? 'Estás DISPONIBLE para recibir trabajos' : 'Estás OCUPADO / No disponible' }}
            </div>
            <div class="disponibilidad-desc">
              {{ perfil.disponible ? 'Los clientes pueden llamarte por WhatsApp y enviarte solicitudes directas.' : 'No aparecerás en las búsquedas activas de clientes hasta que te actives.' }}
            </div>
          </div>
          <button :class="['btn-toggle', perfil.disponible ? 'btn-toggle-off' : 'btn-toggle-on']"
            @click="toggleDisponibilidad" :disabled="toggling">
            {{ toggling ? 'Guardando...' : perfil.disponible ? 'Pausar disponibilidad' : 'Activarme como disponible' }}
          </button>
        </div>

      </div>
    </div>

    <!-- ============================================================= -->
    <!-- MODAL 1: EDITAR INFORMACIÓN PERSONAL                         -->
    <!-- ============================================================= -->
    <div v-if="mostrarModalPersonal" class="modal-overlay" @click.self="mostrarModalPersonal = false">
      <div class="modal-card card">
        <div class="modal-header">
          <h3>Editar Información Personal</h3>
          <button class="modal-close" @click="mostrarModalPersonal = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nombre *</label>
              <input v-model="formPersonal.first_name" type="text" maxlength="40" class="form-input" placeholder="Tu nombre" />
            </div>
            <div class="form-group">
              <label class="form-label">Apellido</label>
              <input v-model="formPersonal.last_name" type="text" maxlength="40" class="form-input" placeholder="Tu apellido" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Correo Electrónico *</label>
            <input v-model="formPersonal.email" type="email" maxlength="80" class="form-input" placeholder="tucorreo@ejemplo.com" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Celular en Cusco (9 dígitos) *</label>
              <input 
                v-model="formPersonal.celular" 
                type="tel" 
                maxlength="9" 
                class="form-input" 
                placeholder="984123456" 
                @input="formPersonal.celular = formPersonal.celular.replace(/\D/g, '').slice(0, 9)"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Distrito (Cusco)</label>
              <select v-model="formPersonal.distrito" class="form-select">
                <option value="">Selecciona distrito</option>
                <option v-for="d in distritos" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>

          <div v-if="errorPersonal" class="alert alert-error">{{ errorPersonal }}</div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="mostrarModalPersonal = false" :disabled="guardandoPersonal">Cancelar</button>
          <button class="btn-primary" @click="guardarPersonal" :disabled="guardandoPersonal">
            {{ guardandoPersonal ? 'Guardando cambios...' : 'Guardar información' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- MODAL 2: CAMBIAR CONTRASEÑA                                  -->
    <!-- ============================================================= -->
    <div v-if="mostrarModalPassword" class="modal-overlay" @click.self="mostrarModalPassword = false">
      <div class="modal-card card">
        <div class="modal-header">
          <h3>Cambiar Contraseña</h3>
          <button class="modal-close" @click="mostrarModalPassword = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Contraseña Actual *</label>
            <input v-model="formPassword.password_actual" type="password" maxlength="64" class="form-input" placeholder="Tu contraseña actual" />
          </div>

          <div class="form-group">
            <label class="form-label">Nueva Contraseña * (mínimo 8 caracteres)</label>
            <input v-model="formPassword.password_nueva" type="password" maxlength="64" class="form-input" placeholder="Mínimo 8 caracteres" />
          </div>

          <div class="form-group">
            <label class="form-label">Confirmar Nueva Contraseña *</label>
            <input v-model="formPassword.password_confirmar" type="password" maxlength="64" class="form-input" placeholder="Repite la nueva contraseña" />
          </div>

          <div v-if="errorPassword" class="alert alert-error">{{ errorPassword }}</div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="mostrarModalPassword = false" :disabled="guardandoPassword">Cancelar</button>
          <button class="btn-primary" @click="guardarPassword" :disabled="guardandoPassword">
            {{ guardandoPassword ? 'Actualizando...' : 'Actualizar contraseña' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- MODAL 3: EDITAR PERFIL TÉCNICO                               -->
    <!-- ============================================================= -->
    <div v-if="mostrarModalTecnico" class="modal-overlay" @click.self="mostrarModalTecnico = false">
      <div class="modal-card card">
        <div class="modal-header">
          <h3>Editar Perfil Profesional</h3>
          <button class="modal-close" @click="mostrarModalTecnico = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Categoría</label>
              <select v-model="formTecnico.categoria" class="form-select">
                <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Experiencia</label>
              <select v-model="formTecnico.experiencia" class="form-select">
                <option v-for="e in experiencias" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Oficio / Título del Servicio (máx. 100 caracteres)</label>
            <input v-model="formTecnico.oficio" type="text" maxlength="100" class="form-input" placeholder="Ej: Electricista de Instalaciones y Tableros" />
          </div>

          <div class="form-group">
            <label class="form-label">Descripción de Servicios (máx. 800 caracteres)</label>
            <textarea v-model="formTecnico.descripcion" maxlength="800" class="form-textarea" rows="3" placeholder="Describe tu experiencia, herramientas, garantía y servicios destacados..."></textarea>
          </div>

          <div v-if="errorTecnico" class="alert alert-error">{{ errorTecnico }}</div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="mostrarModalTecnico = false" :disabled="guardandoTecnico">Cancelar</button>
          <button class="btn-primary" @click="guardarTecnico" :disabled="guardandoTecnico">
            {{ guardandoTecnico ? 'Guardando...' : 'Guardar especialidad' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import type { Trabajador, RolUsuario, EstadoTrabajador, Usuario } from '../types'
import { useAuthStore } from '../stores/auth'
import { comprimirImagen, formatearBytes } from '../utils/imageCompressor'

const auth = useAuthStore()
const perfil = ref<Trabajador | null>(null)
const actualizando = ref(false)
const toggling = ref(false)
const subiendoFoto = ref(false)
const mensajeGlobal = ref('')
const tipoMensajeGlobal = ref<'exito' | 'error'>('exito')

const distritos = ['Cusco', 'Wanchaq', 'San Sebastián', 'San Jerónimo', 'Santiago']
const categorias = [
  'Electricidad',
  'Gasfitería',
  'Carpintería',
  'Cerrajería',
  'Pintura',
  'Albañilería y Construcción',
  'Drywall y Cielorraso',
  'Soldadura y Estructuras Metálicas',
  'Reparación de Electrodomésticos',
  'Termas Solares y Calefacción',
  'Refrigeración y Climatización',
  'Vidriería y Aluminios',
  'Jardinería y Áreas Verdes',
  'Mantenimiento de Cómputo y Redes',
  'Limpieza y Desinfección',
  'Otro'
]
const experiencias = ['Menos de 1 año', '1-3 años', '3-5 años', 'Más de 5 años']

const rolTexto: Record<RolUsuario, string> = { cliente: 'Cliente', trabajador: 'Técnico Profesional', admin: 'Administrador' }
const rolBadge: Record<RolUsuario, string> = { cliente: 'badge-blue', trabajador: 'badge-green', admin: 'badge-amber' }
const estadoTexto: Record<EstadoTrabajador, string> = { pendiente: '⏳ Pendiente de Aprobación', aprobado: '✅ Aprobado', rechazado: '❌ Rechazado' }
const estadoBadge: Record<EstadoTrabajador, string> = { pendiente: 'badge-amber', aprobado: 'badge-green', rechazado: 'badge-red' }

// Modal Personal
const mostrarModalPersonal = ref(false)
const guardandoPersonal = ref(false)
const errorPersonal = ref('')
const formPersonal = ref({ first_name: '', last_name: '', email: '', celular: '', distrito: '' })

// Modal Password
const mostrarModalPassword = ref(false)
const guardandoPassword = ref(false)
const errorPassword = ref('')
const formPassword = ref({ password_actual: '', password_nueva: '', password_confirmar: '' })

// Modal Técnico
const mostrarModalTecnico = ref(false)
const guardandoTecnico = ref(false)
const errorTecnico = ref('')
const formTecnico = ref({ categoria: '', oficio: '', experiencia: '', descripcion: '' })

function mostrarMensaje(msg: string, tipo: 'exito' | 'error' = 'exito') {
  mensajeGlobal.value = msg
  tipoMensajeGlobal.value = tipo
  setTimeout(() => mensajeGlobal.value = '', 4000)
}

async function cargarPerfil() {
  if (auth.esTrabajador) {
    try {
      const res = await api.get<Trabajador>('/trabajadores/mi-perfil/')
      perfil.value = res.data
    } catch (e) {
      console.error('Error al cargar perfil de trabajador:', e)
    }
  }
}

// Subir foto de perfil con compresión y optimización automática
async function subirFotoUsuario(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    return mostrarMensaje('La foto no debe superar los 10 MB.', 'error')
  }

  subiendoFoto.value = true
  try {
    mostrarMensaje('⚙️ Optimizando y comprimiendo imagen...', 'exito')
    
    // Compresión client-side a WebP / JPEG de alta calidad
    const optimizada = await comprimirImagen(file, {
      maxWidth: 900,
      maxHeight: 900,
      quality: 0.85,
      format: 'image/webp'
    })

    console.log(`Foto optimizada: ${formatearBytes(optimizada.originalSize)} ➔ ${formatearBytes(optimizada.compressedSize)} (Ahorro: ${optimizada.compressionRatio}%)`)

    const formData = new FormData()
    formData.append('foto', optimizada.file)
    const res = await api.post<{ mensaje: string; foto_url: string; usuario: Usuario }>('/usuarios/foto/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    auth.actualizarUsuarioLocal(res.data.usuario)
    if (perfil.value) {
      perfil.value.foto_url = res.data.foto_url
    }
    mostrarMensaje(`✅ Foto actualizada (${optimizada.compressionRatio}% más ligera).`, 'exito')
  } catch (err: any) {
    mostrarMensaje(err.response?.data?.error || 'Error al procesar y subir la foto de perfil.', 'error')
  } finally {
    subiendoFoto.value = false
  }
}

// Modal Personal
function abrirModalPersonal() {
  formPersonal.value = {
    first_name: auth.usuario?.first_name || '',
    last_name: auth.usuario?.last_name || '',
    email: auth.usuario?.email || '',
    celular: auth.usuario?.celular || '',
    distrito: auth.usuario?.distrito || ''
  }
  errorPersonal.value = ''
  mostrarModalPersonal.value = true
}

async function guardarPersonal() {
  errorPersonal.value = ''
  if (!formPersonal.value.first_name.trim()) {
    errorPersonal.value = 'El nombre es obligatorio.'
    return
  } else if (formPersonal.value.first_name.trim().length < 2) {
    errorPersonal.value = 'El nombre debe tener al menos 2 caracteres.'
    return
  }

  const cel = formPersonal.value.celular?.replace(/\D/g, '')
  if (cel && !/^9\d{8}$/.test(cel)) {
    errorPersonal.value = 'El celular debe tener 9 dígitos (iniciar con 9).'
    return
  }

  guardandoPersonal.value = true
  try {
    const res = await api.patch<{ mensaje: string; usuario: Usuario }>('/usuarios/perfil/', formPersonal.value)
    auth.actualizarUsuarioLocal(res.data.usuario)
    mostrarModalPersonal.value = false
    mostrarMensaje('✅ Información personal actualizada exitosamente.', 'exito')
  } catch (err: any) {
    const data = err.response?.data
    if (data?.celular) errorPersonal.value = `Celular: ${data.celular[0]}`
    else if (data?.email) errorPersonal.value = `Correo: ${data.email[0]}`
    else errorPersonal.value = data?.error || 'Error al actualizar información.'
  } finally {
    guardandoPersonal.value = false
  }
}

// Modal Password
function abrirModalPassword() {
  formPassword.value = { password_actual: '', password_nueva: '', password_confirmar: '' }
  errorPassword.value = ''
  mostrarModalPassword.value = true
}

async function guardarPassword() {
  errorPassword.value = ''
  if (!formPassword.value.password_actual || !formPassword.value.password_nueva) {
    errorPassword.value = 'Completa todos los campos.'
    return
  }
  if (formPassword.value.password_nueva.length < 8) {
    errorPassword.value = 'La nueva contraseña debe tener al menos 8 caracteres.'
    return
  }
  if (formPassword.value.password_nueva !== formPassword.value.password_confirmar) {
    errorPassword.value = 'Las contraseñas no coinciden.'
    return
  }

  guardandoPassword.value = true
  try {
    await api.post('/usuarios/cambiar-password/', {
      password_actual: formPassword.value.password_actual,
      password_nueva: formPassword.value.password_nueva
    })
    mostrarModalPassword.value = false
    mostrarMensaje('✅ Contraseña actualizada correctamente.', 'exito')
  } catch (err: any) {
    errorPassword.value = err.response?.data?.error || 'No se pudo cambiar la contraseña. Verifica tu contraseña actual.'
  } finally {
    guardandoPassword.value = false
  }
}

// Modal Técnico
function abrirModalTecnico() {
  if (!perfil.value) return
  formTecnico.value = {
    categoria: perfil.value.categoria,
    oficio: perfil.value.oficio,
    experiencia: perfil.value.experiencia,
    descripcion: perfil.value.descripcion || ''
  }
  errorTecnico.value = ''
  mostrarModalTecnico.value = true
}

async function guardarTecnico() {
  errorTecnico.value = ''
  if (!formTecnico.value.oficio.trim()) {
    errorTecnico.value = 'El oficio o título es obligatorio.'
    return
  } else if (formTecnico.value.oficio.trim().length < 3) {
    errorTecnico.value = 'El oficio debe tener al menos 3 caracteres.'
    return
  }

  guardandoTecnico.value = true
  try {
    const res = await api.patch<{ mensaje: string; trabajador: Trabajador }>('/trabajadores/mi-perfil/', formTecnico.value)
    perfil.value = res.data.trabajador
    mostrarModalTecnico.value = false
    mostrarMensaje('✅ Perfil técnico actualizado correctamente.', 'exito')
  } catch (err: any) {
    errorTecnico.value = err.response?.data?.error || 'Error al actualizar perfil técnico.'
  } finally {
    guardandoTecnico.value = false
  }
}

async function toggleDisponibilidad() {
  toggling.value = true
  try {
    const res = await api.patch<{ mensaje: string; disponible: boolean }>('/trabajadores/disponibilidad/')
    if (perfil.value) {
      perfil.value.disponible = res.data.disponible
    }
    mostrarMensaje(res.data.mensaje, 'exito')
  } catch {
    mostrarMensaje('Error al actualizar disponibilidad.', 'error')
  } finally {
    toggling.value = false
  }
}

function actualizarUbicacion() {
  if (!navigator.geolocation) return mostrarMensaje('Tu navegador no soporta geolocalización.', 'error')
  actualizando.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        await api.patch('/trabajadores/ubicacion/', {
          latitud: pos.coords.latitude,
          longitud: pos.coords.longitude,
        })
        if (perfil.value) {
          perfil.value.latitud = pos.coords.latitude
          perfil.value.longitud = pos.coords.longitude
        }
        mostrarMensaje('✅ Ubicación GPS actualizada exitosamente.', 'exito')
      } catch {
        mostrarMensaje('Error al guardar ubicación GPS.', 'error')
      } finally {
        actualizando.value = false
      }
    },
    () => {
      mostrarMensaje('No se pudo obtener tu ubicación actual.', 'error')
      actualizando.value = false
    }
  )
}

// Calificaciones recibidas como Cliente
const calificacionesCliente = ref<any[]>([])
const cargandoCalificaciones = ref(false)

function calcularPromedioCliente(): number {
  if (!calificacionesCliente.value.length) return 0
  const suma = calificacionesCliente.value.reduce((acc, c) => acc + c.puntuacion, 0)
  return suma / calificacionesCliente.value.length
}

function formatFechaCorta(f: string): string {
  if (!f) return ''
  return new Date(f).toLocaleDateString('es-PE', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function cargarCalificacionesCliente() {
  if (!auth.usuario?.id) return
  cargandoCalificaciones.value = true
  try {
    const res = await api.get<any[]>(`/calificaciones/cliente/${auth.usuario.id}/`)
    calificacionesCliente.value = res.data
  } catch (e) {
    console.error('Error al cargar calificaciones del cliente:', e)
  } finally {
    cargandoCalificaciones.value = false
  }
}

onMounted(async () => {
  await cargarPerfil()
  await cargarCalificacionesCliente()
})
</script>

<style scoped>
.rep-score-pill {
  font-size: 13px;
  font-weight: 800;
  color: #D97706;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
}

.califs-loading, .califs-vacio {
  padding: 18px 0;
  color: var(--text3);
  font-size: 13.5px;
}

.califs-lista {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.calif-cliente-item {
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
}

.calif-cliente-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
  gap: 8px;
}

.calif-tecnico-info strong {
  font-size: 14px;
  color: var(--text);
}

.calif-tecnico-oficio {
  font-size: 13px;
  color: var(--text2);
  margin-left: 4px;
}

.calif-stars {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-rating-text {
  font-size: 12.5px;
  font-weight: 700;
  color: #D97706;
}

.calif-fecha {
  font-size: 11.5px;
  color: var(--text3);
}

.calif-comentario {
  font-size: 13.5px;
  color: var(--text);
  font-style: italic;
  margin: 0;
  line-height: 1.5;
}
.page {
  min-height: calc(100vh - 68px);
}

.page-header {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: 40px 24px;
}

.page-header-inner {
  max-width: 800px;
  margin: 0 auto;
}

.perfil-top {
  display: flex;
  align-items: center;
  gap: 24px;
}

.perfil-badges {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 6px;
}

.badge-subtle {
  background: var(--surface-subtle);
  color: var(--text2);
  border: 1px solid var(--border);
}

.perfil-avatar {
  width: 76px;
  height: 76px;
  border-radius: 20px;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  box-shadow: var(--shadow-md);
}

.perfil-top h1 {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 2px;
}

.contenedor {
  max-width: 800px;
  margin: 0 auto;
  padding: 36px 24px 60px;
}

.layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.seccion {
  padding: 28px;
}

.seccion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.seccion-header h3 {
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 2px;
}

.seccion-sub {
  font-size: 13px;
  color: var(--text2);
}

.btn-sm {
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  border: 1px solid var(--border);
}

.info-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.info-val {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.item-desc-box {
  margin-top: 16px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  border: 1px solid var(--border);
}

.item-desc-box p {
  font-size: 14px;
  color: var(--text);
  line-height: 1.5;
  margin-top: 4px;
}

.ubicacion-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 20px;
  padding: 20px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.ubicacion-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}

.ubicacion-desc {
  font-size: 13.5px;
  color: var(--text2);
}

.disponibilidad-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.disponibilidad-title {
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.disponibilidad-desc {
  font-size: 13.5px;
  color: var(--text2);
}

.dot-estado {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.dot-estado.verde {
  background: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.dot-estado.gris {
  background: #9CA3AF;
  box-shadow: 0 0 0 3px rgba(156, 163, 175, 0.2);
}

.btn-toggle {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.btn-toggle-off {
  background: #FEF3C7;
  color: #92400E;
}

.btn-toggle-off:hover {
  background: #FDE68A;
}

.btn-toggle-on {
  background: var(--green-light);
  color: #065F46;
}

.btn-toggle-on:hover {
  background: #A7F3D0;
}

.btn-toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.perfil-avatar-wrap {
  position: relative;
  width: 76px;
  height: 76px;
  flex-shrink: 0;
}

.perfil-avatar-img {
  width: 76px;
  height: 76px;
  border-radius: 20px;
  object-fit: cover;
  border: 3px solid var(--border);
  box-shadow: var(--shadow-md);
}

.foto-upload-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  border: 2px solid var(--surface);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease;
}

.foto-upload-btn:hover {
  transform: scale(1.15);
  background: var(--primary-hover);
}

/* ========================================================= */
/* MODALES                                                   */
/* ========================================================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  width: 520px;
  max-width: 100%;
  padding: 32px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 800;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: var(--text3);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.modal-close:hover {
  color: var(--text);
  background: var(--surface-subtle);
}

.modal-body {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>