<template>
  <div class="home">
    <!-- HERO -->
    <div class="hero">
      <div class="hero-content">
        <div class="hero-badge">📍 Cusco, Perú</div>
        <h1>Encuentra técnicos<br>verificados cerca de ti</h1>
        <p>Conecta con electricistas, gasfiteros, carpinteros y más — con reputación verificada por la comunidad cusqueña.</p>
        <div class="hero-btns">
          <router-link to="/buscar" class="btn-primary" style="padding:13px 28px;font-size:15px">
            Buscar técnicos
          </router-link>
          <router-link to="/registro-trabajador" class="btn-secondary" style="padding:13px 28px;font-size:15px">
            Soy técnico →
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-card">
          <div class="hc-avatar" style="background:#DBEAFE;color:#1D4ED8">CH</div>
          <div>
            <div class="hc-name">Carlos Huanca</div>
            <div class="hc-job">⚡ Electricista</div>
          </div>
          <span class="badge badge-green" style="margin-left:auto">● Disponible</span>
        </div>
        <div class="hero-card">
          <div class="hc-avatar" style="background:#D1FAE5;color:#065F46">MQ</div>
          <div>
            <div class="hc-name">Miguel Quispe</div>
            <div class="hc-job">💧 Gasfitero</div>
          </div>
          <span class="badge badge-green" style="margin-left:auto">● Disponible</span>
        </div>
        <div class="hero-card">
          <div class="hc-avatar" style="background:#FEF3C7;color:#92400E">RP</div>
          <div>
            <div class="hc-name">Rosa Pumaccahua</div>
            <div class="hc-job">🪚 Carpintera</div>
          </div>
          <span class="badge badge-green" style="margin-left:auto">● Disponible</span>
        </div>
        <div class="hero-stats">
          <div class="hs"><strong>50+</strong><span>Técnicos</span></div>
          <div class="hs-div"></div>
          <div class="hs"><strong>4.8⭐</strong><span>Promedio</span></div>
          <div class="hs-div"></div>
          <div class="hs"><strong>200+</strong><span>Servicios</span></div>
        </div>
      </div>
    </div>

    <!-- CATEGORIAS -->
    <div class="categorias-section">
      <h2>¿Qué servicio necesitas?</h2>
      <div class="categorias-grid">
        <router-link v-for="cat in categorias" :key="cat.nombre" to="/buscar" class="cat-card">
          <div class="cat-icon">{{ cat.icon }}</div>
          <div class="cat-nombre">{{ cat.nombre }}</div>
        </router-link>
      </div>
    </div>

    <!-- COMO FUNCIONA -->
    <div class="como-section">
      <h2>¿Cómo funciona?</h2>
      <div class="pasos-grid">
        <div class="paso-card" v-for="paso in pasos" :key="paso.num">
          <div class="paso-num">{{ paso.num }}</div>
          <div class="paso-icon">{{ paso.icon }}</div>
          <h3>{{ paso.titulo }}</h3>
          <p>{{ paso.desc }}</p>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="cta-section">
      <h2>¿Eres técnico independiente?</h2>
      <p>Únete a TécniCusco y conecta con clientes que necesitan tus servicios</p>
      <router-link to="/registro-trabajador" class="btn-primary" style="padding:13px 28px;font-size:15px">
        Registrarme como técnico
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
const categorias = [
  { icon: '⚡', nombre: 'Electricidad' },
  { icon: '💧', nombre: 'Gasfitería' },
  { icon: '🪚', nombre: 'Carpintería' },
  { icon: '🔑', nombre: 'Cerrajería' },
  { icon: '🎨', nombre: 'Pintura' },
]

const pasos = [
  { num: '01', icon: '🔍', titulo: 'Busca un técnico', desc: 'Filtra por categoría o usa tu ubicación para encontrar técnicos cercanos.' },
  { num: '02', icon: '📩', titulo: 'Envía una solicitud', desc: 'Describe tu problema y envía la solicitud directamente al técnico.' },
  { num: '03', icon: '🔧', titulo: 'Recibe el servicio', desc: 'El técnico acepta, se comunica contigo y realiza el trabajo.' },
  { num: '04', icon: '⭐', titulo: 'Califica al técnico', desc: 'Deja tu opinión para ayudar a otros clientes a elegir mejor.' },
]
</script>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 72px 32px;
  align-items: center;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  margin-bottom: 20px;
}
.hero-content h1 {
  font-size: 42px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -1px;
  color: var(--text);
  margin-bottom: 16px;
}
.hero-content p {
  font-size: 16px;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 28px;
  max-width: 420px;
}
.hero-btns { display: flex; gap: 12px; flex-wrap: wrap; }
.hero-visual { display: flex; flex-direction: column; gap: 12px; }
.hero-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow);
}
.hc-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.hc-name { font-size: 14px; font-weight: 600; }
.hc-job { font-size: 12px; color: var(--text2); margin-top: 1px; }
.hero-stats {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: var(--shadow);
}
.hs { text-align: center; }
.hs strong { display: block; font-size: 18px; font-weight: 700; color: var(--text); }
.hs span { font-size: 12px; color: var(--text2); }
.hs-div { width: 1px; height: 32px; background: var(--border); }

.categorias-section {
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 56px 32px;
  text-align: center;
}
.categorias-section h2 { font-size: 26px; font-weight: 700; margin-bottom: 32px; }
.categorias-grid {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
  max-width: 700px;
  margin: 0 auto;
}
.cat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 24px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s;
  min-width: 110px;
}
.cat-card:hover { border-color: var(--primary); background: var(--primary-light); color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow-md); }
.cat-icon { font-size: 28px; }

.como-section {
  padding: 56px 32px;
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
}
.como-section h2 { font-size: 26px; font-weight: 700; margin-bottom: 40px; }
.pasos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
  gap: 24px;
}
.paso-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center;
  box-shadow: var(--shadow);
}
.paso-num { font-size: 11px; font-weight: 700; color: var(--primary); letter-spacing: 0.1em; margin-bottom: 12px; }
.paso-icon { font-size: 32px; margin-bottom: 12px; }
.paso-card h3 { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.paso-card p { font-size: 13px; color: var(--text2); line-height: 1.6; }

.cta-section {
  background: var(--primary);
  padding: 56px 32px;
  text-align: center;
  color: #fff;
}
.cta-section h2 { font-size: 26px; font-weight: 700; margin-bottom: 10px; }
.cta-section p { font-size: 16px; opacity: 0.85; margin-bottom: 28px; }
.cta-section .btn-primary { background: #fff; color: var(--primary); }
.cta-section .btn-primary:hover { background: #EFF6FF; }
</style>