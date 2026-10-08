<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiError } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()
const form = reactive({ username: '', password: '' })
const submitting = ref(false)

async function submit() {
  if (!form.username || !form.password) return
  submitting.value = true
  try {
    await auth.login({ username: form.username.trim(), password: form.password })
    toast.success('欢迎回来')
    router.push(String(route.query.redirect || '/'))
  } catch (error) {
    toast.error(apiError(error, '登录失败'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-card">
      <div class="auth-kicker">Welcome back</div>
      <h1 class="auth-title">登录</h1>
      <p class="auth-sub">继续阅读，或者写点什么。</p>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">用户名</label>
          <input v-model="form.username" class="form-control" autocomplete="username" required />
        </div>
        <div class="mb-3">
          <label class="form-label">密码</label>
          <input v-model="form.password" class="form-control" type="password" autocomplete="current-password" required />
        </div>
        <button class="btn btn-accent w-100" type="submit" :disabled="submitting">
          {{ submitting ? '登录中…' : '登录' }}
        </button>
      </form>
      <div class="auth-foot">
        还没有账号？<router-link :to="{ name: 'register' }">注册一个</router-link>
        · <router-link :to="{ name: 'reset-password' }">忘记密码</router-link>
      </div>
    </div>
  </section>
</template>
