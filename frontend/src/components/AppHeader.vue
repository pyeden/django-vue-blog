<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserAvatar from './UserAvatar.vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationsStore } from '../stores/notifications'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const notifications = useNotificationsStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const title = import.meta.env.VITE_BLOG_TITLE || '纸上集'
const subtitle = import.meta.env.VITE_BLOG_SUBTITLE || 'Seres 的个人博客'
const unread = computed(() => notifications.unreadCount)

async function logout() {
  try {
    await auth.logout()
    toast.success('已退出登录')
    if (route.meta.requiresAuth) router.push({ name: 'home' })
  } catch (error) {
    toast.error('退出登录失败，请稍后再试')
  }
}
</script>

<template>
  <header class="site-header">
    <div class="container-narrow header-inner">
      <router-link class="brand" :to="{ name: 'home' }">
        <span class="brand-mark"></span>
        <span>{{ title }}</span>
        <span class="brand-sub">{{ subtitle }}</span>
      </router-link>

      <nav class="header-nav">
        <router-link :to="{ name: 'home' }">首页</router-link>
        <router-link :to="{ name: 'search' }">搜索</router-link>
        <router-link v-if="auth.isAuthenticated" :to="{ name: 'write' }">写文章</router-link>
      </nav>

      <span class="header-spacer"></span>

      <div class="header-actions">
        <router-link
          v-if="auth.isAuthenticated"
          class="icon-btn"
          :to="{ name: 'notifications' }"
          title="通知"
          aria-label="通知"
        >
          <i class="bi bi-bell"></i>
          <span v-if="unread" class="notif-dot has-count">{{ notifications.badgeText }}</span>
        </router-link>

        <template v-if="auth.isAuthenticated">
          <router-link class="icon-btn" :to="{ name: 'profile' }" title="个人资料" aria-label="个人资料">
            <UserAvatar :name="auth.username" :avatar="auth.profile.avatar" :size="28" />
          </router-link>
          <button class="btn btn-sm btn-quiet" type="button" @click="logout">退出</button>
        </template>
        <template v-else>
          <router-link class="btn btn-sm btn-ghost" :to="{ name: 'login' }">登录</router-link>
          <router-link class="btn btn-sm btn-accent" :to="{ name: 'register' }">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>
