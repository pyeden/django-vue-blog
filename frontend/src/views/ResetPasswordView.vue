<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { passwordResetConfirm, passwordResetRequest } from '../api'
import { apiError } from '../api/client'
import { useToastStore } from '../stores/toast'

const toast = useToastStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = reactive({ value: '', confirm: '' })
const confirmMode = computed(() => Boolean(route.query.uid && route.query.token))
const confirming = ref(false)
const submitting = ref(false)
const sent = ref(false)

async function confirmReset() {
  if (!password.value) {
    toast.error('请输入新密码')
    return
  }
  if (password.value !== password.confirm) {
    toast.error('两次输入的密码不一致')
    return
  }
  confirming.value = true
  try {
    await passwordResetConfirm({ uid: route.query.uid, token: route.query.token, password: password.value })
    toast.success('密码已重置，请重新登录')
    router.push({ name: 'login' })
  } catch (error) {
    toast.error(apiError(error, '重置失败'))
  } finally {
    confirming.value = false
  }
}

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
      <form v-if="confirmMode" @submit.prevent="confirmReset">
        <div class="mb-3">
          <label class="form-label">新密码</label>
          <input v-model="password.value" class="form-control" type="password" autocomplete="new-password" required />
        </div>
        <div class="mb-3">
          <label class="form-label">确认新密码</label>
          <input v-model="password.confirm" class="form-control" type="password" autocomplete="new-password" required />
        </div>
        <button class="btn btn-accent w-100" type="submit" :disabled="confirming">
          {{ confirming ? '重置中…' : '重置密码' }}
        </button>
      </form>
      <form v-else-if="!sent" @submit.prevent="submit">
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
