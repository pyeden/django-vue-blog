import { defineStore } from 'pinia'
import {
  ensureCsrf,
  fetchMe,
  loginRequest,
  logoutRequest,
  registerRequest,
} from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    ready: false,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user),
    username: (state) => state.user?.username || '',
    isStaff: (state) => Boolean(state.user?.is_staff),
    profile: (state) => state.user?.profile || { phone: '', bio: '', avatar: '' },
  },
  actions: {
    async bootstrap(force = false) {
      if (this.ready && !force) return this.user
      this.loading = true
      try {
        await ensureCsrf()
        this.user = await fetchMe()
      } catch (error) {
        // An anonymous visitor is a valid state; never block page rendering.
        this.user = null
      } finally {
        this.loading = false
        this.ready = true
      }
      return this.user
    },
    async login(payload) {
      await ensureCsrf()
      const data = await loginRequest(payload)
      this.user = data?.user ?? (await fetchMe())
      this.ready = true
      return this.user
    },
    async register(payload) {
      await ensureCsrf()
      const data = await registerRequest(payload)
      this.user = data?.user ?? (await fetchMe())
      this.ready = true
      return this.user
    },
    async logout() {
      try {
        await logoutRequest()
      } finally {
        this.user = null
      }
    },
    async refresh() {
      try {
        this.user = await fetchMe()
      } catch (error) {
        this.user = null
      }
      return this.user
    },
  },
})
