<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row">
          <MeroKharchaLogo :size="10" />
        </div>
        <!-- <q-btn flat round dense icon="notifications_none" color="grey-8" size="sm" /> -->
      </div>

      <!-- Just-scanned receipt banner -->
      <transition name="mk-fade">
        <div v-if="scannedBanner" class="mk-scan-banner" @click="goFinishScannedExpense">
          <q-icon name="receipt_long" size="22px" color="white" class="mk-scan-banner-icon" />
          <div class="col">
            <div class="mk-scan-banner-title">Receipt scanned</div>
            <div class="mk-scan-banner-text">
              Rs. {{ formatAmount(scannedBanner.amount) }}
              <span v-if="scannedBanner.date">&middot; {{ scannedBanner.date }}</span>
              — tap to finish adding it
            </div>
          </div>
          <q-btn
            round
            flat
            dense
            icon="close"
            size="sm"
            color="white"
            @click.stop="dismissScannedBanner"
          />
        </div>
      </transition>

      <!-- Loading skeletons -->
      <template v-if="isLoading">
        <q-skeleton type="text" width="140px" class="q-mb-xs" />
        <q-skeleton type="text" height="38px" width="200px" class="q-mb-md" />
        <q-skeleton type="rect" height="80px" class="q-mb-md rounded-borders" />
        <q-skeleton type="rect" height="90px" class="q-mb-md rounded-borders" />
        <q-skeleton type="rect" height="130px" width="240px" class="q-mb-md rounded-borders" />
        <q-skeleton type="rect" height="64px" class="q-mb-sm rounded-borders" />
        <q-skeleton type="rect" height="64px" class="rounded-borders" />
      </template>

      <template v-else>
        <!-- Balance -->
        <div class="mk-balance-block">
          <div class="mk-eyebrow">TOTAL AVAILABLE BALANCE</div>
          <div class="mk-balance">Rs. {{ formatAmount(totalBalance) }}</div>
          <div class="mk-date-row">
            <q-icon name="event" size="14px" />
            <span>{{ todayLabel }}</span>
          </div>
        </div>

        <!-- Financial Health Score -->
        <q-card flat class="mk-health-card">
          <q-card-section class="row no-wrap items-center q-gutter-md">
            <div class="mk-health-ring-wrap">
              <svg viewBox="0 0 80 80" class="mk-health-ring">
                <circle cx="40" cy="40" r="34" class="mk-ring-track" />
                <circle
                  cx="40" cy="40" r="34"
                  class="mk-ring-progress"
                  :style="healthRingStyle"
                />
              </svg>
              <div class="mk-health-ring-value">
                <template v-if="healthScore !== null">{{ Math.round(healthScore) }}</template>
                <template v-else>—</template>
              </div>
            </div>
            <div class="col">
              <div class="mk-health-title">Financial Health Score</div>
              <div class="mk-health-text">
                <template v-if="healthScore !== null">
                  {{ healthMessage }}
                </template>
                <template v-else>
                  Add a budget, a goal, and a bit of history to unlock your score.
                </template>
              </div>
              <div class="mk-health-toggle" @click="showHealthDetail = !showHealthDetail">
                {{ showHealthDetail ? 'Hide breakdown' : 'View breakdown' }}
                <q-icon :name="showHealthDetail ? 'expand_less' : 'expand_more'" size="16px" />
              </div>
            </div>
          </q-card-section>

          <q-slide-transition>
            <q-card-section v-if="showHealthDetail" class="mk-health-detail">
              <div
                v-for="(comp, key) in healthComponents"
                :key="key"
                class="mk-health-row"
              >
                <div class="mk-health-row-label">{{ healthLabels[key] || key }}</div>
                <div v-if="comp.score !== null" class="row items-center q-gutter-xs">
                  <q-linear-progress
                    :value="comp.score / 100"
                    size="6px"
                    rounded
                    track-color="grey-3"
                    :color="scoreColor(comp.score)"
                    class="mk-health-bar"
                  />
                  <span class="mk-health-row-score">{{ Math.round(comp.score) }}</span>
                </div>
                <div v-else class="mk-health-row-empty">{{ comp.reason || 'Not enough data' }}</div>
              </div>
            </q-card-section>
          </q-slide-transition>
        </q-card>

        <!-- Spending velocity -->
        <q-card flat class="mk-velocity-card">
          <q-card-section class="row no-wrap items-start q-gutter-md">
            <div class="mk-velocity-icon">
              <q-icon name="speed" size="22px" color="amber-9" />
            </div>
            <div class="col">
              <div class="mk-velocity-title">Spending Velocity</div>
              <div class="mk-velocity-text">
                You've spent {{ spendingPercent }}% of your {{ currentMonthLabel }} budget.
                <span class="mk-velocity-highlight">
                  {{ spendingPercent > 80 ? 'Slow down!' : 'Take it easy!' }}
                </span>
              </div>
              <q-linear-progress
                :value="spendingPercent / 100"
                size="8px"
                rounded
                track-color="grey-3"
                :color="spendingPercent > 80 ? 'negative' : 'amber-6'"
                class="q-mt-sm"
              />
            </div>
          </q-card-section>
        </q-card>

        <!-- My Accounts -->
        <div class="mk-section-header row items-center justify-between">
          <div class="mk-section-title">My Accounts</div>
          <div class="mk-view-all" @click="goToLinkedAccounts">VIEW ALL</div>
        </div>

        <div class="mk-accounts-scroll">
          <div
            v-for="account in accounts"
            :key="account.id"
            class="mk-account-card"
            :style="{ background: account.gradient || 'linear-gradient(135deg, #0f6b46, #0a4a30)' }"
          >
            <div class="row items-start justify-between">
              <div class="mk-account-name">{{ account.name }}</div>
              <q-icon name="account_balance" size="26px" class="mk-account-icon" />
            </div>
            <div class="mk-account-number">{{ account.masked || '•••• ' + (account.id || '0000') }}</div>
            <div class="mk-account-bottom">
              <div class="mk-account-label">BALANCE</div>
              <div class="mk-account-balance">Rs. {{ formatAmount(account.balance) }}</div>
            </div>
          </div>
        </div>

        <!-- Recent Transactions -->
        <div class="mk-section-header row items-center justify-between">
          <div class="mk-section-title">Recent Transactions</div>
          <q-btn flat round dense size="sm" icon="tune" color="grey-7" @click="goToReports" />
        </div>

        <div v-if="categoryChips.length > 1" class="mk-chip-row">
          <div
            v-for="chip in categoryChips"
            :key="chip"
            class="mk-chip"
            :class="{ 'mk-chip-active': activeCategory === chip }"
            @click="activeCategory = activeCategory === chip ? null : chip"
          >
            {{ chip }}
          </div>
        </div>

        <div class="mk-transactions">
          <div
            v-for="tx in filteredTransactions"
            :key="tx.id"
            class="mk-transaction-row"
          >
            <q-avatar size="40px" class="mk-tx-avatar" :style="{ background: tx.iconBg || '#e7f3ee' }">
              <q-icon :name="tx.icon || 'receipt'" size="18px" :color="tx.iconColor || 'primary'" />
            </q-avatar>
            <div class="col mk-tx-info">
              <div class="mk-tx-name">{{ tx.name }}</div>
              <div class="mk-tx-date">{{ tx.date }}</div>
            </div>
            <div class="text-right">
              <div class="mk-tx-amount" :class="tx.amount < 0 ? 'mk-negative' : 'mk-positive'">
                {{ tx.amount < 0 ? '-' : '+' }} Rs. {{ formatAmount(Math.abs(tx.amount)) }}
              </div>
              <div class="mk-tx-category">{{ tx.category }}</div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredTransactions.length === 0" class="mk-empty-state">
            <q-icon name="receipt_long" size="32px" color="grey-5" />
            <div class="q-mt-sm">
              {{ transactions.length === 0 ? 'No transactions recorded yet.' : 'No transactions in this category.' }}
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Floating Action Button -->
    <q-btn
      round
      unelevated
      icon="add"
      color="primary"
      class="mk-fab"
      @click.stop="navigateToOptionpage"
    />

    <!-- Bottom Navigation -->
    <div class="mk-bottom-nav">
      <div
        v-for="item in navItems"
        :key="item.name"
        class="mk-nav-item"
        :class="{ 'mk-nav-active': activeNav === item.name }"
        @click="setActive(item.name)"
      >
        <div class="mk-nav-icon-wrap">
          <q-icon :name="item.icon" size="20px" />
        </div>
        <div class="mk-nav-label">{{ item.label }}</div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import MeroKharchaLogo from '@/components/MeroKharchaLogo.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

