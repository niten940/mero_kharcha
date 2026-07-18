<template>
  <q-page class="mk-page flex flex-center">
    <div class="mk-shell">
      <div class="mk-brand">
        <h1 class="mk-title">Mero Kharcha</h1>
        <p class="mk-subtitle">Your financial companion for the journey ahead.</p>
      </div>

      <q-form @submit="onSubmit" class="mk-card bg-white">
        <div class="mk-card-header text-center">
          <h2 class="mk-card-title">Welcome Dear User</h2>
        </div>

        <div class="q-gutter-y-md mk-form-body">
          <!-- Full Name -->
          <!-- <div>
            <div class="mk-label">Full Name</div>
            <q-input
              v-model="fullName"
              dense
              outlined
              placeholder="Aayush Shreshta"
              class="mk-input"
              :rules="[val => !!val || 'Full Name is required']"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="person_outline" size="20px" class="text-grey-6" />
              </template>
            </q-input>
          </div> -->

          <!-- Email Address -->
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
                <q-icon name="mail_outline" size="20px" class="text-grey-6" />
              </template>
            </q-input>
          </div>

          <!-- Password with Inline Forgot Option -->
          <div>
            <div class="row justify-between items-center q-mb-xs">
              <div class="mk-label q-mb-none">Password</div>
              <router-link to="/reset-password" class="mk-forgot-link">Forgot Password?</router-link>
            </div>
            <q-input
              v-model="password"
              dense
              outlined
              :type="showPassword ? 'text' : 'password'"
              placeholder="Enter a secure password"
              class="mk-input"
              :rules="[val => !!val || 'Password is required']"
              lazy-rules
            >
              <template #prepend>
                <q-icon name="lock_outline" size="20px" class="text-grey-6" />
              </template>
              <template #append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  size="20px"
                  class="cursor-pointer text-grey-6"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>
          </div>

          <!-- Terms Agreement Checkbox -->
          <div class="row items-center mk-terms-wrapper">
            <q-checkbox 
              v-model="agreeTerms" 
              dense 
              class="mk-checkbox" 
              :rules="[val => val === true || 'You must agree to the terms']"
            />
            <span class="mk-terms-text q-ml-sm">
              I agree to the 
              <router-link to="/terms" class="mk-inline-link">Terms</router-link> 
              and 
              <router-link to="/privacy" class="mk-inline-link">Privacy Policy</router-link>
            </span>
          </div>

          <!-- Standard Submit CTA Button -->
          <div class="q-pt-xs">
            <q-btn
              unelevated
              no-caps
              class="mk-cta"
              label="Log In"
              icon-right="arrow_forward"
              :disable="!isValid || isLoading"
              :loading="isLoading"
              type="submit"
            />
          </div>

          <!-- Visual Separation Section Divider -->
          <div class="row items-center q-my-sm">
            <q-separator class="col" />
            <span class="q-px-sm text-caption text-grey-5 text-weight-medium">OR</span>
            <q-separator class="col" />
          </div>

          <!-- Google OAuth Alternate Provider Action Button -->
          <div>
            <q-btn
              outline
              no-caps
              class="mk-google-btn"
              @click="onGoogleSignUp"
            >
              <div class="row items-center justify-center full-width">
                <svg class="q-mr-sm" width="18" height="18" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v3.92h6.69c-.29 1.5-1.14 2.77-2.4 3.61v3h3.86c2.26-2.09 3.59-5.17 3.59-8.46z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96H1.21v3.11C3.18 21.88 7.31 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.27 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.6H1.21C.44 8.13 0 9.85 0 11.7s.44 3.57 1.21 5.1l4.06-3.11z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.18 2.12 1.21 5.7L5.27 8.8c.95-2.85 3.6-4.95 6.73-4.95z"/>
                </svg>
                <span>Sign up with Google</span>
              </div>
            </q-btn>
          </div>

          <!-- Foot Navigation Link Toggle -->
          <div class="text-center mk-toggle-wrap q-pt-xs">
            <router-link to="/" class="mk-toggle-link">create new account</router-link>
          </div>
        </div>
      </q-form>

      <div class="mk-footer">
        <div class="mk-footer-brand">BY BUG CREATOR &bull; 2083 B.S.</div>
        <div class="mk-footer-links q-mt-xs">
          <router-link to="/privacy" class="mk-link-muted">Privacy Policy</router-link>
          <span class="mk-dot">&bull;</span>
          <router-link to="/terms" class="mk-link-muted">Terms of Service</router-link>
        </div>
      </div>
    </div>
  </q-page>
