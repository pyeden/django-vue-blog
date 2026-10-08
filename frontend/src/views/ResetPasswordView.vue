<script setup>
import { ref } from 'vue'
import { passwordResetRequest } from '../api'
import { apiError } from '../api/client'
import { useToastStore } from '../stores/toast'

const toast = useToastStore()
const email = ref('')
const submitting = ref(false)
const sent = ref(false)

async function submit() {
  submitting.value = true
  try {
    await passwordResetRequest(email.value.trim())
    sent.value = true
    toast.success('如果邮箱已注册，重置邮件已发出')
  } catch (error) {
    toast.error(apiError(error, '发送失败'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-card">
      <div class="auth-kicker">Reset</div>
      <h1 class="auth-title">找回密码</h1>
      <p class="auth-sub">
        输入注册邮箱。开发环境邮件会打印在后端控制台；生产环境需要配置 SMTP。
      </p>
      <form v-if="!sent" @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">邮箱</label>
          <input v-model="email" class="form-control" type="email" required />
        </div>
        <button class="btn btn-accent w-100" type="submit" :disabled="submitting || !email">
          {{ submitting ? '发送中…' : '发送重置邮件' }}
        </button>
      </form>
      <div v-else class="empty-state">
        <i class="bi bi-envelope-check"></i>
        <div class="empty-title">邮件已发送</div>
        <div>请检查邮箱，并按邮件里的标识重置密码。</div>
      </div>
      <div class="auth-foot"><router-link :to="{ name: 'login' }">返回登录</router-link></div>
    </div>
  </section>
</template>
