<template>
  <q-page class="mk-page flex flex-center">
    <div class="mk-shell">
      <!-- Brand -->
      <div class="mk-brand">
        <div class="mk-logo">
          <q-icon name="account_balance_wallet" size="28px" color="white" />
        </div>
        <div class="mk-title">Mero Kharcha</div>
        <div class="mk-subtitle">Your personal financial companion for mindful spending.</div>
      </div>

      <!-- Login Card -->
      <q-form @submit="onSubmit" class="mk-card q-pa-md">
        <div class="mk-card-header">
          <div class="mk-card-title">Welcome Back</div>
          <div class="mk-card-desc">Sign in to continue your growth journey.</div>
        </div>

        <div class="q-gutter-md">
          <!-- Email -->
          <div>
            <div class="mk-label">EMAIL ADDRESS</div>
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
            <div class="mk-label">PASSWORD</div>
            <q-input
              v-model="password"
              dense
              outlined
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter your password"
              class="mk-input"
              :rules="[val => !!val || 'Password is required']"
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
          </div>

          <!-- Remember & Forgot -->
          <div class="row items-center justify-between">
  <q-checkbox v-model="remember" dense label="Remember me" class="mk-remember" />
  
  <!-- Changed from a span with an emit to a proper RouterLink -->
  <router-link to="/reset-password" class="mk-link text-teal text-weight-medium cursor-pointer" style="text-decoration: none;">
    Forgot Password?
  </router-link>
</div>

          <!-- Submit -->
          <q-btn
            unelevated
            no-caps
            class="mk-cta"
            label="Sign In"
            icon-right="arrow_forward"
            :disable="!isValid || isLoading"
            :loading="isLoading"
            type="submit"
          />

          <!-- Divider -->
          <div class="mk-divider-row">
            <div class="mk-divider-line" />
            <div class="mk-divider-text">OR CONTINUE WITH</div>
            <div class="mk-divider-line" />
          </div>

          <!-- Social buttons -->
          <div class="row q-col-gutter-sm">
            <div class="col-6">
              <q-btn
                outline
                no-caps
                class="mk-social-btn"
                @click="emit('login-google')"
                :disable="isLoading"
              >
                <q-icon name="fab fa-google" size="18px" class="q-mr-sm" color="red-6" />
                Google
              </q-btn>
            </div>
            <div class="col-6">
              <q-btn
                outline
                no-caps
                class="mk-social-btn"
                @click="emit('login-facebook')"
                :disable="isLoading"
              >
                <q-icon name="fab fa-facebook" size="18px" class="q-mr-sm" color="blue-8" />
                Facebook
              </q-btn>
            </div>
          </div>
        </div>
      </q-form>

      <!-- Footer link -->
      <div class="text-center mk-footer-link-wrap">
        Don't have an account?
        <!-- <span class="mk-link" @click="emit('go-signup')">Sign up for free</span> -->
         <router-link to="/" class="mk-link text-teal text-weight-bold cursor-pointer" style="text-decoration: none;">
  Sign up for free
</router-link>
      </div>

      <!-- Page Footer -->
      <div class="mk-footer">
        <div class="mk-footer-links">
          <span class="mk-link-muted">Privacy Policy</span>
          <span class="mk-dot">&bull;</span>
          <span class="mk-link-muted">Terms of Service</span>
        </div>
        <div class="mk-footer-brand">by Bug Creator &bull; 2083 B.S.</div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, defineEmits, defineExpose } from 'vue'

const emit = defineEmits([
  'go-reset',
  'go-signup',
  'login-google',
  'login-facebook',
  'submit'
])

// Form fields
const email = ref('')
const password = ref('')
const remember = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)

// Validation state
const isValid = computed(() => {
  return (
    email.value.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) &&
    password.value.trim() !== ''
  )
})

// Submit handler
async function onSubmit() {
  if (!isValid.value) return
  isLoading.value = true
  try {
    emit('submit', {
      email: email.value,
      password: password.value,
      remember: remember.value
    })
    // Optionally reset after successful submission (handled by parent)
  } catch (error) {
    // Handle error (e.g., show a notification)
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

// Expose reset method
function resetForm() {
  email.value = ''
  password.value = ''
  remember.value = false
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
  max-width: 380px;
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

.mk-card-desc {
  font-size: 14px;
  color: var(--mk-muted);
  margin-top: 2px;
}

.mk-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #6b7280;
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

.mk-remember :deep(.q-checkbox__label) {
  font-size: 13px;
  color: #4b5563;
}

.mk-link {
  color: var(--mk-green);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s;
}

.mk-link:hover {
  color: var(--mk-green-dark);
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

.mk-divider-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0 4px;
}

.mk-divider-line {
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}

.mk-divider-text {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #9ca3af;
  white-space: nowrap;
}

.mk-social-btn {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  color: #374151;
  font-weight: 500;
  font-size: 13px;
  padding: 10px 0;
  transition: background 0.2s, border-color 0.2s;
}

.mk-social-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.mk-social-btn:active {
  transform: scale(0.97);
}

.mk-footer-link-wrap {
  font-size: 14px;
  color: #6b7280;
  margin-top: 20px;
}

.mk-footer {
  text-align: center;
  margin-top: 20px;
}

.mk-link-muted {
  color: #9ca3af;
  font-size: 11px;
  cursor: pointer;
}

.mk-dot {
  color: #d1d5db;
  margin: 0 8px;
}

.mk-footer-brand {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 6px;
}
</style>