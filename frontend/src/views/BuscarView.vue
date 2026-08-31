<template>
  <div class="page">
    <div class="search-header">
      <div class="search-inner">
        <div class="search-titles">
          <span class="search-tag">DIRECTORIO PROFESIONAL CUSCO</span>
          <h1>Técnicos calificados en Cusco</h1>
          <p>Explora profesionales certificados cerca de tu barrio, filtra por calificación y solicita presupuestos de manera directa</p>
        </div>

        <!-- BARRA DE BÚSQUEDA PRINCIPAL -->
        <div class="search-bar card">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input v-model="busqueda" @input="buscar" class="search-input"
              placeholder="Buscar por oficio, nombre o distrito (ej. termas, Wanchaq, albañil, drywall)..." />
          </div>
          <div class="select-wrapper">
            <select v-model="categoria" @change="buscar" class="search-select">
              <option value="">Todas las categorías</option>
              <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <button class="btn-primary btn-geo" @click="usarUbicacion" :disabled="buscandoUbicacion">
            <span>📍</span> {{ buscandoUbicacion ? 'Buscando...' : 'Cerca de mí' }}
          </button>
          <button v-if="usandoUbicacion" class="btn-secondary btn-clear-geo" @click="limpiarUbicacion">✕ Quitar GPS</button>
        </div>

        <!-- FILTROS AVANZADOS Y ORDENAMIENTO -->
        <div class="filtros-avanzados-bar">
          <div class="filtro-grupo">
            <span class="filtro-label">⭐ Calificación:</span>
            <button
              v-for="opc in opcionesCalif"
              :key="opc.val"
              :class="['btn-filtro-pill', minCalificacion === opc.val ? 'activo' : '']"
              @click="setMinCalif(opc.val)"
            >
              {{ opc.texto }}
            </button>
          </div>

          <div class="filtro-grupo">
            <button
              :class="['btn-filtro-pill', soloDisponibles ? 'activo-verde' : '']"
              @click="toggleDisponibles"
            >
              <span class="dot-verde"></span> Solo técnicos disponibles
            </button>
          </div>

          <div class="filtro-grupo sort-grupo">
            <span class="filtro-label">Ordenar por:</span>
            <select v-model="ordenarPor" @change="buscar" class="sort-select">
              <option value="cercania">📍 Más cercanos</option>
              <option value="calificacion">⭐ Mejor calificados</option>
              <option value="servicios">🏆 Más servicios realizados</option>
            </select>
          </div>

          <button v-if="hayFiltrosActivos" class="btn-reset-filtros" @click="resetearFiltros">
            ✕ Limpiar filtros
          </button>
        </div>

        <div v-if="usandoUbicacion" class="ubicacion-aviso">
          📍 <strong>Ubicación GPS activa:</strong> Mostrando técnicos ordenados por cercanía (radio de 10 km).
        </div>
      </div>
    </div>

    <!-- TOGGLE VISTA -->
    <div class="vista-toggle-bar">
      <div class="vista-inner">
        <div class="resultados-count">
          Encontrados <strong>{{ tecnicos.length }}</strong> profesional{{ tecnicos.length !== 1 ? 'es' : '' }} en Cusco
        </div>
        <div class="vista-btns">
          <button :class="['vista-btn', vista === 'lista' ? 'active' : '']" @click="vista = 'lista'">
            <span>☰</span> Lista de tarjetas
          </button>
          <button :class="['vista-btn', vista === 'mapa' ? 'active' : '']" @click="vista = 'mapa'">
            <span>🗺</span> Mapa interactivo
          </button>
        </div>
      </div>
    </div>

    <div class="contenido">
      <!-- VISTA LISTA -->
      <div v-if="vista === 'lista'">
        <div v-if="cargando" class="estado">
          <div class="spinner"></div>
          <p>Consultando técnicos disponibles...</p>
        </div>

        <!-- CASO 0 RESULTADOS: TARJETA DE REQUERIMIENTO ESPECIAL -->
        <div v-else-if="tecnicos.length === 0" class="no-results-wrap">
          <div class="card empty-card">
            <div style="font-size:44px;margin-bottom:12px">🔍</div>
            <h3>No encontramos técnicos registrados con estos filtros</h3>
            <p>Prueba reduciendo los filtros o cuéntanos qué especialista necesitas en el formulario a continuación.</p>
            <button class="btn-secondary" style="margin-top:12px" @click="resetearFiltros">Restablecer filtros</button>
          </div>

          <!-- MÓDULO PIDE TU TÉCNICO / OFICIO NO LISTADO -->
          <div class="card pedir-card">
            <div class="pedir-header">
              <div class="pedir-icon">🛠️</div>
              <div>
                <h3>¿No encuentras el oficio o especialista que buscas?</h3>
                <p class="pedir-sub">
                  Déjanos tu requerimiento en Cusco. Nos comunicaremos contigo para ayudarte a conectar con un técnico disponible o registrar la necesidad en tu zona.
                </p>
              </div>
            </div>

            <!-- BLOQUEO SI NO ESTÁ AUTENTICADO -->
            <div v-if="!auth.estaAutenticado" class="pedir-auth-lock">
              <div class="lock-icon">🔒</div>
              <h4>Inicia sesión para registrar tu solicitud de oficio</h4>
              <p class="pedir-sub">
                Para solicitar un oficio personalizado y recibir seguimiento directo de nuestro equipo en Cusco, necesitas ingresar con tu cuenta de usuario.
              </p>
              <div class="pedir-lock-actions">
                <router-link to="/login" class="btn-primary">
                  🔑 Iniciar Sesión ➔
                </router-link>
                <router-link to="/registro-cliente" class="btn-secondary">
                  Crear cuenta gratis
                </router-link>
                <a :href="`https://wa.me/51984123456?text=Hola%20T%C3%A9cniCusco,%20estoy%20buscando%20un%20servicio%20de%20${encodeURIComponent(busqueda || 'un oficio no listado')}`" target="_blank" rel="noopener noreferrer" class="btn-whatsapp-sm">
                  💬 Consultar por WhatsApp
                </a>
              </div>
            </div>

            <!-- FORMULARIO PARA USUARIOS AUTENTICADOS -->
            <div v-else class="pedir-form">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Tu Nombre *</label>
                  <input 
                    v-model="formPedido.nombre" 
                    type="text" 
                    maxlength="60"
                    :class="['form-input', errorPedidoNombre ? 'is-invalid' : '']" 
                    placeholder="Ej: Carlos Ramos" 
                    @input="errorPedidoNombre = ''"
                  />
                  <span v-if="errorPedidoNombre" class="form-field-error">⚠️ {{ errorPedidoNombre }}</span>
                </div>
                <div class="form-group">
                  <label class="form-label">Celular en Cusco (9 dígitos) *</label>
                  <input 
                    v-model="formPedido.celular" 
                    type="tel" 
                    maxlength="9" 
                    :class="['form-input', errorPedidoCelular ? 'is-invalid' : '']" 
                    placeholder="984123456" 
                    @input="onInputCelularPedido"
                  />
                  <span v-if="errorPedidoCelular" class="form-field-error">⚠️ {{ errorPedidoCelular }}</span>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Distrito en Cusco *</label>
                  <select v-model="formPedido.distrito" class="form-select">
                    <option value="Cusco">Cusco</option>
                    <option value="Wanchaq">Wanchaq</option>
                    <option value="San Sebastián">San Sebastián</option>
                    <option value="San Jerónimo">San Jerónimo</option>
                    <option value="Santiago">Santiago</option>
                    <option value="Otro">Otro distrito</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">¿Qué oficio o servicio necesitas? *</label>
                  <input 
                    v-model="formPedido.oficio" 
                    type="text" 
                    maxlength="100"
                    :class="['form-input', errorPedidoOficio ? 'is-invalid' : '']" 
                    placeholder="Ej: Tapicero de muebles, Instalador de cámaras, Drywall..." 
                    @input="errorPedidoOficio = ''"
                  />
                  <span v-if="errorPedidoOficio" class="form-field-error">⚠️ {{ errorPedidoOficio }}</span>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Detalle breve del trabajo requerido (máx. 500 caracteres)</label>
                <textarea 
                  v-model="formPedido.descripcion" 
                  rows="2" 
                  maxlength="500"
                  class="form-textarea" 
                  placeholder="Cuéntanos brevemente qué necesitas realizar en tu domicilio o local..."
                ></textarea>
                <span class="form-field-hint" style="text-align: right; display: block; font-size: 11px; margin-top: 4px; color: var(--text3)">
                  {{ formPedido.descripcion.length }}/500 caracteres
                </span>
              </div>

              <div v-if="msgPedidoError" class="alert alert-error">{{ msgPedidoError }}</div>
              <div v-if="msgPedidoExito" class="alert alert-success">{{ msgPedidoExito }}</div>

              <div class="pedir-actions">
                <button class="btn-primary" @click="enviarPedidoEspecial" :disabled="enviandoPedido">
                  {{ enviandoPedido ? 'Guardando requerimiento en sistema...' : 'Registrar requerimiento de servicio ➔' }}
                </button>
                <a :href="`https://wa.me/51984123456?text=Hola%20T%C3%A9cniCusco,%20soy%20${encodeURIComponent(formPedido.nombre || auth.usuario?.first_name || 'un usuario registrado')}%20y%20estoy%20buscando%20un%20servicio%20de%20${encodeURIComponent(formPedido.oficio || busqueda || 'un oficio no listado')}%20en%20${encodeURIComponent(formPedido.distrito)}`" target="_blank" rel="noopener noreferrer" class="btn-whatsapp-sm">
                  💬 Consultar por WhatsApp
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- GRILLA DE RESULTADOS -->
        <div v-else>
          <div class="grid">
            <div v-for="t in tecnicos" :key="t.id" class="worker-card card">
              <div class="wc-top">
                <div class="wc-avatar-wrap">
                  <img 
                    v-if="t.foto_url" 
                    :src="t.foto_url" 
                    class="wc-avatar-img" 
                    :alt="'Foto de perfil del técnico ' + t.usuario.first_name + ' ' + t.usuario.last_name + ' (' + t.oficio + ')'" 
                  />
                  <div v-else class="wc-avatar" :style="{ background: getColor(t.id) }">
                    {{ getIniciales(t.usuario.first_name, t.usuario.last_name) }}
                  </div>
                </div>
                <div class="wc-info">
                  <div class="wc-name">{{ t.usuario.first_name }} {{ t.usuario.last_name }}</div>
                  <div class="wc-job">{{ t.oficio }}</div>
                </div>
              </div>

              <div class="wc-middle">
                <div class="wc-stars-wrap">
                  <div class="wc-stars">
                    <span v-for="n in 5" :key="n">{{ n <= Math.round(t.calificacion_promedio) ? '⭐' : '☆' }}</span>
                  </div>
                  <span class="wc-cal">{{ t.calificacion_promedio.toFixed(1) }} <span class="wc-num-cal">({{ t.num_calificaciones }} reseñas)</span></span>
                </div>
                <span :class="['badge', t.disponible ? 'badge-green' : 'badge-gray']">
                  {{ t.disponible ? '● Disponible' : '● Ocupado' }}
                </span>
              </div>

              <div class="wc-tags">
                <span class="badge badge-blue">{{ t.categoria }}</span>
                <span v-if="t.distancia_km !== null && t.distancia_km !== undefined" class="badge badge-amber">
                  📍 {{ t.distancia_km }} km
                </span>
                <span class="badge badge-gray">{{ t.usuario.distrito || 'Cusco' }}</span>
              </div>

              <div class="wc-footer">
                <router-link :to="`/trabajador/${t.id}`" class="btn-primary wc-btn">
                  Ver perfil completo ➔
                </router-link>
              </div>
            </div>
          </div>

          <!-- BANNER INFERIOR PARA OFICIOS NO LISTADOS -->
          <div class="card banner-otro-oficio">
            <div class="boo-content">
              <span class="boo-icon">💡</span>
              <div>
                <strong>¿Buscas una especialidad o trabajo técnico diferente?</strong>
                <p>Si requieres un servicio no catalogado, puedes dejarnos tu requerimiento o consultarnos vía WhatsApp.</p>
              </div>
            </div>
            <div class="boo-actions">
              <router-link to="/contacto" class="btn-secondary btn-sm">Contactar con soporte</router-link>
              <a href="https://wa.me/51984123456?text=Hola%20T%C3%A9cniCusco,%20busco%20un%20servicio%20t%C3%A9cnico%20especial%20en%20Cusco" target="_blank" rel="noopener noreferrer" class="btn-whatsapp-sm">
                💬 WhatsApp
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- VISTA MAPA -->
      <div v-if="vista === 'mapa'" class="mapa-section card">
        <div v-if="cargando" class="estado">
          <div class="spinner"></div>
          <p>Cargando mapa interactivo...</p>
        </div>
        <div v-else>
          <MapaTecnicos :tecnicos="tecnicos" :lat-usuario="latitud" :lon-usuario="longitud" @seleccionar="irAPerfil" />
          <div v-if="tecnicos.filter(t => t.latitud && t.longitud).length === 0" class="mapa-aviso">
            ℹ️ Los técnicos listados aún no han registrado sus coordenadas GPS exactas.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import type { Trabajador } from '../types'
