import axios from 'axios'

// Direct connection to FastAPI backend (or proxied /api in dev)
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8082',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT Bearer Token if stored
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('stardust_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Intercept 401s for automatic logout
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes('/auth')) {
      localStorage.removeItem('stardust_token')
      localStorage.removeItem('stardust_user')
      window.dispatchEvent(new Event('auth_logout'))
    }
    return Promise.reject(error)
  }
)
