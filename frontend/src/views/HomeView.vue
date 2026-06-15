<template>
  <div class="home">
    <div class="hero">
      <h1>Encuentra técnicos verificados en Cusco</h1>
      <p>Conecta con carpinteros, gasfiteros, electricistas y más</p>
      <div class="hero-btns">
        <router-link to="/buscar" class="btn-verde">Buscar técnicos</router-link>
        <router-link to="/registro-trabajador" class="btn-outline">Soy técnico, quiero registrarme</router-link>
      </div>
    </div>
    <div class="features">
      <div class="feature">
        <div class="icon">✅</div>
        <h3>Técnicos verificados</h3>
        <p>Cada técnico es revisado y aprobado por nuestro equipo antes de aparecer en la plataforma.</p>
      </div>
      <div class="feature">
        <div class="icon">📍</div>
        <h3>Búsqueda por ubicación</h3>
        <p>Encuentra técnicos cercanos a ti usando geolocalización en tiempo real.</p>
      </div>
      <div class="feature">
        <div class="icon">⭐</div>
        <h3>Calificaciones reales</h3>
        <p>Lee comentarios de otros clientes para elegir al mejor profesional.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 64px 32px;
  text-align: center;
}
.hero h1 { font-size: 32px; font-weight: 700; margin-bottom: 12px; }
.hero p { font-size: 16px; color: #666; margin-bottom: 28px; }
.hero-btns { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.btn-verde {
  background: #1D9E75; color: #fff;
  padding: 12px 24px; border-radius: 8px;
  text-decoration: none; font-weight: 600;
}
.btn-outline {
  border: 1px solid #1D9E75; color: #1D9E75;
  padding: 12px 24px; border-radius: 8px;
  text-decoration: none; font-weight: 600;
}
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  max-width: 900px;
  margin: 48px auto;
  padding: 0 24px;
}
.feature {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}
.icon { font-size: 32px; margin-bottom: 12px; }
.feature h3 { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.feature p { font-size: 14px; color: #666; line-height: 1.6; }
</style>