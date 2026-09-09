<template>
  <div class="page-center">
    <div class="login-wrapper">
      <div class="login-glow"></div>
      <div class="login-card card">
        <div class="login-header">
          <div class="login-icon">🔧</div>
          <h2>Bienvenido a Llankay</h2>
          <p>Ingresa tus credenciales para acceder a tu cuenta</p>
        </div>

        <!-- BOTÓN GOOGLE SIGN-IN OFICIAL -->
        <div class="google-btn-wrap">
          <div id="googleBtnContainer" ref="googleBtnRef" class="g-btn-container"></div>
          <div v-if="cargandoGoogle" class="google-loading-text">
            <span>🔄 Autenticando con Google...</span>
          </div>
        </div>

        <div class="login-separator">
          <span>o ingresa con tu usuario</span>
        </div>

        <div class="form-group">
          <label class="form-label">Nombre de Usuario</label>
          <input 
            v-model="form.username" 
            type="text" 
            maxlength="30"
            :class="['form-input', errores.username || error ? 'is-invalid' : '']" 
            placeholder="Ej: juan_electricista"
            @input="errores.username = ''; error = ''"
            @keydown.enter="iniciarSesion" 
          />
          <span v-if="errores.username" class="form-field-error">⚠️ {{ errores.username }}</span>
        </div>

        <div class="form-group">
          <div class="label-with-link">
            <label class="form-label">Contraseña</label>
            <router-link to="/recuperar-password" class="forgot-link">¿Olvidaste tu contraseña?</router-link>
          </div>
          <input 
            v-model="form.password" 
            type="password" 
            maxlength="64"
            :class="['form-input', errores.password || error ? 'is-invalid' : '']" 
            placeholder="••••••••"
            @input="errores.password = ''; error = ''"
            @keydown.enter="iniciarSesion" 
          />
          <span v-if="errores.password" class="form-field-error">⚠️ {{ errores.password }}</span>
        </div>

        <!-- WIDGET CAPTCHA DE SEGURIDAD -->
        <CaptchaWidget
          ref="captchaRef"
          :tiene-error="!!errores.captcha"
          :mensaje-error="errores.captcha"
          @update:captcha="actualizarCaptcha"
          @submit="iniciarSesion"
        />

        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <button class="btn-primary btn-submit" @click="iniciarSesion" :disabled="cargando">
          {{ cargando ? 'Iniciando sesión...' : 'Ingresar a mi cuenta ➔' }}
        </button>

        <hr class="divider">

        <p class="login-footer">
          ¿Aún no tienes una cuenta?
          <span class="footer-links">
            <router-link to="/registro-cliente" class="reg-link">Crear cuenta Cliente</router-link>
            ·
            <router-link to="/registro-trabajador" class="reg-link">Soy Técnico</router-link>
          </span>
        </p>

        <div class="login-legal-hint">
          Al iniciar sesión aceptas nuestros 
          <router-link to="/terminos-condiciones">Términos</router-link> y 
          <router-link to="/politica-privacidad">Política de Privacidad</router-link>.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import CaptchaWidget from '../components/CaptchaWidget.vue'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const errores = ref<{ username?: string; password?: string; captcha?: string }>({})
const cargando = ref(false)
const cargandoGoogle = ref(false)
const googleBtnRef = ref<HTMLElement | null>(null)
const captchaRef = ref<InstanceType<typeof CaptchaWidget> | null>(null)
const form = ref({ username: '', password: '' })
const captchaData = ref({ key: '', value: '' })

function actualizarCaptcha(data: { key: string; value: string }) {
  captchaData.value = data
  if (errores.value.captcha) {
    errores.value.captcha = ''
  }
}

