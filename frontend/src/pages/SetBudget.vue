<template>
  <q-page class="budget-page">
    <div class="budget-wrap">
      <div class="page-header">
        <q-btn
          round
          outline
          color="primary"
          icon="arrow_back"
          class="back-btn"
          @click="$router.back()"
        />
        <div class="text-h6 text-weight-bold header-title">Set Budget</div>
      </div>

      <q-card flat class="limit-card">
        <q-card-section class="text-center">
          <div class="limit-label">MONTHLY LIMIT (NPR)</div>
          <div class="limit-amount-row">
            <span class="rs-prefix">Rs.</span>
            <span class="limit-amount">{{ formattedAmount }}</span>
          </div>
          <q-slider
            v-model="amount"
            :min="1000"
            :max="100000"
            :step="500"
            color="primary"
            class="limit-slider"
          />
          <div class="period-label">{{ periodLabel }}</div>
        </q-card-section>
      </q-card>

      <div class="toggle-row">
        <q-btn-toggle
          v-model="mode"
          spread
          no-caps
          toggle-color="primary"
          color="white"
          text-color="dark"
          class="mode-toggle"
          :options="[
            { label: 'Monthly', value: 'monthly' },
            { label: 'Custom', value: 'custom' },
          ]"
        />
      </div>

      <div class="section-label">SELECT CATEGORY</div>
      <div class="category-grid">
        <div
          v-for="cat in categories"
          :key="cat.value"
          class="category-item"
          :class="{ active: selectedCategory === cat.value }"
          @click="selectedCategory = cat.value"
        >
          <div class="category-icon" :class="{ active: selectedCategory === cat.value }">
            <q-icon :name="cat.icon" size="20px" />
          </div>
          <div class="category-name">{{ cat.label }}</div>
        </div>
      </div>

      <q-card flat class="spending-card">
        <q-card-section>
          <div class="spending-row">
            <span class="spending-label">Last Month's Spending</span>
            <span class="spending-amount">Rs. {{ formattedLastSpending }}</span>
          </div>
          <q-linear-progress
            :value="spendingRatio"
            color="primary"
            track-color="grey-3"
            rounded
            size="6px"
            class="q-my-sm"
          />
          <div class="spending-note">
            <q-icon name="trending_up" size="14px" color="primary" />
            {{ spendingNote }}
          </div>
        </q-card-section>
      </q-card>

      <q-btn
        unelevated
        no-caps
        class="set-budget-btn"
        label="Set Budget"
        :disable="!selectedCategory"
        :loading="submitting"
        @click="onSubmit"
      />
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '../api'

const $q = useQuasar()

const amount = ref(15000)
const mode = ref('monthly')
const selectedCategory = ref('food')
const submitting = ref(false)
const lastMonthSpending = ref(12450)
const periodLabel = ref('Shrawan (July/Aug)')
const budgetExists = ref(false)

const emit = defineEmits(['budget-set'])

const categories = [
  { value: 'food', label: 'Food & Groceries', icon: 'restaurant' },
  { value: 'transport', label: 'Transport', icon: 'directions_car' },
  { value: 'rent', label: 'Rent & Utilities', icon: 'home' },
  { value: 'shopping', label: 'Shopping', icon: 'shopping_bag' },
  { value: 'health', label: 'Health', icon: 'medical_services' },
  { value: 'education', label: 'Education', icon: 'school' },
  { value: 'entertainment', label: 'Entertainment', icon: 'movie' },
  { value: 'other', label: 'Other', icon: 'add' },
]

const formattedAmount = computed(() => amount.value.toLocaleString('en-IN'))
const formattedLastSpending = computed(() => lastMonthSpending.value.toLocaleString('en-IN'))

const spendingRatio = computed(() => {
  if (amount.value === 0) return 0
  return Math.min(lastMonthSpending.value / amount.value, 1)
})

const percentChange = computed(() => {
  if (lastMonthSpending.value === 0) return 0
  return Math.round(((amount.value - lastMonthSpending.value) / lastMonthSpending.value) * 100)
})

