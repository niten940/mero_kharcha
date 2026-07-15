<template>
  <q-page class="mk-page flex flex-center">
    <div class="mk-shell">
      <!-- Brand -->
      <div class="mk-brand">
        <h1 class="mk-title">Mero Kharcha</h1>
        <p class="mk-subtitle">Your financial companion for the journey ahead.</p>
      </div>

      <!-- Signup Card -->
      <q-form @submit="onSubmit" class="mk-card bg-white">
        <div class="mk-card-header text-center">
          <h2 class="mk-card-title">Start Your Journey</h2>
          <div class="mk-card-eyebrow">CREATE A NEW ACCOUNT</div>
        </div>

        <div class="q-gutter-y-md">
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
                <q-icon name="person_outline" size="20px" class="text-slate-4" />
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
                <q-icon name="mail_outline" size="20px" class="text-slate-4" />
              </template>
            </q-input>
          </div>

          <!-- Phone Number & Base Currency -->
          <div class="row q-col-gutter-x-md">
            <div class="col-8">
              <div class="mk-label">Phone Number</div>
              <q-input
                v-model="phone"
                dense
                outlined
                type="tel"
                placeholder="98XXXXXXXX"
                class="mk-input"
                :rules="[
                  val => !!val || 'Phone number is required',
                  val => /^\+?[0-9]{7,15}$/.test(val) || 'Enter a valid phone number'
                ]"
                lazy-rules
              >
                <template #prepend>
                  <q-icon name="phone" size="20px" class="text-slate-4" />
                </template>
              </q-input>
            </div>
            
            <div class="col-4">
              <div class="mk-label">Currency</div>
              <q-select
                v-model="currency"
                :options="currencyOptions"
                dense
                outlined
                emit-value
                map-options
                class="mk-input"
              />
            </div>
          </div>

          <!-- Nationality -->
          <div>
            <div class="mk-label">Nationality</div>
            <q-select
              v-model="nationality"
              :options="nationalityOptions"
              dense
              outlined
              use-input
              fill-input
              hide-selected
              input-debounce="0"
              @filter="filterNationality"
              placeholder="Select your country"
              class="mk-input"
              :rules="[val => !!val || 'Nationality is required']"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="public" size="20px" class="text-slate-4" />
              </template>
            </q-select>
          </div>

          <!-- Age & Gender -->
          <div class="row q-col-gutter-x-md">
            <div class="col-4">
              <div class="mk-label">Age</div>
              <q-input
                v-model.number="age"
                type="number"
                dense
                outlined
                placeholder="Ex: 25"
                class="mk-input"
                :rules="[
                  val => !!val || 'Required',
                  val => (val > 0 && val < 120) || 'Invalid age'
                ]"
                lazy-rules
              />
            </div>

            <div class="col-8">
              <div class="mk-label">Gender</div>
              <q-select
                v-model="gender"
                :options="genderOptions"
                dense
                outlined
                emit-value
                map-options
                placeholder="Select Gender"
                class="mk-input"
                :rules="[val => !!val || 'Gender is required']"
                lazy-rules
              >
                <template #prepend>
                  <q-icon name="wc" size="20px" class="text-slate-4" />
                </template>
              </q-select>
            </div>
          </div>

          <!-- Password with Advanced Strength Processing -->
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
                <q-icon name="lock_outline" size="20px" class="text-slate-4" />
              </template>
              <template #append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  size="20px"
                  class="cursor-pointer text-slate-4"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>

            <!-- Password Strength Indicator Component Wrapper -->
            <div v-if="password.length > 0" class="q-mt-xs">
              <q-linear-progress
                :value="passwordStrengthScore / 4"
                :color="strengthColor"
                track-color="grey-3"
                class="mk-strength-bar"
              />
              <div class="row justify-between items-center q-mt-xs">
                <span class="mk-strength-text" :class="`text-${strengthColor}`">
                  Strength: {{ strengthLabel }}
                </span>
                <span class="mk-pw-hint text-grey-6">Min. 8 chars, numbers & casing</span>
              </div>
            </div>
          </div>

          <!-- Confirm Password -->
          <div>
            <div class="mk-label">Confirm Password</div>
            <q-input
              v-model="confirmPassword"
              dense
              outlined
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="Re-enter your password"
              class="mk-input"
              :rules="[
                val => !!val || 'Please confirm your password',
                val => val === password || 'Passwords do not match'
              ]"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="lock_reset" size="20px" class="text-slate-4" />
              </template>
              <template #append>
                <q-icon
                  :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                  size="20px"
                  class="cursor-pointer text-slate-4"
                  @click="showConfirmPassword = !showConfirmPassword"
                />
              </template>
            </q-input>
          </div>

          <!-- Terms & Agreement Checkbox -->
          <div class="row items-center mk-terms-row">
            <q-checkbox v-model="agree" dense class="mk-checkbox" />
            <span class="mk-terms-text q-ml-sm">
              I agree to the
              <router-link to="/terms" class="mk-link">Terms</router-link>
              and
              <router-link to="/privacy" class="mk-link">Privacy Policy</router-link>
            </span>
          </div>

          <!-- Submit Button -->
          <div class="q-pt-sm">
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
          </div>

          <!-- Footer Switch Link -->
          <div class="text-center mk-footer-link q-pt-xs">
            Already have an account?
            <router-link to="/login" class="mk-link-action">Log In</router-link>
          </div>
        </div>
      </q-form>

      <!-- Page Footer -->
      <div class="mk-footer">
        <div class="mk-footer-brand">BY BUG CREATOR &bull; 2083 B.S.</div>
        <div class="mk-footer-links">
          <router-link to="/privacy" class="mk-link-muted">Privacy Policy</router-link>
          <span class="mk-dot">&bull;</span>
          <router-link to="/terms" class="mk-link-muted">Terms of Service</router-link>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const router = useRouter()
