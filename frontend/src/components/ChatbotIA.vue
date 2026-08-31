<template>
  <div class="chatbot-container" :class="{ 'chatbot-abierto': abierto, 'chatbot-minimizado': !abierto }">
    <!-- BOTÓN FLOTANTE TRIGGER -->
    <div v-if="!abierto" class="chatbot-trigger-wrapper">
      <!-- Tooltip de bienvenida inicial -->
      <transition name="fade">
        <div v-if="mostrarTooltip && mensajes.length <= 1" class="chatbot-tooltip" @click="toggleChat">
          <div class="tooltip-content">
            <span class="tooltip-badge">IA Asistente</span>
            <p>¡Hola! 👋 ¿Buscas un técnico en Cusco o tienes alguna duda?</p>
          </div>
          <button class="tooltip-close" @click.stop="mostrarTooltip = false">✕</button>
        </div>
      </transition>

      <button
        id="btn-chatbot-toggle"
        class="chatbot-fab"
        @click="toggleChat"
        title="Chatear con el Asistente IA LlankAI"
        aria-label="Abrir asistente de inteligencia artificial LlankAI"
      >
        <div class="fab-icon-wrap">
          <span class="fab-icon">🤖</span>
          <span class="fab-sparkle">✨</span>
        </div>
        <span class="fab-pulse"></span>
        <span class="fab-badge">LlankAI</span>
      </button>
    </div>

    <!-- VENTANA DEL CHATBOT -->
    <transition name="chat-slide">
      <div v-if="abierto" class="chatbot-window card">
        <!-- HEADER -->
        <div class="chatbot-header">
          <div class="chatbot-header-info">
            <div class="header-avatar-wrap">
              <div class="header-avatar">🤖</div>
              <span class="status-dot"></span>
            </div>
            <div class="header-titles">
              <div class="header-name-row">
                <h3>LlankAI</h3>
                <span class="model-badge">LLaMA 3.3 70B</span>
              </div>
              <div class="header-sub-row">
                <p class="header-sub">Groq API • En línea</p>
                <span v-if="cuotaInfo" class="header-cuota-pill" :class="{ 'cuota-baja': cuotaInfo.restantes <= 5 }">
                  ⚡ {{ cuotaInfo.restantes }}/{{ cuotaInfo.limite_diario }} hoy
                </span>
              </div>
            </div>
          </div>

          <div class="chatbot-header-actions">
            <button
              class="btn-header-action"
              @click="limpiarHistorial"
              title="Reiniciar conversación"
              aria-label="Reiniciar conversación"
            >
              🔄
            </button>
            <button
              class="btn-header-action"
              @click="toggleChat"
              title="Cerrar chat"
              aria-label="Cerrar chat"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- CUERPO DE MENSAJES -->
        <div class="chatbot-body" ref="chatBodyRef">
          <!-- Mensaje de bienvenida / info de contexto -->
          <div class="chat-welcome-banner">
            <span class="welcome-icon">⚡</span>
            <div class="welcome-text">
              <strong>Asistente Virtual LlankAI</strong>
              <p>Impulsado por Groq LLaMA 3.3. Puedo ayudarte a encontrar gasfiteros, electricistas o cotizar servicios en Cusco.</p>
            </div>
          </div>

          <!-- LISTA DE MENSAJES -->
          <div
            v-for="(msg, index) in mensajes"
            :key="index"
            :class="['chat-bubble-wrap', msg.role === 'user' ? 'bubble-user-wrap' : 'bubble-bot-wrap']"
          >
            <div v-if="msg.role === 'assistant'" class="bot-bubble-avatar">🤖</div>

            <div :class="['chat-bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-bot', msg.error ? 'bubble-error' : '']">
              <!-- Mensaje renderizado con soporte de párrafos y formato -->
              <div class="bubble-text" v-html="formatearTexto(msg.content)"></div>

              <!-- Footer del mensaje: hora y tokens si existen -->
              <div class="bubble-footer">
                <span class="bubble-time">{{ msg.timestamp }}</span>
                <span v-if="msg.uso" class="bubble-tokens" title="Tokens consumidos">
                  ⚡ {{ msg.uso.total_tokens }} tok
                </span>
              </div>
            </div>
          </div>

          <!-- INDICADOR DE PENSANDO / ESCRIBIENDO -->
          <div v-if="cargando" class="chat-bubble-wrap bubble-bot-wrap">
            <div class="bot-bubble-avatar">🤖</div>
            <div class="chat-bubble bubble-bot bubble-typing">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="typing-label">LlankAI está respondiendo...</span>
            </div>
          </div>

          <!-- BANNER DE ERROR CON REINTENTO -->
          <div v-if="ultimoError" class="chat-error-banner">
            <div class="error-msg-row">
              <span class="error-icon">⚠️</span>
              <span>{{ ultimoError }}</span>
            </div>
            <button class="btn-retry" @click="reintentarUltimoMensaje">
              🔄 Reintentar
            </button>
          </div>

          <!-- SUGERENCIAS RÁPIDAS (CHIPS) -->
          <div v-if="mensajes.length <= 3 && !cargando" class="chat-quick-suggestions">
            <span class="suggestions-label">Sugerencias rápidas:</span>
            <div class="chips-list">
              <button
                v-for="(chip, idx) in sugerencias"
                :key="idx"
                class="suggestion-chip"
                @click="enviarSugerencia(chip)"
              >
                {{ chip }}
              </button>
            </div>
          </div>
        </div>

        <!-- FOOTER / ENTRADA DE TEXTO -->
        <div class="chatbot-footer">
          <form @submit.prevent="enviarMensajeUsuario" class="chat-input-form">
            <textarea
              ref="inputRef"
              v-model="nuevoMensaje"
              rows="1"
              placeholder="Escribe tu consulta aquí..."
              class="chat-textarea"
              @keydown.enter.exact.prevent="enviarMensajeUsuario"
              @input="ajustarAlturaTextarea"
              :disabled="cargando"
            ></textarea>
            <button
              type="submit"
              class="btn-chat-send"
              :disabled="!nuevoMensaje.trim() || cargando"
              aria-label="Enviar mensaje"
            >
              <span v-if="!cargando">➔</span>
              <span v-else class="spinner-inline"></span>
            </button>
          </form>
          <div class="chatbot-disclaimer">
            <span>Tecnología Groq Inferencia Ultrarrápida • Llankay 2026</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { enviarMensajeChat, type MensajeTurno } from '../services/agenteService'

