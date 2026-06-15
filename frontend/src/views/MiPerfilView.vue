<template>
  <div class="contenedor">
    <div class="card" v-if="auth.usuario">
      <h2>Mi perfil</h2>
      <div class="info-row"><span>Nombre</span><strong>{{ auth.usuario.first_name }} {{ auth.usuario.last_name }}</strong></div>
      <div class="info-row"><span>Usuario</span><strong>{{ auth.usuario.username }}</strong></div>
      <div class="info-row"><span>Correo</span><strong>{{ auth.usuario.email }}</strong></div>
      <div class="info-row"><span>Celular</span><strong>{{ auth.usuario.celular }}</strong></div>
      <div class="info-row"><span>Distrito</span><strong>{{ auth.usuario.distrito }}</strong></div>
      <div class="info-row"><span>Rol</span><strong class="rol">{{ auth.usuario.rol }}</strong></div>

      <!-- Si es trabajador -->
      <div v-if="auth.esTrabajador && perfil">
        <hr>
        <h3>Mi perfil técnico</h3>
        <div :class="['estado-badge', perfil.estado]">
          {{ estadoTexto[perfil.estado] }}
        </div>
        <div v-if="perfil.estado === 'pendiente'" class="aviso-pendiente">
          ⏳ Tu solicitud está siendo revisada por un administrador. Te notificaremos pronto.
        </div>
        <div v-if="perfil.estado === 'rechazado'" class="aviso-rechazo">
          ❌ Tu solicitud fue rechazada. Motivo: {{ perfil.motivo_rechazo }}
        </div>
        <div v-if="perfil.estado === 'aprobado'" class="aviso-aprobado">
          ✅ ¡Estás aprobado! Ya apareces en los resultados de búsqueda.
        </div>
        <div class="info-row"><span>Categoría</span><strong>{{ perfil.categoria }}</strong></div>
        <div class="info-row"><span>Oficio</span><strong>{{ perfil.oficio }}</strong></div>
        <div class="info-row"><span>Experiencia</span><strong>{{ perfil.experiencia }}</strong></div>
        <div class="info-row"><span>Calificación</span><strong>⭐ {{ perfil.calificacion_promedio.toFixed(1) }} ({{ perfil.num_calificaciones }} calif.)</strong></div>

        <div v-if="perfil.estado === 'aprobado'" class="ubicacion-seccion">
          <h3>Mi ubicación actual</h3>
          <p class="ubicacion-desc">Actualiza tu ubicación para que los clientes cercanos puedan encontrarte.</p>
          <button class="btn-verde" @click="actualizarUbicacion" :disabled="actualizando">
            {{ actualizando ? '📍 Obteniendo ubicación...' : '📍 Actualizar mi ubicación' }}
          </button>
          <div v-if="ubicacionMsg" class="exito">{{ ubicacionMsg }}</div>
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

const estadoTexto: any = {
  pendiente: '⏳ Pendiente de aprobación',
  aprobado: '✅ Aprobado',
  rechazado: '❌ Rechazado'
}

async function cargarPerfil() {
  if (!auth.esTrabajador) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/trabajadores/mi-perfil/')
    perfil.value = res.data
  } catch (e) {
    console.error(e)
  }
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
      } catch (e) {
        alert('Error al actualizar ubicación')
      } finally {
        actualizando.value = false
      }
    },
    () => {
      alert('No se pudo obtener tu ubicación')
      actualizando.value = false
    }
  )
}

onMounted(() => cargarPerfil())
</script>

<style scoped>
.contenedor { max-width: 600px; margin: 40px auto; padding: 0 24px; }
.card { background: #fff; border: 1px solid #e0e0e0; border-radius: 16px; padding: 32px; }
h2 { font-size: 20px; font-weight: 700; margin-bottom: 20px; }
h3 { font-size: 16px; font-weight: 600; margin: 20px 0 12px; }
.info-row { display: flex; justify-content: space-between; font-size: 14px; padding: 8px 0; border-bottom: 1px solid #f0eeea; }
.info-row span { color: #888; }
.rol { text-transform: capitalize; color: #1D9E75; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 20px 0; }
.estado-badge {
  display: inline-block; padding: 6px 14px;
  border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 12px;
}
.estado-badge.pendiente { background: #FFF8E1; color: #7A5800; }
.estado-badge.aprobado { background: #e1f5ee; color: #0f6e56; }
.estado-badge.rechazado { background: #fde8e8; color: #c0392b; }
.aviso-pendiente { background: #FFF8E1; border: 1px solid #FFD54F; color: #7A5800; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; }
.aviso-aprobado { background: #e1f5ee; border: 1px solid #5DCAA5; color: #0f6e56; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; }
.aviso-rechazo { background: #fde8e8; border: 1px solid #f5a5a5; color: #c0392b; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; }
.ubicacion-seccion { margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0; }
.ubicacion-desc { font-size: 13px; color: #666; margin-bottom: 12px; }
.btn-verde {
  padding: 10px 20px; background: #1D9E75; color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn-verde:disabled { background: #aaa; cursor: not-allowed; }
.exito { background: #e1f5ee; color: #0f6e56; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 10px; }
</style>