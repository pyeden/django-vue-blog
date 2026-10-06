import { defineStore } from 'pinia'
import {
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../api'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [],
    unreadCount: 0,
    loading: false,
    loaded: false,
    error: '',
  }),
  getters: {
    hasUnread: (state) => state.unreadCount > 0,
    badgeText: (state) => (state.unreadCount > 99 ? '99+' : String(state.unreadCount)),
  },
  actions: {
    async load(silent = false) {
      if (this.loading) return
      if (!silent) this.loading = true
      this.error = ''
      try {
        const data = await fetchNotifications()
        this.items = data.results
        this.unreadCount = data.unread_count
        this.loaded = true
      } catch (error) {
        this.error = '通知加载失败'
      } finally {
        this.loading = false
      }
    },
    async readAll() {
      await markAllNotificationsRead()
      this.unreadCount = 0
      this.items = this.items.map((item) => ({ ...item, unread: false }))
    },
    async readOne(id) {
      const item = this.items.find((entry) => entry.id === id)
      if (!item || !item.unread) return
      await markNotificationRead(id)
      item.unread = false
      this.unreadCount = Math.max(0, this.unreadCount - 1)
    },
    reset() {
      this.items = []
      this.unreadCount = 0
      this.loaded = false
      this.error = ''
    },
  },
})
