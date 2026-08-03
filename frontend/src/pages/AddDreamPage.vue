<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <q-btn round flat dense icon="arrow_back" color="primary" class="mk-icon-btn" @click="goBack" />
        <div class="mk-page-title">Add Dream</div>
        <q-btn round flat dense icon="help_outline" color="grey-7" @click="$emit('open-help')" />
      </div>

      <!-- Image upload dropzone -->
      <div
        class="mk-image-drop"
        :style="imageUrl ? { backgroundImage: `url(${imageUrl})` } : {}"
        @click="triggerFilePicker"
      >
        <div class="mk-image-drop-overlay">
          <div class="mk-camera-btn">
            <q-icon name="add_a_photo" size="20px" color="white" />
          </div>
          <div class="mk-image-drop-label">VISUALIZE YOUR DREAM</div>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="mk-hidden-input"
          @change="onImageSelected"
        >
      </div>

      <!-- Details card -->
      <q-card flat class="mk-card">
        <q-card-section class="q-gutter-md">
          <div>
            <div class="mk-label">What are you dreaming of?</div>
            <q-input
              v-model="form.name"
              dense
              outlined
              placeholder="e.g. World Tour, Electric SUV"
              class="mk-input"
            />
          </div>

          <div>
            <div class="mk-label">Capital Required (Rs.)</div>
            <q-input
              v-model.number="form.capitalRequired"
              dense
              outlined
              type="number"
              placeholder="0.00"
              class="mk-input mk-currency-input"
            >
              <template #prepend>
                <q-icon name="currency_rupee" size="20px" color="primary" />
              </template>
            </q-input>
          </div>

          <div>
            <div class="mk-label">Dream Category</div>
            <div class="mk-category-scroll">
              <div
                v-for="cat in categories"
                :key="cat.id"
                class="mk-category-pill"
                :class="{ 'mk-category-pill-active': form.category === cat.id }"
                @click="form.category = cat.id"
              >
                <q-icon :name="cat.icon" size="16px" class="q-mr-xs" />
                {{ cat.label }}
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Timeline -->
      <q-card flat class="mk-card">
        <q-card-section>
          <div class="row items-center justify-between q-mb-sm">
            <div class="mk-label">TIMELINE (B.S. CALENDAR)</div>
            <q-icon name="event" size="18px" color="grey-6" />
          </div>

          <div class="row q-col-gutter-sm">
            <div class="col-4">
              <div class="mk-sublabel">YEAR</div>
              <q-select
                v-model="form.year"
                dense
                outlined
                :options="yearOptions"
                class="mk-select"
              />
            </div>
            <div class="col-4">
              <div class="mk-sublabel">MONTH</div>
              <q-select
                v-model="form.month"
                dense
                outlined
                :options="monthOptions"
                class="mk-select mk-select-highlight"
              />
            </div>
            <div class="col-4">
              <div class="mk-sublabel">DAY</div>
              <q-select
                v-model="form.day"
                dense
                outlined
                :options="dayOptions"
                class="mk-select"
              />
            </div>
          </div>

          <div class="mk-time-to-achieve">
            <q-icon name="schedule" size="14px" class="q-mr-xs" />
            Time to achieve: {{ timeToAchieveLabel }}
          </div>
        </q-card-section>
      </q-card>

      <!-- Save -->
      <q-btn
        unelevated
        no-caps
        class="mk-cta"
        icon="save"
        label="Save Dream"
        :loading="saving"
        :disable="saving || !form.name"
        @click="onSave"
      />

      <div class="mk-footer">
        <div class="mk-footer-brand">by Bug Creator &bull; 2083 B.S.</div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['open-help', 'save-dream'])

const router = useRouter()

const saving = ref(false)
const imageUrl = ref('')
const fileInput = ref(null)

const form = reactive({
  name: '',
  capitalRequired: null,
  category: 'real-estate',
  year: 2083,
  month: 'Shraw',
  day: 20
})

const categories = [
  { id: 'travel', label: 'Travel', icon: 'flight' },
  { id: 'real-estate', label: 'Real Estate', icon: 'home' },
  { id: 'vehicle', label: 'Vehicle', icon: 'directions_car' },
  { id: 'education', label: 'Education', icon: 'school' },
  { id: 'other', label: 'Other', icon: 'category' }
]

