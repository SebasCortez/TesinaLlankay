<template>
  <div class="captcha-widget">
    <div class="captcha-header">
      <label class="form-label captcha-label">
        <span class="shield-icon">🛡️</span> Verificación de Seguridad (CAPTCHA)
      </label>
      <button
        type="button"
        class="btn-refresh-captcha"
        @click="refrescarCaptcha"
        :disabled="cargando"
        title="Generar nuevo código de verificación"
        aria-label="Refrescar CAPTCHA"
      >
        <span :class="['refresh-icon', cargando ? 'spinning' : '']">🔄</span>
        <span>Cambiar código</span>
      </button>
    </div>

    <div class="captcha-content">
      <!-- Visor SVG del CAPTCHA -->
      <div class="captcha-image-wrapper">
        <div v-if="cargando" class="captcha-skeleton">
          <div class="spinner-sm"></div>
          <span>{{ estadoTexto }}</span>
        </div>
        <div v-else-if="errorCarga" class="captcha-error-card">
          <span>⚠️ Error de conexión</span>
          <button type="button" @click="() => obtenerNuevoCaptcha(0)" class="btn-retry-sm">🔄 Reintentar</button>
        </div>
        <div v-else class="captcha-svg-container" v-html="svgContent"></div>
      </div>

      <!-- Input de Respuesta -->
      <div class="captcha-input-wrapper">
        <input
          v-model="respuestaUsuario"
          type="text"
          class="form-input captcha-input"
          :class="{ 'is-invalid': tieneError }"
          placeholder="Resultado"
          maxlength="10"
          autocomplete="off"
          @input="emitirRespuesta"
          @keydown.enter="$emit('submit')"
        />
      </div>
    </div>

    <span v-if="tieneError" class="form-field-error">
      ⚠️ {{ mensajeError || 'Por favor resuelve el cálculo de seguridad' }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'

interface CaptchaResponse {
  captcha_key: string
  svg_image: string
  pregunta?: string
  expira_en_segundos?: number
}

const props = defineProps<{
  tieneError?: boolean
  mensajeError?: string
}>()

const emit = defineEmits<{
  (e: 'update:captcha', data: { key: string; value: string }): void
  (e: 'submit'): void
}>()

const cargando = ref(false)
const errorCarga = ref(false)
const captchaKey = ref('')
const svgContent = ref('')
const respuestaUsuario = ref('')
const estadoTexto = ref('Generando reto...')
const maxIntentos = 4

async function obtenerNuevoCaptcha(reintento = 0) {
  cargando.value = true
  errorCarga.value = false
  if (reintento === 0) {
    respuestaUsuario.value = ''
    emit('update:captcha', { key: '', value: '' })
  }

  if (reintento > 0) {
    estadoTexto.value = `Conectando (${reintento + 1}/${maxIntentos})...`
  } else {
    estadoTexto.value = 'Cargando reto...'
  }

  try {
    const res = await api.get<CaptchaResponse>('/usuarios/captcha/', { timeout: 12000 })
    captchaKey.value = res.data.captcha_key
    svgContent.value = res.data.svg_image
    errorCarga.value = false
    cargando.value = false
    emit('update:captcha', { key: captchaKey.value, value: respuestaUsuario.value })
  } catch (err: any) {
    console.warn(`Intento ${reintento + 1} de cargar CAPTCHA falló:`, err)
    if (reintento < maxIntentos - 1) {
      setTimeout(() => {
        obtenerNuevoCaptcha(reintento + 1)
      }, 2000)
    } else {
      cargando.value = false
      errorCarga.value = true
    }
  }
}

function emitirRespuesta() {
  emit('update:captcha', { key: captchaKey.value, value: respuestaUsuario.value.trim() })
}

function refrescarCaptcha() {
  obtenerNuevoCaptcha(0)
}

onMounted(() => {
  obtenerNuevoCaptcha(0)
})

defineExpose({
  obtenerNuevoCaptcha: () => obtenerNuevoCaptcha(0),
  limpiar: () => {
    respuestaUsuario.value = ''
    obtenerNuevoCaptcha(0)
  }
})
</script>

<style scoped>
.captcha-widget {
  margin-bottom: 18px;
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
}

.captcha-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.captcha-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.shield-icon {
  font-size: 0.95rem;
}

.btn-refresh-captcha {
  background: transparent;
  border: none;
  color: var(--primary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-refresh-captcha:hover {
  background: var(--primary-light);
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.3s ease;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.captcha-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.captcha-image-wrapper {
  flex: 1;
  min-height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
}

.captcha-svg-container {
  width: 100%;
  display: flex;
  align-items: center;
}

.captcha-svg-container :deep(svg) {
  width: 100%;
  height: 52px;
  display: block;
}

.captcha-skeleton {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--text3);
}

.captcha-error-card {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--red);
}

.btn-retry-sm {
  background: var(--red-light);
  border: 1px solid var(--red);
  color: var(--red);
  font-size: 0.72rem;
  font-weight: 700;
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
}

.captcha-input-wrapper {
  width: 110px;
  flex-shrink: 0;
}

.captcha-input {
  text-align: center;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 10px 8px;
  height: 52px;
}

.form-field-error {
  display: block;
  font-size: 0.76rem;
  color: var(--red);
  margin-top: 6px;
  font-weight: 600;
}
</style>