const router = useRouter()
const route = useRoute()

const emit = defineEmits(['open-settings', 'view-all-accounts', 'add-transaction', 'nav-change'])

const isLoading = ref(true)
const activeNav = ref('home')

const todayLabel = ref('Today')
const currentMonthLabel = ref('This month')
const totalBalance = ref(0)
const spendingPercent = ref(0)

const accounts = ref([])
const transactions = ref([])
const activeCategory = ref(null)

// Financial Health Score
const healthScore = ref(null)
const healthComponents = ref({})
const showHealthDetail = ref(false)

const healthLabels = {
  savings_rate: 'Savings Rate',
  budget_adherence: 'Budget Adherence',
  goal_progress: 'Goal Progress',
  expense_consistency: 'Expense Consistency',
  income_stability: 'Income Stability'
}

// "Just scanned" receipt banner — shows a scan from the last hour that
// hasn't been dismissed, so the amount/date are visible even before the
// resulting expense is saved via AddExpensePage.
const scannedBanner = ref(null)
const SCAN_BANNER_MAX_AGE_MS = 60 * 60 * 1000 // 1 hour

function checkScannedReceipt() {
  const raw = localStorage.getItem('scannedReceiptData')
  if (!raw) {
    scannedBanner.value = null
    return
  }
  try {
    const data = JSON.parse(raw)
    const age = Date.now() - (data.scannedAt || 0)
    scannedBanner.value = age <= SCAN_BANNER_MAX_AGE_MS ? data : null
  } catch {
    scannedBanner.value = null
  }
}

