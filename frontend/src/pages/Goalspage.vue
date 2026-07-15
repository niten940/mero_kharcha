<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header (Clicking the brand now redirects Home!) -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row cursor-pointer" @click="goHome">
          <q-avatar size="36px" class="mk-avatar">
            <q-icon name="person" size="20px" color="white" />
          </q-avatar>
          <div class="mk-brand-name">Mero Kharcha</div>
        </div>
        <q-btn flat round dense icon="settings" color="grey-8" @click="$emit('open-settings')" />
      </div>

      <!-- Vision board hero -->
      <div class="mk-hero">
        <div class="mk-hero-eyebrow">VISION BOARD</div>
        <div class="mk-hero-title">My Future Dreams</div>
        <div class="mk-hero-text">
          Manifesting growth, one rupee at a time. Tracking {{ goals.length }} dreams for {{ yearLabel }}.
        </div>
        <q-icon name="auto_awesome" class="mk-hero-icon" size="90px" />
      </div>

      <!-- Featured goal -->
      <div class="mk-featured-card" :style="{ background: featuredGoal.gradient }">
        <div class="mk-featured-visual">
          <q-icon :name="featuredGoal.icon" size="72px" color="white" class="mk-featured-icon" />
          <div class="mk-badge">{{ featuredGoal.progress }}% ACHIEVED</div>
          <div class="mk-featured-name">{{ featuredGoal.name }}</div>
        </div>
        <div class="mk-featured-body">
          <div class="row items-center justify-between">
            <div>
              <div class="mk-stat-label">SAVED</div>
              <div class="mk-stat-value mk-green-text">Rs. {{ formatAmount(featuredGoal.saved) }}</div>
            </div>
            <div class="text-right">
              <div class="mk-stat-label">LEFT</div>
              <div class="mk-stat-value mk-red-text">Rs. {{ formatAmount(featuredGoal.left) }}</div>
            </div>
          </div>
          <q-linear-progress
            :value="featuredGoal.progress / 100"
            size="8px"
            rounded
            track-color="grey-3"
            color="primary"
            class="q-mt-sm"
          />
        </div>
      </div>

      <!-- Goal grid -->
      <div class="mk-goal-grid">
        <div v-for="goal in otherGoals" :key="goal.id" class="mk-goal-tile">
          <div class="mk-goal-visual" :style="{ background: goal.gradient }">
            <q-icon :name="goal.icon" size="40px" color="white" />
          </div>
          <div class="mk-goal-tile-body">
            <div class="mk-goal-name">{{ goal.name }}</div>
            <div class="mk-goal-left">Rs. {{ formatAmount(goal.left) }} left</div>
            <q-linear-progress
              :value="goal.progress / 100"
              size="6px"
              rounded
              track-color="grey-3"
              :color="goal.progress >= 50 ? 'primary' : 'amber-6'"
              class="q-mt-xs"
            />
          </div>
        </div>
      </div>

      <!-- Add new dream -->
      <q-btn
        flat
        no-caps
        class="mk-add-dream"
        @click="$emit('add-goal')"
      >
        <q-icon name="add_circle_outline" size="20px" class="q-mr-sm" />
        Add New Dream
      </q-btn>

      <!-- Summary stats -->
      <div class="mk-summary-row">
        <div class="mk-summary-card">
          <div class="mk-summary-value mk-green-text">{{ goals.length }}</div>
          <div class="mk-summary-label">ACTIVE DREAMS</div>
        </div>
        <div class="mk-summary-card">
          <div class="mk-summary-value mk-amber-text">{{ avgProgress }}%</div>
          <div class="mk-summary-label">AVG PROGRESS</div>
        </div>
      </div>

      <!-- Footer (Now with active Router Links) -->
      <div class="mk-footer">
        <div class="mk-footer-brand">by Bug Creator &bull; 2083 B.S.</div>
        <div class="mk-footer-links">
          <router-link to="/privacy" class="mk-link-muted">Privacy Policy</router-link>
          <span class="mk-dot">&bull;</span>
          <router-link to="/terms" class="mk-link-muted">Terms of Service</router-link>
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
      @click="$emit('add-goal')"
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

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router' // 👈 1. Import Vue Router

defineEmits(['open-settings', 'add-goal', 'nav-change'])

const router = useRouter() // 👈 2. Initialize the router instance

const activeNav = ref('goals')
const yearLabel = '2083 B.S.'

