<template>
  <q-page class="mk-page">
    <div class="mk-shell">
      <!-- Header -->
      <div class="mk-header row items-center justify-between">
        <div class="row items-center mk-brand-row">
          <MeroKharchaLogo :size="10" />
        </div>
        <q-btn
          round
          flat
          dense
          icon="close"
          color="grey-8"
          @click="goBack"
        />
      </div>

      <!-- Content -->
      <div class="mk-content">
        <div class="question">What would you like to add?</div>

        <div class="option expense" @click="selectExpense">
          <div class="circle">
            <q-icon name="south" size="20px" />
          </div>
          <div class="option-title">Expense</div>
          <div class="option-subtitle">Record money spent</div>
        </div>

        <div class="option income" @click="selectIncome">
          <div class="circle">
            <q-icon name="north" size="20px" />
          </div>
          <div class="option-title">Income</div>
          <div class="option-subtitle">Log money received</div>
        </div>

        <div class="flex flex-center q-mt-lg">
          <q-btn
            no-caps
            unelevated
            class="scan-btn"
            icon="qr_code_scanner"
            label="Scan receipt"
            @click="selectScan"
          />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import MeroKharchaLogo from '@/components/MeroKharchaLogo.vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const router = useRouter()
const $q = useQuasar()

function goBack() {
  router.back()
}

function selectExpense() {
  router.push('/addexpense')
}

function selectIncome() {
  router.push('/setbudget')
}

function selectScan() {
  router.push('/receipt-scanner').catch(() => {
    router.push({ name: 'receipt-scanner' }).catch(() => {})
  })
}
</script>

<style scoped>
.mk-page {
  --mk-green: #0f6b46;
  --mk-text: #1c1c1c;
  background: #eef1f0;
  min-height: 100vh;
  padding-bottom: 20px;
}

.mk-shell {
  padding: 18px 16px;
  max-width: 400px;
  margin: 0 auto;
}

.mk-header {
  margin-bottom: 24px;
}

.mk-brand-row {
  gap: 10px;
}

.mk-content {
  padding: 0 8px;
}

.question {
  text-align: center;
  font-size: 21px;
  font-weight: 700;
  color: var(--mk-text);
  line-height: 1.35;
  margin: 6px 0 32px;
}

.option {
  background: #fff;
  border: 1.5px dashed #b9c6e0;
  border-radius: 16px;
  padding: 28px 16px;
  text-align: center;
  margin-bottom: 18px;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 2px 8px rgba(20, 30, 25, 0.04);
}

.option:hover {
  border-color: var(--mk-green);
  box-shadow: 0 4px 12px rgba(20, 30, 25, 0.08);
  transform: translateY(-2px);
}

.option .circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  font-size: 24px;
}

.option.expense .circle {
  background: #fbe9d2;
  color: #c98a2e;
}

.option.income .circle {
  background: #d7ecdf;
  color: var(--mk-green);
}

.option-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--mk-text);
  margin-bottom: 4px;
}

.option-subtitle {
  font-size: 13px;
  color: #9298a3;
}

.scan-btn {
  background: #e1f5ee;
  color: var(--mk-green);
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 13px;
  font-weight: 700;
  text-transform: none;
}

.scan-btn:hover {
  background: #d0f0eb;
}
</style>