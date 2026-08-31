<template>
  <div v-if="mostrarBanner" class="cookie-banner-overlay">
    <div class="cookie-banner card">
      <div class="cookie-content">
        <div class="cookie-icon-wrap">
          <span class="cookie-icon">🍪</span>
        </div>

        <div class="cookie-text">
          <div class="cookie-title">
            <strong>Control de Privacidad y Uso de Cookies</strong>
            <span class="cookie-badge">Ley N° 29733</span>
          </div>
          <p>
            Utilizamos cookies propias y de terceros para garantizar el correcto funcionamiento del mapa interactivo, recordar tus preferencias de tema y analizar el rendimiento de la plataforma en Cusco. Puedes aceptar todas, rechazarlas o configurar tus preferencias.
            <router-link to="/politica-privacidad" class="cookie-link" @click="mostrarBanner = false">
              Leer Política de Privacidad
            </router-link>
          </p>
        </div>
      </div>

      <!-- BOTONES DE ACCIÓN RÁPIDA -->
      <div v-if="!modoConfigurar" class="cookie-actions">
        <button class="btn-secondary btn-sm" @click="modoConfigurar = true">
          ⚙️ Personalizar
        </button>
        <button class="btn-secondary btn-sm" @click="guardarConsentimiento('esenciales')">
          Solo esenciales
        </button>
        <button class="btn-primary btn-sm" @click="guardarConsentimiento('todas')">
          Aceptar todas ➔
        </button>
      </div>

      <!-- PANEL DE CONFIGURACIÓN GRANULAR -->
      <div v-else class="cookie-config-panel">
        <div class="config-grid">
          <div class="config-item">
            <div class="config-info">
              <strong>Cookies Técnicas Esenciales (Obligatorias)</strong>
              <p>Necesarias para mantener tu sesión segura, modo dual cliente/técnico y CSRF.</p>
            </div>
            <input type="checkbox" checked disabled class="config-check" />
          </div>

          <div class="config-item">
            <div class="config-info">
              <strong>Cookies de Preferencias y Tema</strong>
              <p>Guardan tu selección de modo claro/oscuro y distrito preferido de Cusco.</p>
            </div>
            <input v-model="prefs.preferencias" type="checkbox" class="config-check" />
          </div>

          <div class="config-item">
            <div class="config-info">
              <strong>Cookies de Rendimiento y Análisis</strong>
              <p>Nos ayudan a optimizar la velocidad de búsqueda de técnicos en el mapa satelital.</p>
            </div>
            <input v-model="prefs.analiticas" type="checkbox" class="config-check" />
          </div>
        </div>

        <div class="config-actions">
          <button class="btn-secondary btn-sm" @click="modoConfigurar = false">
            Volver
          </button>
          <button class="btn-primary btn-sm" @click="guardarConsentimiento('personalizado')">
            Guardar preferencias seleccionadas
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const STORAGE_KEY = 'cookie_consent_llankay'

const mostrarBanner = ref(false)
const modoConfigurar = ref(false)

const prefs = ref({
  esenciales: true,
  preferencias: true,
  analiticas: true
})

function verificarConsentimiento() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) {
    // Mostrar si no ha tomado decisión
    mostrarBanner.value = true
  }
}

function guardarConsentimiento(tipo: 'todas' | 'esenciales' | 'personalizado') {
  let decision = {
    esenciales: true,
    preferencias: tipo === 'todas' || (tipo === 'personalizado' && prefs.value.preferencias),
    analiticas: tipo === 'todas' || (tipo === 'personalizado' && prefs.value.analiticas),
    fecha: new Date().toISOString()
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(decision))
  mostrarBanner.value = false
  modoConfigurar.value = false
}

// Método público para abrir desde el footer
function abrirConfiguracion() {
  modoConfigurar.value = true
  mostrarBanner.value = true
}

defineExpose({
  abrirConfiguracion
})

onMounted(() => {
  verificarConsentimiento()
})
</script>

<style scoped>
.cookie-banner-overlay {
  position: fixed;
  bottom: 24px;
  left: 24px;
  right: 24px;
  max-width: 1100px;
  margin: 0 auto;
  z-index: 999;
  animation: slideUpFade 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUpFade {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cookie-banner {
  padding: 24px 28px;
  border-radius: var(--radius);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.25);
  border: 1.5px solid var(--border);
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.cookie-content {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.cookie-icon-wrap {
  width: 44px;
  height: 44px;
  background: var(--amber-light);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.cookie-text {
  flex: 1;
}

.cookie-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.cookie-title strong {
  font-size: 15px;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.cookie-badge {
  font-size: 10.5px;
  font-weight: 700;
  background: var(--primary-light);
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 6px;
}

.cookie-text p {
  font-size: 13px;
  color: var(--text2);
  line-height: 1.5;
  margin: 0;
}

.cookie-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}

.cookie-link:hover {
  text-decoration: underline;
}

.cookie-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

/* PANEL CONFIGURACIÓN */
.cookie-config-panel {
  border-top: 1px solid var(--border);
  padding-top: 16px;
  margin-top: 8px;
}

.config-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface-subtle);
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.config-info strong {
  display: block;
  font-size: 13px;
  color: var(--text);
  margin-bottom: 2px;
}

.config-info p {
  font-size: 12px;
  color: var(--text3);
  margin: 0;
}

.config-check {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 640px) {
  .cookie-banner-overlay {
    bottom: 12px;
    left: 12px;
    right: 12px;
  }
  .cookie-banner {
    padding: 18px 16px;
  }
  .cookie-content {
    flex-direction: column;
    gap: 12px;
  }
  .cookie-actions {
    flex-direction: column;
  }
  .cookie-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>
