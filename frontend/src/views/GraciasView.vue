<template>
  <div class="gracias-page page-center">
    <div class="gracias-wrapper">
      <div class="gracias-glow"></div>
      <div class="card gracias-card">
        <!-- ÍCONO DE CELEBRACIÓN -->
        <div class="gracias-icon-wrap">
          <div class="gracias-icon">
            <span v-if="tipo === 'solicitud'">🛠️</span>
            <span v-else-if="tipo === 'contacto'">✉️</span>
            <span v-else-if="tipo === 'registro'">🎉</span>
            <span v-else>✅</span>
          </div>
          <div class="gracias-check">✓</div>
        </div>

        <!-- TÍTULO DINÁMICO -->
        <h2>{{ titulo }}</h2>
        <p class="gracias-sub">{{ descripcion }}</p>

        <!-- TARJETA DE PRÓXIMOS PASOS -->
        <div class="pasos-card">
          <h4>📋 ¿Qué sucederá a continuación?</h4>
          <div class="pasos-items">
            <div class="paso-row" v-for="(p, i) in proximosPasos" :key="i">
              <div class="paso-badge">{{ i + 1 }}</div>
              <div class="paso-text">
                <strong>{{ p.titulo }}</strong>
                <p>{{ p.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ACCIONES RÁPIDAS -->
        <div class="gracias-actions">
          <router-link v-if="auth.estaAutenticado" to="/solicitudes" class="btn-primary gracias-btn">
            <span>📋</span> Ver mis solicitudes
          </router-link>
          <router-link to="/buscar" class="btn-secondary gracias-btn">
            <span>🔍</span> Explorar más técnicos
          </router-link>
          <router-link to="/" class="btn-secondary gracias-btn">
            <span>🏠</span> Inicio
          </router-link>
        </div>

        <p class="gracias-contacto">
          ¿Dudas o consultas? Escríbenos directamente a <a href="mailto:proyectollankay@gmail.com">proyectollankay@gmail.com</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()

const tipo = computed(() => (route.query.tipo as string) || 'solicitud')
const nombre = computed(() => (route.query.nombre as string) || '')
const tecnico = computed(() => (route.query.tecnico as string) || '')

const titulo = computed(() => {
  if (tipo.value === 'contacto') return '¡Gracias por comunicarte con nosotros!'
  if (tipo.value === 'registro') return '¡Bienvenido a Llankay!'
  return '¡Tu solicitud fue enviada con éxito!'
})

const descripcion = computed(() => {
  if (tipo.value === 'contacto') {
    return `Hemos recibido tu mensaje${nombre.value ? ', ' + nombre.value : ''}. Te responderemos a tu correo a la brevedad.`
  }
  if (tipo.value === 'registro') {
    return 'Tu cuenta ha sido creada exitosamente. Ya puedes buscar técnicos o gestionar tus servicios en Cusco.'
  }
  return `La solicitud fue remitida${tecnico.value ? ' a ' + tecnico.value : ' al técnico'}. En breve se comunicará contigo para coordinar la visita y cotización.`
})

const proximosPasos = computed(() => {
  if (tipo.value === 'contacto') {
    return [
      { titulo: 'Revisión por soporte', desc: 'Nuestro equipo revisará tu mensaje y requerimientos.' },
      { titulo: 'Respuesta por correo', desc: 'Te responderemos por correo electrónico a la brevedad.' },
      { titulo: 'Solución a tu consulta', desc: 'Brindaremos seguimiento hasta que tu duda quede resuelta.' },
    ]
  }
  return [
    { titulo: 'Notificación al técnico', desc: 'El profesional recibe una alerta inmediata con los detalles de tu solicitud.' },
    { titulo: 'Aceptación y contacto', desc: 'El técnico aceptará el trabajo y te escribirá o llamará a tu celular para coordinar.' },
    { titulo: 'Seguimiento y Calificación', desc: 'Puedes ver el estado en "Mis Solicitudes" y calificar el trabajo al finalizar.' },
  ]
})
</script>

<style scoped>
.gracias-page {
  padding: 40px 16px 60px;
}

.gracias-wrapper {
  position: relative;
  width: 620px;
  max-width: 100%;
}

.gracias-glow {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, rgba(99, 102, 241, 0.1) 60%, transparent 80%);
  filter: blur(60px);
  pointer-events: none;
}

.gracias-card {
  padding: 48px 40px;
  text-align: center;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.gracias-icon-wrap {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.gracias-icon {
  width: 80px;
  height: 80px;
  background: var(--primary-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 38px;
  box-shadow: 0 8px 24px var(--primary-glow);
}

.gracias-check {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  background: #10B981;
  color: #fff;
  border-radius: 50%;
  border: 3px solid var(--surface);
  font-size: 14px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gracias-card h2 {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 10px;
}

.gracias-sub {
  font-size: 15px;
  color: var(--text2);
  line-height: 1.6;
  max-width: 480px;
  margin: 0 auto 28px;
}

.pasos-card {
  background: var(--surface-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 24px;
  text-align: left;
  margin-bottom: 28px;
}

.pasos-card h4 {
  font-size: 15px;
  font-weight: 800;
  margin-bottom: 16px;
  color: var(--text);
}

.pasos-items {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.paso-row {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.paso-badge {
  width: 24px;
  height: 24px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 50%;
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.paso-text strong {
  display: block;
  font-size: 13.5px;
  color: var(--text);
  margin-bottom: 2px;
}

.paso-text p {
  font-size: 12.5px;
  color: var(--text2);
  margin: 0;
  line-height: 1.4;
}

.gracias-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.gracias-btn {
  padding: 12px 22px;
  font-size: 14px;
}

.gracias-contacto {
  font-size: 13px;
  color: var(--text3);
  margin-top: 24px;
}

.gracias-contacto a {
  color: #10B981;
  font-weight: 700;
  text-decoration: none;
}

.gracias-contacto a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .gracias-card {
    padding: 32px 18px;
  }
  .gracias-card h2 {
    font-size: 22px;
  }
  .gracias-actions {
    flex-direction: column;
  }
  .gracias-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
