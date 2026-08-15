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

      <!-- Title -->
      <div class="mk-page-title">Statement Parser</div>
      <div class="mk-page-subtitle">
        Import your bank statements to automatically track your expenses.
      </div>

      <!-- Upload zone -->
      <div
        class="mk-dropzone"
        :class="{ 'mk-dropzone-active': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
      >
        <div class="mk-dropzone-icon">
          <q-icon name="upload_file" size="28px" color="white" />
        </div>
        <div class="mk-dropzone-text">
          Drag-and-drop or
          <span class="mk-link" @click="triggerBrowse">Browse</span>
        </div>
        <div class="mk-dropzone-support">SUPPORTS CSV, EXCEL (XLSX), AND PDF STATEMENTS</div>
        <input
          ref="fileInput"
          type="file"
          class="mk-hidden-input"
          accept=".csv,.xlsx,.pdf"
          @change="onFileSelected"
        >
      </div>

      <!-- Preview header -->
      <div class="mk-preview-header row items-center justify-between">
        <div class="mk-preview-title">TRANSACTION PREVIEW (PARSED)</div>
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
      </div>

      <!-- Parsed transactions -->
      <div class="mk-parsed-list">
        <div v-for="tx in parsedTransactions" :key="tx.id" class="mk-parsed-row">
          <div class="mk-parsed-date">
            <div>{{ tx.date }}</div>
            <div class="mk-parsed-date-sub">{{ tx.dateLabel }}</div>
          </div>
          <q-avatar size="36px" class="mk-parsed-avatar" :style="{ background: tx.iconBg }">
            <q-icon :name="tx.icon" size="16px" :color="tx.iconColor" />
          </q-avatar>
          <div class="col mk-parsed-info">
            <div class="mk-parsed-name">{{ tx.name }}</div>
            <div class="mk-parsed-category">Category: {{ tx.category }}</div>
          </div>
          <div class="mk-parsed-amount" :class="tx.amount < 0 ? 'mk-negative' : 'mk-positive'">
            {{ tx.amount < 0 ? '' : '+' }}{{ formatAmount(tx.amount) }}
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="mk-summary-row">
        <div class="mk-summary-card">
          <div class="mk-summary-label">Total Expenses</div>
          <div class="mk-summary-value mk-red-text">Rs. {{ formatAmount(totalExpenses) }}</div>
        </div>
        <div class="mk-summary-card">
          <div class="mk-summary-label">Parsed Items</div>
          <div class="mk-summary-value mk-green-text">{{ parsedTransactions.length }} Transactions</div>
        </div>
      </div>

      <!-- Actions -->
      <q-btn
        unelevated
        no-caps
        class="mk-cta"
        :loading="confirming"
        icon="check_circle"
        label="Confirm Ingestion"
        @click="confirmIngestion"
      />
      <q-btn
        outline
        no-caps
        class="mk-secondary-btn"
        icon="restart_alt"
        label="Reset Parser"
        @click="resetParser"
      />
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
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import api from '../api'

const emit = defineEmits(['open-settings', 'confirm-ingestion', 'reset-parser', 'files-dropped', 'nav-change'])
const router = useRouter()

const activeNav = ref('import')
const isDragging = ref(false)
const calendarMode = ref('bs')
const fileInput = ref(null)
const $q = useQuasar()

const parsing = ref(false)
const confirming = ref(false)

const parsedTransactions = ref([])

const totalExpenses = computed(() =>
  parsedTransactions.value
    .filter(tx => tx.amount < 0)
    .reduce((sum, tx) => sum + Math.abs(tx.amount), 0)
)

const navItems = [
  { name: 'dashboard', label: 'Home', icon: 'home' },
  { name: 'goals', label: 'Goals', icon: 'flag' },
  { name: 'reports', label: 'Report', icon: 'bar_chart' },
  { name: 'imports', label: 'Import', icon: 'file_upload' },
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
  } else if (name === 'reports') {
    router.push('/reports')
  }
}

function triggerBrowse () {
  fileInput.value?.click()
}

function onFileSelected (event) {
  const files = Array.from(event.target.files || [])
  if (files.length) {
    emit('files-dropped', files)
    parseUploadedFiles(files)
  }
}

function onDrop (event) {
  isDragging.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  if (files.length) {
    emit('files-dropped', files)
    parseUploadedFiles(files)
  }
}

