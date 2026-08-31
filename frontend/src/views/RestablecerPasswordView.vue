<template>
  <div class="page-center">
    <div class="reset-wrapper">
      <div class="reset-glow"></div>
      <div class="reset-card card">
        <div class="reset-header">
          <div class="reset-icon">🔒</div>
          <h2>Nueva Contraseña</h2>
          <p>Ingresa y confirma tu nueva contraseña de acceso.</p>
        </div>

        <div v-if="!tokenValido" class="alert alert-error">
          ⚠️ El enlace de recuperación es inválido o faltan parámetros de seguridad. Solicita un nuevo enlace.
        </div>

        <div v-else>
          <div class="form-group">
            <label class="form-label">Nueva Contraseña (mínimo 8 caracteres)</label>
            <input
              v-model="password"
              type="password"
              maxlength="64"
              :class="['form-input', error ? 'is-invalid' : '']"
              placeholder="Mínimo 8 caracteres"
              @input="error = ''"
              :disabled="exito !== ''"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Confirmar Nueva Contraseña</label>
            <input
              v-model="passwordConfirm"
              type="password"
              maxlength="64"
              :class="['form-input', error ? 'is-invalid' : '']"
              placeholder="Repite la contraseña"
              @input="error = ''"
              @keydown.enter="restablecer"
              :disabled="exito !== ''"
            />
          </div>

          <div v-if="error" class="alert alert-error">{{ error }}</div>
          <div v-if="exito" class="alert alert-success">{{ exito }}</div>

          <button
            v-if="!exito"
            class="btn-primary btn-submit"
            @click="restablecer"
            :disabled="cargando"
          >
            {{ cargando ? 'Guardando contraseña...' : 'Actualizar contraseña ➔' }}
          </button>
        </div>

        <hr class="divider">

        <p class="reset-footer">
          <router-link to="/login" class="login-link">← Volver al inicio de sesión</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()

const password = ref('')
const passwordConfirm = ref('')
const cargando = ref(false)
const error = ref('')
const exito = ref('')

const uid = computed(() => (route.query.uid as string) || '')
const token = computed(() => (route.query.token as string) || '')
const tokenValido = computed(() => !!uid.value && !!token.value)

async function restablecer() {
  error.value = ''
  exito.value = ''

  if (!tokenValido.value) {
    error.value = 'El enlace no contiene un token válido.'
    return
  }

  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }

  if (password.value !== passwordConfirm.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  cargando.value = true
  try {
    const res = await api.post<{ mensaje: string }>('/usuarios/restablecer-password/', {
      uid: uid.value,
      token: token.value,
      password: password.value
    })
    exito.value = res.data.mensaje || '¡Contraseña actualizada con éxito! Redirigiendo...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'No se pudo actualizar la contraseña. El enlace puede haber expirado.'
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  if (!tokenValido.value) {
    error.value = 'Faltan parámetros en el enlace de recuperación.'
  }
})
</script>

<style scoped>
.reset-wrapper {
  position: relative;
  width: 440px;
  max-width: 100%;
}

.reset-glow {
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

.reset-card {
  padding: 44px 36px;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.reset-header {
  text-align: center;
  margin-bottom: 28px;
}

.reset-icon {
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

.reset-header h2 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 6px;
}

.reset-header p {
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

.reset-footer {
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
