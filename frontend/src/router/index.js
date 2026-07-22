import { createRouter, createWebHistory } from 'vue-router'

// 1. Import your root page layouts
import SignupView from '../pages/signup.vue'
import LoginPageView from '../pages/Loginpage.vue'
import ResetPasswordView from '../pages/Resetpassword.vue'
import termsView from '../pages/TermsPage.vue'
import policy from '../pages/PrivacyPage.vue'
import dashboard from '../pages/DashBoardPage.vue' 
import goals from '../pages/Goalspage.vue'
import imports from '../pages/Imports.vue'
import profile from '../pages/ProfilePage.vue'
import AddExpensePage from '../pages/AddExpensePage.vue'
import LinkedAccountsView from '../pages/LinkedAccountsPage.vue' // 👈 Fixed missing import!

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'signup',
      component: SignupView
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
    },
    {
      path: '/terms',
      name: 'terms',
      component: termsView
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: policy
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: dashboard
    },
    {
      path: '/goals',
      name: 'goals',
      component: goals
    },
    {
      path: '/imports',
      name: 'imports',
      component: imports
    },
    {
      path: '/profile',
      name: 'profile',
      component: profile
    },
    {
      path: '/addexpense',
      name: 'addexpense',
      component: AddExpensePage
    },
    {
      path: '/linked-accounts',
      name: 'linked-accounts',
      component: LinkedAccountsView
    },
    // Catch-all fallback to Dashboard if unknown path is entered
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ]
})

export default router