</template>

<!-- <script setup>
import { ref, computed, defineEmits, defineExpose } from 'vue'

const emit = defineEmits(['submit'])

// Form fields matching the Mockup Sign-up Flow
const fullName = ref('')
const email = ref('')
const password = ref('')
const agreeTerms = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)

// Precise validation state checks
const isValid = computed(() => {
  return (
    fullName.value.trim() !== '' &&
    email.value.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) &&
    password.value.trim() !== '' &&
    agreeTerms.value === true
  )
})

// Submit handler
async function onSubmit() {
  if (!isValid.value) return
  isLoading.value = true
  try {
    emit('submit', {
      fullName: fullName.value,
      email: email.value,
      password: password.value
    })
  } catch (error) {
    console.error('Registration error:', error)
  } finally {
    isLoading.value = false
  }
}

// Google OAuth Authorization Redirection
function onGoogleSignUp() {
  // 1. Replace with your actual credentials from Google Cloud Console
  const clientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com' 
  
  // 2. Where google should send the user back after successful login
  const redirectUri = window.location.origin + '/login' 
  
  const scope = 'openid profile email'
  const responseType = 'token' // 'token' for Implicit Grant flow, 'code' for Authorization Code flow
  
  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` + 
    `client_id=${clientId}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=${responseType}` +
    `&scope=${encodeURIComponent(scope)}` +
    `&prompt=select_account` // 👈 This forces the account chooser/email selection window

  // Execute external browser redirection
  window.location.href = googleAuthUrl
}

// Reset form exposed API method
function resetForm() {
  fullName.value = ''
  email.value = ''
  password.value = ''
  agreeTerms.value = false
  isLoading.value = false
}
defineExpose({ resetForm })
</script> -->
<script setup>
import { ref, computed, defineEmits, defineExpose } from 'vue'
import { useRouter } from 'vue-router' // 👈 1. Import Vue Router

const emit = defineEmits(['submit'])
const router = useRouter() // 👈 2. Initialize the router instance

// Form fields matching the Flow
const email = ref('')
const password = ref('')
const agreeTerms = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)

// Precise validation state checks (Removed fullName since it is commented out)
const isValid = computed(() => {
  return (
    email.value.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value) &&
    password.value.trim() !== '' &&
    agreeTerms.value === true
  )
})

// Submit handler
async function onSubmit() {
  if (!isValid.value) return
  isLoading.value = true
  try {
    emit('submit', {
      email: email.value,
      password: password.value
    })

    // 👈 3. Redirect to the dashboard route after submit succeeds
    await router.push('/dashboard') 
    
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

// Google OAuth Authorization Redirection
function onGoogleSignUp() {
  const clientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com' 
  const redirectUri = window.location.origin + '/login' 
  const scope = 'openid profile email'
  const responseType = 'token'
  
  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` + 
    `client_id=${clientId}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=${responseType}` +
    `&scope=${encodeURIComponent(scope)}` +
    `&prompt=select_account`

  window.location.href = googleAuthUrl
}

// Reset form exposed API method
function resetForm() {
  email.value = ''
  password.value = ''
  agreeTerms.value = false
  isLoading.value = false
}
defineExpose({ resetForm })
</script>
<style scoped>
/* Color tokens precisely sampled from your mock image */
.mk-page {
  --mk-bg: #f2f4f3;
  --mk-teal-primary: #528b75;
  --mk-teal-hover: #437361;
  --mk-text-dark: #121824;
  --mk-text-muted: #64748b;
  --mk-border-color: #cbd5e1;
  --mk-input-bg: #f8fafc;

  background-color: var(--mk-bg);
  min-height: 100vh;
  padding: 40px 16px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.mk-shell {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
}

/* Header branding classes */
.mk-brand {
  text-align: center;
  margin-bottom: 28px;
}

.mk-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--mk-text-dark);
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.mk-subtitle {
  font-size: 15px;
  color: var(--mk-text-muted);
  margin: 0;
  font-weight: 400;
}

