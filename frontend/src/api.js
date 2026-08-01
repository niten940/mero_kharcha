import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:3000', // Matches your running FastAPI server
})

// Automatically attach saved JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
