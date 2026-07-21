<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row">
          <q-avatar size="36px" class="mk-avatar">
            <q-icon name="person" size="20px" color="white" />
          </q-avatar>
          <div class="mk-brand-name">Mero Kharcha</div>
        </div>
        <q-btn flat round dense icon="settings" color="grey-8" @click="$emit('open-settings')" />
      </div>

      <!-- Balance -->
      <div class="mk-balance-block">
        <div class="mk-eyebrow">TOTAL AVAILABLE BALANCE</div>
        <div class="mk-balance">Rs. {{ formatAmount(totalBalance) }}</div>
        <div class="mk-date-row">
          <q-icon name="event" size="14px" />
          <span>{{ todayLabel }}</span>
        </div>
      </div>

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
              <span class="mk-velocity-highlight">Take it easy!</span>
            </div>
            <q-linear-progress
              :value="spendingPercent / 100"
              size="8px"
              rounded
              track-color="grey-3"
              color="amber-6"
              class="q-mt-sm"
            />
          </div>
        </q-card-section>
      </q-card>

      <!-- My Accounts -->
      <div class="mk-section-header row items-center justify-between">
        <div class="mk-section-title">My Accounts</div>
        <div class="mk-view-all" @click="$emit('view-all-accounts')">VIEW ALL</div>
      </div>

      <div class="mk-accounts-scroll">
        <div
          v-for="account in accounts"
          :key="account.id"
          class="mk-account-card"
          :style="{ background: account.gradient }"
        >
          <div class="row items-start justify-between">
            <div class="mk-account-name">{{ account.name }}</div>
            <q-icon name="account_balance" size="26px" class="mk-account-icon" />
          </div>
          <div class="mk-account-number">{{ account.masked }}</div>
          <div class="mk-account-bottom">
            <div class="mk-account-label">BALANCE</div>
            <div class="mk-account-balance">Rs. {{ formatAmount(account.balance) }}</div>
          </div>
        </div>
      </div>

      <!-- Recent Transactions -->
      <div class="mk-section-header row items-center justify-between">
        <div class="mk-section-title">Recent Transactions</div>
        <q-btn flat round dense size="sm" icon="tune" color="grey-7" />
      </div>

      <div class="mk-transactions">
        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="mk-transaction-row"
        >
          <q-avatar size="40px" class="mk-tx-avatar" :style="{ background: tx.iconBg }">
            <q-icon :name="tx.icon" size="18px" :color="tx.iconColor" />
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
      </div>
    </div>

    <!-- Floating action button -->
    <q-btn
      round
      unelevated
      icon="add"
      color="primary"
      class="mk-fab"
      @click="$emit('add-transaction')"
    />

    <!-- Bottom navigation -->
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

<!-- <script setup>
import { ref } from 'vue'

defineEmits(['open-settings', 'view-all-accounts', 'add-transaction', 'nav-change'])

const activeNav = ref('home')
const todayLabel = '15 Shrawan 2083'
const currentMonthLabel = 'Bhadra'
const totalBalance = 145000
const spendingPercent = 40

const accounts = ref([
  {
    id: 1,
    name: 'Nabil Bank Ltd.',
    masked: '**** 4421',
    balance: 82450,
    gradient: 'linear-gradient(135deg, #0f6b46, #0a4a30)'
  },
  {
    id: 2,
    name: 'eSewa',
    masked: '9841******',
    balance: 12000,
    gradient: 'linear-gradient(135deg, #6cc06a, #4a9e4e)'
  },
  {
    id: 3,
    name: 'Nepal Investment Bank',
    masked: '**** 7790',
    balance: 50000,
    gradient: 'linear-gradient(135deg, #2f6f8f, #1f4e66)'
  }
])

const transactions = ref([
  {
    id: 1,
    name: 'Bhat-Bhateni Supermarket',
    date: '14 Shrawan 2083',
    amount: -4250,
    category: 'Food & Groceries',
    icon: 'shopping_bag',
    iconBg: '#e7f3ee',
    iconColor: 'primary'
  },
  {
    id: 2,
    name: 'The Bakery Cafe',
    date: '13 Shrawan 2083',
    amount: -1200,
    category: 'Dining',
    icon: 'restaurant',
    iconBg: '#fdeee0',
    iconColor: 'orange-8'
  },
  {
    id: 3,
    name: 'Salary Deposit',
    date: '10 Shrawan 2083',
    amount: 65000,
    category: 'Income',
    icon: 'account_balance_wallet',
    iconBg: '#e7f3ee',
    iconColor: 'primary'
  }
])

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function setActive (name) {
  activeNav.value = name
}

function formatAmount (value) {
  return Number(value).toLocaleString('en-IN')
}
</script> -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router' // 👈 1. Import Vue Router

defineEmits(['open-settings', 'view-all-accounts', 'add-transaction', 'nav-change'])

const router = useRouter() // 👈 2. Initialize the router instance

const activeNav = ref('home')
const todayLabel = '15 Shrawan 2083'
const currentMonthLabel = 'Bhadra'
const totalBalance = 145000
const spendingPercent = 40

const accounts = ref([
  {
    id: 1,
    name: 'Nabil Bank Ltd.',
    masked: '**** 4421',
    balance: 82450,
    gradient: 'linear-gradient(135deg, #0f6b46, #0a4a30)'
  },
  {
    id: 2,
    name: 'eSewa',
    masked: '9841******',
    balance: 12000,
    gradient: 'linear-gradient(135deg, #6cc06a, #4a9e4e)'
  },
  {
    id: 3,
    name: 'Nepal Investment Bank',
    masked: '**** 7790',
    balance: 50000,
    gradient: 'linear-gradient(135deg, #2f6f8f, #1f4e66)'
  }
])

const transactions = ref([
  {
    id: 1,
    name: 'Bhat-Bhateni Supermarket',
    date: '14 Shrawan 2083',
    amount: -4250,
    category: 'Food & Groceries',
    icon: 'shopping_bag',
    iconBg: '#e7f3ee',
    iconColor: 'primary'
  },
  {
    id: 2,
    name: 'The Bakery Cafe',
    date: '13 Shrawan 2083',
    amount: -1200,
    category: 'Dining',
    icon: 'restaurant',
    iconBg: '#fdeee0',
    iconColor: 'orange-8'
  },
  {
    id: 3,
    name: 'Salary Deposit',
    date: '10 Shrawan 2083',
    amount: 65000,
    category: 'Income',
    icon: 'account_balance_wallet',
    iconBg: '#e7f3ee',
    iconColor: 'primary'
  }
])

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'imports', label: 'Imports', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

// 👈 3. Update the navigation handler
function setActive (name) {
  activeNav.value = name
  
  if (name === 'home') {
    router.push('/dashboard')
  } else if (name === 'goals') {
    router.push('/goals')
  } else if (name === 'imports') { // 👈 Changed 'imports' to 'import' to match your navItems list
    router.push('/imports')
  } else if (name === 'profile') {
    router.push('/profile')
  }
}

function formatAmount (value) {
  return Number(value).toLocaleString('en-IN')
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

.mk-avatar {
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
}

.mk-brand-name {
  font-weight: 700;
  font-size: 16px;
  color: var(--mk-green);
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

.mk-fab {
  position: fixed;
  right: 20px;
  bottom: 84px;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  box-shadow: 0 10px 20px rgba(15, 107, 70, 0.35);
  z-index: 20;
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
  padding: 8px 8px calc(8px + env(safe-area-inset-bottom));
  z-index: 15;
}

.mk-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 14px;
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