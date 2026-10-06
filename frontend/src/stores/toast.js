import { defineStore } from 'pinia'

let nextId = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [],
  }),
  actions: {
    push(message, type = 'info', timeout = 3600) {
      if (!message) return
      const id = ++nextId
      this.items.push({ id, message: String(message), type })
      if (timeout > 0) {
        window.setTimeout(() => this.dismiss(id), timeout)
      }
      // Keep the stack short; toasts are transient feedback.
      if (this.items.length > 4) this.items.splice(0, this.items.length - 4)
      return id
    },
    success(message) {
      return this.push(message, 'success')
    },
    error(message) {
      return this.push(message, 'error', 4800)
    },
    info(message) {
      return this.push(message, 'info')
    },
    dismiss(id) {
      const index = this.items.findIndex((item) => item.id === id)
      if (index !== -1) this.items.splice(index, 1)
    },
  },
})
