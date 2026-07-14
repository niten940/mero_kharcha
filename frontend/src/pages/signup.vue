<template>
  <q-page class="mk-page flex flex-center">
    <div class="mk-shell">
      <!-- Brand -->
      <div class="mk-brand">
        <!-- <div class="mk-logo">
          <q-icon name="account_balance_wallet" size="28px" color="white" />
        </div> -->
        <div class="mk-title">Mero Kharcha</div>
        <div class="mk-subtitle">Your financial companion for the journey ahead.</div>
      </div>

      <!-- Signup Card -->
      <q-form @submit="onSubmit" class="mk-card q-pa-md">
        <div class="mk-card-header">
          <div class="mk-card-title">Start Your Journey</div>
          <div class="mk-card-eyebrow">CREATE A NEW ACCOUNT</div>
        </div>

        <div class="q-gutter-md">
          <!-- Full Name -->
          <div>
            <div class="mk-label">Full Name</div>
            <q-input
              v-model="fullName"
              dense
              outlined
              placeholder="Aayush Shrestha"
              class="mk-input"
              :rules="[val => !!val || 'Full name is required']"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="person_outline" size="20px" />
              </template>
            </q-input>
          </div>

          <!-- Email -->
          <div>
            <div class="mk-label">Email Address</div>
            <q-input
              v-model="email"
              dense
              outlined
              type="email"
              placeholder="name@example.com"
              class="mk-input"
              :rules="[
                val => !!val || 'Email is required',
                val => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) || 'Please enter a valid email'
              ]"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="mail_outline" size="20px" />
              </template>
            </q-input>
          </div>

          <!-- Password -->
          <div>
            <div class="mk-label">Password</div>
            <q-input
              v-model="password"
              dense
              outlined
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter a secure password"
              class="mk-input"
              :rules="[
                val => !!val || 'Password is required',
                val => val.length >= 8 || 'Password must be at least 8 characters'
              ]"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="lock_outline" size="20px" />
              </template>
              <template #append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  size="20px"
                  class="cursor-pointer"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>
            <!-- Optional strength hint -->
            <div class="mk-pw-hint" v-if="password.length > 0">
              <span v-if="password.length < 8"> Use at least 8 characters</span>
              <span v-else> Secured Password </span>
            </div>
          </div>

          <!-- Terms -->
          <q-checkbox v-model="agree" dense class="mk-checkbox">
            <span class="mk-terms-text">
              I agree to the
              <span class="mk-link">Terms</span>
              and
              <span class="mk-link">Privacy Policy</span>
            </span>
          </q-checkbox>

          <!-- Submit -->
          <q-btn
            unelevated
            no-caps
            class="mk-cta"
            label="Create Account"
            icon-right="arrow_forward"
            :disable="!isValid || isLoading"
            :loading="isLoading"
            type="submit"
          />

         <!-- Footer link -->
<div class="text-center mk-footer-link">
  Already have an account?
  <!-- RouterLink automatically hooks into your router configurations -->
  <router-link to="/login" class="mk-link text-teal text-weight-bold cursor-pointer" style="text-decoration: none;">
    Log In
  </router-link>
</div>
</div>
</q-form>

      <!-- Page Footer -->
      <div class="mk-footer">
        <div class="mk-footer-brand">BY BUG CREATOR &bull; 2083 B.S.</div>
        <div class="mk-footer-links">
          <span class="mk-link-muted">Privacy Policy</span>
          <span class="mk-dot">&bull;</span>
          <span class="mk-link-muted">Terms of Service</span>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, defineEmits, defineExpose } from 'vue'

const emit = defineEmits(['go-login', 'submit'])

// Form fields
const fullName = ref('')
const email = ref('')
const password = ref('')
const agree = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)

// Validation state
const isValid = computed(() => {
  return (
    fullName.value.trim() !== '' &&
    email.value.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) &&
    password.value.length >= 8 &&
    agree.value
  )
})

// Submit handler
async function onSubmit() {
  if (!isValid.value) return
  isLoading.value = true
  try {
    // Emit the form data to parent
    emit('submit', {
      fullName: fullName.value,
      email: email.value,
      password: password.value,
      agree: agree.value
    })
    // Optionally reset after a successful submission (handled by parent)
  } catch (error) {
    // Handle error (e.g., show a notification)
    console.error('Signup error:', error)
  } finally {
    isLoading.value = false
  }
}

// Expose a reset method if needed
function resetForm() {
  fullName.value = ''
  email.value = ''
  password.value = ''
  agree.value = false
  isLoading.value = false
}
defineExpose({ resetForm })
</script>

<style scoped>
.mk-page {
  --mk-green: #0f6b46;
  --mk-green-dark: #0b5637;
  --mk-text: #1c1c1c;
  --mk-muted: #6b7280;
  background: linear-gradient(180deg, #f3f5f4 0%, #eef1f0 100%);
  min-height: 100vh;
  padding: 24px 16px;
}

.mk-shell {
  width: 100%;
  max-width: 380px; /* slightly wider for better readability */
  margin: 0 auto;
}

.mk-brand {
  text-align: center;
  margin-bottom: 24px;
}

.mk-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 8px 20px rgba(15, 107, 70, 0.3);
}

.mk-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-subtitle {
  font-size: 14px;
  color: var(--mk-muted);
  margin-top: 4px;
  line-height: 1.4;
}

.mk-card {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.05);
  padding: 8px 0 4px;
}

.mk-card-header {
  padding: 8px 0 4px;
}

.mk-card-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-card-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.mk-input :deep(.q-field__control) {
  border-radius: 12px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  transition: border-color 0.2s;
}

.mk-input :deep(.q-field__control:hover) {
  border-color: #d1d5db;
}

.mk-input :deep(.q-field__control--focused) {
  border-color: var(--mk-green) !important;
}

.mk-input :deep(.q-field__native) {
  padding: 4px 0;
}

.mk-pw-hint {
  font-size: 12px;
  color: var(--mk-muted);
  margin-top: 4px;
}

.mk-checkbox {
  align-items: flex-start;
  margin: 8px 0 4px;
}

.mk-terms-text {
  font-size: 13px;
  color: #4b5563;
}

.mk-link {
  color: var(--mk-green);
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s;
}

.mk-link:hover {
  color: var(--mk-green-dark);
}

.mk-link-muted {
  color: #9ca3af;
  font-size: 12px;
  cursor: pointer;
}

.mk-dot {
  color: #d1d5db;
  margin: 0 8px;
}

.mk-cta {
  width: 100%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  border-radius: 14px;
  font-weight: 600;
  padding: 14px 0;
  font-size: 16px;
  transition: transform 0.15s, box-shadow 0.2s;
}

.mk-cta:not(:disabled):hover {
  transform: scale(1.01);
  box-shadow: 0 6px 16px rgba(15, 107, 70, 0.3);
}

.mk-cta:disabled {
  opacity: 0.6;
}

.mk-footer-link {
  font-size: 14px;
  color: #6b7280;
  margin-top: 8px;
}

.mk-footer {
  text-align: center;
  margin-top: 24px;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #9ca3af;
}

.mk-footer-links {
  margin-top: 6px;
  display: flex;
  justify-content: center;
  gap: 8px;
}
</style>