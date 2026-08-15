<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row">
          <MeroKharchaLogo :size="10" />
        </div>
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

      <!-- Profile Details Card -->
      <q-card flat class="mk-details-card q-mt-md">
        <q-card-section>
          <div class="text-subtitle2 text-weight-bold q-mb-md">Profile Information</div>
          
          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Email</div>
            <div class="mk-field-value">{{ user.email || '-' }}</div>
          </div>

          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Phone</div>
            <div class="mk-field-value">{{ user.phone || '-' }}</div>
          </div>

          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Age</div>
            <div class="mk-field-value">{{ user.age || '-' }}</div>
          </div>

          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Gender</div>
            <div class="mk-field-value">{{ user.gender || '-' }}</div>
          </div>

          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Nationality</div>
            <div class="mk-field-value">{{ user.nationality || '-' }}</div>
          </div>

          <div class="mk-profile-field q-mb-md">
            <div class="mk-field-label">Currency</div>
            <div class="mk-field-value">{{ user.currency || 'NPR' }}</div>
          </div>

          <q-btn
            flat
            unelevated
            color="primary"
            label="Edit Profile"
            class="full-width q-mt-md"
            icon="edit"
            @click="showEditDialog = true"
          />
        </q-card-section>
      </q-card>

      <!-- Edit Profile Dialog -->
      <q-dialog v-model="showEditDialog" position="bottom">
        <q-card class="edit-profile-card">
          <q-card-section class="row items-center justify-between q-pb-none">
            <div class="text-subtitle2 text-weight-bold">Edit Profile</div>
            <q-btn icon="close" flat round dense @click="showEditDialog = false" />
          </q-card-section>

          <q-card-section class="q-pt-md">
            <q-input
              v-model="editForm.full_name"
              label="Full Name"
              outlined
              dense
              class="q-mb-md"
            />
            <q-input
              v-model="editForm.phone"
              label="Phone"
              outlined
              dense
              class="q-mb-md"
            />
            <q-input
              v-model.number="editForm.age"
              label="Age"
              type="number"
              outlined
              dense
              class="q-mb-md"
            />
            <q-select
              v-model="editForm.gender"
              :options="['Male', 'Female', 'Other']"
              label="Gender"
              outlined
              dense
              emit-value
              map-options
              class="q-mb-md"
            />
            <q-input
              v-model="editForm.nationality"
              label="Nationality"
              outlined
              dense
              class="q-mb-md"
            />
            <q-input
              v-model="editForm.currency"
              label="Currency"
              outlined
              dense
              class="q-mb-md"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="grey" @click="showEditDialog = false" />
            <q-btn 
              unelevated 
              label="Save" 
              color="primary" 
              :loading="isSavingProfile"
              @click="saveProfile" 
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Preferences -->
      <!-- <div class="mk-section-title">PREFERENCES</div>

      <div class="mk-pref-list">
        <div class="mk-pref-row" @click="$router.push('/settings')">
          <q-avatar size="38px" class="mk-pref-icon" style="background:#e7f3ee">
            <q-icon name="shield" size="18px" color="primary" />
          </q-avatar>
          <div class="col mk-pref-info">
            <div class="mk-pref-title">Account Settings</div>
          </div>
          <q-icon name="chevron_right" size="20px" color="grey-5" />
        </div>

        <div class="mk-pref-row" @click="$emit('open-notifications')">
          <q-avatar size="38px" class="mk-pref-icon" style="background:#fdf1d8">
            <q-icon name="notifications" size="18px" color="amber-8" />
          </q-avatar>
          <div class="col mk-pref-info">
            <div class="mk-pref-title">Notifications</div>
          </div>
          <q-icon name="chevron_right" size="20px" color="grey-5" />
        </div>
      </div> -->

      <!-- Theme -->
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
          @click.stop="goToLogin"
        />
      </div>

      <!-- App brand footer -->
      <div class="mk-brand-footer">
        <BugCreatorLogo :size="6" />
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
import BugCreatorLogo from '@/components/BugCreatorLogo.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import api from '../api'

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

const isLoading = ref(true)
const isEditingName = ref(false)
const isSaving = ref(false)
const isSavingProfile = ref(false)
const editedName = ref('')
const showEditDialog = ref(false)

const user = ref({
  name: 'Guest User',
  email: '',
  phone: '',
  age: null,
  gender: '',
  nationality: '',
  currency: 'NPR',
  tier: 'Free Tier',
  since: '2080 B.S.',
  isPro: false
})

const editForm = ref({
  full_name: '',
  phone: '',
  age: null,
  gender: '',
  nationality: '',
  currency: 'NPR'
})

