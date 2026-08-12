<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row">
          <!-- <q-avatar size="36px" class="mk-avatar">
            <q-icon name="person" size="20px" color="white" />
          </q-avatar> -->
          <MeroKharchaLogo :size="10" />
        </div>
        <!-- <q-btn flat round dense icon="settings" color="grey-8" @click="$emit('open-settings')" /> -->
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center q-my-xl">
        <q-spinner-dots color="primary" size="42px" />
        <div class="text-caption text-grey-7 q-mt-sm">Loading profile...</div>
      </div>

      <!-- Profile summary -->
      <div v-else class="mk-profile-summary">
        <div class="mk-profile-avatar-wrap">
          <q-avatar size="88px" class="mk-profile-avatar">
            <q-icon name="person" size="46px" color="white" />
          </q-avatar>
          <div v-if="user.isPro" class="mk-pro-badge">
            <q-icon name="star" size="12px" class="q-mr-xs" />
            PRO
          </div>
        </div>

        <!-- Dynamic User Display / Edit Name Mode -->
        <div class="q-mt-md">
          <div v-if="!isEditingName" class="row items-center justify-center">
            <div class="mk-profile-name">{{ user.name }}</div>
            <q-btn flat round dense icon="edit" size="sm" color="grey-7" class="q-ml-xs" @click="startEditingName" />
          </div>

          <!-- Edit Name Input -->
          <div v-else class="row items-center justify-center q-gutter-x-xs q-mt-sm">
            <q-input
              v-model="editedName"
              dense
              outlined
              autofocus
              maxlength="50"
              style="max-width: 200px"
              placeholder="Enter name"
              @keyup.enter="saveName"
            />
            <q-btn round dense icon="check" color="primary" size="sm" :loading="isSaving" @click="saveName" />
            <q-btn round dense icon="close" color="grey" flat size="sm" :disable="isSaving" @click="cancelEditingName" />
          </div>
        </div>

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
            <div class="mk-pref-title">Account Settings</div>
            <!-- <div class="mk-pref-sub">2FA, Biometrics, Password</div> -->
          </div>
          <q-icon name="chevron_right" size="20px" color="grey-5" />
        </div>

        <div class="mk-pref-row" @click="$emit('open-notifications')">
          <q-avatar size="38px" class="mk-pref-icon" style="background:#fdf1d8">
            <q-icon name="notifications" size="18px" color="amber-8" />
          </q-avatar>
          <div class="col mk-pref-info">
            <div class="mk-pref-title">Notifications</div>
            <!-- <div class="mk-pref-sub">Alerts, Reports, Budgets</div> -->
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

        <!-- <div class="row items-center justify-between mk-settings-row">
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
        </div> -->
      </div>

      <!-- Logout Button -->
      <div class="q-mb-md">
        <q-btn
          outline
          color="negative"
          class="full-width mk-logout-btn"
          icon="logout"
          label="Log Out"
          no-caps
          @click.stop="goTologin"
        />
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
import MeroKharchaLogo from '@/components/MeroKharchaLogo.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const $q = useQuasar()
const router = useRouter()

const emit = defineEmits([
  'open-settings',
  'open-security',
  'open-notifications',
  'theme-change',
  'language-change',
  'nav-change'
])

const activeNav = ref('profile')
const theme = ref('light')
const language = ref('en')

const isLoading = ref(true)
const isEditingName = ref(false)
const isSaving = ref(false)
const editedName = ref('')

const user = ref({
  name: 'Guest User',
  tier: 'Free Tier',
  since: '2080 B.S.',
  isPro: false
})

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'imports', label: 'Imports', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function goTologin() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_name')

  // Safely attempt Vue Router navigation, fallback to direct browser load
  if (router) {
    router.push('/login').catch(() => {
      window.location.href = '/login'
    })
  } else {
    window.location.href = '/login'
  }
}

async function fetchUserProfile() {
  isLoading.value = true
  try {
    const localName = localStorage.getItem('user_name')
    const token = localStorage.getItem('auth_token')

    const response = await axios.get(`${API_BASE_URL}/profile`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })

    if (response.data) {
      user.value = {
        name: localName || response.data.name || 'User',
        tier: response.data.tier || 'Free Tier',
        since: response.data.since || '2080 B.S.',
        isPro: response.data.isPro ?? true
      }
    }
  } catch (error) {
    console.warn('Backend connection failed, falling back to local storage:', error)
    const storedName = localStorage.getItem('user_name')
    if (storedName) {
      user.value.name = storedName
    }
  } finally {
    isLoading.value = false
  }
}

async function saveName() {
  if (!editedName.value.trim()) return

  isSaving.value = true
  try {
    const token = localStorage.getItem('auth_token')
    
    await axios.patch(
      `${API_BASE_URL}/profile`,
      { name: editedName.value.trim() },
      { headers: token ? { Authorization: `Bearer ${token}` } : {} }
    )

    user.value.name = editedName.value.trim()
    localStorage.setItem('user_name', user.value.name)

    isEditingName.value = false
    if ($q && $q.notify) {
      $q.notify({ type: 'positive', message: 'Name updated successfully!' })
    }
  } catch (error) {
    console.error('Failed to update user name:', error)
    user.value.name = editedName.value.trim()
    localStorage.setItem('user_name', user.value.name)
    isEditingName.value = false
  } finally {
    isSaving.value = false
  }
}

function startEditingName() {
  editedName.value = user.value.name
  isEditingName.value = true
}

function cancelEditingName() {
  isEditingName.value = false
}

onMounted(() => {
  fetchUserProfile()
})

function setActive(name) {
  activeNav.value = name
  emit('nav-change', name)

  if (router) {
    if (name === 'home') router.push('/dashboard')
    else if (name === 'goals') router.push('/goals')
    else if (name === 'imports') router.push('/imports')
    else if (name === 'profile') router.push('/profile')
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
}

.mk-profile-meta {
  font-size: 13px;
  color: var(--mk-muted);
  margin-top: 4px;
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
  margin-bottom: 16px;
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

.mk-logout-btn {
  border-radius: 12px;
  font-weight: 700;
  background: #ffffff;
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