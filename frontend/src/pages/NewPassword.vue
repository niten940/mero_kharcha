<template>
  <q-page class="reset-page flex flex-center">
    <div class="reset-card-wrap">
      <q-btn
        round
        outline
        color="primary"
        icon="arrow_back"
        class="back-btn"
        @click="$router.back()"
      />

      <div class="icon-badge">
        <q-icon name="lock_reset" size="28px" color="white" />
      </div>

      <div class="text-h6 text-weight-bold text-center title-text">
        Reset Password
      </div>
      <div class="text-center subtitle-text">
        Choose a strong password to protect your account.
      </div>

      <q-card flat class="form-card">
        <q-card-section>
          <div class="field-label">New Password</div>
          <q-input
            v-model="newPassword"
            :type="showNew ? 'text' : 'password'"
            outlined
            dense
            placeholder="Enter new password"
            class="pw-input"
          >
            <template #prepend>
              <q-icon name="lock" size="18px" color="grey-5" />
            </template>
            <template #append>
              <q-icon
                :name="showNew ? 'visibility' : 'visibility_off'"
                size="18px"
                color="grey-5"
                class="cursor-pointer"
                @click="showNew = !showNew"
              />
            </template>
          </q-input>

          <div class="strength-row">
            <q-linear-progress
              :value="strengthScore"
              :color="strengthColor"
              track-color="grey-3"
              rounded
              size="6px"
              class="q-mb-xs"
            />
            <div class="text-right strength-label" :style="{ color: strengthHex }">
              {{ strengthLabel }}
            </div>
          </div>

          <div
            v-for="req in requirements"
            :key="req.label"
            class="req-row"
            :class="{ done: req.met }"
          >
            <div class="req-dot">
              <q-icon v-if="req.met" name="check" size="10px" color="white" />
            </div>
            <span :class="req.met ? 'text-dark' : 'text-grey-5'">{{ req.label }}</span>
          </div>

          <div class="field-label q-mt-md">Confirm Password</div>
          <q-input
            v-model="confirmPassword"
            :type="showConfirm ? 'text' : 'password'"
            outlined
            dense
            placeholder="Re-enter password"
            class="pw-input"
            :error="!!confirmPassword && confirmPassword !== newPassword"
            error-message="Passwords don't match"
          >
            <template #prepend>
              <q-icon name="lock" size="18px" color="grey-5" />
            </template>
            <template #append>
              <q-icon
                :name="showConfirm ? 'visibility' : 'visibility_off'"
                size="18px"
                color="grey-5"
                class="cursor-pointer"
                @click="showConfirm = !showConfirm"
              />
            </template>
          </q-input>

          <q-btn
            unelevated
            no-caps
            class="update-btn q-mt-md"
            label="Update Password"
            icon-right="arrow_forward"
            :disable="!canSubmit"
            :loading="submitting"
            @click="onSubmit"
          />
        </q-card-section>
      </q-card>

      <div class="footer-links">
        <span>Privacy Policy</span>
        <span class="dot-sep">&bull;</span>
        <span>Terms of Service</span>
      </div>
      <div class="footer-brand">by Bug Creator &bull; 2083 B.S.</div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

const newPassword = ref('')
const confirmPassword = ref('')
const showNew = ref(false)
const showConfirm = ref(false)
const submitting = ref(false)

const emit = defineEmits(['password-updated'])

const requirements = computed(() => [
  { label: 'At least 8 characters', met: newPassword.value.length >= 8 },
  { label: 'One special character (!@#$%)', met: /[!@#$%^&*]/.test(newPassword.value) },
])

const strengthScore = computed(() => {
  const metCount = requirements.value.filter((r) => r.met).length
  if (newPassword.value.length === 0) return 0
  return metCount / requirements.value.length
})

const strengthLabel = computed(() => {
  if (newPassword.value.length === 0) return ''
  if (strengthScore.value >= 1) return 'Strong'
  if (strengthScore.value >= 0.5) return 'Weak'
  return 'Too short'
})

const strengthColor = computed(() => {
  if (strengthScore.value >= 1) return 'positive'
  if (strengthScore.value >= 0.5) return 'warning'
  return 'negative'
})

const strengthHex = computed(() => {
  if (strengthScore.value >= 1) return '#0f6e56'
  if (strengthScore.value >= 0.5) return '#e29b2e'
  return '#d85a30'
})

const canSubmit = computed(() =>
  requirements.value.every((r) => r.met) &&
  confirmPassword.value.length > 0 &&
  confirmPassword.value === newPassword.value
)

async function onSubmit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    emit('password-updated', newPassword.value)
    $q.notify({ type: 'positive', message: 'Password updated' })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.reset-page {
  background: #eceef4;
  background-image: radial-gradient(circle, #d9dbe3 1px, transparent 1px);
  background-size: 16px 16px;
}

.reset-card-wrap {
  width: 100%;
  max-width: 360px;
  padding: 28px 20px;
}

.back-btn {
  border-style: dashed;
}

.icon-badge {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #0f6e56;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px auto 18px;
}

.title-text {
  color: #0b5d45;
  font-size: 22px;
}

.subtitle-text {
  color: #5b6472;
  font-size: 13.5px;
  line-height: 1.4;
  padding: 0 12px;
  margin-bottom: 22px;
}

.form-card {
  border-radius: 20px;
  box-shadow: 0 10px 24px rgba(20, 30, 60, 0.06);
}

.field-label {
  font-size: 12px;
  color: #9298a3;
  margin-bottom: 8px;
}

.pw-input {
  margin-bottom: 4px;
}

.pw-input :deep(.q-field__control) {
  border-radius: 12px;
}

.strength-row {
  margin: 10px 0 14px;
}

.strength-label {
  font-size: 11.5px;
  font-weight: 600;
}

.req-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 6px;
}

.req-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 1.5px solid #c9cdd4;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.req-row.done .req-dot {
  background: #0f6e56;
  border-color: #0f6e56;
}

.update-btn {
  width: 100%;
  background: #0f6e56;
  color: #fff;
  border-radius: 14px;
  padding: 12px;
  font-weight: 700;
  font-size: 15px;
}

.footer-links {
  text-align: center;
  font-size: 11.5px;
  color: #9298a3;
  margin-top: 20px;
}

.dot-sep {
  margin: 0 6px;
}

.footer-brand {
  text-align: center;
  font-size: 11px;
  color: #a8adb8;
  margin-top: 8px;
}
</style>