async function iniciarSesion() {
  error.value = ''
  errores.value = {}

  if (!form.value.username.trim()) {
    errores.value.username = 'Ingresa tu nombre de usuario'
  }
  if (!form.value.password) {
    errores.value.password = 'Ingresa tu contraseña'
  }
  if (!captchaData.value.value.trim()) {
    errores.value.captcha = 'Resuelve el cálculo de seguridad'
  }

  if (Object.keys(errores.value).length > 0) {
    error.value = 'Completa todos los campos requeridos'
    return
  }

  cargando.value = true
  try {
    await auth.login(
      form.value.username,
      form.value.password,
      captchaData.value.key,
      captchaData.value.value
    )
    if (auth.esAdmin) router.push('/admin')
    else router.push('/buscar')
  } catch (err: any) {
    const errorData = err.response?.data
    if (errorData?.captcha) {
      errores.value.captcha = Array.isArray(errorData.captcha) ? errorData.captcha[0] : errorData.captcha
      error.value = errores.value.captcha || 'Código de seguridad incorrecto o expirado'
    } else if (err.response?.status === 429) {
      error.value = 'Has superado el límite de intentos de inicio de sesión (5/min). Por favor espera un momento.'
    } else {
      error.value = errorData?.detail || 'Usuario o contraseña incorrectos. Verifica tus datos.'
    }
    // Refrescar captcha al fallar
    captchaRef.value?.obtenerNuevoCaptcha()
  } finally {
    cargando.value = false
  }
}

async function handleGoogleCallback(response: any) {
  if (!response?.credential) return
  cargandoGoogle.value = true
  error.value = ''
  try {
    await auth.loginConGoogle(response.credential)
    if (auth.esAdmin) router.push('/admin')
    else router.push('/buscar')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'No se pudo iniciar sesión con Google. Inténtalo de nuevo.'
  } finally {
    cargandoGoogle.value = false
  }
}

function initGoogleAuth() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '605736068030-jru251fq1896bsar8p90skg4hdl4q768.apps.googleusercontent.com'
  if (!googleClientId) return

  const renderBtn = () => {
    const google = (window as any).google
    if (google?.accounts?.id && googleBtnRef.value) {
      google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleGoogleCallback,
        auto_select: false
      })
      googleBtnRef.value.innerHTML = ''
      const isDark = document.documentElement.classList.contains('dark')
      google.accounts.id.renderButton(googleBtnRef.value, {
        theme: isDark ? 'filled_black' : 'outline',
        size: 'large',
        width: 378,
        text: 'continue_with',
        shape: 'rectangular',
        logo_alignment: 'center'
      })
      // Opcional: One Tap
      try {
        google.accounts.id.prompt()
      } catch (e) {
        // One tap silencioso si está bloqueado por el navegador
      }
    }
  }

  const g = (window as any).google
  if (g?.accounts?.id) {
    renderBtn()
  } else {
    let retries = 0
    const interval = setInterval(() => {
      retries++
      if ((window as any).google?.accounts?.id && googleBtnRef.value) {
        clearInterval(interval)
        renderBtn()
      } else if (retries > 25) {
        clearInterval(interval)
      }
    }, 150)
  }
}

onMounted(() => {
  initGoogleAuth()
})
</script>

<style scoped>
.login-wrapper {
  position: relative;
  width: 450px;
  max-width: 100%;
}

.login-glow {
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

.login-card {
  padding: 44px 36px;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-icon {
  width: 56px;
  height: 56px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  margin: 0 auto 14px;
  box-shadow: 0 6px 16px var(--primary-glow);
  color: #fff;
}

.login-header h2 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 6px;
}

.login-header p {
  font-size: 14px;
  color: var(--text2);
}

.google-btn-wrap {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.g-btn-container {
  display: flex;
  justify-content: center;
  width: 100%;
  min-height: 44px;
}

.google-loading-text {
  margin-top: 8px;
  font-size: 13px;
  color: var(--primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.login-separator {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
  color: var(--text3);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.login-separator::before,
.login-separator::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border);
}

.login-separator span {
  padding: 0 12px;
}

.label-with-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.label-with-link .form-label {
  margin-bottom: 0;
}

.forgot-link {
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.15s ease;
}

.forgot-link:hover {
  text-decoration: underline;
}

.btn-submit {
  width: 100%;
  justify-content: center;
  padding: 13px;
  font-size: 15px;
  margin-top: 8px;
}

.login-footer {
  font-size: 13.5px;
  color: var(--text2);
  text-align: center;
  line-height: 1.6;
}

.footer-links {
  display: block;
  margin-top: 4px;
}

.reg-link {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
  transition: color 0.15s ease;
}

.reg-link:hover {
  text-decoration: underline;
}

.login-legal-hint {
  font-size: 11.5px;
  color: var(--text3);
  text-align: center;
  margin-top: 14px;
  line-height: 1.4;
}

.login-legal-hint a {
  color: var(--text2);
  text-decoration: underline;
}

.login-legal-hint a:hover {
  color: var(--primary);
}
</style>