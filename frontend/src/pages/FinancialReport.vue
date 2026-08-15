<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <q-btn flat round dense icon="menu" color="grey-8" @click="$emit('open-menu')" />
        <div class="mk-header-title">Financial Reports</div>
        <q-btn flat round dense icon="calendar_today" color="grey-8" @click="showMonthPicker = !showMonthPicker" />
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="row justify-center q-my-xl">
        <q-spinner-dots color="primary" size="40px" />
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="q-pa-md text-negative text-center">
        <q-icon name="error_outline" size="32px" />
        <div class="q-mt-sm">{{ errorMessage }}</div>
        <q-btn flat color="primary" label="Retry" class="q-mt-xs" @click="fetchReportsData" />
      </div>

      <template v-else>
        <!-- Total spent card -->
        <div class="mk-total-card">
          <div class="row items-center justify-between">
            <div class="mk-total-label">TOTAL SPENT</div>
            <div class="mk-change-chip" :class="{ 'mk-change-negative': changePercent < 0 }">
              <q-icon :name="changePercent >= 0 ? 'trending_up' : 'trending_down'" size="13px" />
              {{ changePercent >= 0 ? '+' : '' }}{{ changePercent }}% from {{ previousMonthLabel }}
            </div>
          </div>

          <div class="mk-total-amount-row">
            <span class="mk-rs">Rs.</span>
            <span class="mk-total-amount">{{ wholeAmount }}</span>
            <span class="mk-total-decimals">.{{ decimalAmount }}</span>
          </div>

          <div class="row items-center q-gutter-sm q-mt-md">
            <q-btn
              unelevated
              no-caps
              label="View Statement"
              class="mk-view-statement-btn col"
              @click="$emit('view-statement')"
            />
            <q-btn
              round
              unelevated
              icon="more_horiz"
              class="mk-more-btn"
              @click="$emit('open-options')"
            />
          </div>
        </div>

        <!-- Top merchant / busiest day -->
        <div class="mk-stat-grid">
          <div class="mk-stat-card">
            <div class="mk-stat-icon mk-stat-icon-amber">
              <q-icon name="storefront" size="20px" />
            </div>
            <div class="mk-stat-label">Top Merchant</div>
            <div class="mk-stat-value">{{ topMerchant.name }}</div>
            <div class="mk-stat-sub">{{ topMerchant.transactionCount }} transactions this month</div>
          </div>

          <div class="mk-stat-card">
            <div class="mk-stat-icon mk-stat-icon-pink">
              <q-icon name="wb_sunny" size="20px" />
            </div>
            <div class="mk-stat-label">Busiest Day</div>
            <div class="mk-stat-value">{{ busiestDay.name }}</div>
            <div class="mk-stat-sub">Avg. Rs. {{ formatAmount(busiestDay.avgAmount) }} per weekend</div>
          </div>
        </div>

        <!-- Spending trend -->
        <q-card flat class="mk-trend-card">
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="mk-section-title">Spending Trend</div>
              <q-btn-toggle
                v-model="trendRange"
                dense
                no-caps
                spread
                toggle-color="primary"
                color="white"
                text-color="grey-7"
                class="mk-range-toggle"
                :options="[
                  { label: '5M', value: '5m' },
                  { label: '1Y', value: '1y' },
                ]"
              />
            </div>

            <div v-if="visibleTrend.length" class="mk-bar-chart">
              <div
                v-for="(bar, index) in visibleTrend"
                :key="bar.label"
                class="mk-bar-col"
              >
                <div
                  v-if="index === visibleTrend.length - 1"
                  class="mk-bar-tooltip"
                >
                  Rs. {{ formatCompact(bar.value) }}
                </div>
                <div
                  class="mk-bar"
                  :class="{ 'mk-bar-active': index === visibleTrend.length - 1 }"
                  :style="{ height: barHeight(bar.value) + 'px' }"
                />
                <div class="mk-bar-label">{{ bar.label }}</div>
              </div>
            </div>
            <div v-else class="text-caption text-grey text-center q-pa-md">
              No trend data available.
            </div>
          </q-card-section>
        </q-card>

        <!-- BS month selector -->
        <div class="mk-month-scroll">
          <div
            v-for="month in bsMonths"
            :key="month"
            class="mk-month-item"
            :class="{ 'mk-month-active': selectedMonth === month }"
            @click="selectedMonth = month"
          >
            {{ month }}
          </div>
        </div>

        <!-- Category breakdown -->
        <q-card flat class="mk-category-card">
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="mk-section-title">Category Breakdown</div>
              <div class="mk-see-all" @click="$emit('view-all-categories')">See All</div>
            </div>

            <div v-if="categories.length">
              <div
                v-for="cat in categories"
                :key="cat.label"
                class="mk-category-row"
              >
                <div class="mk-category-icon" :style="{ background: cat.bg, color: cat.color }">
                  <q-icon :name="cat.icon" size="18px" />
                </div>
                <div class="col mk-category-info">
                  <div class="row items-center justify-between">
                    <div class="mk-category-label">{{ cat.label }}</div>
                    <div class="mk-category-amount">Rs. {{ formatAmount(cat.amount) }}</div>
                  </div>
                  <div class="row items-center q-gutter-sm q-mt-xs">
                    <q-linear-progress
                      :value="cat.percent / 100"
                      size="6px"
                      rounded
                      track-color="grey-3"
                      :color="cat.progressColor || 'primary'"
                      class="mk-category-bar"
                    />
                    <span class="mk-category-percent">{{ cat.percent }}%</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-caption text-grey text-center q-pa-md">
              No category data recorded.
            </div>
          </q-card-section>
        </q-card>
      </template>
    </div>

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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