import { useAuthStore } from '../stores/auth'
import MapaTecnicos from '../components/MapaTecnicos.vue'

const router = useRouter()
const auth = useAuthStore()
const busqueda = ref('')
const categoria = ref('')
const minCalificacion = ref<number>(0)
const soloDisponibles = ref<boolean>(false)
const ordenarPor = ref<'cercania' | 'calificacion' | 'servicios'>('cercania')
const tecnicos = ref<Trabajador[]>([])
const cargando = ref(false)
const buscandoUbicacion = ref(false)
const usandoUbicacion = ref(false)
const latitud = ref<number | null>(null)
const longitud = ref<number | null>(null)
const vista = ref<'lista' | 'mapa'>('lista')

// FORMULARIO PEDIDO ESPECIAL (Solo usuarios autenticados)
const formPedido = ref({
  nombre: '',
  celular: '',
  distrito: 'Wanchaq',
  oficio: '',
  descripcion: ''
})
const enviandoPedido = ref(false)
const msgPedidoError = ref('')
const msgPedidoExito = ref('')
const errorPedidoNombre = ref('')
const errorPedidoCelular = ref('')
const errorPedidoOficio = ref('')

function inicializarFormularioConUsuario() {
  if (auth.estaAutenticado && auth.usuario) {
    const nombreCompleto = `${auth.usuario.first_name || ''} ${auth.usuario.last_name || ''}`.trim()
    formPedido.value.nombre = nombreCompleto || auth.usuario.username
    formPedido.value.celular = auth.usuario.celular || ''
    if (auth.usuario.distrito) {
      formPedido.value.distrito = auth.usuario.distrito
    }
  }
}

