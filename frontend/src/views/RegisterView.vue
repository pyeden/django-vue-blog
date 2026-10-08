<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiError } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const form = reactive({ username: '', email: '', password1: '', password2: '' })
const submitting = ref(false)

async function submit() {
  submitting.value = true
  try {
    await auth.register({ ...form, username: form.username.trim(), email: form.email.trim() })
    toast.success('账号已创建')
    router.push({ name: 'home' })
  } catch (error) {
    toast.error(apiError(error, '注册失败'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-card">
      <div class="auth-kicker">Join the paper</div>
      <h1 class="auth-title">注册</h1>
      <p class="auth-sub">只需要一个用户名和密码。</p>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">用户名</label>
          <input v-model="form.username" class="form-control" maxlength="150" required />
        </div>
        <div class="mb-3">
          <label class="form-label">邮箱（可选，用于找回密码）</label>
          <input v-model="form.email" class="form-control" type="email" />
        </div>
        <div class="mb-3">
          <label class="form-label">密码</label>
          <input v-model="form.password1" class="form-control" type="password" autocomplete="new-password" required />
        </div>
        <div class="mb-3">
          <label class="form-label">确认密码</label>
          <input v-model="form.password2" class="form-control" type="password" autocomplete="new-password" required />
        </div>
        <button class="btn btn-accent w-100" type="submit" :disabled="submitting">
          {{ submitting ? '创建中…' : '创建账号' }}
        </button>
      </form>
      <div class="auth-foot">已有账号？<router-link :to="{ name: 'login' }">直接登录</router-link></div>
    </div>
  </section>
</template>