const router = useRouter()
const route = useRoute()

defineEmits(['open-menu', 'view-statement', 'open-options', 'view-all-categories'])

// Reactive UI states
const loading = ref(true)
const errorMessage = ref('')
const showMonthPicker = ref(false)
const trendRange = ref('5m')

// Data from backend
const totalSpent = ref(0)
const changePercent = ref(0)
const previousMonthLabel = ref('Previous Month')
const trend = ref([])
const categories = ref([])

// Default static metrics
const topMerchant = ref({ name: 'Bhat-Bhateni', transactionCount: 12 })
const busiestDay = ref({ name: 'Saturdays', avgAmount: 8500 })

const bsMonths = ['Chaitra', 'Baishak', 'Jestha', 'Asar', 'Shrawan']
const selectedMonth = ref('Shrawan')
// NOTE: this selector is currently cosmetic only. /reports/category has no
// month filter on the backend, so it always returns all-time totals per
// category regardless of which BS month is selected here. Wire this up by
// adding a `month` (or date-range) query param to that endpoint, and pass
// selectedMonth through on fetchReportsData() if you want it to actually
// filter — otherwise consider removing the selector so it doesn't imply
// functionality that isn't there yet.

// Category mappings
const categoryStyleMap = {
  'Food & Groceries': { icon: 'restaurant', bg: '#fdf0d9', color: '#c98a2e', progressColor: 'orange-6' },
  'Food': { icon: 'restaurant', bg: '#fdf0d9', color: '#c98a2e', progressColor: 'orange-6' },
  'Rent & Utilities': { icon: 'home', bg: '#e1f0e5', color: '#0f6e56', progressColor: 'primary' },
  'Housing': { icon: 'home', bg: '#e1f0e5', color: '#0f6e56', progressColor: 'primary' },
  'Fuel & Transport': { icon: 'directions_car', bg: '#dde7fb', color: '#3762d6', progressColor: 'blue-7' },
  'Transportation': { icon: 'directions_car', bg: '#dde7fb', color: '#3762d6', progressColor: 'blue-7' },
  'Social & Dining': { icon: 'groups', bg: '#ece2f9', color: '#7c4fc9', progressColor: 'purple-6' },
  'Entertainment': { icon: 'movie', bg: '#ece2f9', color: '#7c4fc9', progressColor: 'purple-6' },
  'Health & Pharmacy': { icon: 'health_and_safety', bg: '#fbdfe6', color: '#d63e6a', progressColor: 'pink-6' },
  'Medical': { icon: 'health_and_safety', bg: '#fbdfe6', color: '#d63e6a', progressColor: 'pink-6' },
  'Default': { icon: 'category', bg: '#f0f0f0', color: '#666666', progressColor: 'grey-7' }
}

