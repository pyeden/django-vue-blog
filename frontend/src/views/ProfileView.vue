<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import UserAvatar from '../components/UserAvatar.vue'
import { deleteAccountRequest, fetchProfile, updateProfile, uploadAvatar } from '../api'
import { apiError } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const router = useRouter()
const toast = useToastStore()
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const fileInput = ref(null)
const form = reactive({ phone: '', bio: '' })
const avatarUrl = ref('')

const user = computed(() => auth.user || {})

function fill(profile) {
  form.phone = profile?.phone || ''
  form.bio = profile?.bio || ''
  avatarUrl.value = profile?.avatar || ''
}

async function load() {
  loading.value = true
  try {
    fill(await fetchProfile())
  } catch (error) {
    toast.error(apiError(error, '资料加载失败'))
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    const profile = await updateProfile({ phone: form.phone, bio: form.bio })
    avatarUrl.value = profile.avatar || avatarUrl.value
    await auth.refresh()
    toast.success('资料已保存')
  } catch (error) {
    toast.error(apiError(error, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function onAvatar(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const profile = await uploadAvatar(file)
    avatarUrl.value = profile.avatar || ''
    await auth.refresh()
    toast.success('头像已更新')
  } catch (error) {
    toast.error(apiError(error, '头像上传失败'))
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function removeAccount() {
  if (!window.confirm('确定删除账号吗？你的文章和评论会一起删除，且不可恢复。')) return
  const password = window.prompt('输入当前密码以确认删除：')
  if (!password) return
  try {
    await deleteAccountRequest(password)
    auth.user = null
    toast.success('账号已删除')
    router.push({ name: 'home' })
  } catch (error) {
    toast.error(apiError(error, '删除账号失败'))
  }
}

onMounted(load)
</script>

<template>
  <section class="profile-page">
    <div class="container-narrow">
      <div class="section-head">
        <div>
          <div class="hero-kicker">Profile</div>
          <h1 class="section-title mt-2">个人资料</h1>
        </div>
        <router-link class="btn btn-sm btn-ghost" :to="{ name: 'home' }">返回首页</router-link>
      </div>

      <div class="profile-grid">
        <aside class="profile-card">
          <div class="profile-avatar">
            <img v-if="avatarUrl" :src="avatarUrl" :alt="user.username" />
            <template v-else>{{ (user.username || '?').slice(0, 1) }}</template>
          </div>
          <h2 class="profile-name">{{ user.username }}</h2>
          <div class="text-muted-ink small">{{ user.email || '未填写邮箱' }}</div>
          <button class="btn btn-sm btn-ghost mt-3" type="button" :disabled="uploading" @click="fileInput?.click()">
            {{ uploading ? '上传中…' : '更换头像' }}
          </button>
          <input ref="fileInput" class="d-none" type="file" accept="image/*" @change="onAvatar" />
          <p class="profile-bio mt-3">{{ form.bio || '还没有写简介。' }}</p>
          <button class="btn btn-sm btn-quiet text-danger mt-2" type="button" @click="removeAccount">删除账号</button>
        </aside>

        <div class="panel">
          <h3 class="panel-title">编辑资料</h3>
          <div v-if="loading" class="skeleton skeleton-line" v-for="n in 4" :key="n"></div>
          <form v-else @submit.prevent="save">
            <div class="mb-3">
              <label class="form-label">电话</label>
              <input v-model="form.phone" class="form-control" maxlength="32" placeholder="可选" />
            </div>
            <div class="mb-3">
              <label class="form-label">简介</label>
              <textarea v-model="form.bio" class="form-control" rows="4" maxlength="500" placeholder="一句话介绍自己"></textarea>
            </div>
            <button class="btn btn-accent" type="submit" :disabled="saving">
              {{ saving ? '保存中…' : '保存资料' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>
