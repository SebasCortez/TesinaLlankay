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

        <!-- BOTÓN GOOGLE SIGN-IN -->
        <div class="google-btn-wrap">
          <div id="googleBtnContainer" ref="googleBtnRef" class="g-btn-hidden"></div>
          <button class="btn-google" @click="iniciarConGoogle" :disabled="cargandoGoogle">
            <svg class="google-svg" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>{{ cargandoGoogle ? 'Conectando con Google...' : 'Continuar con Google' }}</span>
          </button>
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

function iniciarConGoogle() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const google = (window as any).google

  if (google && googleClientId) {
    google.accounts.id.prompt((notification: any) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        const btn = googleBtnRef.value?.querySelector('div[role="button"]') as HTMLElement
        if (btn) btn.click()
      }
    })
  } else {
    // Si aún no se configuró Client ID de Google Cloud, permitir prueba rápida inmediata
    const mockEmail = prompt('Prueba de inicio de sesión con Google:\nIngresa un correo de prueba (ej: tu.nombre@gmail.com):', 'usuario.demo@gmail.com')
    if (mockEmail && mockEmail.includes('@')) {
      cargandoGoogle.value = true
      error.value = ''
      auth.loginConGoogle(`demo-google-token:${mockEmail.trim()}`).then(() => {
        if (auth.esAdmin) router.push('/admin')
        else router.push('/buscar')
      }).catch((err: any) => {
        error.value = err.response?.data?.error || 'Error al procesar el inicio con Google'
      }).finally(() => {
        cargandoGoogle.value = false
      })
    }
  }
}


onMounted(() => {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  // Cargar Google Identity Services SDK si no existe
  if (!document.getElementById('google-gsi-client')) {
    const script = document.createElement('script')
    script.id = 'google-gsi-client'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => {
      const google = (window as any).google
      if (google && googleClientId) {
        google.accounts.id.initialize({
          client_id: googleClientId,
          callback: handleGoogleCallback,
          auto_select: false
        })
        if (googleBtnRef.value) {
          google.accounts.id.renderButton(googleBtnRef.value, {
            theme: 'outline',
            size: 'large',
            width: 360,
            text: 'continue_with'
          })
        }
      }
    }
    document.head.appendChild(script)
  }
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

/* BOTON GOOGLE */
.google-btn-wrap {
  margin-bottom: 20px;
}

.g-btn-hidden {
  display: none;
}

.btn-google {
  width: 100%;
  padding: 11px 18px;
  background: var(--surface);
  color: var(--text);
  border: 1.5px solid var(--border2);
  border-radius: var(--radius-sm);
  font-size: 14.5px;
  font-weight: 600;
  font-family: 'Plus Jakarta Sans', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.btn-google:hover {
  background: var(--surface-subtle);
  border-color: var(--text3);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.google-svg {
  width: 20px;
  height: 20px;
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