function formatMonthLabel(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? dateStr : date.toLocaleDateString('en-US', { month: 'short' })
}

async function fetchReportsData() {
  loading.value = true
  errorMessage.value = ''

  try {
    // Uses the shared `api` instance (same base URL + auth handling as every
    // other page) instead of a separate hardcoded axios client, so this
    // works the same in dev and production and picks up whatever auth token
    // your app actually stores.
    const [monthlyRes, categoryRes] = await Promise.all([
      api.get('/reports/monthly'),
      api.get('/reports/category')
    ])

    // Process Monthly Trends
    const monthlyData = monthlyRes.data || []
    if (monthlyData.length > 0) {
      trend.value = monthlyData.map((item) => ({
        label: formatMonthLabel(item.month),
        value: item.total
      }))

      const current = monthlyData[monthlyData.length - 1]
      totalSpent.value = current.total

      if (monthlyData.length >= 2) {
        const prev = monthlyData[monthlyData.length - 2]
        previousMonthLabel.value = formatMonthLabel(prev.month)
        if (prev.total > 0) {
          const diff = current.total - prev.total
          changePercent.value = Math.round((diff / prev.total) * 100)
        } else {
          changePercent.value = 100
        }
      } else {
        changePercent.value = 0
        previousMonthLabel.value = 'N/A'
      }
    }

    // Process Category Breakdown
    const categoryData = categoryRes.data || []
    const grandTotal = categoryData.reduce((acc, c) => acc + c.total, 0)

    categories.value = categoryData.map((c) => {
      const style = categoryStyleMap[c.category] || categoryStyleMap['Default']
      const percent = grandTotal > 0 ? Math.round((c.total / grandTotal) * 100) : 0
      return {
        label: c.category,
        amount: c.total,
        percent: percent,
        icon: style.icon,
        bg: style.bg,
        color: style.color,
        progressColor: style.progressColor
      }
    })
  } catch (error) {
    console.error('Failed to fetch reports data:', error)
    if (error.response?.status === 401) {
      errorMessage.value = 'Unauthorized: Please log in again.'
    } else {
      errorMessage.value = 'Unable to fetch report data from server.'
    }
  } finally {
    loading.value = false
  }
}

// Navigation logic — names match navItems exactly (dashboard/goals/reports/
// imports/profile), consistent with DashBoardPage.vue, GoalsPage.vue,
// ImportsPage.vue, and ProfilePage.vue.
const activeNav = ref('reports')
const navItems = [
  { name: 'dashboard', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'imports', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' },
  { name: 'reports', label: 'Reports', icon: 'bar_chart' }
]

function syncActiveNavFromRoute() {
  const path = route.path
  if (path.startsWith('/dashboard')) activeNav.value = 'dashboard'
  else if (path.startsWith('/goals')) activeNav.value = 'goals'
  else if (path.startsWith('/import')) activeNav.value = 'imports'
  else if (path.startsWith('/profile')) activeNav.value = 'profile'
  else if (path.startsWith('/reports')) activeNav.value = 'reports'
}

function setActive(name) {
  activeNav.value = name
  if (!router) return
  if (name === 'dashboard') router.push('/dashboard')
  else if (name === 'goals') router.push('/goals')
  else if (name === 'imports') router.push('/imports')
  else if (name === 'profile') router.push('/profile')
  else if (name === 'reports') router.push('/reports')
}

// Formatting helpers
const wholeAmount = computed(() => Math.floor(totalSpent.value).toLocaleString('en-IN'))
const decimalAmount = computed(() => {
  const decimals = Math.round((totalSpent.value % 1) * 100)
  return decimals.toString().padStart(2, '0')
})

const visibleTrend = computed(() => {
  if (trendRange.value === '5m') {
    return trend.value.slice(-5)
  }
  return trend.value.slice(-12)
})

const maxTrendValue = computed(() => Math.max(...visibleTrend.value.map((b) => b.value), 1))

function barHeight(value) {
  const maxHeight = 90
  return Math.max(8, (value / maxTrendValue.value) * maxHeight)
}

function formatAmount(value) {
  return Number(value || 0).toLocaleString('en-IN')
}

function formatCompact(value) {
  if (value >= 1000) return `${Math.round(value / 1000)}k`
  return value
}

onMounted(() => {
  syncActiveNavFromRoute()
  fetchReportsData()
})

watch(() => route.path, () => {
  syncActiveNavFromRoute()
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
  padding: 18px 16px 32px;
  max-width: 400px;
  margin: 0 auto;
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

.mk-header {
  margin-bottom: 16px;
}

.mk-header-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--mk-green);
}

.mk-total-card {
  background: linear-gradient(135deg, var(--mk-green), var(--mk-green-dark));
  border-radius: 20px;
  padding: 20px;
  color: #fff;
  margin-bottom: 16px;
  box-shadow: 0 12px 24px rgba(15, 107, 70, 0.22);
}

.mk-total-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  opacity: 0.85;
}