function onInputCelularPedido() {
  formPedido.value.celular = formPedido.value.celular.replace(/\D/g, '').slice(0, 9)
  errorPedidoCelular.value = ''
}

async function enviarPedidoEspecial() {
  msgPedidoError.value = ''
  msgPedidoExito.value = ''
  errorPedidoNombre.value = ''
  errorPedidoCelular.value = ''
  errorPedidoOficio.value = ''

  if (!auth.estaAutenticado) {
    msgPedidoError.value = 'Debes iniciar sesión con tu cuenta para registrar un requerimiento.'
    return
  }

  if (!formPedido.value.nombre.trim()) {
    errorPedidoNombre.value = 'Ingresa tu nombre'
  } else if (formPedido.value.nombre.trim().length < 2) {
    errorPedidoNombre.value = 'El nombre es muy corto'
  }

  const cel = formPedido.value.celular.replace(/\D/g, '')
  if (!cel) {
    errorPedidoCelular.value = 'Ingresa tu número celular'
  } else if (!/^9\d{8}$/.test(cel)) {
    errorPedidoCelular.value = 'Debe ser un celular válido de 9 dígitos (inicia con 9)'
  }

  if (!formPedido.value.oficio.trim()) {
    errorPedidoOficio.value = 'Indica qué trabajo u oficio necesitas'
  } else if (formPedido.value.oficio.trim().length < 3) {
    errorPedidoOficio.value = 'Escribe al menos 3 caracteres'
  }

  if (errorPedidoNombre.value || errorPedidoCelular.value || errorPedidoOficio.value) {
    msgPedidoError.value = 'Por favor completa correctamente los campos señalados.'
    return
  }

  enviandoPedido.value = true
  try {
    const payload = {
      nombre_contacto: formPedido.value.nombre,
      celular_contacto: formPedido.value.celular,
      distrito: formPedido.value.distrito,
      oficio_solicitado: formPedido.value.oficio,
      descripcion: formPedido.value.descripcion
    }
    await api.post('/solicitudes/requerimientos/crear/', payload)
    
    msgPedidoExito.value = `✅ ¡Requerimiento registrado con éxito! Se ha guardado en el sistema y nuestro equipo en Cusco se comunicará contigo al ${formPedido.value.celular}.`
    setTimeout(() => {
      formPedido.value.oficio = ''
      formPedido.value.descripcion = ''
    }, 4500)
  } catch (err: any) {
    msgPedidoError.value = err.response?.data?.error || err.response?.data?.detail || 'No se pudo registrar el requerimiento. Por favor intenta de nuevo o contáctanos por WhatsApp.'
  } finally {
    enviandoPedido.value = false
  }
}

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