const STORAGE_KEY = 'llankay_chat_historial'

const abierto = ref(false)
const mostrarTooltip = ref(true)
const cargando = ref(false)
const nuevoMensaje = ref('')
const ultimoError = ref<string | null>(null)
const chatBodyRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)
const cuotaInfo = ref<{ restantes: number; limite_diario: number; segundos_reinicio: number } | null>(null)

const sugerencias = [
  '🔧 Necesito un gasfitero en Wanchaq',
  '⚡ ¿Tienen electricistas disponibles hoy?',
  '🔑 Busco un cerrajero urgente',
  '💰 ¿Cómo se calculan las tarifas?',
  '⭐ ¿Cómo veo los técnicos mejor calificados?'
]

const obtenerHoraActual = () => {
  const ahora = new Date()
  return ahora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const mensajeInicial: MensajeTurno = {
  role: 'assistant',
  content: '¡Hola! 👋 Soy **LlankAI**, tu asistente inteligente de **Llankay**. ¿En qué puedo orientarte hoy? Puedo ayudarte a encontrar el técnico ideal para tu hogar en cualquier distrito de Cusco.',
  timestamp: obtenerHoraActual()
}

const mensajes = ref<MensajeTurno[]>([mensajeInicial])

onMounted(() => {
  const guardado = sessionStorage.getItem(STORAGE_KEY)
  if (guardado) {
    try {
      const parsed = JSON.parse(guardado)
      if (Array.isArray(parsed) && parsed.length > 0) {
        mensajes.value = parsed
        mostrarTooltip.value = false
      }
    } catch {
      // Ignorar error al parsear
    }
  }
})

watch(
  mensajes,
  (nuevos) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(nuevos))
    } catch {
      // Ignorar quota storage
    }
  },
  { deep: true }
)

