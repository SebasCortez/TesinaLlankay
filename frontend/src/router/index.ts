import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/HomeView.vue') },
    { path: '/login', component: () => import('../views/LoginView.vue') },
    { path: '/registro-cliente', component: () => import('../views/RegistroClienteView.vue') },
    { path: '/registro-trabajador', component: () => import('../views/RegistroTrabajadorView.vue') },
    { path: '/buscar', component: () => import('../views/BuscarView.vue') },
    { path: '/trabajador/:id', component: () => import('../views/PerfilTrabajadorView.vue') },
    {
      path: '/mi-perfil',
      component: () => import('../views/MiPerfilView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
  ]
})

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

export default router