const $q = useQuasar()

// Form Fields
const fullName = ref('')
const email = ref('')
const phone = ref('')
const currency = ref('NPR')
const nationality = ref(null)
const age = ref(null)
const gender = ref(null)
const password = ref('')
const confirmPassword = ref('')
const agree = ref(false)

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)

// Selection Config Arrays
const currencyOptions = ['NPR', 'USD', 'INR', 'EUR', 'GBP']
const genderOptions = [
  { label: 'Male', value: 'male' },
  { label: 'Female', value: 'female' },
  { label: 'Other', value: 'other' }
]
const allCountries = ['Nepal', 'India', 'United States', 'United Kingdom', 'Australia', 'Canada', 'United Arab Emirates']
const nationalityOptions = ref(allCountries)

function filterNationality(val, update) {
  if (val === '') {
    update(() => { nationalityOptions.value = allCountries })
    return
  }
  update(() => {
    const needle = val.toLowerCase()
    nationalityOptions.value = allCountries.filter(v => v.toLowerCase().indexOf(needle) > -1)
  })
}

// Complex Multi-metric Password Strength Validation Check
const passwordStrengthScore = computed(() => {
  let score = 0
  const pass = password.value
  if (!pass || pass.length < 8) return 0
  
  if (/[A-Z]/.test(pass) && /[a-z]/.test(pass)) score++ // Casing verification
  if (/[0-9]/.test(pass)) score++                       // Numbers logic check
  if (/[^A-Za-z0-9]/.test(pass)) score++                // Special character validation
  if (pass.length >= 12) score++                        // Length structural weight
  
  return score === 0 ? 1 : score // If it hits length requirement but fails metrics, fallback score to 1
})

const strengthLabel = computed(() => {
  const score = passwordStrengthScore.value
  if (score === 0) return 'Too Short'
  if (score === 1) return 'Weak'
  if (score === 2) return 'Fair'
  if (score === 3) return 'Good'
  return 'Excellent'
})

const strengthColor = computed(() => {
  const score = passwordStrengthScore.value
  if (score === 0) return 'negative'
  if (score === 1) return 'deep-orange'
  if (score === 2) return 'warning'
  if (score === 3) return 'teal'
  return 'positive'
})

// Validation State matching safe patterns and blocking weak score thresholds (Score must be >= 2)
const isValid = computed(() => {
  return (
    fullName.value.trim() !== '' &&
    email.value.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) &&
    /^\+?[0-9]{7,15}$/.test(phone.value) &&
    !!nationality.value &&
    age.value > 0 &&
    !!gender.value &&
    password.value.length >= 8 &&
    passwordStrengthScore.value >= 2 && // Restrict submission if code falls under a 'Fair' evaluation threshold
    confirmPassword.value === password.value &&
    agree.value
  )
})

