<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <q-btn round flat dense icon="arrow_back" color="primary" class="mk-icon-btn" @click="goBack" />
        <div class="mk-page-title">Linked Accounts</div>
        <q-btn round flat dense icon="help_outline" color="primary" class="mk-icon-btn" @click="$emit('open-help')" />
      </div>

      <!-- Security banner -->
      <div class="mk-security-banner row no-wrap items-start q-gutter-md">
        <div class="mk-security-icon">
          <q-icon name="verified_user" size="20px" color="white" />
        </div>
        <div class="col">
          <div class="mk-security-title">Securely Managed</div>
          <div class="mk-security-text">
            Your banking data is protected by bank-grade 256-bit AES encryption.
            Mero Kharcha never stores your login credentials.
          </div>
        </div>
      </div>

      <!-- Connected accounts -->
      <div class="mk-section-header row items-center justify-between">
        <div class="mk-section-label">CONNECTED ACCOUNTS</div>
        <div class="mk-active-count">{{ activeCount }} Active</div>
      </div>

      <div class="mk-account-list">
        <div v-for="account in accounts" :key="account.id" class="mk-account-row">
          <q-avatar size="42px" class="mk-account-avatar">
            <q-icon :name="account.icon" size="20px" color="grey-7" />
          </q-avatar>
          <div class="col mk-account-info">
            <div class="mk-account-name">{{ account.name }}</div>
            <div class="mk-account-sub">{{ account.subtitle }}</div>
            <div class="mk-status-row">
              <span class="mk-status-dot" :class="account.status === 'synced' ? 'mk-dot-synced' : 'mk-dot-pending'" />
              <span
                class="mk-status-text"
                :class="account.status === 'synced' ? 'mk-status-synced' : 'mk-status-pending'"
              >
                {{ account.status === 'synced' ? 'SYNCED' : 'PENDING SYNC' }}
              </span>
            </div>
          </div>
          <q-btn
            round
            flat
            dense
            icon="link_off"
            color="grey-6"
            @click="$emit('unlink-account', account.id)"
          />
        </div>
      </div>

      <!-- Add new account -->
      <q-btn
        unelevated
        no-caps
        class="mk-cta"
        icon="add"
        label="Add New Account"
        @click="$emit('add-account')"
      />

      <!-- Legal text -->
      <div class="mk-legal-text">
        By linking your accounts, you agree to our
        <span class="mk-link" @click="$emit('open-terms')">Terms of Service</span>
        for data aggregation. All data is handled in accordance with our Privacy Policy.
      </div>

      <div class="mk-footer">
        <div class="mk-footer-brand">by Bug Creator &bull; 2083 B.S.</div>
      </div>
    </div>

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

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['open-help', 'unlink-account', 'add-account', 'open-terms', 'nav-change'])

const router = useRouter()

// Matches the bottom-nav highlighting shown in the screenshot (Profile tab
// stays highlighted here, since this screen is reached from the account
// section of the app). Adjust if you'd rather it track a different tab.
const activeNav = ref('profile')

const accounts = ref([
  {
    id: 1,
    name: 'Nabil Bank',
    subtitle: 'Account ending in 4421',
    status: 'synced',
    icon: 'account_balance'
  },
  {
    id: 2,
    name: 'eSewa Wallet',
    subtitle: '984\u2022\u2022\u2022412',
    status: 'synced',
    icon: 'account_balance_wallet'
  },
  {
    id: 3,
    name: 'NIC Asia Bank',
    subtitle: 'Account ending in 8829',
    status: 'pending',
    icon: 'account_balance'
  }
])

const activeCount = computed(() => accounts.value.filter(a => a.status === 'synced').length)

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function setActive (name) {
  activeNav.value = name
  emit('nav-change', name)
}

function goBack () {
  router.back()
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
  margin-bottom: 16px;
}

.mk-icon-btn {
  border: 1px solid #d7dedb;
}

.mk-page-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mk-green);
}

.mk-security-banner {
  background: #e2f3ea;
  border-radius: 16px;
  padding: 14px;
  margin-bottom: 20px;
}

.mk-security-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--mk-green);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mk-security-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--mk-green-dark);
}

.mk-security-text {
  font-size: 12px;
  color: #35543f;
  line-height: 1.5;
  margin-top: 2px;
}

.mk-section-header {
  margin-bottom: 10px;
}

.mk-section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
}

.mk-active-count {
  font-size: 12px;
  font-weight: 600;
  color: var(--mk-muted);
}

.mk-account-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.mk-account-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-account-avatar {
  background: #eef1f0;
}

.mk-account-info {
  min-width: 0;
}

.mk-account-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-account-sub {
  font-size: 12px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-status-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.mk-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.mk-dot-synced {
  background: #16a34a;
}

.mk-dot-pending {
  background: #d97706;
}

.mk-status-text {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.mk-status-synced {
  color: #16a34a;
}

.mk-status-pending {
  color: #d97706;
}

.mk-cta {
  width: 100%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  border-radius: 12px;
  font-weight: 700;
  padding: 12px 0;
  font-size: 14px;
  margin-bottom: 16px;
}

.mk-legal-text {
  font-size: 11px;
  color: #9ca3af;
  text-align: center;
  line-height: 1.6;
  padding: 0 8px;
}

.mk-link {
  color: var(--mk-green);
  text-decoration: underline;
  cursor: pointer;
}

.mk-footer {
  text-align: center;
  margin-top: 14px;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #9ca3af;
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

.mk-nav-label {
  font-size: 10px;
  font-weight: 600;
}

.mk-nav-active {
  color: var(--mk-green-dark);
  background: #fdf1d8;
}
</style>