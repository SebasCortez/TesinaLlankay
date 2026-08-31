<template>
  <div class="legal-page">
    <!-- HERO HEADER -->
    <div class="legal-header">
      <div class="legal-header-glow"></div>
      <div class="legal-header-content">
        <div class="legal-badge">
          <span>⚖️ Marco Legal y Normativa de Servicio</span>
        </div>
        <h1>Términos y Condiciones de Uso</h1>
        <p class="legal-sub">
          Vigente a partir del 28 de agosto de 2026 · Llankay · Cusco, Perú
        </p>
      </div>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <div class="legal-container">
      <div class="legal-card card">
        <div class="legal-intro">
          <p>
            Bienvenido a <strong>Llankay</strong>. Al acceder, registrarte o utilizar nuestra plataforma web y servicios de intermediación técnica, aceptas de manera plena y sin reservas los presentes Términos y Condiciones. Si no estás de acuerdo con alguna disposición, te solicitamos abstenerte de utilizar la plataforma.
          </p>
        </div>

        <hr class="divider">

        <!-- SECCIÓN 1 -->
        <section class="legal-section">
          <h2>1. Naturaleza y Objeto de la Plataforma</h2>
          <p>
            Llankay es una plataforma tecnológica de intermediación digital diseñada para conectar a <strong>Clientes</strong> que requieren servicios técnicos en el hogar o comercio, con <strong>Técnicos y Profesionales Independientes</strong> calificados en la región del Cusco (electricistas, gasfiteros, carpinteros, cerrajeros, pintores y afines).
          </p>
          <div class="alert alert-warning">
            ℹ️ <strong>Importante:</strong> Llankay actúa exclusivamente como facilitador de contacto y visualización georreferenciada. Los técnicos registrados operan como profesionales independientes y no mantienen relación laboral de subordinación con la plataforma.
          </div>
        </section>

        <!-- SECCIÓN 2 -->
        <section class="legal-section">
          <h2>2. Registro y Cuentas de Usuario</h2>
          <ul class="legal-list">
            <li><strong>Mayoría de edad:</strong> Para registrarse como cliente o técnico es obligatorio ser mayor de 18 años y contar con capacidad legal para contratar según las leyes peruanas.</li>
            <li><strong>Veracidad de la información:</strong> El usuario garantiza que los datos suministrados (nombres, celular de 9 dígitos, distrito, correo y experiencia técnica) son veraces, vigentes y comprobables.</li>
            <li><strong>Custodia de credenciales:</strong> Cada usuario es responsable de mantener la confidencialidad de su contraseña y de las actividades que ocurran bajo su cuenta.</li>
          </ul>
        </section>

        <!-- SECCIÓN 3 -->
        <section class="legal-section">
          <h2>3. Proceso de Verificación y Aprobación de Técnicos</h2>
          <p>
            Para garantizar la seguridad de la comunidad de Cusco:
          </p>
          <ul class="legal-list">
            <li>Toda solicitud de registro en <strong>Modo Técnico</strong> pasa por un proceso de revisión y validación administrativa por el equipo de Llankay antes de ser publicada en el mapa.</li>
            <li>Llankay se reserva el derecho de rechazar, suspender o revocar el acceso a cualquier técnico que incumpla las políticas de calidad o presente información falsa.</li>
          </ul>
        </section>

        <!-- SECCIÓN 4 -->
        <section class="legal-section">
          <h2>4. Contratación, Presupuestos y Pagos</h2>
          <ul class="legal-list">
            <li><strong>Acuerdo directo:</strong> La cotización final, alcance de trabajo, materiales y forma de pago son acordados directamente entre el cliente y el técnico prestador del servicio.</li>
            <li><strong>Cumplimiento y puntualidad:</strong> Los técnicos se comprometen a respetar los horarios y presupuestos acordados con los clientes.</li>
            <li><strong>Garantía de servicio:</strong> Los técnicos responderán directamente ante el cliente por la calidad de la mano de obra realizada.</li>
          </ul>
        </section>

        <!-- SECCIÓN 5 -->
        <section class="legal-section">
          <h2>5. Sistema de Calificaciones, Reseñas y Reputación</h2>
          <p>
            Una vez completado un servicio, los clientes pueden emitir una valoración de 1 a 5 estrellas y un comentario sobre el desempeño del profesional:
          </p>
          <ul class="legal-list">
            <li>Las reseñas deben fundamentarse en experiencias reales y mantener un lenguaje respetuoso.</li>
            <li>No se tolerarán reseñas falsas, difamatorias, con fines extorsivos o de competencia desleal. Llankay podrá moderar y eliminar comentarios que violen estas normas.</li>
          </ul>
        </section>

        <!-- SECCIÓN 6 -->
        <section class="legal-section">
          <h2>6. Conductas Prohibidas</h2>
          <p>Queda estrictamente prohibido en la plataforma:</p>
          <ul class="legal-list">
            <li>Suplantar la identidad de otra persona o registrar datos de terceros sin autorización.</li>
            <li>Utilizar la plataforma para ofrecer servicios ilegales o no autorizados por la normativa peruana.</li>
            <li>Vulnerar la seguridad del sistema, realizar scraping no autorizado o inyectar código malicioso.</li>
            <li>Acosar, discriminar o incurrir en conductas violentas hacia clientes o técnicos.</li>
          </ul>
        </section>

        <!-- SECCIÓN 7 -->
        <section class="legal-section">
          <h2>7. Propiedad Intelectual</h2>
          <p>
            Todos los logotipos, isotipos, marcas, diseños, código fuente y contenidos de Llankay son propiedad exclusiva de sus desarrolladores y están protegidos por las leyes peruanas e internacionales de derechos de autor y propiedad industrial.
          </p>
        </section>

        <!-- SECCIÓN 8 -->
        <section class="legal-section">
          <h2>8. Ley Aplicable y Jurisdicción</h2>
          <p>
            Estos Términos y Condiciones se rigen por las leyes de la <strong>República del Perú</strong>. Para cualquier controversia o discrepancia derivada del uso de la plataforma, las partes renuncian a cualquier otro fuero y se someten expresamente a la jurisdicción de los <strong>Juzgados y Tribunales del Distrito Judicial del Cusco, Perú</strong>.
          </p>
        </section>

        <!-- BOTÓN VOLVER -->
        <div class="legal-footer-btns">
          <router-link to="/" class="btn-secondary">← Volver al Inicio</router-link>
          <router-link to="/politica-privacidad" class="btn-primary">Ver Política de Privacidad ➔</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Vista de Términos y Condiciones de Llankay