const opcionesCalif = [
  { val: 0, texto: 'Todas' },
  { val: 4.0, texto: '⭐ 4.0+' },
  { val: 4.5, texto: '⭐ 4.5+' },
]

const hayFiltrosActivos = computed(() => {
  return busqueda.value || categoria.value || minCalificacion.value > 0 || soloDisponibles.value || ordenarPor.value !== 'cercania' || usandoUbicacion.value
})

function getIniciales(nombre?: string, apellido?: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}

function getColor(id: number) {
  const colores = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return colores[id % colores.length]
}

function setMinCalif(val: number) {
  minCalificacion.value = val
  buscar()
}

function toggleDisponibles() {
  soloDisponibles.value = !soloDisponibles.value
  buscar()
}

function resetearFiltros() {
  busqueda.value = ''
  categoria.value = ''
  minCalificacion.value = 0
  soloDisponibles.value = false
  ordenarPor.value = 'cercania'
  limpiarUbicacion()
}

async function buscar() {
  cargando.value = true
  try {
    const params: Record<string, string | number | boolean> = {}
    if (busqueda.value.trim()) params.busqueda = busqueda.value.trim()
    if (categoria.value) params.categoria = categoria.value
    if (minCalificacion.value > 0) params.min_calificacion = minCalificacion.value
    if (soloDisponibles.value) params.solo_disponibles = true
    if (ordenarPor.value) params.ordenar_por = ordenarPor.value

    if (latitud.value && longitud.value) {
      params.lat = latitud.value
      params.lon = longitud.value
      params.radio = 10
    }
    const res = await api.get<Trabajador[]>('/trabajadores/', { params })
    tecnicos.value = res.data

    // Si no hay resultados y el usuario escribió algo en búsqueda, precargar el campo de oficio
    if (res.data.length === 0 && busqueda.value.trim()) {
      formPedido.value.oficio = busqueda.value.trim()
    }
  } catch (error) {
    console.error('Error al buscar técnicos:', error)
  } finally {
    cargando.value = false
  }
}