// Account Creation Submit Flow Handler with Notification and Redirection routing hooks
async function onSubmit() {
  if (!isValid.value) return
  isLoading.value = true
  
  try {
    // 1. Simulating your backend network request
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // 2. Trigger the notification immediately
    $q.notify({
      type: 'positive',
      icon: 'check_circle',
      message: 'Account Created Successfully!',
      caption: 'Please log in to verify your registration details.',
      position: 'top',
      timeout: 4000
    })

    // 3. Pause for 800ms so the user can actually process the notification
    await new Promise((resolve) => setTimeout(resolve, 800))

    // 4. Smoothly route them over to the verification/login view
    router.push('/login')
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to create account. Please try again.',
      position: 'top'
    })
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

</script>

<style scoped>
.mk-page {
  --mk-teal: #528b75;
  --mk-teal-dark: #3f6c5a;
  --mk-text-dark: #1e293b;
  --mk-text-muted: #64748b;
  --mk-border: #cbd5e1;
  --mk-bg-grey: #f8fafc;
  
  background: #f1f5f9;
  min-height: 100vh;
  padding: 48px 16px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.mk-shell {
  width: 100%;
  max-width: 460px;
  margin: 0 auto;
}

.mk-brand {
  text-align: center;
  margin-bottom: 24px;
}

.mk-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--mk-text-dark);
  margin: 0 0 4px 0;
  letter-spacing: -0.025em;
}

.mk-subtitle {
  font-size: 14px;
  color: var(--mk-text-muted);
  margin: 0;
}

.mk-card {
  border-radius: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  padding: 36px 32px 28px;
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.mk-card-header {
  margin-bottom: 24px;
}

.mk-card-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--mk-text-dark);
  margin: 0 0 2px 0;
}

.mk-card-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.mk-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.mk-input :deep(.q-field__control) {
  border-radius: 12px;
  background-color: var(--mk-bg-grey);
  border: 1px solid var(--mk-border);
  transition: all 0.2s ease-in-out;
}

.mk-input :deep(.q-field__control:before),
.mk-input :deep(.q-field__control:after) {
  display: none !important;
}

.mk-input :deep(.q-field__control:hover) {
  border-color: #94a3b8;
}

.mk-input :deep(.q-field__control--focused) {
  border-color: var(--mk-teal) !important;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(82, 139, 117, 0.15);
}

.mk-input :deep(.q-field__native) {
  font-size: 14px;
  color: var(--mk-text-dark);
}

.mk-input :deep(.q-field__bottom-row) {
  padding: 4px 0 0 4px;
}

.text-slate-4 {
  color: #94a3b8;
}

/* Password Strength custom elements styling */
.mk-strength-bar {
  border-radius: 4px;
  height: 4px;
}

.mk-strength-text {
  font-size: 12px;
  font-weight: 700;
}

.mk-pw-hint {
  font-size: 11px;
}

.mk-terms-row {
  align-items: center;
  font-size: 13px;
  color: #475569;
  line-height: 1.4;
}

.mk-checkbox :deep(.q-checkbox__inner) {
  color: var(--mk-border);
}

.mk-checkbox :deep(.q-checkbox__inner--active) {
  color: var(--mk-teal);
}

.mk-link {
  color: var(--mk-teal);
  text-decoration: none;
  font-weight: 600;
}

.mk-link:hover {
  text-decoration: underline;
}

.mk-cta {
  width: 100%;
  background: var(--mk-teal);
  color: #ffffff;
  border-radius: 14px;
  font-weight: 600;
  padding: 12px 0;
  font-size: 15px;
  transition: background-color 0.2s ease;
}

.mk-cta:not(:disabled):hover {
  background-color: var(--mk-teal-dark);
}

.mk-footer-link {
  font-size: 14px;
  color: var(--mk-text-muted);
  font-weight: 500;
}

.mk-link-action {
  color: var(--mk-teal);
  text-decoration: none;
  font-weight: 700;
  margin-left: 3px;
}

.mk-link-action:hover {
  text-decoration: underline;
}

.mk-footer {
  text-align: center;
  margin-top: 32px;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.mk-footer-links {
  margin-top: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.mk-link-muted {
  color: #94a3b8;
  font-size: 12px;
  text-decoration: none;
}

.mk-link-muted:hover {
  color: var(--mk-text-muted);
}

.mk-dot {
  color: var(--mk-border);
  font-size: 10px;
}
</style>