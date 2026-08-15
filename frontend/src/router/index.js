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
import LinkedAccountsView from '../pages/LinkedAccountsPage.vue'
import AddDream from '../pages/AddDreamPage.vue'
import settings from '../pages/ProfileSetting.vue'
import Optionpage from '../pages/OptionPage.vue'
import Resetpass from '../pages/NewPassword.vue'
import Setbudget from '../pages/SetBudget.vue'
import ReceiptScanner from '../pages/ReceiptScanner.vue'
import reports from '../pages/FinancialReport.vue'

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
    {
      path: '/add-dream',
      name: 'add-dream',
      component: AddDream
    },
    {
      path: '/settings',
      name: 'settings',
      component: settings
    },
    {
      path: '/Optionpage',
      name: 'Optionpage',
      component: Optionpage
    },
    {path: '/resetpass',
      name: 'resetpass',
      component: Resetpass
    },
    {
      path: '/setbudget',
      name: 'setbudget',
      component: Setbudget
    },
    {
      path: '/receipt-scanner',
      name: 'receipt-scanner',
      component: ReceiptScanner
    },
    {
      path: '/reports', 
      name: 'reports',
      component: reports
    },
    // Catch-all fallback to Dashboard if unknown path is entered
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ]
})

export default router