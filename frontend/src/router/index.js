import { createRouter, createWebHistory } from 'vue-router'

// 1. Import your root page layouts
import SignupView from '../pages/signup.vue'
import LoginPageView from '../pages/Loginpage.vue'
import ResetPasswordView from '../pages/Resetpassword.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'signup',
      component: SignupView // This makes your form the default home page!
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPageView
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPasswordView
    }
  ]
})

export default router