function dismissScannedBanner() {
  localStorage.removeItem('scannedReceiptData')
  scannedBanner.value = null
}

function goFinishScannedExpense() {
  router.push('/addexpense').catch(() => {
    router.push({ name: 'addexpense' }).catch(() => {})
  })
}

// Route names/paths follow router/index.js. Reports isn't in the router file
// you shared earlier — register it there (e.g. path: '/reports', name: 'reports',
// component: FinancialReportsPage) or update this to match whatever you use.
const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'flag' },       // Or your specific icon
  { name: 'reports', label: 'Report', icon: 'bar_chart' }, // Added between Goals & Import
  { name: 'import', label: 'Import', icon: 'file_upload' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function mapTransaction(tx, fallbackIcon = 'receipt') {
  const amount = Number(tx.amount ?? 0)
  return {
    id: tx.id || Math.random(),
    name: tx.title || tx.name || tx.description || 'Transaction',
    date: tx.date || 'Today',
    category: tx.category || tx.received_from || 'General',
    amount,
    icon: tx.icon || (amount < 0 ? 'shopping_bag' : fallbackIcon),
    iconBg: tx.iconBg || (amount < 0 ? '#fee2e2' : '#e7f3ee'),
    iconColor: tx.iconColor || (amount < 0 ? 'negative' : 'primary')
  }
}

async function fetchDashboardData() {
  isLoading.value = true

  try {
    const [budgetRes, expensesRes, incomesRes, goalsRes, healthRes] = await Promise.all([
      api.get('/budget/watchdog').catch(() => ({ data: { spending_percent: 0, total_spent: 0, monthly_limit: 0 } })),
      api.get('/expenses/').catch(() => ({ data: [] })),
      api.get('/incomes/').catch(() => ({ data: [] })),
      api.get('/goals/').catch(() => ({ data: [] })),
      // Mounted as app.include_router(router_financial_health, prefix="/health")
      // in main.py, so the live path is /health/score.
      api.get('/health/score').catch(() => ({ data: null }))
    ])

    const expenses = Array.isArray(expensesRes.data) ? expensesRes.data : []
    const incomes = Array.isArray(incomesRes.data) ? incomesRes.data : []
    const goals = Array.isArray(goalsRes.data) ? goalsRes.data : []

    const totalExpenses = expenses.reduce((sum, item) => sum + Number(item.amount || 0), 0)
    const totalIncomes = incomes.reduce((sum, item) => sum + Number(item.amount || 0), 0)
    const totalGoalSavings = goals.reduce((sum, item) => sum + Number(item.current_amount || 0), 0)

    const budget = budgetRes.data || {}
    totalBalance.value = totalIncomes - totalExpenses + totalGoalSavings
    spendingPercent.value = Number(budget.spending_percent ?? 0)
    todayLabel.value = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    currentMonthLabel.value = new Date().toLocaleDateString('en-US', { month: 'long' })

    const health = healthRes?.data
    if (health && health.total_score !== undefined) {
      healthScore.value = health.total_score
      healthComponents.value = health.components || {}
    } else {
      healthScore.value = null
      healthComponents.value = {}
    }

    accounts.value = [
      {
        id: 1,
        name: 'Cash & Wallet',
        balance: totalBalance.value,
        masked: '•••• 0001',
        gradient: 'linear-gradient(135deg, #0f6b46, #0a4a30)'
      }
    ]

    const rawTransactions = [...expenses, ...incomes]
      .sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
      .slice(0, 8)
      .map((tx) => mapTransaction(tx, tx.title ? 'account_balance_wallet' : 'receipt'))

    transactions.value = rawTransactions
  } catch (error) {
    console.warn('Backend API connection failed, showing default state:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
  checkScannedReceipt()

  // Keep the bottom nav's active pill in sync with the current route,
  // so landing directly on /reports (or refreshing there) highlights it.
  syncActiveNavFromRoute()
})

// Auto-refresh when returning from other pages (e.g. after saving a scanned
// expense on AddExpensePage) — also re-checks the scanned-receipt banner.
watch(() => route.path, (newPath) => {
  if (newPath === '/dashboard') {
    fetchDashboardData()
    checkScannedReceipt()
  }
  syncActiveNavFromRoute()
})

function syncActiveNavFromRoute() {
  const path = route.path
  if (path.startsWith('/dashboard')) activeNav.value = 'home'
  else if (path.startsWith('/goals')) activeNav.value = 'goals'
  else if (path.startsWith('/import')) activeNav.value = 'import'
  else if (path.startsWith('/profile')) activeNav.value = 'profile'
  else if (path.startsWith('/reports')) activeNav.value = 'reports'
}

const categoryChips = computed(() => {
  const set = new Set(transactions.value.map((tx) => tx.category).filter(Boolean))
  return Array.from(set)
})

const filteredTransactions = computed(() => {
  if (!activeCategory.value) return transactions.value
  return transactions.value.filter((tx) => tx.category === activeCategory.value)
})

function scoreColor(score) {
  if (score >= 70) return 'positive'
  if (score >= 40) return 'amber-6'
  return 'negative'
}

const healthMessage = computed(() => {
  const s = healthScore.value
  if (s === null) return ''
  if (s >= 70) return "You're in great shape — keep it up."
  if (s >= 40) return 'Decent, but there\'s room to tighten things up.'
  return 'Your finances need some attention right now.'
})

const healthRingStyle = computed(() => {
  const circumference = 2 * Math.PI * 34
  const s = healthScore.value ?? 0
  const offset = circumference - (s / 100) * circumference
  const color = healthScore.value === null
    ? '#d1d5db'
    : healthScore.value >= 70
      ? '#0f6b46'
      : healthScore.value >= 40
        ? '#e29b2e'
        : '#dc2626'
  return {
    strokeDasharray: `${circumference}`,
    strokeDashoffset: `${offset}`,
    stroke: color
  }
})

function navigateToOptionpage() {
  if (router) {
    router.push('/Optionpage').catch(() => {
      router.push({ name: 'Optionpage' }).catch(() => {})
    })
  }
}

function goToLinkedAccounts() {
  if (router) {
    router.push('/linked-accounts').catch(() => {
      emit('view-all-accounts')
    })
  } else {
    emit('view-all-accounts')
  }
}

function goToReports() {
  if (router) {
    router.push('/reports').catch(() => {
      router.push({ name: 'reports' }).catch(() => {})
    })
  }
}

function setActive(name) {
  activeNav.value = name

  if (!router) return
  if (name === 'home') router.push('/dashboard')
  else if (name === 'goals') router.push('/goals')
  else if (name === 'import' || name === 'imports') router.push('/imports')
  else if (name === 'profile') router.push('/profile')
  else if (name === 'reports') router.push('/reports')
}

function formatAmount(value) {
  const num = Number(value)
  if (isNaN(num)) return '0'
  return num.toLocaleString('en-IN')
}
</script>

<style scoped>
.mk-page {
  --mk-green: #0f6b46;
  --mk-green-dark: #0b5637;
  --mk-text: #1c1c1c;
  --mk-muted: #6b7280;
  background: #eef1f0;
  min-height: 100vh;
  padding-bottom: 90px;
}

.mk-shell {
  padding: 18px 16px 8px;
  max-width: 400px;
  margin: 0 auto;
}

.mk-header {
  margin-bottom: 18px;
}

.mk-brand-row {
  gap: 10px;
}

.mk-scan-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #0f6b46, #0a4a30);
  border-radius: 14px;
  padding: 12px 14px;
  margin-bottom: 16px;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(15, 107, 70, 0.25);
}

.mk-scan-banner-icon {
  flex-shrink: 0;
}

.mk-scan-banner-title {
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.mk-scan-banner-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  margin-top: 2px;
}

.mk-fade-enter-active,
.mk-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.mk-fade-enter-from,
.mk-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.mk-balance-block {
  margin-bottom: 18px;
}

.mk-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--mk-muted);
}

