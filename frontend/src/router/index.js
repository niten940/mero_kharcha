import { createRouter, createWebHistory } from 'vue-router'

// 1. Import your root page layouts
import SignupView from '../pages/signup.vue'
import LoginPageView from '../pages/Loginpage.vue'
import ResetPasswordView from '../pages/Resetpassword.vue'
import termsView from '../pages/TermsPage.vue'
import policy from '../pages/PrivacyPage.vue'
import dashboard from '../pages/DashBoardPage.vue' 
import goals from '../pages/Goalspage.vue'
import imports from '../pages/Imports.vue'// Import your terms and conditions page
import profile from '../pages/ProfilePage.vue' // Import your profile page

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
   
    {
      path: '/login',
      name: 'login',
      component: LoginPageView
    },
     {
      path: '/',
      name: 'signup',
      component: SignupView // This makes your form the default home page!
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPasswordView
    },
    {
      path: '/terms',
      name: 'terms',
      component: termsView // This is a placeholder for your terms and conditions page
    },
      {
        path: '/privacy',
        name: 'privacy',
        component: policy // This is a placeholder for your privacy policy page
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: dashboard // This is a placeholder for your dashboard page
    },
    {
      path: '/goals',
      name: 'goals',
      component: goals // This is a placeholder for your goals page
    },
    {
      path: '/imports',
      name: 'imports',
      component: imports // This is a placeholder for your imports page
    },
    {
      path: '/profile',
      name: 'profile',
      component: profile // This is a placeholder for your profile page
    }
  ]
})

export default router