const goals = ref([
  {
    id: 1,
    name: 'Electric Bike',
    icon: 'electric_moped',
    gradient: 'linear-gradient(135deg, #2f6f52, #163f2c)',
    saved: 135000,
    left: 45000,
    progress: 75
  },
  {
    id: 2,
    name: 'New Laptop',
    icon: 'laptop_mac',
    gradient: 'linear-gradient(135deg, #6b5b3f, #3f3527)',
    saved: 15000,
    left: 45000,
    progress: 25
  },
  {
    id: 3,
    name: 'Mustang Trip',
    icon: 'terrain',
    gradient: 'linear-gradient(135deg, #3b6d8c, #1e3c50)',
    saved: 38000,
    left: 22000,
    progress: 63
  }
])

const featuredGoal = computed(() => goals.value[0])
const otherGoals = computed(() => goals.value.slice(1))

const avgProgress = computed(() => {
  const total = goals.value.reduce((sum, g) => sum + g.progress, 0)
  return Math.round(total / goals.value.length)
})

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

// 👈 3. Updated navigation method
function setActive (name) {
  activeNav.value = name
  if (name === 'home') {
    router.push('/dashboard')
  } else if (name === 'goals') {
    router.push('/goals')
  } else if (name === 'import') {
    router.push('/import')
  } else if (name === 'profile') {
    router.push('/profile')
  }
}

// 👈 4. Helper function to go straight back to Dashboard/Home
function goHome () {
  router.push('/dashboard')
}

function formatAmount (value) {
  return Number(value).toLocaleString('en-IN')
}
</script>

<style scoped>
/* Utility class for cursor styling */
.cursor-pointer {
  cursor: pointer;
}

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

.mk-hero {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  padding: 20px;
  margin-bottom: 18px;
}

.mk-hero-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  opacity: 0.85;
}

.mk-hero-title {
  font-size: 24px;
  font-weight: 800;
  margin-top: 6px;
}

.mk-hero-text {
  font-size: 13px;
  opacity: 0.9;
  margin-top: 8px;
  line-height: 1.5;
  max-width: 220px;
}

.mk-hero-icon {
  position: absolute;
  right: -10px;
  bottom: -16px;
  opacity: 0.18;
}

.mk-featured-card {
  border-radius: 18px;
  overflow: hidden;
  margin-bottom: 18px;
  box-shadow: 0 10px 24px rgba(20, 30, 25, 0.1);
}

.mk-featured-visual {
  position: relative;
  min-height: 150px;
  display: flex;
  align-items: flex-end;
  padding: 14px;
}

.mk-featured-icon {
  position: absolute;
  right: 14px;
  top: 20px;
  opacity: 0.85;
}

.mk-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  background: #f5a524;
  color: #1c1c1c;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}

.mk-featured-name {
  color: #fff;
  font-size: 19px;
  font-weight: 700;
}

.mk-featured-body {
  background: #ffffff;
  padding: 14px 16px 16px;
}

.mk-stat-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
}

.mk-stat-value {
  font-size: 17px;
  font-weight: 800;
  margin-top: 2px;
}

.mk-green-text {
  color: var(--mk-green);
}

.mk-red-text {
  color: #dc2626;
}

.mk-amber-text {
  color: #b45309;
}

.mk-goal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.mk-goal-tile {
  border-radius: 16px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(20, 30, 25, 0.06);
}

.mk-goal-visual {
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mk-goal-tile-body {
  padding: 10px 12px 12px;
}

.mk-goal-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-goal-left {
  font-size: 12px;
  font-weight: 700;
  color: #dc2626;
  margin-top: 2px;
}

.mk-add-dream {
  width: 100%;
  background: #e6ecea;
  color: #374151;
  border-radius: 14px;
  font-weight: 600;
  padding: 10px 0;
  margin-bottom: 16px;
}

.mk-summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 8px;
}

.mk-summary-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  text-align: center;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-summary-value {
  font-size: 22px;
  font-weight: 800;
}

.mk-summary-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
  margin-top: 2px;
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

.mk-link-muted {
  color: #9ca3af;
  font-size: 11px;
  cursor: pointer;
  text-decoration: none;
}
.mk-link-muted:hover {
  color: var(--mk-text);
}

.mk-dot {
  color: #d1d5db;
  margin: 0 6px;
  font-size: 11px;
}

.mk-footer-links {
  margin-top: 6px;
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

.mk-nav-label {
  font-size: 10px;
  font-weight: 600;
}

.mk-nav-active {
  color: var(--mk-green-dark);
  background: #fdf1d8;
}
</style>