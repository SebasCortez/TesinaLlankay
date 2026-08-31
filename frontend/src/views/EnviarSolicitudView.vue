<template>
  <div class="page-center">
    <div class="solicitud-wrapper" v-if="trabajador">
      <div class="solicitud-glow"></div>
      <div class="card solicitud-card">
        <div class="sol-header">
          <div class="sol-avatar-wrap">
            <img 
              v-if="trabajador.foto_url" 
              :src="trabajador.foto_url" 
              class="sol-avatar-img" 
              :alt="'Foto de perfil del técnico ' + trabajador.usuario.first_name + ' ' + trabajador.usuario.last_name" 
            />
            <div v-else class="sol-avatar" :style="{ background: getColor(trabajador.id) }">
              {{ getIniciales(trabajador.usuario.first_name, trabajador.usuario.last_name) }}
            </div>
          </div>
          <div>
            <h2>{{ trabajador.usuario.first_name }} {{ trabajador.usuario.last_name }}</h2>
            <p class="sol-oficio">{{ trabajador.oficio }} · {{ trabajador.categoria }}</p>
          </div>
        </div>

        <hr class="divider">

        <h3>Solicitud de Servicio</h3>
        <p class="sol-desc">Describe tu requerimiento con detalle para coordinar la visita técnica y presupuesto.</p>

        <div class="form-group">
          <label class="form-label">Mensaje o Asunto Breve * (máx. 200 caracteres)</label>
          <textarea 
            v-model="form.mensaje" 
            maxlength="200"
            :class="['form-textarea', errores.mensaje ? 'is-invalid' : '']"
            placeholder="Ej: Hola, requiero una visita técnica para revisar una avería eléctrica en mi domicilio..." 
            rows="2"
            @input="errores.mensaje = ''"
          ></textarea>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span v-if="errores.mensaje" class="form-field-error">⚠️ {{ errores.mensaje }}</span>
            <span v-else></span>
            <span class="form-field-hint" style="font-size: 11px; color: var(--text3)">{{ form.mensaje.length }}/200</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción Detallada del Trabajo o Falla * (máx. 1000 caracteres)</label>
          <textarea 
            v-model="form.descripcion_problema" 
            maxlength="1000"
            :class="['form-textarea', errores.descripcion_problema ? 'is-invalid' : '']"
            placeholder="Describe qué sucede, desde cuándo ocurre, herramientas o materiales necesarios..."
            rows="3"
            @input="errores.descripcion_problema = ''"
          ></textarea>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span v-if="errores.descripcion_problema" class="form-field-error">⚠️ {{ errores.descripcion_problema }}</span>
            <span v-else></span>
            <span class="form-field-hint" style="font-size: 11px; color: var(--text3)">{{ form.descripcion_problema.length }}/1000</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Dirección exacta del trabajo en Cusco * (máx. 150 caracteres)</label>
          <input 
            v-model="form.direccion" 
            type="text"
            maxlength="150"
            :class="['form-input', errores.direccion ? 'is-invalid' : '']" 
            placeholder="Ej: Av. Tullumayo 450, Wanchaq, Cusco" 
            @input="errores.direccion = ''"
          />
          <span v-if="errores.direccion" class="form-field-error">⚠️ {{ errores.direccion }}</span>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="exito" class="alert alert-success">{{ exito }}</div>

        <div class="sol-btns">
          <router-link :to="`/trabajador/${trabajador.id}`" class="btn-secondary">← Volver al perfil</router-link>
          <button class="btn-primary" @click="enviar" :disabled="cargando">
            {{ cargando ? 'Enviando solicitud...' : 'Enviar solicitud ➔' }}
          </button>
        </div>
      </div>
    </div>
    <div v-else class="estado-carga">
      <div class="spinner"></div>
      <p>Cargando información del técnico...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import type { Trabajador } from '../types'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const trabajador = ref<Trabajador | null>(null)
const error = ref('')
const exito = ref('')
const errores = ref<{ [key: string]: string }>({})
const cargando = ref(false)
const form = ref({ mensaje: '', descripcion_problema: '', direccion: '' })

function getIniciales(nombre?: string, apellido?: string) {
  return (nombre?.[0] || '') + (apellido?.[0] || '')
}

function getColor(id: number) {
  const colores = ['#DBEAFE', '#D1FAE5', '#FEF3C7', '#FCE7F3', '#EDE9FE', '#FFEDD5']
  return colores[id % colores.length]
}

async function cargarTrabajador() {
  try {
    const res = await api.get<Trabajador>(`/trabajadores/${route.params.id}/`)
    trabajador.value = res.data
  } catch (err) {
    console.error('Error al cargar datos del trabajador:', err)
  }
}

function validar(): boolean {
  errores.value = {}
  error.value = ''

  if (!form.value.mensaje.trim()) {
    errores.value.mensaje = 'Por favor escribe un mensaje o asunto inicial.'
  } else if (form.value.mensaje.trim().length < 5) {
    errores.value.mensaje = 'El mensaje debe tener al menos 5 caracteres.'
  }

  if (!form.value.descripcion_problema.trim()) {
    errores.value.descripcion_problema = 'Describe el trabajo o problema a resolver.'
  } else if (form.value.descripcion_problema.trim().length < 10) {
    errores.value.descripcion_problema = 'Por favor describe con más detalle (al menos 10 caracteres).'
  }

  if (!form.value.direccion.trim()) {
    errores.value.direccion = 'Indica la dirección del trabajo en Cusco.'
  } else if (form.value.direccion.trim().length < 5) {
    errores.value.direccion = 'La dirección debe ser más específica (al menos 5 caracteres).'
  }

  return Object.keys(errores.value).length === 0
}

async function enviar() {
  if (!validar()) {
    error.value = 'Completa los campos obligatorios señalados en rojo.'
    return
  }

  if (trabajador.value && trabajador.value.usuario.id === auth.usuario?.id) {
    error.value = 'No puedes enviarte una solicitud de servicio a ti mismo.'
    return
  }

  cargando.value = true
  try {
    await api.post('/solicitudes/crear/', {
      trabajador: route.params.id,
      ...form.value
    })
    
    // Redirigir a página de Gracias
    router.push({
      path: '/gracias',
      query: {
        tipo: 'solicitud',
        tecnico: `${trabajador.value?.usuario.first_name || ''} ${trabajador.value?.usuario.last_name || ''}`.trim()
      }
    })
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Error al enviar la solicitud. Inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
}

onMounted(() => cargarTrabajador())
</script>

<style scoped>
.solicitud-wrapper {
  position: relative;
  width: 540px;
  max-width: 100%;
}

.solicitud-glow {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 300px;
  background: var(--primary-glow);
  filter: blur(50px);
  pointer-events: none;
}

.solicitud-card {
  padding: 36px;
  position: relative;
  z-index: 1;
}

.sol-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sol-avatar-wrap {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
}

.sol-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sol-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: var(--text);
}

.sol-header h2 {
  font-size: 19px;
  font-weight: 800;
  margin-bottom: 2px;
}

.sol-oficio {
  font-size: 13.5px;
  color: var(--text2);
}

.sol-desc {
  font-size: 13.5px;
  color: var(--text2);
  margin-bottom: 20px;
}

.sol-btns {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 24px;
}

.estado-carga {
  text-align: center;
  padding: 40px;
  color: var(--text2);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@media (max-width: 540px) {
  .solicitud-card {
    padding: 24px 16px;
  }
  .sol-btns {
    flex-direction: column;
  }
  .sol-btns button,
  .sol-btns a {
    width: 100%;
    justify-content: center;
  }
}
</style>