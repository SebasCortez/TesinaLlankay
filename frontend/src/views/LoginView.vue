<template>
  <div class="page-center">
    <div class="login-card card">
      <div class="login-header">
        <div class="login-icon">🔧</div>
        <h2>Bienvenido de nuevo</h2>
        <p>Inicia sesión en tu cuenta de TécniCusco</p>
      </div>

      <div class="form-group">
        <label class="form-label">Usuario</label>
        <input v-model="form.username" class="form-input" type="text" placeholder="Tu nombre de usuario"
          @keydown.enter="iniciarSesion" />
      </div>
      <div class="form-group">
        <label class="form-label">Contraseña</label>
        <input v-model="form.password" class="form-input" type="password" placeholder="Tu contraseña"
          @keydown.enter="iniciarSesion" />
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <button class="btn-primary" style="width:100%;justify-content:center;padding:12px" @click="iniciarSesion"
        :disabled="cargando">
        {{ cargando ? 'Ingresando...' : 'Iniciar sesión' }}
      </button>

      <hr class="divider">

      <p class="login-footer">
        ¿No tienes cuenta?
        <router-link to="/registro-cliente">Regístrate como cliente</router-link>
        o
        <router-link to="/registro-trabajador">como técnico</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const cargando = ref(false)
const form = ref({ username: '', password: '' })

async function iniciarSesion() {
  error.value = ''
  if (!form.value.username || !form.value.password)
    return error.value = 'Completa todos los campos'
  cargando.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    if (auth.esAdmin) router.push('/admin')
    else router.push('/buscar')
  } catch {
    error.value = 'Usuario o contraseña incorrectos'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.login-card {
  padding: 40px;
  width: 420px;
  max-width: 100%;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  width: 52px;
  height: 52px;
  background: var(--primary-light);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin: 0 auto 16px;
}

.login-header h2 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.login-header p {
  font-size: 14px;
  color: var(--text2);
}

.login-footer {
  font-size: 13px;
  color: var(--text2);
  text-align: center;
}

.login-footer a {
  color: var(--primary);
  font-weight: 500;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>