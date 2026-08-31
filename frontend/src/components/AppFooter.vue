<template>
  <footer class="app-footer">
    <div class="footer-top">
      <div class="footer-container">
        <div class="footer-grid">

          <!-- COLUMNA 1: MARCA Y SEDE REAL -->
          <div class="footer-col brand-col">
            <router-link to="/" class="footer-logo">
              <div class="logo-icon">🔧</div>
              <div class="logo-text-wrap">
                <span class="logo-text">Llankay</span>
                <span class="logo-badge">Cusco</span>
              </div>
            </router-link>
            <p class="footer-tagline">
              La plataforma líder en Cusco que conecta vecinos con especialistas verificados, geolocalización en tiempo real y calificaciones confiables.
            </p>
            <div class="footer-address-box">
              <div class="fab-row">
                <span class="fab-icon">📍</span>
                <span>Plataforma 100% Digital · Cusco, Perú</span>
              </div>
              <div class="fab-row">
                <span class="fab-icon">✉️</span>
                <a href="mailto:proyectollankay@gmail.com" class="footer-email-link">proyectollankay@gmail.com</a>
              </div>
            </div>
          </div>

          <!-- COLUMNA 2: ESPECIALIDADES EN CUSCO -->
          <div class="footer-col">
            <h4>Especialidades Técnicas</h4>
            <ul class="footer-links">
              <li><router-link to="/buscar?categoria=Electricidad">⚡ Electricistas en Cusco</router-link></li>
              <li><router-link to="/buscar?categoria=Gasfitería">💧 Gasfitería y Termas</router-link></li>
              <li><router-link to="/buscar?categoria=Albañilería y Construcción">🧱 Albañilería y Obras</router-link></li>
              <li><router-link to="/buscar?categoria=Drywall y Cielorraso">🏗️ Drywall y Cielorraso</router-link></li>
              <li><router-link to="/buscar?categoria=Soldadura y Estructuras Metálicas">🔥 Soldadura y Herrería</router-link></li>
              <li><router-link to="/buscar?categoria=Carpintería">🪚 Carpintería Fina</router-link></li>
              <li><router-link to="/buscar">🗺️ Ver Todas las Especialidades</router-link></li>
            </ul>
          </div>

          <!-- COLUMNA 3: PROFESIONALES Y CLIENTES -->
          <div class="footer-col">
            <h4>Acceso y Registro</h4>
            <ul class="footer-links">
              <li><router-link to="/registro-trabajador">👷 Únete como Técnico</router-link></li>
              <li><router-link to="/registro-cliente">👤 Registro de Clientes</router-link></li>
              <li><router-link to="/login">🔑 Iniciar Sesión</router-link></li>
              <li><router-link to="/recuperar-password">❓ Recuperar Contraseña</router-link></li>
              <li><router-link to="/contacto">✉️ Centro de Contacto</router-link></li>
            </ul>
          </div>

          <!-- COLUMNA 4: LEGAL Y PRIVACIDAD -->
          <div class="footer-col">
            <h4>Transparencia y Legal</h4>
            <ul class="footer-links">
              <li><router-link to="/politica-privacidad">📄 Política de Privacidad</router-link></li>
              <li><router-link to="/terminos-condiciones">⚖️ Términos y Condiciones</router-link></li>
              <li>
                <a href="#" @click.prevent="$emit('configurar-cookies')">
                  🍪 Configurar Cookies
                </a>
              </li>
              <li>
                <router-link to="/contacto">
                  ✉️ Atención al Usuario
                </router-link>
              </li>
            </ul>

            <div class="garantia-badge">
              <span class="gb-icon">🛡️</span>
              <div class="gb-text">
                <strong>Verificación Segura</strong>
                <span>Perfiles revisados y validados</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- FOOTER BOTTOM -->
    <div class="footer-bottom">
      <div class="footer-container fb-inner">
        <div class="fb-copy">
          © {{ new Date().getFullYear() }} Llankay. Todos los derechos reservados. Desarrollado para la región del Cusco, Perú.
        </div>
        <div class="fb-badges">
          <span class="badge badge-gray">🇵🇪 Cusco · Perú</span>
          <span class="badge badge-gray">Ley N° 29733</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
defineEmits(['configurar-cookies'])
</script>

<style scoped>
.app-footer {
  margin-top: auto;
  background: var(--surface);
  border-top: 1px solid var(--border);
  color: var(--text2);
  font-size: 13.5px;
}

.footer-top {
  padding: 56px 24px 44px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1.2fr;
  gap: 40px;
}

@media (max-width: 960px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
}

@media (max-width: 600px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}

.footer-logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 800;
  font-size: 18px;
  margin-bottom: 14px;
}

.footer-tagline {
  line-height: 1.6;
  color: var(--text2);
  margin-bottom: 18px;
  max-width: 380px;
}

.footer-address-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--surface-subtle);
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.fab-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text);
}

.fab-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.footer-col h4 {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 16px;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.footer-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-links a {
  color: var(--text2);
  text-decoration: none;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
}

.footer-links a:hover {
  color: var(--primary);
  transform: translateX(3px);
}

.whatsapp-link {
  color: #10B981 !important;
  font-weight: 600;
}

.garantia-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  padding: 12px 14px;
  background: var(--primary-light);
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: var(--radius-sm);
}

.gb-icon {
  font-size: 20px;
}

.gb-text strong {
  display: block;
  font-size: 12.5px;
  color: var(--primary);
}

.gb-text span {
  font-size: 11px;
  color: var(--text2);
}

.footer-bottom {
  background: var(--surface-subtle);
  border-top: 1px solid var(--border);
  padding: 20px 24px;
  font-size: 12.5px;
}

.fb-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.fb-copy {
  color: var(--text3);
}

.fb-badges {
  display: flex;
  gap: 8px;
}
</style>
