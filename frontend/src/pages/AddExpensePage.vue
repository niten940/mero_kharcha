<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
                  
        <q-btn round flat dense icon="arrow_back" color="primary" class="mk-icon-btn" @click="goBack" />
        <MeroKharchaLogo :size="10" />
        <div class="mk-page-title">Add Expense</div>
        <!-- <q-btn round flat dense icon="settings" color="grey-8" @click="$emit('open-settings')" /> -->
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
              { label: 'A.D.', value: 'ad' },
              { label: 'B.S.', value: 'bs' }
            ]"
          />
          <div class="mk-change-link" @click="showDatePicker = true">Change</div>
        </div>
      </div>

      <!-- Date Picker Dialog -->
      <q-dialog v-model="showDatePicker" position="bottom">
        <q-card class="date-picker-card">
          <q-card-section class="row items-center justify-between q-pb-none">
            <div class="text-subtitle2 text-weight-bold">
              Select {{ calendarMode === 'ad' ? 'A.D.' : 'B.S.' }} Date
            </div>
            <q-btn icon="close" flat round dense @click="showDatePicker = false" />
          </q-card-section>

          <q-card-section v-if="calendarMode === 'ad'" class="q-pt-md">
            <q-input
              v-model="adDate"
              type="date"
              outlined
              dense
              @update:model-value="convertADToBS"
            />
          </q-card-section>

          <q-card-section v-else class="q-pt-md">
            <div class="row q-gutter-md">
              <q-input
                v-model.number="bsDate.year"
                label="Year"
                type="number"
                outlined
                dense
                style="flex: 1"
                @update:model-value="convertBSToAD(bsDate.year, bsDate.month, bsDate.day)"
              />
              <q-input
                v-model.number="bsDate.month"
                label="Month"
                type="number"
                outlined
                dense
                style="flex: 1"
                @update:model-value="convertBSToAD(bsDate.year, bsDate.month, bsDate.day)"
              />
              <q-input
                v-model.number="bsDate.day"
                label="Day"
                type="number"
                outlined
                dense
                style="flex: 1"
                @update:model-value="convertBSToAD(bsDate.year, bsDate.month, bsDate.day)"
              />
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Done" color="primary" @click="showDatePicker = false" />
          </q-card-actions>
        </q-card>
      </q-dialog>

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
      <div class="mk-section-label">DESCRIPTION</div>
      <q-input
        v-model="form.title"
        outlined
        dense
        placeholder="What was this for? (e.g. Lunch with team)"
        class="mk-title-field q-mb-md"
      />
      <q-input
        v-model="form.description"
        type="textarea"
        outlined
        dense
        rows="3"
        placeholder="Additional notes (optional)"
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
import MeroKharchaLogo from '@/components/MeroKharchaLogo.vue'
import { computed, reactive, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import api from '../api'

const emit = defineEmits(['open-settings', 'change-date', 'save-expense', 'nav-change'])

const router = useRouter()
const $q = useQuasar()

const saving = ref(false)
const calendarMode = ref('ad')
const activeNav = ref('')
const loadingDate = ref(false)
const showDatePicker = ref(false)

// Store both AD and BS dates
const adDate = ref(new Date().toISOString().split('T')[0])
const bsDate = reactive({
  year: 2083,
  month: 1,
  day: 1,
  label: '2083-01-01'
})

const form = reactive({
  title: '',
  description: '',
  amount: '',
  category: 'food',
  paidVia: 'nabil-bank'
})

const displayDate = computed(() => {
  if (calendarMode.value === 'ad') {
    return adDate.value
  } else {
    return bsDate.label
  }
})

const displayDateSub = computed(() => {
  const date = new Date(adDate.value)
  return date.toLocaleDateString('en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

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

const navItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'track_changes' },
  { name: 'import', label: 'Import', icon: 'description' },
  { name: 'profile', label: 'Profile', icon: 'person_outline' }
]

// Convert AD to BS
async function convertADToBS(ad_date_str) {
  try {
    loadingDate.value = true
    const response = await api.post('/calendar/ad-to-bs', {
      ad_date: ad_date_str
    })
    
    const data = response.data
    bsDate.year = data.bs_year
    bsDate.month = data.bs_month
    bsDate.day = data.bs_day
    bsDate.label = data.bs_label
  } catch (error) {
    console.error('Failed to convert AD to BS:', error)
  } finally {
    loadingDate.value = false
  }
}

// Convert BS to AD
async function convertBSToAD(bs_year, bs_month, bs_day) {
  try {
    loadingDate.value = true
    const response = await api.post('/calendar/bs-to-ad', {
      bs_year,
      bs_month,
      bs_day
    })
    
    adDate.value = response.data.ad_date
  } catch (error) {
    console.error('Failed to convert BS to AD:', error)
  } finally {
    loadingDate.value = false
  }
}

// Watch for calendar mode changes
watch(calendarMode, (newMode, oldMode) => {
  // If switching to BS and haven't converted yet
  if (newMode === 'bs' && (bsDate.year === 2083 && bsDate.month === 1 && bsDate.day === 1)) {
    convertADToBS(adDate.value)
  }
})

// Initialize with today's date in both formats
onMounted(async () => {
  try {
    const response = await api.get('/calendar/today')
    const data = response.data
    
    adDate.value = data.ad_date
    bsDate.year = data.bs_year
    bsDate.month = data.bs_month
    bsDate.day = data.bs_day
    bsDate.label = data.bs_label
  } catch (error) {
    console.error('Failed to fetch today date:', error)
    // Fallback: convert current date
    await convertADToBS(adDate.value)
  }

  // Check if there's scanned receipt data to pre-fill
  const scannedDataJson = localStorage.getItem('scannedReceiptData')
  if (scannedDataJson) {
    try {
      const scannedData = JSON.parse(scannedDataJson)
      
      // Pre-fill form with scanned data
      form.title = scannedData.title || ''
      form.amount = scannedData.amount || ''
      form.description = scannedData.description || ''
      
      // Set category from suggestion
      if (scannedData.suggested_category) {
        const categoryId = scannedData.suggested_category.toLowerCase()
        if (categories.find(c => c.id === categoryId)) {
          form.category = categoryId
        }
      }
      
      // Set date from receipt if available
      if (scannedData.date) {
        adDate.value = scannedData.date
        await convertADToBS(scannedData.date)
      }
      
      // Clear the stored data so it doesn't persist
      localStorage.removeItem('scannedReceiptData')
      
      // Notify user that data was pre-filled
      $q.notify({
        type: 'info',
        message: 'Receipt data pre-filled. Please review before saving.',
        position: 'bottom'
      })
    } catch (error) {
      console.error('Failed to parse scanned receipt data:', error)
      localStorage.removeItem('scannedReceiptData')
    }
  }
})

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
  if (!form.title.trim()) {
    $q.notify({
      type: 'negative',
      message: 'Please enter a description',
      position: 'bottom'
    })
    return
  }

  if (!form.amount || Number(form.amount) <= 0) {
    $q.notify({
      type: 'negative',
      message: 'Please enter a valid amount',
      position: 'bottom'
    })
    return
  }

  saving.value = true
  try {
    const expenseData = {
      title: form.title.trim(),
      description: form.description.trim(),
      amount: Number(form.amount),
      category: form.category,
      date: adDate.value
    }

    await api.post('/expenses/post/', expenseData)

    $q.notify({
      type: 'positive',
      message: 'Expense saved successfully!',
      position: 'bottom'
    })

    form.title = ''
    form.description = ''
    form.amount = ''
    form.category = 'food'
    form.paidVia = 'nabil-bank'

    emit('save-expense', expenseData)
    router.push('/dashboard')
  } catch (error) {
    console.error('Failed to save expense:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.detail || 'Failed to save expense',
      position: 'bottom'
    })
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

.mk-title-field {
  margin-bottom: 12px;
}

.mk-title-field :deep(.q-field__control) {
  border-radius: 12px;
}

.mk-notes-field {
  margin-bottom: 20px;
}

.mk-notes-field :deep(.q-field__control) {
  border-radius: 12px;
}

.date-picker-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px 16px 0 0;
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