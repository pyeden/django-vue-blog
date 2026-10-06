<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ToastHost from './components/ToastHost.vue'
import BackToTop from './components/BackToTop.vue'
import { useAuthStore } from './stores/auth'
import { useNotificationsStore } from './stores/notifications'

const auth = useAuthStore()
const notifications = useNotificationsStore()

let pollTimer = null

function refreshNotifications() {
  if (auth.isAuthenticated) {
    notifications.load(true)
  } else {
    notifications.reset()
  }
}

function onVisibility() {
  if (document.visibilityState === 'visible') refreshNotifications()
}

onMounted(async () => {
  await auth.bootstrap()
  if (auth.isAuthenticated) {
    notifications.load(true)
    pollTimer = window.setInterval(refreshNotifications, 60000)
  }
  document.addEventListener('visibilitychange', onVisibility)
})

watch(
  () => auth.isAuthenticated,
  (loggedIn) => {
    if (loggedIn) {
      notifications.load(true)
      if (!pollTimer) pollTimer = window.setInterval(refreshNotifications, 60000)
    } else {
      notifications.reset()
      if (pollTimer) {
        window.clearInterval(pollTimer)
        pollTimer = null
      }
    }
  }
)

onBeforeUnmount(() => {
  if (pollTimer) window.clearInterval(pollTimer)
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <div class="app-frame">
    <AppHeader />
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
    <BackToTop />
    <ToastHost />
  </div>
</template>
