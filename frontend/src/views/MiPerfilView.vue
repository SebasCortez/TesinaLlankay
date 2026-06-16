<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header-inner">
        <div class="perfil-top">
          <div class="perfil-avatar">
            {{ auth.usuario?.first_name?.[0] }}{{ auth.usuario?.last_name?.[0] }}
          </div>
          <div>
            <h1>{{ auth.usuario?.first_name }} {{ auth.usuario?.last_name }}</h1>
            <span :class="['badge', rolBadge[auth.usuario?.rol]]">{{ rolTexto[auth.usuario?.rol] }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="contenedor">
      <div class="layout">

        <!-- Info personal -->
        <div class="card seccion">
          <h3>Información personal</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Nombre completo</span>
              <span class="info-val">{{ auth.usuario?.first_name }} {{ auth.usuario?.last_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Usuario</span>
              <span class="info-val">@{{ auth.usuario?.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Correo</span>
              <span class="info-val">{{ auth.usuario?.email || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Celular</span>
              <span class="info-val">{{ auth.usuario?.celular || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Distrito</span>
              <span class="info-val">{{ auth.usuario?.distrito || '—' }}, Cusco</span>
            </div>
          </div>
        </div>

        <!-- Perfil técnico si es trabajador -->
        <div v-if="auth.esTrabajador && perfil" class="card seccion">
          <div class="seccion-header">
            <h3>Mi perfil técnico</h3>
            <span :class="['badge', estadoBadge[perfil.estado]]">{{ estadoTexto[perfil.estado] }}</span>
          </div>

          <div v-if="perfil.estado === 'pendiente'" class="alert alert-warning">
            ⏳ Tu solicitud está siendo revisada por un administrador. Te avisaremos pronto.
          </div>
          <div v-if="perfil.estado === 'rechazado'" class="alert alert-error">
            ❌ Tu solicitud fue rechazada. Motivo: <strong>{{ perfil.motivo_rechazo }}</strong>
          </div>
          <div v-if="perfil.estado === 'aprobado'" class="alert alert-success">
            ✅ ¡Estás aprobado! Ya apareces en los resultados de búsqueda.
          </div>

          <div class="info-grid" style="margin-top:16px">
            <div class="info-item">
              <span class="info-label">Categoría</span>
              <span class="info-val">{{ perfil.categoria }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Oficio</span>
              <span class="info-val">{{ perfil.oficio }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Experiencia</span>
              <span class="info-val">{{ perfil.experiencia }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Calificación</span>
              <span class="info-val">⭐ {{ perfil.calificacion_promedio.toFixed(1) }} ({{ perfil.num_calificaciones }}
                calif.)</span>
            </div>
          </div>

          <!-- Actualizar ubicación -->
          <div v-if="perfil.estado === 'aprobado'" class="ubicacion-box">
            <div class="ubicacion-info">
              <div class="ubicacion-title">📍 Mi ubicación</div>
              <div class="ubicacion-desc">Actualiza tu ubicación para que los clientes cercanos te encuentren más
                fácilmente.</div>
            </div>
            <button class="btn-primary" @click="actualizarUbicacion" :disabled="actualizando">
              {{ actualizando ? '📍 Obteniendo...' : '📍 Actualizar ubicación' }}
            </button>
          </div>
          <div v-if="ubicacionMsg" class="alert alert-success" style="margin-top:12px">{{ ubicacionMsg }}</div>
        </div>

        <!-- Stats si es trabajador aprobado -->
        <div v-if="auth.esTrabajador && perfil && perfil.estado === 'aprobado'" class="stats-row">
          <div class="stat-card card">
            <div class="stat-num">{{ perfil.num_calificaciones }}</div>
            <div class="stat-label">Servicios</div>
          </div>
          <div class="stat-card card">
            <div class="stat-num">{{ perfil.calificacion_promedio.toFixed(1) }}⭐</div>
            <div class="stat-label">Calificación</div>
          </div>
          <div class="stat-card card">
            <div class="stat-num" style="color:var(--green)">{{ perfil.disponible ? 'Sí' : 'No' }}</div>
            <div class="stat-label">Disponible</div>
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
const perfil = ref<any>(null)
const actualizando = ref(false)
const ubicacionMsg = ref('')

const rolTexto: any = { cliente: 'Cliente', trabajador: 'Técnico', admin: 'Administrador' }
const rolBadge: any = { cliente: 'badge-blue', trabajador: 'badge-green', admin: 'badge-amber' }
const estadoTexto: any = { pendiente: '⏳ Pendiente', aprobado: '✅ Aprobado', rechazado: '❌ Rechazado' }
const estadoBadge: any = { pendiente: 'badge-amber', aprobado: 'badge-green', rechazado: 'badge-red' }

async function cargarPerfil() {
  if (!auth.esTrabajador) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/trabajadores/mi-perfil/')
    perfil.value = res.data
  } catch (e) { console.error(e) }
}

function actualizarUbicacion() {
  if (!navigator.geolocation) return alert('Tu navegador no soporta geolocalización')
  actualizando.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        await axios.patch('http://127.0.0.1:8000/api/trabajadores/ubicacion/', {
          latitud: pos.coords.latitude,
          longitud: pos.coords.longitude,
        })
        ubicacionMsg.value = '✅ Ubicación actualizada correctamente'
        setTimeout(() => ubicacionMsg.value = '', 3000)
      } catch {
        alert('Error al actualizar ubicación')
      } finally { actualizando.value = false }
    },
    () => { alert('No se pudo obtener tu ubicación'); actualizando.value = false }
  )
}

onMounted(() => cargarPerfil())
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
  max-width: 720px;
  margin: 0 auto;
}

.perfil-top {
  display: flex;
  align-items: center;
  gap: 16px;
}

.perfil-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  border: 3px solid var(--border);
}

.perfil-top h1 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.contenedor {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 32px;
}

.layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.seccion {
  padding: 24px;
}

.seccion h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}

.seccion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.seccion-header h3 {
  margin-bottom: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.info-item {
  background: var(--bg);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  border: 1px solid var(--border);
}

.info-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.info-val {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

.ubicacion-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 20px;
  padding: 16px;
  background: var(--bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.ubicacion-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.ubicacion-desc {
  font-size: 13px;
  color: var(--text2);
}

.stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 14px;
}

.stat-card {
  padding: 20px;
  text-align: center;
}

.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
}

.stat-label {
  font-size: 12px;
  color: var(--text2);
  margin-top: 4px;
}
</style>