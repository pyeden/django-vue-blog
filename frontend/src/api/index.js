import api, { unwrapList } from './client'

/* ---------------------------------- auth --------------------------------- */

export async function ensureCsrf() {
  const { data } = await api.get('/auth/csrf/')
  return data
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me/')
  return data?.user ?? null
}

export async function loginRequest(payload) {
  const { data } = await api.post('/auth/login/', payload)
  return data
}

export async function registerRequest(payload) {
  const { data } = await api.post('/auth/register/', payload)
  return data
}

export async function deleteAccountRequest(password) {
  const { data } = await api.post('/auth/delete/', { password })
  return data
}

export async function logoutRequest() {
  const { data } = await api.post('/auth/logout/')
  return data
}

export async function passwordResetConfirm(payload) {
  const { data } = await api.post('/auth/password-reset/confirm/', payload)
  return data
}

export async function passwordResetRequest(email) {
  const { data } = await api.post('/auth/password-reset/', { email })
  return data
}

/* --------------------------------- profile -------------------------------- */

export async function fetchProfile() {
  const { data } = await api.get('/profile/')
  return data
}

export async function updateProfile(payload) {
  const { data } = await api.patch('/profile/', payload)
  return data
}

export async function uploadAvatar(file) {
  const form = new FormData()
  form.append('avatar', file)
  const { data } = await api.post('/profile/avatar/', form)
  return data
}

/* --------------------------------- articles ------------------------------- */

export async function listArticles(params = {}) {
  const { data } = await api.get('/articles/', { params })
  return unwrapList(data)
}

export async function fetchArticle(slug) {
  const { data } = await api.get(`/articles/${encodeURIComponent(slug)}/`)
  return data
}

export async function createArticle(payload) {
  const { data } = await api.post('/articles/', payload)
  return data
}

export async function updateArticle(slug, payload) {
  const { data } = await api.patch(`/articles/${encodeURIComponent(slug)}/`, payload)
  return data
}

export async function deleteArticle(slug) {
  const { data } = await api.delete(`/articles/${encodeURIComponent(slug)}/`)
  return data
}

export async function uploadArticleCover(slug, file) {
  const form = new FormData()
  form.append('cover', file)
  const { data } = await api.post(`/articles/${encodeURIComponent(slug)}/cover/`, form)
  return data
}

export async function toggleArticleLike(slug) {
  const { data } = await api.post(`/articles/${encodeURIComponent(slug)}/like/`)
  return data
}

export async function fetchHotArticles() {
  const { data } = await api.get('/articles/hot/')
  return unwrapList(data).results
}

/* -------------------------------- taxonomy -------------------------------- */

export async function fetchColumns() {
  const { data } = await api.get('/columns/')
  return unwrapList(data).results
}

export async function fetchTags() {
  const { data } = await api.get('/tags/')
  return unwrapList(data).results
}

/* -------------------------------- comments -------------------------------- */

export async function fetchComments(slug) {
  const { data } = await api.get(`/articles/${encodeURIComponent(slug)}/comments/`)
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  if (Array.isArray(data?.comments)) return data.comments
  return []
}

export async function createComment(slug, payload) {
  const { data } = await api.post(`/articles/${encodeURIComponent(slug)}/comments/`, payload)
  return data
}

export async function deleteComment(id) {
  const { data } = await api.delete(`/comments/${id}/`)
  return data
}

/* ------------------------------ notifications ------------------------------ */

export async function fetchNotifications() {
  const { data } = await api.get('/notifications/')
  return {
    unread_count: data?.unread_count ?? 0,
    results: Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [],
  }
}

export async function markAllNotificationsRead() {
  const { data } = await api.post('/notifications/read-all/')
  return data
}

export async function markNotificationRead(id) {
  const { data } = await api.post(`/notifications/${id}/read/`)
  return data
}