const spendingNote = computed(() => {
  const pct = percentChange.value
  if (pct > 0) return `Setting Rs. ${formattedAmount.value} allows for a ${pct}% increase from last month.`
  if (pct < 0) return `Setting Rs. ${formattedAmount.value} is a ${Math.abs(pct)}% decrease from last month.`
  return `Setting Rs. ${formattedAmount.value} matches last month's spending.`
})

async function fetchExistingBudget() {
  try {
    const response = await api.get('/budget')
    if (response.data) {
      amount.value = parseFloat(response.data.monthly_limit)
      budgetExists.value = true
    }
  } catch (error) {
    // Budget doesn't exist yet, that's fine
    budgetExists.value = false
  }
}

async function onSubmit() {
  submitting.value = true
  try {
    const budgetData = {
      monthly_limit: amount.value,
    }

    if (budgetExists.value) {
      // Update existing budget
      await api.put('/budget', budgetData)
      $q.notify({ 
        type: 'positive', 
        message: 'Budget updated successfully!' 
      })
    } else {
      // Create new budget
      await api.post('/budget', budgetData)
      budgetExists.value = true
      $q.notify({ 
        type: 'positive', 
        message: 'Budget set successfully!' 
      })
    }

    // Emit event for parent component
    emit('budget-set', {
      amount: amount.value,
      mode: mode.value,
      category: selectedCategory.value,
    })
  } catch (error) {
    console.error('Budget error:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to set budget'
    $q.notify({ 
      type: 'negative', 
      message: errorMsg 
    })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchExistingBudget()
})
</script>

<style scoped>
.budget-page {
  background: #eceef4;
  background-image: radial-gradient(circle, #d9dbe3 1px, transparent 1px);
  background-size: 16px 16px;
}

.budget-wrap {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px 18px 28px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.back-btn {
  border-style: dashed;
}

.header-title {
  color: #1b2430;
  font-size: 19px;
}

.limit-card {
  border-radius: 18px;
  background: #e6efe9;
  margin-bottom: 18px;
}

.limit-label {
  font-size: 11px;
  letter-spacing: 0.5px;
  color: #7d8b84;
  font-weight: 600;
  margin-bottom: 10px;
}

.limit-amount-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.rs-prefix {
  font-size: 15px;
  color: #5b6472;
  font-weight: 600;
}

.limit-amount {
  font-size: 34px;
  font-weight: 800;
  color: #0b5d45;
}

.limit-slider {
  margin-top: 10px;
}

.period-label {
  font-size: 13px;
  color: #7d8b84;
  border-top: 1px solid #d3ddd7;
  padding-top: 10px;
  margin-top: 6px;
}

.toggle-row {
  margin-bottom: 20px;
}

.mode-toggle {
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e7e9f0;
}

.mode-toggle :deep(.q-btn) {
  font-weight: 600;
  font-size: 13.5px;
}

.section-label {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #5b6472;
  margin-bottom: 12px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px 8px;
  margin-bottom: 20px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 4px;
  border-radius: 12px;
  border: 1.5px solid transparent;
}

.category-item.active {
  border-color: #0f6e56;
  background: #f2f9f6;
}

.category-icon {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: #eef0f4;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon.active {
  background: #0f6e56;
  color: #fff;
}

.category-name {
  font-size: 10.5px;
  text-align: center;
  color: #4a4f58;
  font-weight: 600;
  line-height: 1.25;
}

.spending-card {
  border-radius: 16px;
  margin-bottom: 22px;
}

.spending-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13.5px;
}

.spending-label {
  color: #4a4f58;
  font-weight: 600;
}

.spending-amount {
  color: #1b2430;
  font-weight: 700;
}

.spending-note {
  font-size: 12px;
  color: #5b6472;
  display: flex;
  align-items: center;
  gap: 4px;
}

.set-budget-btn {
  width: 100%;
  background: #0b5d45;
  color: #fff;
  border-radius: 14px;
  padding: 14px;
  font-weight: 700;
  font-size: 15px;
  border: 2px dashed rgba(255, 255, 255, 0.4);
}
</style>