async function parseUploadedFiles (files) {
  const file = files[0]
  if (!file) return

  const allowed = ['.csv', '.xlsx', '.xls', '.pdf']
  const lower = file.name.toLowerCase()
  if (!allowed.some(ext => lower.endsWith(ext))) {
    $q.notify({ type: 'negative', message: 'Unsupported file type. Use CSV, XLSX, XLS, or PDF.' })
    return
  }

  parsing.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)

    const resp = await api.post('/imports/parse', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // backend returns list of parsed transactions
    parsedTransactions.value = resp.data.map((t, idx) => ({
      id: idx + 1,
      date: t.date,
      dateLabel: t.date, // frontend may format later
      name: t.title || t.name || '',
      category: t.category || 'Uncategorized',
      amount: t.amount,
      icon: 'receipt_long',
      iconBg: '#e7f3ee',
      iconColor: 'primary',
      description: t.description || ''
    }))

    $q.notify({ type: 'positive', message: `Parsed ${parsedTransactions.value.length} transactions.`, timeout: 3000 })
  } catch (err) {
    console.error('Parse Error:', err)
    const msg = err.response?.data?.detail || 'Could not parse file. Check format.'
    $q.notify({ type: 'negative', message: msg })
  } finally {
    parsing.value = false
  }
}

async function confirmIngestion () {
  if (!parsedTransactions.value.length) {
    $q.notify({ type: 'negative', message: 'No parsed transactions to ingest.' })
    return
  }

  confirming.value = true
  try {
    // map to backend model
    const payload = {
      transactions: parsedTransactions.value.map(t => ({
        date: t.date,
        title: t.name,
        category: t.category,
        description: t.description || t.name,
        amount: t.amount
      }))
    }

    const resp = await api.post('/imports/confirm', payload)

    $q.notify({ type: 'positive', message: resp.data.message || 'Ingestion complete', timeout: 4000 })
    // clear parsed data
    parsedTransactions.value = []
  } catch (err) {
    console.error('Confirm Error:', err)
    const msg = err.response?.data?.detail || 'Could not ingest transactions.'
    $q.notify({ type: 'negative', message: msg })
  } finally {
    confirming.value = false
  }
}

function formatAmount (value) {
  return Number(Math.abs(value)).toLocaleString('en-IN', { minimumFractionDigits: 2 })
}

function resetParser () {
  parsedTransactions.value = []
  $q.notify({ type: 'info', message: 'Parser reset.' })
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

.mk-page-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--mk-green);
}

.mk-page-subtitle {
  font-size: 13px;
  color: var(--mk-muted);
  margin-top: 4px;
  margin-bottom: 18px;
  line-height: 1.5;
}

.mk-dropzone {
  border: 2px dashed #c9d3ce;
  border-radius: 16px;
  background: #f5f7f6;
  padding: 28px 16px;
  text-align: center;
  position: relative;
  margin-bottom: 20px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.mk-dropzone-active {
  border-color: var(--mk-green);
  background: #eaf5ef;
}

.mk-dropzone-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.mk-dropzone-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-link {
  color: var(--mk-green);
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}

.mk-dropzone-support {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #9ca3af;
  margin-top: 8px;
}

.mk-hidden-input {
  display: none;
}

.mk-preview-header {
  margin-bottom: 10px;
}

.mk-preview-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #b45309;
}

.mk-toggle {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.mk-parsed-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.mk-parsed-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 6px 16px rgba(20, 30, 25, 0.04);
}

.mk-parsed-date {
  font-size: 12px;
  font-weight: 700;
  color: var(--mk-text);
  min-width: 62px;
}

.mk-parsed-date-sub {
  font-size: 10px;
  font-weight: 500;
  color: var(--mk-muted);
}

.mk-parsed-info {
  min-width: 0;
}

.mk-parsed-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--mk-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mk-parsed-category {
  font-size: 11px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-parsed-amount {
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.mk-negative {
  color: #dc2626;
}

.mk-positive {
  color: var(--mk-green);
}

.mk-summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}

.mk-summary-card {
  background: #eef2f0;
  border-radius: 14px;
  padding: 14px;
}

.mk-summary-label {
  font-size: 12px;
  color: var(--mk-muted);
}

.mk-summary-value {
  font-size: 17px;
  font-weight: 800;
  margin-top: 4px;
}

.mk-red-text {
  color: #dc2626;
}

.mk-green-text {
  color: var(--mk-green);
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

.mk-secondary-btn {
  width: 100%;
  border-radius: 12px;
  border-color: #e5e7eb;
  color: #4b5563;
  font-weight: 600;
  padding: 12px 0;
  margin-bottom: 8px;
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