.mk-balance {
  font-size: 32px;
  font-weight: 800;
  color: var(--mk-green);
  margin-top: 4px;
}

.mk-date-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--mk-muted);
  margin-top: 6px;
}

.mk-health-card {
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(20, 30, 25, 0.05);
  margin-bottom: 16px;
}

.mk-health-ring-wrap {
  position: relative;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}

.mk-health-ring {
  width: 64px;
  height: 64px;
  transform: rotate(-90deg);
}

.mk-ring-track {
  fill: none;
  stroke: #eef0f4;
  stroke-width: 7;
}

.mk-ring-progress {
  fill: none;
  stroke-width: 7;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease, stroke 0.3s ease;
}

.mk-health-ring-value {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 800;
  color: var(--mk-text);
}

.mk-health-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--mk-text);
}

.mk-health-text {
  font-size: 12.5px;
  color: #4b5563;
  margin-top: 2px;
  line-height: 1.4;
}

.mk-health-toggle {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--mk-green);
  margin-top: 6px;
  cursor: pointer;
  width: fit-content;
}

.mk-health-detail {
  padding-top: 0;
  border-top: 1px solid #f0f1f4;
}

.mk-health-row {
  padding: 8px 0;
  border-bottom: 1px solid #f5f6f8;
}

.mk-health-row:last-child {
  border-bottom: none;
}

