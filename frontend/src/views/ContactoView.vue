<template>
  <div class="contacto-page">
    <!-- HEADER HERO -->
    <div class="contacto-header">
      <div class="header-glow"></div>
      <div class="header-content">
        <div class="contacto-badge">
          <span>📍 Sede Central Cusco, Perú</span>
        </div>
        <h1>Contáctanos y Atención al Cliente</h1>
        <p>¿Tienes dudas sobre un servicio técnico, necesitas soporte con tu cuenta o requieres atención para tu empresa?</p>
      </div>
    </div>

    <!-- CONTENEDOR PRINCIPAL -->
    <div class="contacto-container">
      <div class="contacto-grid">

        <!-- COLUMNA IZQUIERDA: INFORMACIÓN REAL Y SEDE -->
        <div class="info-column">
          <div class="card info-card">
            <h3>📍 Oficinas y Atención Presencial</h3>
            <p class="info-desc">Visítanos o comunícate con nuestro equipo en la ciudad del Cusco.</p>

            <div class="info-items">
              <div class="info-item">
                <div class="info-icon">🏢</div>
                <div>
                  <strong>Dirección Real:</strong>
                  <p>Av. de la Cultura 733, Wanchaq, Cusco 08002, Perú</p>
                  <span class="info-hint">(Frente a la UNSAAC / A 2 cuadras de Plaza Túpac Amaru)</span>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">📞</div>
                <div>
                  <strong>Teléfonos de Contacto:</strong>
                  <p><a href="tel:+51984123456">+51 984 123 456</a> · <a href="tel:084240011">(084) 240011</a></p>
                  <span class="info-hint">Atención telefónica directa</span>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">✉️</div>
                <div>
                  <strong>Correos Electrónicos:</strong>
                  <p><a href="mailto:contacto@llankay.pe">contacto@llankay.pe</a></p>
                  <p><a href="mailto:soporte@llankay.pe">soporte@llankay.pe</a></p>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">⏰</div>
                <div>
                  <strong>Horario de Atención:</strong>
                  <p>Lunes a Sábado: 8:00 AM – 7:00 PM</p>
                  <span class="info-hint">Guardias de emergencia técnica 24/7</span>
                </div>
              </div>
            </div>

            <!-- BOTÓN WHATSAPP DIRECTO -->
            <a href="https://wa.me/51984123456?text=Hola%20Llankay,%20necesito%20información%20sobre%20sus%20servicios" 
               target="_blank" 
               rel="noopener noreferrer" 
               class="btn-whatsapp">
              <span>💬</span> Chatear por WhatsApp Directo
            </a>
          </div>

          <!-- MAPA INTEGRADO -->
          <div class="card mapa-card">
            <div class="mapa-header">
              <span class="mapa-title">🗺️ Mapa de Ubicación en Cusco</span>
              <a href="https://maps.google.com/?q=-13.5226,-71.9567" target="_blank" rel="noopener noreferrer" class="mapa-link">
                Abrir en Google Maps ➔
              </a>
            </div>
            <div class="mapa-embed-wrap">
              <iframe 
                src="https://www.openstreetmap.org/export/embed.html?bbox=-71.9700%2C-13.5350%2C-71.9450%2C-13.5150&amp;layer=mapnik&amp;marker=-13.5226%2C-71.9567" 
                title="Mapa de ubicación Llankay en Wanchaq, Cusco"
                class="mapa-iframe"
                loading="lazy"
              ></iframe>
            </div>
          </div>
        </div>

        <!-- COLUMNA DERECHA: FORMULARIO DE CONTACTO -->
        <div class="form-column">
          <div class="card form-card">
            <h3>✉️ Envíanos un Mensaje</h3>
            <p class="form-sub">Completa el formulario y te responderemos a la brevedad posible.</p>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre Completo *</label>
                <input 
                  v-model="form.nombre" 
                  type="text" 
                  maxlength="60"
                  :class="['form-input', errores.nombre ? 'is-invalid' : '']" 
                  placeholder="Ej: Sofía Mendoza" 
                  @input="errores.nombre = ''"
                />
                <span v-if="errores.nombre" class="form-field-error">⚠️ {{ errores.nombre }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Teléfono Celular (9 dígitos) *</label>
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
            </div>

            <div class="form-group">
              <label class="form-label">Correo Electrónico *</label>
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
                <label class="form-label">Distrito en Cusco</label>
                <select v-model="form.distrito" class="form-select">
                  <option value="Cusco">Cusco</option>
                  <option value="Wanchaq">Wanchaq</option>
                  <option value="San Sebastián">San Sebastián</option>
                  <option value="San Jerónimo">San Jerónimo</option>
                  <option value="Santiago">Santiago</option>
                  <option value="Otro">Otro distrito</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Motivo de Contacto *</label>
                <select v-model="form.motivo" :class="['form-select', errores.motivo ? 'is-invalid' : '']" @change="errores.motivo = ''">
                  <option value="">Selecciona motivo</option>
                  <option value="Consulta sobre un servicio">Consulta sobre un servicio</option>
                  <option value="Soporte con mi cuenta">Soporte con mi cuenta</option>
                  <option value="Registro y verificación de técnico">Registro y verificación de técnico</option>
                  <option value="Alianza o convenios corporativos">Alianza o convenios corporativos</option>
                  <option value="Reportar una incidencia">Reportar una incidencia</option>
                </select>
                <span v-if="errores.motivo" class="form-field-error">⚠️ {{ errores.motivo }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Mensaje o Detalle del Requerimiento * (máx. 800 caracteres)</label>
              <textarea 
                v-model="form.mensaje" 
                rows="4" 
                maxlength="800"
                :class="['form-textarea', errores.mensaje ? 'is-invalid' : '']" 
                placeholder="Escribe tu consulta o detalle aquí con la mayor precisión posible..."
                @input="errores.mensaje = ''"
              ></textarea>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span v-if="errores.mensaje" class="form-field-error">⚠️ {{ errores.mensaje }}</span>
                <span v-else></span>
                <span class="form-field-hint" style="font-size: 11px; color: var(--text3)">{{ form.mensaje.length }}/800</span>
              </div>
            </div>

            <div v-if="errorGlobal" class="alert alert-error">{{ errorGlobal }}</div>

            <button class="btn-primary btn-submit" @click="enviarMensaje" :disabled="enviando">
              {{ enviando ? 'Enviando mensaje...' : 'Enviar mensaje de contacto ➔' }}
            </button>
          </div>

          <!-- PREGUNTAS FRECUENTES RÁPIDAS -->
          <div class="card faq-card">
            <h4>❓ Preguntas Frecuentes</h4>
            <div class="faq-list">
              <div class="faq-item">
                <strong>¿Cómo se coordina el pago con los técnicos?</strong>
                <p>El presupuesto y la forma de pago (efectivo, Yape, Plin o transferencia) se acuerdan directamente con el técnico antes de iniciar el trabajo.</p>
              </div>
              <div class="faq-item">
                <strong>¿Cuánto demora la verificación de un técnico?</strong>
                <p>Nuestro equipo valida los perfiles en un plazo máximo de 12 a 24 horas hábiles tras el registro.</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  nombre: '',
  celular: '',
  email: '',
  distrito: 'Wanchaq',
  motivo: '',
  mensaje: ''
})