</script>

<style scoped>
.legal-page {
  min-height: calc(100vh - 68px);
  padding-bottom: 60px;
}

.legal-header {
  position: relative;
  overflow: hidden;
  padding: 50px 24px 40px;
  background: var(--surface-glass);
  border-bottom: 1px solid var(--border);
  text-align: center;
}

.legal-header-glow {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 400px;
  height: 250px;
  background: var(--primary-glow);
  filter: blur(60px);
  pointer-events: none;
}

.legal-header-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

.legal-badge {
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

.legal-header h1 {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 10px;
}

.legal-sub {
  font-size: 14.5px;
  color: var(--text2);
}

.legal-container {
  max-width: 920px;
  margin: 40px auto 0;
  padding: 0 20px;
}

.legal-card {
  padding: 44px 40px;
}

.legal-intro p {
  font-size: 15.5px;
  line-height: 1.7;
  color: var(--text);
}

.legal-section {
  margin-bottom: 36px;
}

.legal-section h2 {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 14px;
  color: var(--text);
  border-left: 4px solid var(--primary);
  padding-left: 12px;
}

.legal-section p {
  font-size: 14.5px;
  line-height: 1.7;
  color: var(--text2);
  margin-bottom: 12px;
}

.legal-list {
  padding-left: 22px;
  color: var(--text2);
  font-size: 14.5px;
  line-height: 1.8;
}

.legal-list li {
  margin-bottom: 8px;
}

.legal-footer-btns {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 36px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .legal-card {
    padding: 24px 18px;
  }
  .legal-header h1 {
    font-size: 28px;
  }
}
</style>