/* Main Card styling matching exact structure */
.mk-card {
  border-radius: 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02), 0 20px 48px rgba(0, 0, 0, 0.04);
  padding: 36px 32px 28px;
  border: 1px solid rgba(0, 0, 0, 0.01);
}

.mk-card-header {
  margin-bottom: 24px;
}

.mk-card-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--mk-text-dark);
  margin: 0 0 4px 0;
  letter-spacing: -0.01em;
}

.mk-form-body {
  display: flex;
  flex-direction: column;
}

/* Input Fields styling overrides */
.mk-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.mk-forgot-link {
  font-size: 12px;
  font-weight: 600;
  color: var(--mk-teal-primary);
  text-decoration: none;
}

.mk-forgot-link:hover {
  text-decoration: underline;
}

.mk-input :deep(.q-field__control) {
  border-radius: 12px;
  background-color: var(--mk-input-bg);
  border: 1px solid var(--mk-border-color);
  transition: all 0.2s ease;
}

.mk-input :deep(.q-field__control:before),
.mk-input :deep(.q-field__control:after) {
  display: none;
}

.mk-input :deep(.q-field__control:hover) {
  border-color: #94a3b8;
}

.mk-input :deep(.q-field__control--focused) {
  border-color: var(--mk-teal-primary) !important;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(82, 139, 117, 0.15);
}

.mk-input :deep(.q-field__native) {
  font-size: 14px;
  color: var(--mk-text-dark);
  font-weight: 400;
}

.mk-input :deep(.q-field__bottom-row) {
  padding: 4px 0 0 4px;
}

/* Agreement checkbox classes */
.mk-terms-wrapper {
  font-size: 13px;
  color: #475569;
  line-height: 1.4;
}

.mk-checkbox :deep(.q-checkbox__inner) {
  color: var(--mk-border-color);
}
.mk-checkbox :deep(.q-checkbox__inner--active) {
  color: var(--mk-teal-primary);
}

.mk-inline-link {
  color: var(--mk-teal-primary);
  text-decoration: none;
  font-weight: 600;
}
.mk-inline-link:hover {
  text-decoration: underline;
}

/* Main Premium Action Button Call to Action */
.mk-cta {
  width: 100%;
  background: var(--mk-teal-primary);
  color: #ffffff;
  border-radius: 14px;
  font-weight: 600;
  padding: 12px 0;
  font-size: 15px;
  letter-spacing: 0.01em;
  transition: background-color 0.2s ease;
}

.mk-cta:not(:disabled):hover {
  background-color: var(--mk-teal-hover);
}

/* Google OAuth custom styling specifications */
.mk-google-btn {
  width: 100%;
  border-radius: 14px;
  border: 1px solid var(--mk-border-color);
  color: #334155;
  background-color: #ffffff;
  padding: 10px 0;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.mk-google-btn:hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

/* Log-in alternate routing footer wrapper */
.mk-toggle-wrap {
  font-size: 14px;
  color: var(--mk-text-muted);
  font-weight: 500;
}

.mk-toggle-link {
  color: var(--mk-teal-primary);
  text-decoration: none;
  font-weight: 700;
  margin-left: 2px;
}
.mk-toggle-link:hover {
  text-decoration: underline;
}

/* Bottom Page Branding Footer */
.mk-footer {
  text-align: center;
  margin-top: 32px;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #94a3b8;
}

.mk-footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.mk-link-muted {
  color: #94a3b8;
  font-size: 12px;
  text-decoration: none;
  transition: color 0.15s ease;
}
.mk-link-muted:hover {
  color: var(--mk-text-muted);
}

.mk-dot {
  color: var(--mk-border-color);
  font-size: 10px;
}
</style>