.mk-change-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}

.mk-change-negative {
  color: #fecaca;
}

.mk-total-amount-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 10px;
}

.mk-rs {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.9;
}

.mk-total-amount {
  font-size: 34px;
  font-weight: 800;
}

.mk-total-decimals {
  font-size: 16px;
  opacity: 0.75;
}

.mk-view-statement-btn {
  background: #fff;
  color: var(--mk-green-dark);
  font-weight: 700;
  border-radius: 12px;
  padding: 10px 0;
}

.mk-more-btn {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.mk-stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.mk-stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.mk-stat-icon-amber {
  background: #fdf0d9;
  color: #c98a2e;
}

.mk-stat-icon-pink {
  background: #fbdfe6;
  color: #d63e6a;
}

.mk-stat-label {
  font-size: 11px;
  color: var(--mk-muted);
  font-weight: 600;
}

.mk-stat-value {
  font-size: 16px;
  font-weight: 800;
  color: var(--mk-text);
  margin-top: 2px;
}

.mk-stat-sub {
  font-size: 10.5px;
  color: var(--mk-muted);
  margin-top: 4px;
  line-height: 1.35;
}

.mk-trend-card,
.mk-category-card {
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 8px 20px rgba(20, 30, 25, 0.05);
  margin-bottom: 16px;
}

.mk-section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-range-toggle {
  border-radius: 10px;
  border: 1px solid #e7e9f0;
  background: #f5f6f8;
  width: 100px;
}

.mk-range-toggle :deep(.q-btn) {
  font-size: 11px;
  font-weight: 700;
  min-height: 26px;
}

.mk-bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 10px;
  height: 130px;
  padding-top: 24px;
}

.mk-bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.mk-bar {
  width: 100%;
  max-width: 32px;
  background: #dbe3f0;
  border-radius: 8px 8px 4px 4px;
  transition: height 0.4s ease;
}

.mk-bar-active {
  background: var(--mk-green);
}

.mk-bar-tooltip {
  position: absolute;
  top: -22px;
  background: #1c1c1c;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  white-space: nowrap;
}

.mk-bar-label {
  font-size: 10px;
  color: var(--mk-muted);
  margin-top: 8px;
  font-weight: 600;
}

.mk-month-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 2px 16px;
}

.mk-month-item {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--mk-muted);
  padding: 8px 4px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  min-width: 60px;
  text-align: center;
}

.mk-month-active {
  color: var(--mk-green);
  border-bottom-color: var(--mk-green);
  font-weight: 700;
}

.mk-see-all {
  font-size: 12px;
  font-weight: 700;
  color: var(--mk-green);
  cursor: pointer;
}

.mk-category-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
}

.mk-category-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mk-category-info {
  min-width: 0;
}

.mk-category-label {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-category-amount {
  font-size: 13px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-category-bar {
  flex: 1;
}

.mk-category-percent {
  font-size: 11px;
  color: var(--mk-muted);
  font-weight: 600;
  width: 28px;
  text-align: right;
}
</style>