const errores = ref<{ [key: string]: string }>({})
const errorGlobal = ref('')
const enviando = ref(false)

function onInputCelular() {
  form.value.celular = form.value.celular.replace(/\D/g, '').slice(0, 9)
  errores.value.celular = ''
}

function validar(): boolean {
  errores.value = {}
  errorGlobal.value = ''

  if (!form.value.nombre.trim()) {
    errores.value.nombre = 'El nombre completo es obligatorio.'
  } else if (form.value.nombre.trim().length < 2) {
    errores.value.nombre = 'Mínimo 2 caracteres.'
  }

  const celularClean = form.value.celular.replace(/\D/g, '')
  if (!celularClean) {
    errores.value.celular = 'El celular es obligatorio.'
  } else if (!/^9\d{8}$/.test(celularClean)) {
    errores.value.celular = 'Ingresa un celular válido de 9 dígitos (inicia con 9).'
  }

  if (!form.value.email.trim()) {
    errores.value.email = 'El correo es obligatorio.'
  } else if (!/^\S+@\S+\.\S+$/.test(form.value.email)) {
    errores.value.email = 'Ingresa un correo electrónico válido.'
  }

  if (!form.value.motivo) {
    errores.value.motivo = 'Selecciona el motivo de tu consulta.'
  }

  if (!form.value.mensaje.trim() || form.value.mensaje.trim().length < 10) {
    errores.value.mensaje = 'Por favor escribe un mensaje de al menos 10 caracteres.'
  }

  return Object.keys(errores.value).length === 0
}