const navItems = [
  { name: 'dashboard', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'imports', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function goToLogin() {
  localStorage.removeItem('token')
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_name')

  router.push('/login').catch(() => {
    window.location.href = '/login'
  })
}

async function fetchUserProfile() {
  isLoading.value = true
  try {
    const response = await api.get('/auth/profile')
    const profile = response.data || {}
    const fullName = profile.full_name || profile.name || profile.username || 'User'

    user.value = {
      name: fullName,
      email: profile.email || '',
      phone: profile.phone || '',
      age: profile.age || null,
      gender: profile.gender || '',
      nationality: profile.nationality || '',
      currency: profile.currency || 'NPR',
      tier: 'Free Tier',
      since: profile.created_at ? new Date(profile.created_at).getFullYear().toString() : '2080 B.S.',
      isPro: false
    }

    // Initialize edit form
    editForm.value = {
      full_name: user.value.name,
      phone: user.value.phone,
      age: user.value.age,
      gender: user.value.gender,
      nationality: user.value.nationality,
      currency: user.value.currency
    }

    localStorage.setItem('user_name', fullName)
  } catch (error) {
    console.warn('Backend profile unavailable:', error)
    const storedName = localStorage.getItem('user_name')
    if (storedName) {
      user.value.name = storedName
      editForm.value.full_name = storedName
    }
  } finally {
    isLoading.value = false
  }
}

async function saveName() {
  if (!editedName.value.trim()) return

  isSaving.value = true
  try {
    const response = await api.put('/auth/profile', { full_name: editedName.value.trim() })

    user.value.name = response.data.full_name || editedName.value.trim()
    editForm.value.full_name = user.value.name
    localStorage.setItem('user_name', user.value.name)

    isEditingName.value = false
    $q.notify({ type: 'positive', message: 'Name updated successfully!' })
  } catch (error) {
    console.error('Failed to update name:', error)
    $q.notify({ 
      type: 'negative', 
      message: error.response?.data?.detail || 'Failed to update name' 
    })
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

async function saveProfile() {
  isSavingProfile.value = true
  try {
    const response = await api.put('/auth/profile', {
      full_name: editForm.value.full_name,
      phone: editForm.value.phone,
      age: editForm.value.age,
      gender: editForm.value.gender,
      nationality: editForm.value.nationality,
      currency: editForm.value.currency
    })

    user.value = {
      name: response.data.full_name || user.value.name,
      email: response.data.email || user.value.email,
      phone: response.data.phone || editForm.value.phone,
      age: response.data.age || editForm.value.age,
      gender: response.data.gender || editForm.value.gender,
      nationality: response.data.nationality || editForm.value.nationality,
      currency: response.data.currency || editForm.value.currency,
      tier: user.value.tier,
      since: user.value.since,
      isPro: user.value.isPro
    }

    showEditDialog.value = false
    $q.notify({ 
      type: 'positive', 
      message: 'Profile updated successfully!' 
    })
  } catch (error) {
    console.error('Failed to update profile:', error)
    $q.notify({ 
      type: 'negative', 
      message: error.response?.data?.detail || 'Failed to update profile' 
    })
  } finally {
    isSavingProfile.value = false
  }
}

function setActive(name) {
  activeNav.value = name
  emit('nav-change', name)

  if (name === 'dashboard') router.push('/dashboard')
  else if (name === 'goals') router.push('/goals')
  else if (name === 'imports') router.push('/imports')
  else if (name === 'profile') router.push('/profile')
}

onMounted(() => {
  fetchUserProfile()
})
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

.mk-profile-summary {
  text-align: center;
  padding: 16px 0;
}

.mk-profile-avatar-wrap {
  position: relative;
  display: inline-block;
}

.mk-profile-avatar {
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
}

.mk-pro-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #fbbf24;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 10px;
}

.mk-profile-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-profile-meta {
  font-size: 12px;
  color: var(--mk-muted);
  margin-top: 6px;
}

.mk-details-card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(20, 30, 25, 0.04);
}

.mk-profile-field {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.mk-profile-field:last-child {
  border-bottom: none;
}

.mk-field-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.mk-field-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--mk-text);
}

.mk-section-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mk-text);
  margin-top: 24px;
  margin-bottom: 12px;
}

.mk-pref-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-bottom: 20px;
}

.mk-pref-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: background 0.15s;
}

.mk-pref-row:hover {
  background: #f9faf9;
}

.mk-pref-icon {
  flex-shrink: 0;
}

.mk-pref-info {
  text-align: left;
}

.mk-pref-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--mk-text);
}

.mk-settings-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 20px;
}

.mk-settings-row {
  padding: 12px 0;
}

.mk-settings-label {
  gap: 8px;
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
  padding: 12px 0;
}

.mk-brand-footer {
  text-align: center;
  padding: 22px 0;
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

.edit-profile-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px 16px 0 0;
}
</style>
