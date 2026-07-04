import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const register          = d  => api.post('/auth/register', d)
export const login             = d  => api.post('/auth/login', d)
export const predictParameters = d  => api.post('/cancer/predict/parameters', d)
export const predictImage      = f  => api.post('/cancer/predict/image', f, { headers: { 'Content-Type': 'multipart/form-data' } })
export const getCancerHistory  = () => api.get('/cancer/history')
export const sendMessage       = d  => api.post('/chatbot/chat', d)
export const logPeriod         = d  => api.post('/period/log', d)
export const getPeriodLog      = () => api.get('/period/log')