function usarUbicacion() {
  if (!navigator.geolocation) return alert('Tu navegador no soporta geolocalización')
  buscandoUbicacion.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      latitud.value = pos.coords.latitude
      longitud.value = pos.coords.longitude
      usandoUbicacion.value = true
      buscandoUbicacion.value = false
      vista.value = 'mapa'
      buscar()
    },
    () => {
      alert('No se pudo obtener tu ubicación. Asegúrate de otorgar permisos de GPS.')
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

function irAPerfil(id: number) {
  router.push(`/trabajador/${id}`)
}

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const cat = urlParams.get('categoria')
  if (cat) categoria.value = cat
  buscar()
})
</script>

<style scoped>
.page {
  min-height: calc(100vh - 68px);
  display: flex;
  flex-direction: column;
}

.search-header {
  padding: 40px 24px 30px;
  background: var(--surface-glass);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(16px);
}

.search-inner {
  max-width: 1180px;
  margin: 0 auto;
}

.search-titles {
  margin-bottom: 24px;
}

.search-tag {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--primary);
  text-transform: uppercase;
}

.search-titles h1 {
  font-size: 32px;
  font-weight: 800;
  margin: 4px 0 6px;
}

.search-titles p {
  font-size: 15px;
  color: var(--text2);
}

.search-bar {
  display: flex;
  gap: 12px;
  padding: 10px;
  align-items: center;
  box-shadow: var(--shadow-md);
  flex-wrap: wrap;
}

