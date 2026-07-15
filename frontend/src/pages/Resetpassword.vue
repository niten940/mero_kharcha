<template>
  <q-page class="mk-page flex flex-center">
    <div class="mk-shell">
      <!-- Back -->
     <router-link to="/login" class="mk-back flex items-center q-gutter-xs text-teal" style="text-decoration: none; cursor: pointer;">
  <q-icon name="arrow_back" size="18px" />
  <span>Back</span>
</router-link>

      <!-- Brand -->
      <div class="mk-brand">
        <div class="mk-logo">
          <q-icon name="lock_reset" size="26px" color="white" />
        </div>
        <div class="mk-title">Mero Kharcha</div>
      </div>

      <!-- Card -->
      <q-card flat class="mk-card">
        <q-card-section>
          <div class="mk-card-title">Reset Password</div>
          <div class="mk-card-desc">
            Enter your email address and we will send you a link to reset your password.
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md q-pt-none">
          <div>
            <div class="mk-label">Email Address</div>
            <q-input
              v-model="email"
              dense
              outlined
              type="email"
              placeholder="yourname@domain.com"
              class="mk-input"
            >
              <template #prepend>
                <q-icon name="mail_outline" size="20px" />
              </template>
            </q-input>
          </div>

          <q-btn
            unelevated
            no-caps
            class="mk-cta"
            label="Send Reset Link"
            icon-right="send"
            @click="onSend"
          />

          <!-- <div class="text-center">
            <span class="mk-link" @click="$emit('go-login')">
              <q-icon name="arrow_back" size="14px" class="q-mr-xs" />
              Back to Login
            </span>
          </div> -->
        </q-card-section>
      </q-card>

      <!-- Illustration panel -->
      <div class="mk-illustration">
        <svg viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg" class="mk-illustration-svg">
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#eaf3ee" />
              <stop offset="100%" stop-color="#cfe4d6" />
            </linearGradient>
            <radialGradient id="sunGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#fff6d9" />
              <stop offset="100%" stop-color="#f4d878" />
            </radialGradient>
          </defs>
          <rect x="0" y="0" width="320" height="170" fill="url(#skyGrad)" />
          <circle cx="235" cy="45" r="26" fill="url(#sunGrad)" opacity="0.9" />
          <path d="M0 130 Q60 95 130 120 T320 105 V170 H0 Z" fill="#8fbfa0" opacity="0.55" />
          <path d="M0 150 Q80 120 160 145 T320 130 V170 H0 Z" fill="#5f9d78" opacity="0.7" />
          <path d="M0 165 Q90 140 180 160 T320 150 V170 H0 Z" fill="#3a7a58" />
          <g transform="translate(148,58)" stroke="#c99a3a" stroke-width="3" fill="none" stroke-linecap="round">
            <circle cx="12" cy="12" r="11" />
            <line x1="20" y1="20" x2="42" y2="42" />
            <line x1="34" y1="34" x2="42" y2="26" />
            <line x1="38" y1="38" x2="46" y2="30" />
          </g>
        </svg>
        <div class="mk-illustration-label">Forgot Password</div>
      </div>

      <div class="mk-footer">
        <div class="mk-footer-brand">by Bug Creator &bull; 2083 B.S.</div>
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
import { ref } from 'vue'

const emit = defineEmits(['go-login', 'submit'])

const email = ref('')

function onSend () {
  emit('submit', { email: email.value })
}
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
  max-width: 360px;
}

.mk-back {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--mk-green);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 12px;
}

.mk-brand {
  text-align: center;
  margin-bottom: 16px;
}

.mk-logo {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  box-shadow: 0 6px 16px rgba(15, 107, 70, 0.28);
}

.mk-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--mk-green);
}

.mk-card {
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(20, 30, 25, 0.06);
  margin-bottom: 18px;
}

.mk-card-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--mk-text);
}

.mk-card-desc {
  font-size: 13px;
  color: var(--mk-muted);
  margin-top: 6px;
  line-height: 1.5;
}

.mk-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.mk-input :deep(.q-field__control) {
  border-radius: 10px;
}

.mk-cta {
  width: 100%;
  background: linear-gradient(160deg, var(--mk-green), var(--mk-green-dark));
  color: #fff;
  border-radius: 12px;
  font-weight: 600;
  padding: 12px 0;
  font-size: 15px;
}

.mk-link {
  color: var(--mk-green);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.mk-illustration {
  border-radius: 18px;
  overflow: hidden;
  background: #dcebe1;
  position: relative;
}

.mk-illustration-svg {
  display: block;
  width: 100%;
  height: auto;
}

.mk-illustration-label {
  position: absolute;
  top: 10px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #2f4c3b;
}

.mk-footer {
  text-align: center;
  margin-top: 18px;
}

.mk-footer-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #9ca3af;
}

.mk-link-muted {
  color: #9ca3af;
  font-size: 11px;
  cursor: pointer;
}

.mk-dot {
  color: #d1d5db;
  margin: 0 6px;
  font-size: 11px;
}

.mk-footer-links {
  margin-top: 6px;
}
</style>