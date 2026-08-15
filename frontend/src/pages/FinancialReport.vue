<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <q-btn flat round dense icon="menu" color="grey-8" @click="$emit('open-menu')" />
        <div class="mk-header-title">Financial Reports</div>
        <q-btn flat round dense icon="calendar_today" color="grey-8" @click="showMonthPicker = !showMonthPicker" />
      </div>

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

          <div class="mk-bar-chart">
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
        </q-card-section>
      </q-card>
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

const router = useRouter()
const route = useRoute()

defineEmits(['open-menu', 'view-statement', 'open-options', 'view-all-categories'])

const props = defineProps({
  totalSpent: { type: Number, default: 142500 },
  changePercent: { type: Number, default: 12 },
  previousMonthLabel: { type: String, default: 'Asar' },
  topMerchant: {
    type: Object,
    default: () => ({ name: 'Bhat-Bhateni', transactionCount: 12 }),
  },
  busiestDay: {
    type: Object,
    default: () => ({ name: 'Saturdays', avgAmount: 8500 }),
  },
  trend: {
    type: Array,
    default: () => [
      { label: 'Baishak', value: 62000 },
      { label: 'Jestha', value: 48000 },
      { label: 'Asar', value: 98000 },
      { label: 'Shrawan', value: 105000 },
      { label: 'Bhadra', value: 142000 },
    ],
  },
  categories: {
    type: Array,
    default: () => [
      { label: 'Food & Groceries', icon: 'restaurant', amount: 45000, percent: 32, bg: '#fdf0d9', color: '#c98a2e', progressColor: 'orange-6' },
      { label: 'Rent & Utilities', icon: 'home', amount: 35000, percent: 25, bg: '#e1f0e5', color: '#0f6e56', progressColor: 'primary' },
      { label: 'Fuel & Transport', icon: 'directions_car', amount: 15500, percent: 11, bg: '#dde7fb', color: '#3762d6', progressColor: 'blue-7' },
      { label: 'Social & Dining', icon: 'groups', amount: 12000, percent: 8, bg: '#ece2f9', color: '#7c4fc9', progressColor: 'purple-6' },
      { label: 'Health & Pharmacy', icon: 'health_and_safety', amount: 8000, percent: 5, bg: '#fbdfe6', color: '#d63e6a', progressColor: 'pink-6' },
    ],
  },
})

const showMonthPicker = ref(false)
const trendRange = ref('5m')

// Same nav set and routing as DashBoardPage.vue, so the bottom bar behaves
// identically across screens.
const activeNav = ref('reports')

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' },
  { name: 'reports', label: 'Reports', icon: 'bar_chart' }
]

function syncActiveNavFromRoute() {
  const path = route.path
  if (path.startsWith('/dashboard')) activeNav.value = 'home'
  else if (path.startsWith('/goals')) activeNav.value = 'goals'
  else if (path.startsWith('/import')) activeNav.value = 'import'
  else if (path.startsWith('/profile')) activeNav.value = 'profile'
  else if (path.startsWith('/reports')) activeNav.value = 'reports'
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

onMounted(() => {
  syncActiveNavFromRoute()
})

watch(() => route.path, () => {
  syncActiveNavFromRoute()
})

const bsMonths = ['Chaitra', 'Baishak', 'Jestha', 'Asar', 'Shrawan']
const selectedMonth = ref('Shrawan')

const wholeAmount = computed(() => Math.floor(props.totalSpent).toLocaleString('en-IN'))
const decimalAmount = computed(() => {
  const decimals = Math.round((props.totalSpent % 1) * 100)
  return decimals.toString().padStart(2, '0')
})

const visibleTrend = computed(() => {
  return trendRange.value === '5m' ? props.trend : props.trend
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