const scrollAlFondo = async () => {
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

const toggleChat = () => {
  abierto.value = !abierto.value
  mostrarTooltip.value = false
  if (abierto.value) {
    scrollAlFondo()
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
}

const ajustarAlturaTextarea = () => {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    inputRef.value.style.height = `${Math.min(inputRef.value.scrollHeight, 120)}px`
  }
}

const limpiarHistorial = () => {
  mensajes.value = [{
    ...mensajeInicial,
    timestamp: obtenerHoraActual()
  }]
  ultimoError.value = null
  sessionStorage.removeItem(STORAGE_KEY)
  scrollAlFondo()
}

const formatearTexto = (texto: string) => {
  if (!texto) return ''
  // Escapar HTML básico
  let sanitizado = texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Negritas **texto**
  sanitizado = sanitizado.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // Cursivas *texto*
  sanitizado = sanitizado.replace(/\*(.*?)\*/g, '<em>$1</em>')
  // Código en línea `codigo`
  sanitizado = sanitizado.replace(/`([^`]+)`/g, '<code>$1</code>')
  // Saltos de línea
  sanitizado = sanitizado.replace(/\n/g, '<br>')
  return sanitizado
}

const enviarSugerencia = (sugerencia: string) => {
  nuevoMensaje.value = sugerencia
  enviarMensajeUsuario()
}

const enviarMensajeUsuario = async () => {
  const texto = nuevoMensaje.value.trim()
  if (!texto || cargando.value) return

  ultimoError.value = null
  const hora = obtenerHoraActual()

  // Agregar turno del usuario a la lista
  const turnoUsuario: MensajeTurno = {
    role: 'user',
    content: texto,
    timestamp: hora
  }
  mensajes.value.push(turnoUsuario)
  nuevoMensaje.value = ''
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }

  scrollAlFondo()
  cargando.value = true

  // Preparar historial limpio para la API
  const historialApi = mensajes.value
    .filter(m => !m.error)
    .map(m => ({ role: m.role, content: m.content }))

  try {
    const respuesta = await enviarMensajeChat({
      historial: historialApi
    })

    if (respuesta.cuota) {
      cuotaInfo.value = respuesta.cuota
    }

    if (respuesta.exito && respuesta.respuesta) {
      mensajes.value.push({
        role: 'assistant',
        content: respuesta.respuesta,
        timestamp: obtenerHoraActual(),
        uso: respuesta.uso ? {
          prompt_tokens: respuesta.uso.prompt_tokens,
          completion_tokens: respuesta.uso.completion_tokens,
          total_tokens: respuesta.uso.total_tokens
        } : undefined
      })
    } else {
      const mensajeError = respuesta.error || 'Ocurrió un error al procesar tu consulta con Groq.'
      ultimoError.value = mensajeError
      mensajes.value.push({
        role: 'assistant',
        content: `⚠️ ${mensajeError}`,
        timestamp: obtenerHoraActual(),
        error: true
      })
    }
  } catch (err: any) {
    const errMsg = err.message || 'Error de comunicación con el servidor.'
    ultimoError.value = errMsg
    mensajes.value.push({
      role: 'assistant',
      content: `⚠️ ${errMsg}`,
      timestamp: obtenerHoraActual(),
      error: true
    })
  } finally {
    cargando.value = false
    scrollAlFondo()
  }
}

const reintentarUltimoMensaje = () => {
  const ultimoUser = [...mensajes.value].reverse().find(m => m.role === 'user')
  if (ultimoUser) {
    // Remover el último error si fue del bot
    if (mensajes.value[mensajes.value.length - 1]?.error) {
      mensajes.value.pop()
    }
    nuevoMensaje.value = ultimoUser.content
    enviarMensajeUsuario()
  }
}
</script>

<style scoped>
.chatbot-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: inherit;
}

/* FAB TRIGGER */
.chatbot-trigger-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chatbot-tooltip {
  position: absolute;
  bottom: 74px;
  right: 0;
  width: 270px;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
  box-shadow: var(--shadow-lg), 0 0 20px rgba(99, 102, 241, 0.15);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  animation: bounceTooltip 4s infinite ease-in-out;
}

@keyframes bounceTooltip {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.tooltip-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--primary-light);
  color: var(--primary);
  padding: 2px 8px;
  border-radius: 999px;
  margin-bottom: 4px;
}

.tooltip-content p {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.35;
  color: var(--text2);
}

.tooltip-close {
  background: none;
  border: none;
  color: var(--text3);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 2px;
  line-height: 1;
}

.tooltip-close:hover {
  color: var(--text);
}

.chatbot-fab {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-gradient);
  color: #ffffff;
  border: none;
  border-radius: 999px;
  padding: 12px 18px 12px 14px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: var(--shadow-glow), 0 8px 24px rgba(79, 70, 229, 0.35);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: visible;
}

.chatbot-fab:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.45);
}

.fab-icon-wrap {
  position: relative;
  font-size: 1.35rem;
  line-height: 1;
  display: flex;
  align-items: center;
}

.fab-sparkle {
  position: absolute;
  top: -6px;
  right: -8px;
  font-size: 0.8rem;
  animation: pulseSparkle 2s infinite ease-in-out;
}

@keyframes pulseSparkle {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.3); opacity: 1; }
}

.fab-badge {
  font-size: 0.85rem;
  letter-spacing: 0.3px;
}

.fab-pulse {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: inherit;
  opacity: 0.4;
  z-index: -1;
  animation: pingFab 2.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes pingFab {
  0% { transform: scale(1); opacity: 0.4; }
  75%, 100% { transform: scale(1.25); opacity: 0; }
}

/* VENTANA DE CHAT */
.chatbot-window {
  width: 390px;
  height: 580px;
  max-height: calc(100vh - 100px);
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg), 0 16px 40px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* HEADER */
.chatbot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.chatbot-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-avatar-wrap {
  position: relative;
}

.header-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--green);
  border: 2px solid var(--surface);
}

.header-titles h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
}

.header-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.model-badge {
  font-size: 0.65rem;
  background: var(--primary-light);
  color: var(--primary);
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 700;
}

.header-sub-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.header-sub {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text3);
}

.header-cuota-pill {
  font-size: 0.65rem;
  font-weight: 700;
  background: var(--surface-subtle);
  color: var(--primary);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 999px;
  letter-spacing: 0.2px;
}

.header-cuota-pill.cuota-baja {
  background: var(--amber-light);
  color: var(--amber);
  border-color: var(--amber);
}

.chatbot-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-header-action {
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  color: var(--text2);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-header-action:hover {
  background: var(--primary-light);
  color: var(--primary);
}

/* CUERPO */
.chatbot-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
}

.chat-welcome-banner {
  display: flex;
  gap: 10px;
  background: var(--surface-subtle);
  border: 1px dashed var(--border2);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 0.8rem;
  color: var(--text2);
}

.welcome-icon {
  font-size: 1.1rem;
}

.welcome-text strong {
  display: block;
  color: var(--text);
  margin-bottom: 2px;
}

.welcome-text p {
  margin: 0;
  line-height: 1.35;
}

/* BURBUJAS */
.chat-bubble-wrap {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  width: 100%;
}

.bubble-user-wrap {
  justify-content: flex-end;
}

.bubble-bot-wrap {
  justify-content: flex-start;
}

.bot-bubble-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.chat-bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 0.88rem;
  line-height: 1.45;
  word-break: break-word;
}

.bubble-user {
  background: var(--primary-gradient);
  color: #ffffff;
  border-bottom-right-radius: 4px;
  box-shadow: var(--shadow-sm);
}

.bubble-bot {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow-sm);
}

.bubble-error {
  background: var(--red-light);
  border-color: var(--red);
  color: var(--red);
}

.bubble-text :deep(strong) {
  font-weight: 700;
  color: inherit;
}

.bubble-text :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  padding: 1px 4px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.82rem;
}

.bubble-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  margin-top: 4px;
  font-size: 0.7rem;
  opacity: 0.8;
}

.bubble-user .bubble-footer {
  color: rgba(255, 255, 255, 0.85);
}

.bubble-bot .bubble-footer {
  color: var(--text3);
}

.bubble-tokens {
  font-weight: 600;
}

/* TYPING INDICATOR */
.bubble-typing {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
}

.typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: bounceTyping 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounceTyping {
  0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.typing-label {
  font-size: 0.78rem;
  color: var(--text3);
}

/* SUGERENCIAS RÁPIDAS */
.chat-quick-suggestions {
  margin-top: 6px;
}

.suggestions-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text3);
  margin-bottom: 6px;
}

.chips-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.suggestion-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--primary);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  font-size: 0.8rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  background: var(--primary-light);
  border-color: var(--border-focus);
  transform: translateX(3px);
}

/* ERROR BANNER */
.chat-error-banner {
  background: var(--red-light);
  border: 1px solid var(--red);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--red);
}

.error-msg-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-retry {
  background: var(--surface);
  border: 1px solid var(--red);
  color: var(--red);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-retry:hover {
  background: var(--red);
  color: #ffffff;
}

/* FOOTER */
.chatbot-footer {
  padding: 12px 14px;
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.chat-input-form {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px 8px 6px 12px;
  transition: border-color 0.2s ease;
}

.chat-input-form:focus-within {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px var(--primary-glow);
}

.chat-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: inherit;
  font-size: 0.88rem;
  color: var(--text);
  resize: none;
  max-height: 120px;
  line-height: 1.4;
  padding: 4px 0;
}

.chat-textarea::placeholder {
  color: var(--text3);
}

.btn-chat-send {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #ffffff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.btn-chat-send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

.btn-chat-send:not(:disabled):hover {
  transform: scale(1.08);
}

.spinner-inline {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chatbot-disclaimer {
  text-align: center;
  margin-top: 6px;
  font-size: 0.68rem;
  color: var(--text3);
}

/* ANIMACIONES */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* RESPONSIVE */
@media (max-width: 480px) {
  .chatbot-container {
    bottom: 16px;
    right: 16px;
  }

  .chatbot-window {
    width: calc(100vw - 32px);
    height: calc(100vh - 100px);
    max-height: 560px;
    right: 0;
  }

  .chatbot-tooltip {
    width: calc(100vw - 80px);
  }
}
</style>
