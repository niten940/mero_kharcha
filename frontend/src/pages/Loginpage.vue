<template>
  <q-page class="mk-login-page row items-center justify-center">
    <div class="mk-login-card">
      <!-- Header / Logo -->
      <div class="text-center q-mb-lg">
        <q-avatar size="56px" class="mk-logo-avatar q-mb-sm">
          <q-icon name="account_balance_wallet" size="32px" color="white" />
        </q-avatar>
        <div class="text-h5 text-weight-bold text-teal-10">Mero Kharcha</div>
        <div class="text-caption text-grey-7">Welcome back! Please login to your account.</div>
      </div>

      <!-- Error Alert -->
      <q-banner v-if="errorMessage" class="bg-red-1 text-red-9 rounded-borders q-mb-md" dense icon="error">
        {{ errorMessage }}
      </q-banner>

      <!-- Login Form -->
      <q-form @submit.prevent="handleLogin" class="q-gutter-md">
        <q-input
          v-model="email"
          label="Email or Username"
          outlined
          dense
          color="teal-9"
          :rules="[val => !!val || 'Field is required']"
        >
          <template v-slot:prepend>
            <q-icon name="person" color="teal-9" />
          </template>
        </q-input>

        <q-input
          v-model="password"
          label="Password"
          type="password"
          outlined
          dense
          color="teal-9"
          :rules="[val => !!val || 'Password is required']"
        >
          <template v-slot:prepend>
            <q-icon name="lock" color="teal-9" />
          </template>
        </q-input>

        <div class="row items-center justify-between q-mt-none">
          <q-checkbox v-model="rememberMe" label="Remember me" dense color="teal-9" class="text-caption" />
          <router-link to="/reset-password" class="text-caption text-teal-9 text-weight-bold style-none">
            Forgot Password?
          </router-link>
        </div>

        <q-btn
          type="submit"
          label="Login"
          color="teal-9"
          class="full-width q-mt-md mk-btn"
          unelevated
          no-caps
          :loading="loading"
        />
      </q-form>

      <!-- Footer / Signup link -->
      <div class="text-center q-mt-lg text-caption text-grey-8">
        Don't have an account?
        <router-link to="/" class="text-teal-9 text-weight-bold style-none">Sign Up</router-link>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api' // Imports directly from src/api.js

const router = useRouter()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  loading.value = true

  try {
    // 1. Prepare form data required by FastAPI OAuth2 endpoint
    const params = new URLSearchParams()
    params.append('username', email.value)
    params.append('password', password.value)

    // 2. Post to FastAPI
    const response = await api.post('/auth_login/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    // 3. Get token from backend response
    const token = response.data.access_token || response.data.token

    if (token) {
      localStorage.setItem('token', token)
      router.push('/dashboard') // Redirects to dashboard upon success
    } else {
      errorMessage.value = 'Login successful, but no token returned.'
    }
  } catch (error) {
    console.error('Login Error:', error)
    if (error.response?.data?.detail) {
      errorMessage.value = typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : 'Invalid credentials'
    } else {
      errorMessage.value = 'Could not connect to backend server or invalid login.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mk-login-page {
  background: #eef1f0;
  min-height: 100vh;
  padding: 16px;
}

.mk-login-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 16px;
  padding: 28px 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.mk-logo-avatar {
  background: linear-gradient(160deg, #0f6b46, #0b5637);
}

.mk-btn {
  height: 44px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 15px;
}

.style-none {
  text-decoration: none;
}
</style>