<template>
  <div class="page-center">
    <div class="registro-wrapper">
      <div class="registro-glow"></div>
      <div class="card registro-card">
        <div class="pasos-header">
          <div class="pasos">
            <div v-for="n in 3" :key="n" :class="['paso', paso === n ? 'activo' : paso > n ? 'listo' : '']">
              {{ paso > n ? '✓' : n }}
            </div>
          </div>
          <div class="paso-label">
            <span class="paso-pill">Paso {{ paso }} de 3</span>
            <span class="paso-titulo">{{ titulos[paso - 1] }}</span>
          </div>
        </div>

        <!-- Paso 1: Datos personales -->
        <div v-if="paso === 1" class="paso-content">
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
              placeholder="Ej: marcos_tecnico" 
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
              <label class="form-label">Distrito de trabajo *</label>
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
        </div>

        <!-- Paso 2: Datos profesionales -->
        <div v-if="paso === 2" class="paso-content">
          <div class="form-group">
            <label class="form-label">Categoría o Rama Técnica *</label>
            <select 
              v-model="form.categoria" 
              :class="['form-select', errores.categoria ? 'is-invalid' : '']"
              @change="errores.categoria = ''"
            >
              <option value="">Selecciona una categoría</option>
              <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
            </select>
            <span v-if="errores.categoria" class="form-field-error">⚠️ {{ errores.categoria }}</span>
          </div>

          <!-- CAMPO DINÁMICO SI SELECCIONA 'OTRO' -->
          <div v-if="form.categoria === 'Otro'" class="form-group alert-personalizado">
            <label class="form-label">Especifica tu especialidad o servicio independiente *</label>
            <input 
              v-model="form.categoria_personalizada" 
              type="text" 
              maxlength="60"
              :class="['form-input', errores.categoria_personalizada ? 'is-invalid' : '']" 
              placeholder="Ej: Tapicería automotriz, Pulido de pisos, Técnico en alarmas..." 
              @input="errores.categoria_personalizada = ''"
            />
            <span v-if="errores.categoria_personalizada" class="form-field-error">⚠️ {{ errores.categoria_personalizada }}</span>
            <span class="form-field-hint">💡 Tu especialidad será evaluada y habilitada por nuestro equipo en Cusco.</span>
          </div>

          <div class="form-group">
            <label class="form-label">Título del Oficio o Especialidad Detallada *</label>
            <input 
              v-model="form.oficio" 
              type="text" 
              maxlength="100"
              :class="['form-input', errores.oficio ? 'is-invalid' : '']" 
              placeholder="Ej: Maestro encofrador, Instalador de termas solares, Técnico de línea blanca" 
              @input="errores.oficio = ''"
            />
            <span v-if="errores.oficio" class="form-field-error">⚠️ {{ errores.oficio }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Años de experiencia *</label>
            <select 
              v-model="form.experiencia" 
              :class="['form-select', errores.experiencia ? 'is-invalid' : '']"
              @change="errores.experiencia = ''"
            >
              <option value="">Selecciona tu experiencia</option>
              <option v-for="e in experiencias" :key="e" :value="e">{{ e }}</option>
            </select>
            <span v-if="errores.experiencia" class="form-field-error">⚠️ {{ errores.experiencia }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Descripción de tus servicios y herramientas (opcional, máx. 800 caracteres)</label>
            <textarea 
              v-model="form.descripcion" 
              maxlength="800"
              class="form-textarea" 
              placeholder="Cuéntanos brevemente sobre tus trabajos anteriores, garantía ofrecida y herramientas..." 
              rows="3"
            ></textarea>
            <span class="form-field-hint" style="text-align: right; display: block; font-size: 11px; margin-top: 4px; color: var(--text3)">
              {{ form.descripcion.length }}/800 caracteres
            </span>
          </div>
        </div>

        <!-- Paso 3: Confirmación -->
        <div v-if="paso === 3" class="paso-content">
          <div class="resumen card">
            <h3>📋 Resumen de tu solicitud</h3>
            <div class="fila"><span>Nombre:</span><strong>{{ form.first_name }} {{ form.last_name }}</strong></div>
            <div class="fila"><span>Usuario:</span><strong>@{{ form.username }}</strong></div>
            <div class="fila"><span>Celular:</span><strong>{{ form.celular }}</strong></div>
            <div class="fila"><span>Distrito:</span><strong>{{ form.distrito }}</strong></div>
            <div class="fila"><span>Categoría:</span><strong>{{ form.categoria }}</strong></div>
            <div class="fila"><span>Oficio:</span><strong>{{ form.oficio }}</strong></div>
            <div class="fila"><span>Experiencia:</span><strong>{{ form.experiencia }}</strong></div>
          </div>

          <div class="legal-consent-box" style="margin-top: 16px;">
            <label class="consent-label">
              <input v-model="aceptoTerminos" type="checkbox" class="consent-check" />
              <span>
                Acepto los <router-link to="/terminos-condiciones" target="_blank">Términos y Condiciones</router-link> y la <router-link to="/politica-privacidad" target="_blank">Política de Privacidad</router-link> de Llankay.
              </span>
            </label>
            <span v-if="errores.terminos" class="form-field-error">⚠️ {{ errores.terminos }}</span>
          </div>

          <div class="alert alert-warning" style="margin-top:16px">
            ⏳ Tu solicitud será revisada y validada por un administrador antes de que tu perfil sea visible en el mapa.
          </div>
        </div>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="exito" class="alert alert-success">{{ exito }}</div>

        <div class="nav-btns">
          <button v-if="paso > 1" class="btn-secondary" @click="paso--">← Atrás</button>
          <button v-if="paso < 3" class="btn-primary" @click="siguiente">Siguiente →</button>
          <button v-if="paso === 3" class="btn-primary" @click="registrar" :disabled="cargando">
            {{ cargando ? 'Enviando solicitud...' : 'Enviar solicitud de técnico ➔' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const paso = ref(1)
const error = ref('')
const exito = ref('')
const aceptoTerminos = ref(true)
const errores = ref<{ [key: string]: string }>({})
const cargando = ref(false)

const titulos = ['Datos personales', 'Datos profesionales', 'Confirmación y envío']
const distritos = ['Cusco', 'Wanchaq', 'San Sebastián', 'San Jerónimo', 'Santiago']
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
const experiencias = ['Menos de 1 año', '1-3 años', '3-5 años', 'Más de 5 años']

const form = ref({
  first_name: '', last_name: '', username: '', email: '',
  celular: '', distrito: '', password: '',
  categoria: '', categoria_personalizada: '',
  oficio: '', experiencia: '', descripcion: ''
})

function onInputUsername() {
  form.value.username = form.value.username.replace(/\s+/g, '').slice(0, 30)
  errores.value.username = ''
}

function onInputCelular() {
  form.value.celular = form.value.celular.replace(/\D/g, '').slice(0, 9)
  errores.value.celular = ''
}

function siguiente() {
  error.value = ''
  errores.value = {}

  if (paso.value === 1) {
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
      errores.value.email = 'Ingresa tu correo'
    } else if (!/^\S+@\S+\.\S+$/.test(form.value.email)) {
      errores.value.email = 'Ingresa un correo válido'
    }

    const cel = form.value.celular.replace(/\D/g, '')
    if (!cel) {
      errores.value.celular = 'Ingresa tu celular'
    } else if (!/^9\d{8}$/.test(cel)) {
      errores.value.celular = 'Debe tener 9 dígitos (iniciar con 9)'
    }

    if (!form.value.distrito) errores.value.distrito = 'Selecciona tu distrito'

    if (!form.value.password) {
      errores.value.password = 'Ingresa una contraseña'
    } else if (form.value.password.length < 8) {
      errores.value.password = 'Mínimo 8 caracteres'
    }

    if (Object.keys(errores.value).length > 0) {
      error.value = 'Completa todos los datos personales obligatorios'
      return
    }
  }

  if (paso.value === 2) {
    if (!form.value.categoria) {
      errores.value.categoria = 'Selecciona una categoría'
    }
    if (form.value.categoria === 'Otro') {
      if (!form.value.categoria_personalizada?.trim()) {
        errores.value.categoria_personalizada = 'Especifica tu especialidad técnica'
      } else if (form.value.categoria_personalizada.trim().length < 3) {
        errores.value.categoria_personalizada = 'Mínimo 3 caracteres'
      }
    }
    if (!form.value.oficio.trim()) {
      errores.value.oficio = 'Ingresa tu oficio o especialidad'
    } else if (form.value.oficio.trim().length < 3) {
      errores.value.oficio = 'Mínimo 3 caracteres'
    }

    if (!form.value.experiencia) {
      errores.value.experiencia = 'Selecciona tus años de experiencia'
    }

    if (Object.keys(errores.value).length > 0) {
      error.value = 'Completa los datos profesionales obligatorios'
      return
    }
  }

  paso.value++
}

async function registrar() {
  error.value = ''
  errores.value = {}

  if (!aceptoTerminos.value) {
    errores.value.terminos = 'Debes aceptar los Términos y la Política de Privacidad'
    error.value = 'Por favor acepta los términos legales para continuar.'
    return
  }

  cargando.value = true
  try {
    const res = await api.post('/usuarios/registro/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      username: form.value.username,
      email: form.value.email,
      celular: form.value.celular,
      distrito: form.value.distrito,
      password: form.value.password,
      rol: 'trabajador'
    })

    if (res.data?.access) {
      auth.guardarSesion(res.data)
    }

    // Si seleccionó 'Otro', guardar con categoria='Otro' y detallar en oficio
    const oficioFinal = form.value.categoria === 'Otro' && form.value.categoria_personalizada
      ? `${form.value.categoria_personalizada} - ${form.value.oficio}`.trim()
      : form.value.oficio

    await api.post('/trabajadores/registro/', {
      categoria: form.value.categoria,
      oficio: oficioFinal,
      experiencia: form.value.experiencia,
      descripcion: form.value.descripcion,
    })
    
    router.push({ path: '/gracias', query: { tipo: 'registro' } })
  } catch (e: any) {
    const data = e.response?.data
    if (data?.username) {
      error.value = `Usuario: ${Array.isArray(data.username) ? data.username[0] : data.username}`
    } else if (data?.email) {
      error.value = `Correo: ${Array.isArray(data.email) ? data.email[0] : data.email}`
    } else if (data?.celular) {
      error.value = `Celular: ${Array.isArray(data.celular) ? data.celular[0] : data.celular}`
    } else if (data?.password) {
      error.value = `Contraseña: ${Array.isArray(data.password) ? data.password[0] : data.password}`
    } else {
      error.value = data?.error || data?.detail || 'Error al registrar el perfil, intenta de nuevo'
    }
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.registro-wrapper {
  position: relative;
  width: 520px;
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

.pasos-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.pasos {
  display: flex;
  align-items: center;
  gap: 8px;
}

.paso {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--surface-subtle);
  border: 1.5px solid var(--border);
  color: var(--text3);
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.paso.activo {
  background: var(--primary-gradient);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.paso.listo {
  background: var(--green);
  border-color: transparent;
  color: #fff;
}

.paso-label {
  display: flex;
  flex-direction: column;
}

.paso-pill {
  font-size: 11px;
  font-weight: 700;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.paso-titulo {
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.resumen {
  padding: 20px;
  background: var(--surface-subtle);
}

.resumen h3 {
  font-size: 15px;
  font-weight: 800;
  margin-bottom: 14px;
}

.fila {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid var(--border);
}

.fila span {
  color: var(--text2);
}

.fila strong {
  color: var(--text);
}

.legal-consent-box {
  margin: 14px 0;
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

.nav-btns {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 540px) {
  .registro-card {
    padding: 24px 16px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .pasos-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>