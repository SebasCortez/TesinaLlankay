<template>
  <div class="page-center">
    <div class="recover-wrapper">
      <div class="recover-glow"></div>
      <div class="recover-card card">
        <div class="recover-header">
          <div class="recover-icon">🔑</div>
          <h2>Recuperar Contraseña</h2>
          <p>Ingresa tu correo registrado y te enviaremos un enlace seguro para restablecerla.</p>
        </div>

        <div class="form-group">
          <label class="form-label">Correo Electrónico</label>
          <input
            v-model="email"
            type="email"
            maxlength="80"
            :class="['form-input', error ? 'is-invalid' : '']"
            placeholder="tucorreo@ejemplo.com"
            @input="error = ''"
            @keydown.enter="solicitarRecuperacion"
            :disabled="enviado"
          />
          <span v-if="error" class="form-field-error">⚠️ {{ error }}</span>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="mensaje" class="alert alert-success">{{ mensaje }}</div>

        <button
          v-if="!enviado"
          class="btn-primary btn-submit"
          @click="solicitarRecuperacion"
          :disabled="cargando"
        >
          {{ cargando ? 'Enviando enlace...' : 'Enviar enlace de recuperación ➔' }}
        </button>

        <div v-else class="enviado-acciones">
          <button class="btn-secondary" @click="enviado = false; mensaje = ''">
            Probar con otro correo
          </button>
        </div>

        <hr class="divider">

        <p class="recover-footer">
          ¿Recordaste tu contraseña?
          <router-link to="/login" class="login-link">Volver al inicio de sesión</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'

const email = ref('')
const cargando = ref(false)
const error = ref('')
const mensaje = ref('')
const enviado = ref(false)

async function solicitarRecuperacion() {
  error.value = ''
  mensaje.value = ''

  if (!email.value.trim()) {
    error.value = 'Por favor, ingresa tu correo electrónico.'
    return
  }

  cargando.value = true
  try {
    const res = await api.post<{ mensaje: string }>('/usuarios/recuperar-password/', {
      email: email.value.trim()
    })
    mensaje.value = res.data.mensaje
    enviado.value = true
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Ocurrió un error al procesar tu solicitud. Inténtalo nuevamente.'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.recover-wrapper {
  position: relative;
  width: 440px;
  max-width: 100%;
}

.recover-glow {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 260px;
  height: 260px;
  background: var(--primary-glow);
  filter: blur(45px);
  pointer-events: none;
}

.recover-card {
  padding: 44px 36px;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.recover-header {
  text-align: center;
  margin-bottom: 28px;
}

.recover-icon {
  width: 56px;
  height: 56px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  margin: 0 auto 16px;
  box-shadow: 0 6px 16px var(--primary-glow);
  color: #fff;
}

.recover-header h2 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 6px;
}

.recover-header p {
  font-size: 14px;
  color: var(--text2);
  line-height: 1.5;
}

.btn-submit {
  width: 100%;
  justify-content: center;
  padding: 13px;
  font-size: 14.5px;
  margin-top: 8px;
}

.enviado-acciones {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.recover-footer {
  font-size: 13.5px;
  color: var(--text2);
  text-align: center;
}

.login-link {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style>
