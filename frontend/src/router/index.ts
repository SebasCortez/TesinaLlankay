import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const DEFAULT_TITLE = 'Llankay | Técnicos y Especialistas en Cusco'
const DEFAULT_DESCRIPTION = 'Encuentra electricistas, gasfiteros, carpinteros y técnicos calificados en Cusco con mapa satelital en tiempo real.'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue'),
      meta: {
        title: 'Inicio · Llankay | Técnicos Verificados en Cusco',
        description: 'Conecta con técnicos calificados, gasfiteros y electricistas cerca de ti en los distritos de Cusco.'
      }
    },
    {
      path: '/buscar',
      name: 'Buscar',
      component: () => import('../views/BuscarView.vue'),
      meta: {
        title: 'Buscar Técnicos en Cusco · Mapa Satelital | Llankay',
        description: 'Explora y filtra especialistas técnicos disponibles en tiempo real en Cusco por categoría y cercanía.'
      }
    },
    {
      path: '/trabajador/:id',
      name: 'PerfilTrabajador',
      component: () => import('../views/PerfilTrabajadorView.vue'),
      meta: {
        title: 'Perfil Profesional del Técnico | Llankay',
        description: 'Conoce la experiencia, calificaciones y reseñas del técnico antes de solicitar su servicio.'
      }
    },
    {
      path: '/trabajador/:id/solicitar',
      name: 'EnviarSolicitud',
      component: () => import('../views/EnviarSolicitudView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Enviar Solicitud de Servicio | Llankay',
        description: 'Solicita una visita técnica o cotización detallando tu requerimiento en Cusco.'
      }
    },
    {
      path: '/solicitudes',
      name: 'Solicitudes',
      component: () => import('../views/SolicitudesView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Mis Solicitudes de Servicio | Llankay',
        description: 'Gestiona tus solicitudes de trabajo activas, completadas o recibidas.'
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: {
        title: 'Iniciar Sesión | Llankay',
        description: 'Ingresa a tu cuenta de cliente o técnico para gestionar tus servicios en Cusco.'
      }
    },
    {
      path: '/registro-cliente',
      name: 'RegistroCliente',
      component: () => import('../views/RegistroClienteView.vue'),
      meta: {
        title: 'Crear Cuenta de Cliente | Llankay',
        description: 'Regístrate gratis para contactar y contratar técnicos verificados en Cusco.'
      }
    },
    {
      path: '/registro-trabajador',
      name: 'RegistroTrabajador',
      component: () => import('../views/RegistroTrabajadorView.vue'),
      meta: {
        title: 'Únete como Técnico Profesional | Llankay',
        description: 'Regístrate como especialista en Cusco, recibe clientes directos y haz crecer tu reputación.'
      }
    },
    {
      path: '/recuperar-password',
      name: 'RecuperarPassword',
      component: () => import('../views/RecuperarPasswordView.vue'),
      meta: {
        title: 'Recuperar Contraseña | Llankay',
        description: 'Solicita un enlace seguro para restablecer la contraseña de tu cuenta.'
      }
    },
    {
      path: '/restablecer-password',
      name: 'RestablecerPassword',
      component: () => import('../views/RestablecerPasswordView.vue'),
      meta: {
        title: 'Restablecer Contraseña | Llankay',
        description: 'Ingresa tu nueva contraseña para acceder a la plataforma.'
      }
    },
    {
      path: '/mi-perfil',
      name: 'MiPerfil',
      component: () => import('../views/MiPerfilView.vue'),
      meta: {
        requiresAuth: true,
        title: 'Mi Perfil de Usuario | Llankay',
        description: 'Administra tus datos personales, foto, especialidad técnica y ubicación GPS.'
      }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('../views/AdminView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        title: 'Panel de Administración | Llankay',
        description: 'Gestión y validación de técnicos y métricas de la plataforma.'
      }
    },
    {
      path: '/politica-privacidad',
      name: 'PoliticaPrivacidad',
      component: () => import('../views/PoliticaPrivacidadView.vue'),
      meta: {
        title: 'Política de Privacidad (Ley N° 29733) | Llankay',
        description: 'Conoce cómo protegemos tus datos personales conforme a las leyes de la República del Perú.'
      }
    },
    {
      path: '/terminos-condiciones',
      name: 'TerminosCondiciones',
      component: () => import('../views/TerminosCondicionesView.vue'),
      meta: {
        title: 'Términos y Condiciones de Uso | Llankay',
        description: 'Normativa de intermediación y condiciones de servicio para clientes y técnicos en Cusco.'
      }
    },
    {
      path: '/contacto',
      name: 'Contacto',
      component: () => import('../views/ContactoView.vue'),
      meta: {
        title: 'Contacto y Sede en Cusco | Llankay',
        description: 'Comunícate con nuestra central en Wanchaq, Cusco, teléfonos o vía WhatsApp directo.'
      }
    },
    {
      path: '/gracias',
      name: 'Gracias',
      component: () => import('../views/GraciasView.vue'),
      meta: {
        title: '¡Muchas Gracias! · Confirmación | Llankay',
        description: 'Confirmación de envío de solicitud y próximos pasos de atención.'
      }
    },
    // Catch-all 404
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFoundView.vue'),
      meta: {
        title: 'Página No Encontrada (404) | Llankay',
        description: 'La página a la que intentas acceder no existe o fue movida.'
      }
    }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

// Control de autenticación
router.beforeEach((to, _, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.estaAutenticado) {
    next('/login')
  } else if (to.meta.requiresAdmin && !auth.esAdmin) {
    next('/')
  } else {
    next()
  }
})

// Meta títulos dinámicos y descripción SEO por página
router.afterEach((to) => {
  const title = (to.meta.title as string) || DEFAULT_TITLE
  document.title = title

  const metaDesc = document.querySelector('meta[name="description"]')
  const descriptionContent = (to.meta.description as string) || DEFAULT_DESCRIPTION
  if (metaDesc) {
    metaDesc.setAttribute('content', descriptionContent)
  } else {
    const newMeta = document.createElement('meta')
    newMeta.name = 'description'
    newMeta.content = descriptionContent
    document.head.appendChild(newMeta)
  }
})

export default router