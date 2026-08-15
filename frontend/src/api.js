import axios from 'axios'

const api = axios.create({
  // Uses VITE_API_BASE_URL from .env or falls back to Android emulator bridge IP
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://10.0.2.2:3000',
  timeout: 15000,
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default api