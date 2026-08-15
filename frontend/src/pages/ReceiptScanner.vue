<template>
  <q-dialog v-model="isOpen" persistent>
    <q-card class="scanner-card">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6 text-weight-bold">Scan Receipt</div>
        <q-btn round flat dense icon="close" @click="close" />
      </q-card-section>

      <q-card-section>
        <!-- Step 1: capture / choose image -->
        <div v-if="!imagePreview" class="capture-zone" @click="triggerFileInput">
          <q-icon name="qr_code_scanner" size="48px" color="primary" />
          <div class="capture-text">Tap to take a photo, or upload an image / PDF</div>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,application/pdf"
            capture="environment"
            class="hidden-input"
            @change="onFileSelected"
          />
        </div>

        <!-- Step 2: preview + scan mode + progress -->
        <div v-else>
          <q-img v-if="!isPdf" :src="imagePreview" class="preview-img" />
          <div v-else class="pdf-chip">
            <q-icon name="picture_as_pdf" size="22px" />
            {{ selectedFile?.name }}
          </div>

          <q-toggle
            v-model="useAiScan"
            label="AI Scan (handwritten / Devanagari / PDF)"
            class="q-mt-md"
            :disable="isProcessing"
          />

          <div v-if="isProcessing" class="q-mt-md text-center">
            <q-spinner color="primary" size="28px" />
            <div class="text-caption q-mt-xs">
              {{ useAiScan ? 'Reading with AI…' : 'Running OCR…' }}
            </div>
          </div>

          <!-- Step 3: editable extracted fields -->
          <div v-else-if="extracted" class="q-mt-md">
            <q-input
              v-model="extracted.title"
              outlined
              dense
              label="Title / Merchant"
              class="q-mb-sm"
            />
            <q-input
              v-model.number="extracted.amount"
              type="number"
              outlined
              dense
              label="Amount (Rs.)"
              class="q-mb-sm"
            />
            <q-input
              v-model="extracted.date"
              outlined
              dense
              label="Date"
              type="date"
              class="q-mb-sm"
            />
            <q-input
              v-model="extracted.suggested_category"
              outlined
              dense
              label="Category"
              class="q-mb-sm"
            />
            <q-input
              v-if="extracted.description"
              v-model="extracted.description"
              outlined
              dense
              autogrow
              label="Description"
              class="q-mb-sm"
            />

            <q-expansion-item
              v-if="extracted.raw_text"
              dense
              label="Raw scanned text"
              class="q-mt-sm"
            >
              <div class="raw-text">{{ extracted.raw_text }}</div>
            </q-expansion-item>
          </div>

          <div v-if="errorMessage" class="text-negative text-caption q-mt-sm">
            {{ errorMessage }}
          </div>

          <div class="row q-gutter-sm q-mt-md">
            <q-btn flat no-caps label="Retake" class="col" @click="reset" />
            <q-btn
              v-if="!extracted && !isProcessing"
              unelevated
              no-caps
              color="primary"
              label="Scan"
              class="col"
              @click="runScan"
            />
            <q-btn
              v-else
              unelevated
              no-caps
              color="primary"
              label="Use this"
              class="col"
              :disable="isProcessing || !extracted"
              @click="confirm"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const props = defineProps({
  modelValue: { type: Boolean, default: undefined },
})
const emit = defineEmits(['update:modelValue', 'scanned'])

const isOpen = computed({
  get: () => props.modelValue ?? true,
  set: (val) => emit('update:modelValue', val),
})

const fileInput = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)
const isProcessing = ref(false)
const extracted = ref(null)
const errorMessage = ref('')
const useAiScan = ref(false)

const isPdf = computed(() => selectedFile.value?.type === 'application/pdf')

function triggerFileInput() {
  fileInput.value?.click()
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  selectedFile.value = file
  errorMessage.value = ''
  extracted.value = null

  // PDFs can't be shown via q-img — only preview images.
  imagePreview.value = file.type === 'application/pdf' ? 'pdf' : URL.createObjectURL(file)

  // PDFs only work through the AI endpoint.
  if (file.type === 'application/pdf') useAiScan.value = true
}

async function runScan() {
  if (!selectedFile.value) return

  isProcessing.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  const endpoint = useAiScan.value ? '/ocr/scan-ai' : '/ocr/scan'

  try {
    const response = await api.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    extracted.value = { ...response.data }
  } catch (err) {
    const detail = err?.response?.data?.detail
    if (err?.response?.status === 422) {
      errorMessage.value = detail || 'Could not read this receipt. Try a clearer photo, or switch on AI Scan.'
    } else if (err?.response?.status === 503) {
      errorMessage.value = 'AI scan is temporarily unavailable. Try the regular scan instead.'
    } else {
      errorMessage.value = detail || 'Something went wrong scanning this receipt.'
    }
    console.error('OCR scan error:', err)
  } finally {
    isProcessing.value = false
  }
}

function reset() {
  selectedFile.value = null
  imagePreview.value = null
  extracted.value = null
  errorMessage.value = ''
  useAiScan.value = false
  if (fileInput.value) fileInput.value.value = ''
}

function confirm() {
  // Save scanned data to localStorage for AddExpensePage to pick up, and for
  // the dashboard to show a "just scanned" preview before the expense is saved.
  const scannedData = {
    title: extracted.value.title,
    amount: extracted.value.amount,
    date: extracted.value.date,
    suggested_category: extracted.value.suggested_category,
    description: extracted.value.description || '',
    raw_text: extracted.value.raw_text || '',
    scannedAt: Date.now()
  }
  localStorage.setItem('scannedReceiptData', JSON.stringify(scannedData))

  emit('scanned', { ...extracted.value })

  // Navigate to expense entry page
  router.push('/addexpense').catch(() => {
    router.push({ name: 'addexpense' }).catch(() => {})
  })
}

function close() {
  reset()

  if (props.modelValue === undefined) {
    router.back()
    return
  }

  isOpen.value = false
}
</script>

<style scoped>
.scanner-card {
  width: 100%;
  max-width: 420px;
  border-radius: 20px;
}

.capture-zone {
  border: 2px dashed #b9c6e0;
  border-radius: 16px;
  padding: 40px 16px;
  text-align: center;
  cursor: pointer;
}

.capture-text {
  font-size: 13px;
  color: #5b6472;
  margin-top: 10px;
}

.hidden-input {
  display: none;
}

.preview-img {
  border-radius: 12px;
  max-height: 220px;
}

.pdf-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #eef0f4;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  color: #374151;
}

.raw-text {
  font-size: 11px;
  color: #6b7280;
  white-space: pre-wrap;
  max-height: 120px;
  overflow-y: auto;
}
</style>