async function enviarMensaje() {
  if (!validar()) {
    errorGlobal.value = 'Por favor corrige los campos señalados en rojo.'
    return
  }

  enviando.value = true
  try {
    // Simular guardado / envío
    await new Promise(r => setTimeout(r, 600))
    // Redirigir a página de Gracias
    router.push({
      path: '/gracias',
      query: { tipo: 'contacto', nombre: form.value.nombre }
    })
  } catch {
    errorGlobal.value = 'Ocurrió un error al enviar el mensaje. Inténtalo nuevamente.'
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
.contacto-page {
  min-height: calc(100vh - 68px);
  padding-bottom: 60px;
}

.contacto-header {
  position: relative;
  overflow: hidden;
  padding: 50px 24px 40px;
  background: var(--surface-glass);
  border-bottom: 1px solid var(--border);
  text-align: center;
}

.header-glow {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 450px;
  height: 250px;
  background: var(--primary-glow);
  filter: blur(60px);
  pointer-events: none;
}

.header-content {
  position: relative;
  z-index: 1;
  max-width: 760px;
  margin: 0 auto;
}

.contacto-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary-light);
  color: var(--primary);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 16px;
}

.contacto-header h1 {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 10px;
}

.contacto-header p {
  font-size: 15px;
  color: var(--text2);
}

.contacto-container {
  max-width: 1160px;
  margin: 40px auto 0;
  padding: 0 20px;
}

.contacto-grid {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 32px;
}

@media (max-width: 900px) {
  .contacto-grid {
    grid-template-columns: 1fr;
  }
}

.info-column,
.form-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.form-card,
.mapa-card,
.faq-card {
  padding: 32px;
}

.info-card h3,
.form-card h3 {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 6px;
}

.info-desc,
.form-sub {
  font-size: 14px;
  color: var(--text2);
  margin-bottom: 24px;
}

.info-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.info-icon {
  font-size: 24px;
  width: 44px;
  height: 44px;
  background: var(--surface-subtle);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--border);
}

.info-item strong {
  display: block;
  font-size: 13.5px;
  color: var(--text);
  margin-bottom: 2px;
}

.info-item p {
  font-size: 14px;
  color: var(--text2);
  margin: 0;
}

.info-item a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.info-item a:hover {
  text-decoration: underline;
}

.info-hint {
  font-size: 12px;
  color: var(--text3);
  display: block;
  margin-top: 2px;
}

.btn-whatsapp {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #25D366;
  color: #FFFFFF;
  text-decoration: none;
  padding: 13px 20px;
  border-radius: var(--radius-sm);
  font-size: 14.5px;
  font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif;
  box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35);
  transition: all 0.2s ease;
}

.btn-whatsapp:hover {
  background: #20BA5A;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 211, 102, 0.45);
}

.mapa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.mapa-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.mapa-link {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  text-decoration: none;
}

.mapa-link:hover {
  text-decoration: underline;
}

.mapa-embed-wrap {
  width: 100%;
  height: 220px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}

.mapa-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .info-card,
  .form-card {
    padding: 24px 18px;
  }
}

.btn-submit {
  width: 100%;
  justify-content: center;
  padding: 14px;
  font-size: 15px;
  margin-top: 8px;
}

.faq-card h4 {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 16px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.faq-item strong {
  display: block;
  font-size: 13.5px;
  color: var(--text);
  margin-bottom: 4px;
}

.faq-item p {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.5;
  margin: 0;
}
</style>
