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

      <!-- Profile summary -->
      <div class="mk-profile-summary">
        <div class="mk-profile-avatar-wrap">
          <q-avatar size="88px" class="mk-profile-avatar">
            <q-icon name="person" size="46px" color="white" />
          </q-avatar>
          <div v-if="user.isPro" class="mk-pro-badge">
            <q-icon name="star" size="12px" class="q-mr-xs" />
            PRO
          </div>
        </div>
        <div class="mk-profile-name">{{ user.name }}</div>
        <div class="mk-profile-meta">{{ user.tier }} &bull; User since {{ user.since }}</div>
      </div>

      <!-- Preferences -->
      <div class="mk-section-title">PREFERENCES</div>

      <div class="mk-pref-list">
        <div class="mk-pref-row" @click="$emit('open-security')">
          <q-avatar size="38px" class="mk-pref-icon" style="background:#e7f3ee">
            <q-icon name="shield" size="18px" color="primary" />
          </q-avatar>
          <div class="col mk-pref-info">
            <div class="mk-pref-title">Account Security</div>
            <div class="mk-pref-sub">2FA, Biometrics, Password</div>
          </div>
          <q-icon name="chevron_right" size="20px" color="grey-5" />
        </div>

        <div class="mk-pref-row" @click="$emit('open-notifications')">
          <q-avatar size="38px" class="mk-pref-icon" style="background:#fdf1d8">
            <q-icon name="notifications" size="18px" color="amber-8" />
          </q-avatar>
          <div class="col mk-pref-info">
            <div class="mk-pref-title">Notification Preferences</div>
            <div class="mk-pref-sub">Alerts, Reports, Budgets</div>
          </div>
          <q-icon name="chevron_right" size="20px" color="grey-5" />
        </div>
      </div>

      <!-- Theme & Language -->
      <div class="mk-settings-card">
        <div class="row items-center justify-between mk-settings-row">
          <div class="row items-center mk-settings-label">
            <q-icon name="dark_mode" size="18px" color="grey-7" class="q-mr-sm" />
            Theme
          </div>
          <q-btn-toggle
            v-model="theme"
            dense
            no-caps
            unelevated
            toggle-color="primary"
            color="white"
            text-color="grey-7"
            class="mk-toggle"
            :options="[
              { label: 'Light', value: 'light' },
              { label: 'Dark', value: 'dark' }
            ]"
            @update:model-value="val => $emit('theme-change', val)"
          />
        </div>

        <q-separator class="q-my-sm" />

        <div class="row items-center justify-between mk-settings-row">
          <div class="row items-center mk-settings-label">
            <q-icon name="language" size="18px" color="grey-7" class="q-mr-sm" />
            Language
          </div>
          <q-btn-toggle
            v-model="language"
            dense
            no-caps
            unelevated
            toggle-color="primary"
            color="white"
            text-color="grey-7"
            class="mk-toggle"
            :options="[
              { label: 'English', value: 'en' },
              { label: 'नेपाली', value: 'ne' }
            ]"
            @update:model-value="val => $emit('language-change', val)"
          />
        </div>
      </div>

      <!-- App brand footer -->
      <div class="mk-brand-footer">
        <div class="mk-brand-icon">
          <q-icon name="terminal" size="24px" color="white" />
        </div>
        <div class="mk-brand-footer-name">Bug Creator</div>
        <div class="mk-brand-footer-tag">Empowering local financial growth</div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits([
  'open-settings',
  'open-security',
  'open-notifications',
  'theme-change',
  'language-change',
  'nav-change'
])

const router = useRouter()

const activeNav = ref('profile')
const theme = ref('light')
const language = ref('en')

const user = ref({
  name: 'Aryan Sharma',
  tier: 'Free Tier',
  since: '2080 B.S.',
  isPro: true
})

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'imports', label: 'Imports', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function setActive (name) {
  activeNav.value = name
  emit('nav-change', name)

  if (name === 'home') {
    router.push('/dashboard')
  } else if (name === 'goals') {
    router.push('/goals')
  } else if (name === 'imports') {
    router.push('/imports')
  } else if (name === 'profile') {
    router.push('/profile')
  }
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
  margin-bottom: 10px;
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

.mk-profile-summary {
  text-align: center;
  margin: 14px 0 22px;
}

.mk-profile-avatar-wrap {
  position: relative;
  display: inline-block;
}

.mk-profile-avatar {
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  border: 3px solid #f5c451;
}

.mk-pro-badge {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  background: #f5a524;
  color: #1c1c1c;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.03em;
  padding: 3px 10px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 10px rgba(245, 165, 36, 0.4);
}

.mk-profile-name {
  font-size: 19px;
  font-weight: 800;
  color: var(--mk-text);
  margin-top: 14px;
}

.mk-profile-meta {
  font-size: 13px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-section-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--mk-green);
  margin-bottom: 10px;
}

.mk-pref-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.mk-pref-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
  cursor: pointer;
}

.mk-pref-info {
  min-width: 0;
}

.mk-pref-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-pref-sub {
  font-size: 12px;
  color: var(--mk-green);
  margin-top: 2px;
}

.mk-settings-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
  margin-bottom: 22px;
}

.mk-settings-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--mk-text);
}

.mk-toggle {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.mk-brand-footer {
  text-align: center;
  padding: 22px 0;
}

.mk-brand-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
}

.mk-brand-footer-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--mk-green);
}

.mk-brand-footer-tag {
  font-size: 12px;
  color: var(--mk-muted);
  margin-top: 2px;
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