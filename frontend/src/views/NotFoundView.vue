<template>
  <div class="not-found-page page-center">
    <div class="not-found-wrapper">
      <div class="nf-glow"></div>
      <div class="card nf-card">
        <!-- ILUSTRACIÓN 404 CUSCO -->
        <div class="nf-visual">
          <div class="nf-number-wrap">
            <span class="nf-num">4</span>
            <div class="nf-icon-disc">
              <span class="nf-tool">🔧</span>
            </div>
            <span class="nf-num">4</span>
          </div>
          <div class="nf-badge">
            <span>📍 Error de Ruta · Llankay</span>
          </div>
        </div>

        <h2>¡Ups! Esta página no se encuentra en el mapa</h2>
        <p class="nf-desc">
          La dirección que buscas no existe, cambió de ubicación o fue movida temporalmente.
        </p>

        <!-- ACCIONES RÁPIDAS -->
        <div class="nf-actions">
          <router-link to="/" class="btn-primary nf-btn">
            <span>🏠</span> Volver al Inicio
          </router-link>
          <router-link to="/buscar" class="btn-secondary nf-btn">
            <span>🔍</span> Explorar Técnicos en Cusco
          </router-link>
        </div>

        <hr class="divider">

        <!-- CATEGORÍAS POPULARES -->
        <div class="nf-suggestions">
          <span class="sugg-label">O explora especialidades populares en Cusco:</span>
          <div class="sugg-tags">
            <router-link to="/buscar?categoria=Electricidad" class="badge badge-blue sugg-tag">⚡ Electricistas</router-link>
            <router-link to="/buscar?categoria=Gasfitería" class="badge badge-green sugg-tag">💧 Gasfitería</router-link>
            <router-link to="/buscar?categoria=Carpintería" class="badge badge-amber sugg-tag">🪚 Carpintería</router-link>
            <router-link to="/buscar?categoria=Cerrajería" class="badge badge-gray sugg-tag">🔑 Cerrajería</router-link>
          </div>
        </div>

        <p class="nf-help">
          ¿Necesitas ayuda? <router-link to="/contacto">Contáctanos directamente aquí</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Vista 404 Personalizada para Llankay
</script>

<style scoped>
.not-found-page {
  padding: 40px 16px 60px;
}

.not-found-wrapper {
  position: relative;
  width: 620px;
  max-width: 100%;
}

.nf-glow {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.1) 60%, transparent 80%);
  filter: blur(60px);
  pointer-events: none;
}

.nf-card {
  padding: 48px 40px;
  text-align: center;
  position: relative;
  z-index: 1;
  box-shadow: var(--shadow-lg);
}

.nf-visual {
  margin-bottom: 24px;
}

.nf-number-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.nf-num {
  font-size: 84px;
  font-weight: 900;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--primary);
  line-height: 1;
  text-shadow: 0 4px 20px var(--primary-glow);
}

.nf-icon-disc {
  width: 72px;
  height: 72px;
  background: var(--primary-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px var(--primary-glow);
  animation: rotateTool 4s ease-in-out infinite alternate;
}

@keyframes rotateTool {
  0% { transform: rotate(-20deg) scale(0.95); }
  100% { transform: rotate(25deg) scale(1.05); }
}

.nf-tool {
  font-size: 34px;
}

.nf-badge {
  display: inline-flex;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 16px;
}

.nf-card h2 {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 12px;
}

.nf-desc {
  font-size: 15px;
  color: var(--text2);
  line-height: 1.6;
  max-width: 460px;
  margin: 0 auto 28px;
}

.nf-actions {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

.nf-btn {
  padding: 12px 24px;
  font-size: 14.5px;
}

.nf-suggestions {
  margin: 20px 0;
}

.sugg-label {
  display: block;
  font-size: 13px;
  color: var(--text3);
  margin-bottom: 10px;
}

.sugg-tags {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.sugg-tag {
  text-decoration: none;
  padding: 6px 14px;
  font-size: 13px;
  transition: transform 0.15s ease;
}

.sugg-tag:hover {
  transform: translateY(-2px);
}

.nf-help {
  font-size: 13.5px;
  color: var(--text2);
  margin-top: 16px;
}

.nf-help a {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.nf-help a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .nf-card {
    padding: 32px 20px;
  }
  .nf-num {
    font-size: 64px;
  }
  .nf-icon-disc {
    width: 56px;
    height: 56px;
  }
  .nf-tool {
    font-size: 26px;
  }
  .nf-card h2 {
    font-size: 22px;
  }
  .nf-actions {
    flex-direction: column;
  }
  .nf-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
