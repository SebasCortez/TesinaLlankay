<template>
  <div class="page-center">
    <div class="card">
      <div class="pasos">
        <div v-for="n in 3" :key="n" :class="['paso', paso === n ? 'activo' : paso > n ? 'listo' : '']">
          {{ paso > n ? '✓' : n }}
        </div>
      </div>
      <div class="paso-label">Paso {{ paso }} de 3 — {{ titulos[paso - 1] }}</div>

      <!-- Paso 1: Datos personales -->
      <div v-if="paso === 1">
        <div class="campo">
          <label>Nombre</label>
          <input v-model="form.first_name" type="text" placeholder="Tu nombre" />
        </div>
        <div class="campo">
          <label>Apellido</label>
          <input v-model="form.last_name" type="text" placeholder="Tu apellido" />
        </div>
        <div class="campo">
          <label>Usuario</label>
          <input v-model="form.username" type="text" placeholder="Nombre de usuario" />
        </div>
        <div class="campo">
          <label>Correo</label>
          <input v-model="form.email" type="email" placeholder="tucorreo@gmail.com" />
        </div>
        <div class="campo">
          <label>Celular</label>
          <input v-model="form.celular" type="tel" placeholder="+51 984 000 000" />
        </div>
        <div class="campo">
          <label>Distrito</label>
          <select v-model="form.distrito">
            <option value="">Selecciona tu distrito</option>
            <option v-for="d in distritos" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="campo">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" placeholder="Mínimo 8 caracteres" />
        </div>
      </div>

      <!-- Paso 2: Datos profesionales -->
      <div v-if="paso === 2">
        <div class="campo">
          <label>Categoría</label>
          <select v-model="form.categoria">
            <option value="">Selecciona una categoría</option>
            <option v-for="c in categorias" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="campo">
          <label>Oficio específico</label>
          <input v-model="form.oficio" type="text" placeholder="Ej: Instalaciones eléctricas domiciliarias" />
        </div>
        <div class="campo">
          <label>Años de experiencia</label>
          <select v-model="form.experiencia">
            <option value="">Selecciona</option>
            <option v-for="e in experiencias" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
        <div class="campo">
          <label>Descripción (opcional)</label>
          <textarea v-model="form.descripcion" placeholder="Cuéntanos sobre tu trabajo..." rows="3"></textarea>
        </div>
      </div>

      <!-- Paso 3: Confirmación -->
      <div v-if="paso === 3">
        <div class="resumen">
          <h3>Resumen de tu solicitud</h3>
          <div class="fila"><span>Nombre</span><strong>{{ form.first_name }} {{ form.last_name }}</strong></div>
          <div class="fila"><span>Usuario</span><strong>{{ form.username }}</strong></div>
          <div class="fila"><span>Celular</span><strong>{{ form.celular }}</strong></div>
          <div class="fila"><span>Distrito</span><strong>{{ form.distrito }}</strong></div>
          <div class="fila"><span>Categoría</span><strong>{{ form.categoria }}</strong></div>
          <div class="fila"><span>Oficio</span><strong>{{ form.oficio }}</strong></div>
          <div class="fila"><span>Experiencia</span><strong>{{ form.experiencia }}</strong></div>
        </div>
        <div class="aviso">
          ⏳ Tu solicitud será revisada por un administrador antes de aparecer en la plataforma.
        </div>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="exito" class="exito">{{ exito }}</div>

      <div class="nav-btns">
        <button v-if="paso > 1" class="btn-outline" @click="paso--">← Atrás</button>
        <button v-if="paso < 3" class="btn-verde" @click="siguiente">Siguiente →</button>
        <button v-if="paso === 3" class="btn-verde" @click="registrar" :disabled="cargando">
          {{ cargando ? 'Enviando...' : 'Enviar solicitud' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const paso = ref(1)
const error = ref('')
const exito = ref('')
const cargando = ref(false)

const titulos = ['Datos personales', 'Datos profesionales', 'Confirmación']
const distritos = ['Cusco', 'San Sebastián', 'San Jerónimo', 'Santiago', 'Wanchaq']
const categorias = ['Electricidad', 'Gasfitería', 'Carpintería', 'Cerrajería', 'Pintura']
const experiencias = ['Menos de 1 año', '1-3 años', '3-5 años', 'Más de 5 años']

const form = ref({
  first_name: '', last_name: '', username: '', email: '',
  celular: '', distrito: '', password: '',
  categoria: '', oficio: '', experiencia: '', descripcion: ''
})

function siguiente() {
  error.value = ''
  if (paso.value === 1) {
    if (!form.value.first_name || !form.value.username || !form.value.password || !form.value.distrito)
      return error.value = 'Completa todos los campos'
    if (form.value.password.length < 8)
      return error.value = 'La contraseña debe tener al menos 8 caracteres'
  }
  if (paso.value === 2) {
    if (!form.value.categoria || !form.value.oficio || !form.value.experiencia)
      return error.value = 'Completa todos los campos'
  }
  paso.value++
}

async function registrar() {
  error.value = ''
  cargando.value = true
  try {
    // 1. Crear usuario con rol trabajador
    await axios.post('http://127.0.0.1:8000/api/usuarios/registro/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      username: form.value.username,
      email: form.value.email,
      celular: form.value.celular,
      distrito: form.value.distrito,
      password: form.value.password,
      rol: 'trabajador'
    })
    // 2. Login automático
    await auth.login(form.value.username, form.value.password)
    // 3. Registrar perfil trabajador
    await axios.post('http://127.0.0.1:8000/api/trabajadores/registro/', {
      categoria: form.value.categoria,
      oficio: form.value.oficio,
      experiencia: form.value.experiencia,
      descripcion: form.value.descripcion,
    })
    exito.value = '¡Solicitud enviada! Un administrador revisará tu perfil pronto.'
    setTimeout(() => router.push('/mi-perfil'), 2000)
  } catch (e: any) {
    error.value = e.response?.data?.username?.[0] || 'Error al registrar, intenta de nuevo'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.page-center {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 32px;
  width: 460px;
  max-width: 100%;
}

.pasos {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.paso {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #aaa;
}

.paso.activo {
  border-color: #1D9E75;
  color: #1D9E75;
  background: #e1f5ee;
}

.paso.listo {
  border-color: #1D9E75;
  background: #1D9E75;
  color: #fff;
}

.paso-label {
  font-size: 13px;
  color: #888;
  margin-bottom: 20px;
}

.campo {
  margin-bottom: 14px;
}

.campo label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 5px;
}

.campo input,
.campo select,
.campo textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.campo input:focus,
.campo select:focus,
.campo textarea:focus {
  border-color: #1D9E75;
}

.resumen {
  background: #f8f7f4;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 14px;
}

.resumen h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.fila {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.aviso {
  background: #FFF8E1;
  border: 1px solid #FFD54F;
  color: #7A5800;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
}

.nav-btns {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: flex-end;
}

.btn-verde {
  padding: 10px 20px;
  background: #1D9E75;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-verde:disabled {
  background: #aaa;
  cursor: not-allowed;
}

.btn-outline {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.error {
  background: #fde8e8;
  color: #c0392b;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
}

.exito {
  background: #e1f5ee;
  color: #0f6e56;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
}
</style>