.mk-health-row-label {
  font-size: 12px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 4px;
}

.mk-health-bar {
  flex: 1;
}

.mk-health-row-score {
  font-size: 11px;
  font-weight: 700;
  color: var(--mk-text);
  width: 24px;
  text-align: right;
}

.mk-health-row-empty {
  font-size: 11px;
  color: #9ca3af;
  font-style: italic;
}

.mk-velocity-card {
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(20, 30, 25, 0.05);
  margin-bottom: 22px;
}

.mk-velocity-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #fdf1d8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mk-velocity-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--mk-text);
}

.mk-velocity-text {
  font-size: 13px;
  color: #4b5563;
  margin-top: 2px;
  line-height: 1.5;
}

.mk-velocity-highlight {
  color: var(--mk-green);
  font-weight: 700;
}

.mk-section-header {
  margin: 4px 0 12px;
}

.mk-section-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-view-all {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--mk-green);
  cursor: pointer;
}

.mk-accounts-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 6px;
  margin: 0 -16px 24px;
  padding-left: 16px;
  padding-right: 16px;
  scroll-snap-type: x mandatory;
}

.mk-account-card {
  min-width: 240px;
  border-radius: 16px;
  padding: 16px;
  color: #fff;
  flex-shrink: 0;
  scroll-snap-align: start;
  box-shadow: 0 10px 20px rgba(15, 107, 70, 0.18);
}

.mk-account-name {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.95;
}

.mk-account-icon {
  opacity: 0.85;
}

.mk-account-number {
  font-size: 15px;
  letter-spacing: 0.05em;
  margin-top: 20px;
  font-weight: 500;
  opacity: 0.9;
}

.mk-account-bottom {
  margin-top: 18px;
}

.mk-account-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  opacity: 0.75;
}

.mk-account-balance {
  font-size: 19px;
  font-weight: 700;
  margin-top: 2px;
}

.mk-chip-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  margin-bottom: 12px;
}

.mk-chip {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 600;
  color: #4b5563;
  background: #ffffff;
  border: 1px solid #e7e9f0;
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
  white-space: nowrap;
}

.mk-chip-active {
  background: var(--mk-green);
  border-color: var(--mk-green);
  color: #fff;
}

.mk-transactions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mk-transaction-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-tx-info {
  min-width: 0;
}

.mk-tx-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--mk-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mk-tx-date {
  font-size: 12px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-tx-amount {
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.mk-negative {
  color: #dc2626;
}

.mk-positive {
  color: var(--mk-green);
}

.mk-tx-category {
  font-size: 11px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-empty-state {
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
  padding: 32px 12px;
  background: #ffffff;
  border-radius: 14px;
}

.mk-fab {
  position: fixed;
  right: 20px;
  bottom: 84px;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  box-shadow: 0 10px 20px rgba(15, 107, 70, 0.35);
  z-index: 99;
  cursor: pointer;
}

.mk-bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
  border-top: 1px solid #eef1f0;
  display: flex;
  justify-content: space-around;
  padding: 8px 4px calc(8px + env(safe-area-inset-bottom));
  z-index: 15;
}

.mk-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  border-radius: 12px;
  color: #9ca3af;
  cursor: pointer;
}

.mk-nav-icon-wrap {
  display: flex;
}

.mk-nav-label {
  font-size: 10px;
  font-weight: 600;
}

.mk-nav-active {
  color: var(--mk-green-dark);
  background: #fdf1d8;
}

.mk-nav-active .mk-nav-icon-wrap {
  color: #d99a1b;
}
</style>