// B.S. year range for the picker - adjust the span as needed.
const yearOptions = Array.from({ length: 10 }, (_, i) => 2080 + i)

// B.S. month names (Baisakh -> Chaitra), abbreviated to match the screenshot.
const monthOptions = [
  'Baisakh', 'Jestha', 'Ashadh', 'Shraw', 'Bhadra', 'Ashwin',
  'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra'
]

const dayOptions = Array.from({ length: 32 }, (_, i) => i + 1)

// PLACEHOLDER calculation only: treats "today" as a fixed reference date
// (2083 Shrawan 1) and estimates months between the two using month index
// position rather than real B.S.<->A.D. calendar math. B.S. months don't
// all have the same day count and leap adjustments differ from A.D., so for
// an accurate "time to achieve" you'll want a proper Bikram Sambat date
// library (e.g. "bikram-sambat-js" or your backend doing the conversion)
// rather than this rough estimate.
const REFERENCE_YEAR = 2083
const REFERENCE_MONTH_INDEX = monthOptions.indexOf('Shraw') // 4

const timeToAchieveLabel = computed(() => {
  const targetMonthIndex = monthOptions.indexOf(form.month)
  if (targetMonthIndex === -1) return '—'

  let totalMonths = (form.year - REFERENCE_YEAR) * 12 + (targetMonthIndex - REFERENCE_MONTH_INDEX)
  if (totalMonths < 0) totalMonths = 0

  const years = Math.floor(totalMonths / 12)
  const months = totalMonths % 12

  const parts = []
  if (years > 0) parts.push(`${years} year${years > 1 ? 's' : ''}`)
  if (months > 0 || parts.length === 0) parts.push(`${months} month${months !== 1 ? 's' : ''}`)
  return parts.join(', ')
})

function goBack () {
  router.back()
}

function triggerFilePicker () {
  fileInput.value?.click()
}

function onImageSelected (event) {
  const file = event.target.files?.[0]
  if (!file) return
  imageUrl.value = URL.createObjectURL(file)
}

async function onSave () {
  saving.value = true
  try {
    emit('save-dream', { ...form })
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
  padding-bottom: 24px;
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

.mk-image-drop {
  position: relative;
  height: 170px;
  border-radius: 16px;
  border: 2px dashed #7fae95;
  background: linear-gradient(135deg, #d9e4de, #c3d4cb);
  background-size: cover;
  background-position: center;
  overflow: hidden;
  cursor: pointer;
  margin-bottom: 18px;
}

.mk-image-drop-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.25);
}

.mk-camera-btn {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 14px rgba(15, 107, 70, 0.3);
}

.mk-image-drop-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #2f4c3b;
}

.mk-hidden-input {
  display: none;
}

.mk-card {
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(20, 30, 25, 0.05);
  margin-bottom: 16px;
}

.mk-label {
  font-size: 12px;
  font-weight: 700;
  color: #374151;
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}

.mk-sublabel {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--mk-muted);
  margin-bottom: 4px;
}

.mk-input :deep(.q-field__control) {
  border-radius: 10px;
}

.mk-currency-input :deep(.q-field__native) {
  font-size: 20px;
  font-weight: 700;
}

.mk-category-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.mk-category-pill {
  display: flex;
  align-items: center;
  white-space: nowrap;
  padding: 8px 16px;
  border-radius: 999px;
  background: #eef1f0;
  color: #4b5563;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease;
}

.mk-category-pill-active {
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #ffffff;
}

.mk-select :deep(.q-field__control) {
  border-radius: 10px;
}

.mk-select-highlight :deep(.q-field__native) {
  color: var(--mk-green);
  font-weight: 700;
}

.mk-time-to-achieve {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--mk-green);
  margin-top: 12px;
}

.mk-cta {
  width: 100%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  border-radius: 12px;
  font-weight: 700;
  padding: 12px 0;
  font-size: 15px;
  margin-bottom: 10px;
}

.mk-footer {
  text-align: center;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #9ca3af;
}
</style>