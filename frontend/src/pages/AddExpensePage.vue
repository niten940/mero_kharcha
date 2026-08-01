<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <q-btn round flat dense icon="arrow_back" color="primary" class="mk-icon-btn" @click="goBack" />
        <div class="mk-page-title">Add Expense</div>
        <q-btn round flat dense icon="settings" color="grey-8" @click="$emit('open-settings')" />
      </div>

      <!-- Amount -->
      <div class="mk-amount-card">
        <div class="mk-amount-label">AMOUNT SPENT</div>
        <div class="row items-baseline mk-amount-row">
          <span class="mk-currency">Rs.</span>
          <q-input
            v-model="form.amount"
            type="number"
            borderless
            dense
            placeholder="0.00"
            input-class="mk-amount-input"
            class="mk-amount-field"
          />
        </div>
      </div>

      <!-- Category -->
      <div class="mk-section-label">CATEGORY</div>
      <div class="mk-category-row">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="mk-category-item"
          @click="form.category = cat.id"
        >
          <div class="mk-category-circle" :class="{ 'mk-category-active': form.category === cat.id }">
            <q-icon :name="cat.icon" size="20px" :color="form.category === cat.id ? 'white' : 'primary'" />
          </div>
          <div class="mk-category-name" :class="{ 'mk-category-name-active': form.category === cat.id }">
            {{ cat.label }}
          </div>
        </div>
      </div>

      <!-- Transaction date -->
      <div class="mk-date-card row items-center justify-between">
        <div class="row items-start no-wrap q-gutter-sm">
          <q-icon name="event" size="20px" color="grey-7" class="q-mt-xs" />
          <div>
            <div class="mk-date-label">TRANSACTION DATE</div>
            <div class="mk-date-value">{{ displayDate }}</div>
            <div class="mk-date-sub">{{ displayDateSub }}</div>
          </div>
        </div>
        <div class="text-right">
          <q-btn-toggle
            v-model="calendarMode"
            dense
            no-caps
            unelevated
            toggle-color="primary"
            color="white"
            text-color="grey-7"
            class="mk-toggle"
            :options="[
              { label: 'B.S.', value: 'bs' },
              { label: 'A.D.', value: 'ad' }
            ]"
          />
          <div class="mk-change-link" @click="$emit('change-date')">Change</div>
        </div>
      </div>

      <!-- Paid via -->
      <div class="mk-section-label">PAID VIA</div>
      <div class="mk-paid-via-row">
        <div
          v-for="method in paymentMethods"
          :key="method.id"
          class="mk-paid-via-item"
          :class="{ 'mk-paid-via-active': form.paidVia === method.id }"
          @click="form.paidVia = method.id"
        >
          <q-icon
            :name="method.icon"
            size="22px"
            :color="form.paidVia === method.id ? 'primary' : 'grey-6'"
          />
          <div class="mk-paid-via-name" :class="{ 'mk-paid-via-name-active': form.paidVia === method.id }">
            {{ method.label }}
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div class="mk-section-label">NOTES</div>
      <q-input
        v-model="form.notes"
        type="textarea"
        outlined
        dense
        rows="3"
        placeholder="What was this for? (e.g. Lunch with team)"
        class="mk-notes-field"
      />

      <!-- Save -->
      <q-btn
        unelevated
        no-caps
        class="mk-cta"
        icon="save"
        label="Save Expense"
        :loading="saving"
        :disable="saving"
        @click="onSave"
      />
    </div>

    <!-- Bottom navigation (Matched with Dashboard) -->
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
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['open-settings', 'change-date', 'save-expense', 'nav-change'])

const router = useRouter()

const saving = ref(false)
const calendarMode = ref('bs')
const activeNav = ref('')

const form = reactive({
  amount: '',
  category: 'food',
  date: '2083 Shrawan 15',
  paidVia: 'nabil-bank',
  notes: ''
})

const displayDate = computed(() => form.date)
const displayDateSub = computed(() => 'Wednesday, Jul 22, 2026')

const categories = [
  { id: 'food', label: 'Food', icon: 'restaurant' },
  { id: 'rent', label: 'Rent', icon: 'home' },
  { id: 'fuel', label: 'Fuel', icon: 'local_gas_station' },
  { id: 'social', label: 'Social', icon: 'groups' },
  { id: 'health', label: 'Health', icon: 'medical_services' }
]

const paymentMethods = [
  { id: 'nabil-bank', label: 'Nabil Bank', icon: 'account_balance' },
  { id: 'esewa', label: 'eSewa', icon: 'account_balance_wallet' },
  { id: 'cash', label: 'Cash', icon: 'payments' }
]

// Updated Navigation Items (Matching Dashboard)
const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

function setActive (name) {
  activeNav.value = name
  emit('nav-change', name)

  if (name === 'home') {
    router.push('/dashboard')
  } else if (name === 'goals') {
    router.push('/goals')
  } else if (name === 'import') {
    router.push('/imports')
  } else if (name === 'profile') {
    router.push('/profile')
  }
}

function goBack () {
  router.back()
}

async function onSave () {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 0))
    emit('save-expense', { ...form })
    router.push('/dashboard')
  } finally {
    saving.value = false
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

.mk-amount-card {
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  border-radius: 18px;
  padding: 18px 20px;
  margin-bottom: 20px;
}

.mk-amount-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

.mk-amount-row {
  justify-content: center;
  margin-top: 6px;
  gap: 8px;
}

.mk-currency {
  color: #ffffff;
  font-size: 22px;
  font-weight: 700;
}

.mk-amount-field {
  max-width: 160px;
}

.mk-amount-field :deep(.mk-amount-input) {
  color: #ffffff;
  font-size: 32px;
  font-weight: 800;
  text-align: left;
}

.mk-amount-field :deep(input::placeholder) {
  color: rgba(255, 255, 255, 0.55);
}

.mk-section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
  margin-bottom: 10px;
}

.mk-category-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.mk-category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  flex: 1;
}

.mk-category-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e7f3ee;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}

.mk-category-active {
  background: var(--mk-green);
}

.mk-category-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--mk-muted);
}

.mk-category-name-active {
  color: var(--mk-green);
  font-weight: 700;
}

.mk-date-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 20px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-date-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
}

.mk-date-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--mk-text);
  margin-top: 2px;
}

.mk-date-sub {
  font-size: 11px;
  color: var(--mk-muted);
  margin-top: 1px;
}

.mk-toggle {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.mk-change-link {
  font-size: 12px;
  font-weight: 700;
  color: var(--mk-green);
  margin-top: 6px;
  cursor: pointer;
}

.mk-paid-via-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.mk-paid-via-item {
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.mk-paid-via-active {
  border-color: var(--mk-green);
}

.mk-paid-via-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--mk-muted);
}

.mk-paid-via-name-active {
  color: var(--mk-green);
  font-weight: 700;
}

.mk-notes-field {
  margin-bottom: 20px;
}

.mk-notes-field :deep(.q-field__control) {
  border-radius: 12px;
}

.mk-cta {
  width: 100%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  border-radius: 12px;
  font-weight: 700;
  padding: 12px 0;
  font-size: 15px;
  margin-bottom: 12px;
}

/* Bottom Navigation Styles (Matched with Dashboard) */
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