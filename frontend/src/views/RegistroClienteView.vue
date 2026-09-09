<template>
  <div class="page-center">
    <div class="registro-wrapper">
      <div class="registro-glow"></div>
      <div class="card registro-card">
        <div class="registro-header">
          <div class="registro-icon">👤</div>
          <h2>Crear cuenta de cliente</h2>
          <p>Encuentra y contrata técnicos verificados en Cusco</p>
        </div>

        <!-- GOOGLE SIGN-UP BUTTON OFICIAL -->
        <div class="google-btn-wrap">
          <div id="googleBtnRegister" ref="googleBtnRef" class="g-btn-container"></div>
          <div v-if="cargandoGoogle" class="google-loading-text">
            <span>🔄 Registrando / Conectando con Google...</span>
          </div>
        </div>

        <div class="login-separator">
          <span>o completa tus datos</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input 
              v-model="form.first_name" 
              type="text" 
              maxlength="40"
              :class="['form-input', errores.first_name ? 'is-invalid' : '']" 
              placeholder="Tu nombre"
              @input="errores.first_name = ''"
            />
            <span v-if="errores.first_name" class="form-field-error">⚠️ {{ errores.first_name }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Apellido *</label>
            <input 
              v-model="form.last_name" 
              type="text" 
              maxlength="40"
              :class="['form-input', errores.last_name ? 'is-invalid' : '']" 
              placeholder="Tu apellido"
              @input="errores.last_name = ''"
            />
            <span v-if="errores.last_name" class="form-field-error">⚠️ {{ errores.last_name }}</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Nombre de usuario * (sin espacios)</label>
          <input 
            v-model="form.username" 
            type="text" 
            maxlength="30"
            :class="['form-input', errores.username ? 'is-invalid' : '']" 
            placeholder="Ej: juan_perez"
            @input="onInputUsername"
          />
          <span v-if="errores.username" class="form-field-error">⚠️ {{ errores.username }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Correo electrónico *</label>
          <input 
            v-model="form.email" 
            type="email" 
            maxlength="80"
            :class="['form-input', errores.email ? 'is-invalid' : '']" 
            placeholder="tucorreo@ejemplo.com"
            @input="errores.email = ''"
          />
          <span v-if="errores.email" class="form-field-error">⚠️ {{ errores.email }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Celular en Cusco (9 dígitos) *</label>
            <input 
              v-model="form.celular" 
              type="tel" 
              maxlength="9"
              :class="['form-input', errores.celular ? 'is-invalid' : '']" 
              placeholder="984123456"
              @input="onInputCelular"
            />
            <span v-if="errores.celular" class="form-field-error">⚠️ {{ errores.celular }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Distrito de residencia *</label>
            <select 
              v-model="form.distrito" 
              :class="['form-select', errores.distrito ? 'is-invalid' : '']"
              @change="errores.distrito = ''"
            >
              <option value="">Selecciona distrito</option>
              <option v-for="d in distritos" :key="d" :value="d">{{ d }}</option>
            </select>
            <span v-if="errores.distrito" class="form-field-error">⚠️ {{ errores.distrito }}</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Contraseña de acceso *</label>
          <input 
            v-model="form.password" 
            type="password" 
            maxlength="64"
            :class="['form-input', errores.password ? 'is-invalid' : '']" 
            placeholder="Mínimo 8 caracteres"
            @input="errores.password = ''"
          />
          <span v-if="errores.password" class="form-field-error">⚠️ {{ errores.password }}</span>
        </div>

        <div class="legal-consent-box">
          <label class="consent-label">
            <input v-model="aceptoTerminos" type="checkbox" class="consent-check" />
            <span>
              He leído y acepto los <router-link to="/terminos-condiciones" target="_blank">Términos y Condiciones</router-link> y la <router-link to="/politica-privacidad" target="_blank">Política de Privacidad</router-link>.
            </span>
          </label>
          <span v-if="errores.terminos" class="form-field-error">⚠️ {{ errores.terminos }}</span>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="exito" class="alert alert-success">{{ exito }}</div>

        <button class="btn-primary btn-submit" @click="registrar" :disabled="cargando">
          {{ cargando ? 'Creando cuenta...' : 'Crear mi cuenta de cliente ➔' }}
        </button>

        <hr class="divider">
        <p class="registro-footer">
          ¿Ya tienes una cuenta? <router-link to="/login">Inicia sesión</router-link> ·
          ¿Eres técnico? <router-link to="/registro-trabajador">Regístrate como profesional</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const error = ref('')
const exito = ref('')
const aceptoTerminos = ref(true)
const errores = ref<{ [key: string]: string }>({})
const cargando = ref(false)
const cargandoGoogle = ref(false)
const googleBtnRef = ref<HTMLElement | null>(null)
const distritos = ['Cusco', 'Wanchaq', 'San Sebastián', 'San Jerónimo', 'Santiago']
const form = ref({ first_name: '', last_name: '', username: '', email: '', celular: '', distrito: '', password: '', rol: 'cliente' })

function onInputUsername() {
  form.value.username = form.value.username.replace(/\s+/g, '').slice(0, 30)
  errores.value.username = ''
}

function onInputCelular() {
  form.value.celular = form.value.celular.replace(/\D/g, '').slice(0, 9)
  errores.value.celular = ''
}

function validar(): boolean {
  errores.value = {}
  error.value = ''

  if (!form.value.first_name.trim()) {
    errores.value.first_name = 'Ingresa tu nombre'
  } else if (form.value.first_name.trim().length < 2) {
    errores.value.first_name = 'Mínimo 2 caracteres'
  }

  if (!form.value.last_name.trim()) {
    errores.value.last_name = 'Ingresa tu apellido'
  } else if (form.value.last_name.trim().length < 2) {
    errores.value.last_name = 'Mínimo 2 caracteres'
  }

  if (!form.value.username.trim()) {
    errores.value.username = 'Ingresa un nombre de usuario'
  } else if (form.value.username.trim().length < 3) {
    errores.value.username = 'Mínimo 3 caracteres'
  } else if (!/^[a-zA-Z0-9_.-]+$/.test(form.value.username)) {
    errores.value.username = 'Solo letras, números, puntos y guiones'
  }
  
  if (!form.value.email.trim()) {
    errores.value.email = 'Ingresa tu correo electrónico'
  } else if (!/^\S+@\S+\.\S+$/.test(form.value.email)) {
    errores.value.email = 'Ingresa un correo electrónico válido'
  }

  const cel = form.value.celular.replace(/\D/g, '')
  if (!cel) {
    errores.value.celular = 'Ingresa tu número celular'
  } else if (!/^9\d{8}$/.test(cel)) {
    errores.value.celular = 'Debe tener 9 dígitos (iniciar con 9)'
  }

  if (!form.value.distrito) {
    errores.value.distrito = 'Selecciona tu distrito en Cusco'
  }

  if (!form.value.password) {
    errores.value.password = 'Ingresa una contraseña'
  } else if (form.value.password.length < 8) {
    errores.value.password = 'La contraseña debe tener al menos 8 caracteres'
  }

  if (!aceptoTerminos.value) {
    errores.value.terminos = 'Debes aceptar los Términos y la Política de Privacidad'
  }

  return Object.keys(errores.value).length === 0
}

async function registrar() {
  if (!validar()) {
    error.value = 'Corrige los campos destacados en rojo.'
    return
  }

  cargando.value = true
  try {
    await api.post('/usuarios/registro/', form.value)
    await auth.login(form.value.username, form.value.password)
    router.push({ path: '/gracias', query: { tipo: 'registro' } })
  } catch (err: any) {
    const data = err.response?.data
    if (data?.username) errores.value.username = data.username[0]
    else if (data?.email) errores.value.email = data.email[0]
    else if (data?.celular) errores.value.celular = data.celular[0]
    else error.value = data?.error || 'Error al registrar la cuenta. Inténtalo nuevamente.'
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
    router.push('/buscar')
  } catch (err: any) {
    error.value = err.response?.data?.error || 'No se pudo conectar con Google. Inténtalo de nuevo.'
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
        text: 'signup_with',
        shape: 'rectangular',
        logo_alignment: 'center'
      })
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
.registro-wrapper {
  position: relative;
  width: 500px;
  max-width: 100%;
}

.registro-glow {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 280px;
  height: 280px;
  background: var(--primary-glow);
  filter: blur(50px);
  pointer-events: none;
}

.registro-card {
  padding: 40px 36px;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.registro-header {
  text-align: center;
  margin-bottom: 24px;
}

.registro-icon {
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

.registro-header h2 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 6px;
}

.registro-header p {
  font-size: 14px;
  color: var(--text2);
}

/* BOTON GOOGLE */
.google-btn-wrap {
  margin-bottom: 16px;
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
  margin: 18px 0;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.legal-consent-box {
  margin: 16px 0 20px;
}

.consent-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12.5px;
  color: var(--text2);
  line-height: 1.45;
  cursor: pointer;
}

.consent-check {
  width: 17px;
  height: 17px;
  accent-color: var(--primary);
  margin-top: 2px;
  flex-shrink: 0;
}

.consent-label a {
  color: var(--primary);
  text-decoration: underline;
  font-weight: 600;
}

.btn-submit {
  width: 100%;
  justify-content: center;
  padding: 13px;
  font-size: 15px;
  margin-top: 8px;
}

.registro-footer {
  font-size: 13.5px;
  color: var(--text2);
  text-align: center;
  line-height: 1.6;
}

.registro-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.registro-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 540px) {
  .registro-card {
    padding: 28px 18px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>