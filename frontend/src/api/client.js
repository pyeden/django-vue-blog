import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  timeout: 20000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
})

function readCookie(name) {
  if (typeof document === 'undefined') return null
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[2]) : null
}

const SAFE_METHODS = ['get', 'head', 'options']

api.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()
  if (!SAFE_METHODS.includes(method)) {
    const token = readCookie('csrftoken')
    if (token) {
      config.headers = config.headers || {}
      config.headers['X-CSRFToken'] = token
    }
  }
  return config
})

const FIELD_LABELS = {
  username: '用户名',
  email: '邮箱',
  password1: '密码',
  password2: '确认密码',
  password: '密码',
  title: '标题',
  body: '正文',
  tags: '标签',
  column: '栏目',
  cover: '封面',
  phone: '电话',
  bio: '简介',
  avatar: '头像',
  detail: '提示',
  non_field_errors: '',
}

export function apiError(error, fallback = '操作失败，请稍后再试') {
  if (!error) return fallback
  if (error.code === 'ECONNABORTED') return '请求超时，请检查网络后重试'
  const response = error.response
  if (!response) return '无法连接服务器，请稍后再试'
  const data = response.data
  if (!data) {
    if (response.status === 401) return '请先登录后再操作'
    if (response.status === 403) return '没有权限执行该操作'
    if (response.status === 404) return '内容不存在或已被删除'
    if (response.status >= 500) return '服务器开小差了，请稍后再试'
    return fallback
  }
  if (typeof data === 'string') return data.slice(0, 300)
  if (data.detail) return String(data.detail)
  if (typeof data === 'object') {
    const parts = []
    for (const [key, value] of Object.entries(data)) {
      const label = FIELD_LABELS[key] ?? key
      const message = Array.isArray(value) ? value.join(' ') : String(value)
      parts.push(label ? `${label}：${message}` : message)
      if (parts.length >= 3) break
    }
    if (parts.length) return parts.join('；')
  }
  if (response.status === 401) return '请先登录后再操作'
  if (response.status === 403) return '没有权限执行该操作'
  return fallback
}

export function unwrapList(data) {
  if (Array.isArray(data)) {
    return { results: data, count: data.length, next: null, previous: null }
  }
  if (data && typeof data === 'object') {
    const results = Array.isArray(data.results) ? data.results : []
    return {
      results,
      count: typeof data.count === 'number' ? data.count : results.length,
      next: data.next ?? null,
      previous: data.previous ?? null,
    }
  }
  return { results: [], count: 0, next: null, previous: null }
}

export default api