.search-input-wrap {
  flex: 2;
  min-width: 260px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.search-icon {
  font-size: 16px;
  color: var(--text3);
}

.search-input {
  width: 100%;
  padding: 14px 0;
  border: none;
  background: transparent;
  font-size: 14.5px;
  color: var(--text);
  outline: none;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.select-wrapper {
  flex: 1;
  min-width: 180px;
}

.search-select {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subtle);
  color: var(--text);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.btn-geo {
  padding: 14px 22px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.btn-clear-geo {
  padding: 14px 16px;
  font-size: 13px;
}

/* FILTROS AVANZADOS */
.filtros-avanzados-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.filtro-grupo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filtro-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
}

.btn-filtro-pill {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text2);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-filtro-pill:hover {
  background: var(--surface-subtle);
  color: var(--text);
}

.btn-filtro-pill.activo {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.btn-filtro-pill.activo-verde {
  background: #10B981;
  color: #fff;
  border-color: transparent;
}

.dot-verde {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
}

.btn-filtro-pill.activo-verde .dot-verde {
  background: #fff;
}

.sort-select {
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}

.btn-reset-filtros {
  background: transparent;
  border: none;
  color: var(--red);
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  padding: 4px 8px;
}

.btn-reset-filtros:hover {
  text-decoration: underline;
}

.ubicacion-aviso {
  margin-top: 14px;
  padding: 10px 16px;
  background: var(--primary-light);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--primary);
  border: 1px solid rgba(79, 70, 229, 0.2);
}

/* VISTA TOGGLE */
.vista-toggle-bar {
  padding: 16px 24px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.vista-inner {
  max-width: 1180px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.resultados-count {
  font-size: 14px;
  color: var(--text2);
}

.vista-btns {
  display: flex;
  gap: 8px;
}

.vista-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  background: var(--surface-subtle);
  color: var(--text2);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.vista-btn:hover {
  color: var(--text);
}

.vista-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

/* CONTENIDO */
.contenido {
  max-width: 1180px;
  margin: 32px auto;
  padding: 0 24px;
  flex: 1;
  width: 100%;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.worker-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.wc-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.wc-avatar-wrap {
  width: 58px;
  height: 58px;
  flex-shrink: 0;
}

.wc-avatar-img {
  width: 58px;
  height: 58px;
  border-radius: 16px;
  object-fit: cover;
  border: 2px solid var(--border);
}

.wc-avatar {
  width: 58px;
  height: 58px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  box-shadow: var(--shadow-sm);
}

.wc-info {
  flex: 1;
  min-width: 0;
}

.wc-name {
  font-size: 17px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 3px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wc-job {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.3;
}

.wc-middle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.wc-stars-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wc-stars {
  font-size: 14px;
}

.wc-cal {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
}

.wc-num-cal {
  font-size: 12px;
  font-weight: 500;
  color: var(--text3);
}

.wc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 20px;
}

.wc-footer {
  margin-top: auto;
}

.wc-btn {
  width: 100%;
  padding: 12px;
  font-size: 13.5px;
  font-weight: 700;
}

/* ======================================================== */
/* MÓDULO PIDE TU TÉCNICO / 0 RESULTADOS                   */
/* ======================================================== */
.no-results-wrap {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 760px;
  margin: 0 auto;
}

.empty-card {
  text-align: center;
  padding: 36px 24px;
}

.empty-card h3 {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 8px;
}

.pedir-card {
  padding: 36px 32px;
}

.pedir-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.pedir-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-light);
  border: 1px solid rgba(79, 70, 229, 0.25);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.pedir-header h3 {
  font-size: 19px;
  font-weight: 800;
  margin-bottom: 6px;
}

.pedir-sub {
  font-size: 14px;
  color: var(--text2);
  line-height: 1.55;
  margin: 0;
}

/* ESTADO BLOQUEADO PARA NO AUTENTICADOS */
.pedir-auth-lock {
  padding: 24px 20px;
  background: var(--surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  text-align: center;
}

.pedir-auth-lock .lock-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.pedir-auth-lock h4 {
  font-size: 17px;
  font-weight: 800;
  margin-bottom: 8px;
  color: var(--text);
}

.pedir-lock-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 18px;
}

.pedir-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 16px;
}

.btn-whatsapp-sm {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #25D366;
  color: #fff;
  text-decoration: none;
  padding: 11px 18px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: all 0.2s ease;
}

.btn-whatsapp-sm:hover {
  background: #20BA5A;
  transform: translateY(-1px);
}

/* BANNER INFERIOR DE OFICIOS NO LISTADOS */
.banner-otro-oficio {
  margin-top: 36px;
  padding: 22px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  background: var(--surface-subtle);
}

.boo-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.boo-icon {
  font-size: 28px;
}

.boo-content strong {
  display: block;
  font-size: 14.5px;
  color: var(--text);
  margin-bottom: 2px;
}

.boo-content p {
  font-size: 13px;
  color: var(--text2);
  margin: 0;
}

.boo-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.mapa-section {
  padding: 24px;
}

.mapa-aviso {
  margin-top: 14px;
  padding: 10px 16px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text2);
  border: 1px solid var(--border);
}

.estado {
  text-align: center;
  padding: 60px 24px;
  color: var(--text2);
}

.spinner {
  width: 44px;
  height: 44px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@media (max-width: 640px) {
  .pedir-card {
    padding: 24px 18px;
  }
  .pedir-header {
    flex-direction: column;
    gap: 10px;
  }
  .pedir-actions {
    flex-direction: column;
  }
  .pedir-actions button,
  .pedir-actions a {
    width: 100%;
    justify-content: center;
  }
  .banner-otro-oficio {
    flex-direction: column;
    align-items: flex-start;
  }
  .boo-actions {
    width: 100%;
    flex-direction: column;
  }
  .boo-actions a {
    width: 100%;
    justify-content: center;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>