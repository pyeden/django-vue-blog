<script setup>
import { computed, ref } from 'vue'
import UserAvatar from './UserAvatar.vue'
import { createComment, deleteComment } from '../api'
import { apiError } from '../api/client'
import { formatDateTime } from '../utils/format'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

defineOptions({ name: 'CommentNode' })

const props = defineProps({
  comment: { type: Object, required: true },
  slug: { type: String, required: true },
  depth: { type: Number, default: 1 },
})
const emit = defineEmits(['changed'])

const auth = useAuthStore()
const toast = useToastStore()
const replying = ref(false)
const replyBody = ref('')
const submitting = ref(false)

const canDelete = computed(() => {
  if (!auth.isAuthenticated) return false
  return auth.isStaff || auth.username === props.comment.user?.username
})
const children = computed(() => props.comment.replies || [])

function toggleReply() {
  if (!auth.isAuthenticated) {
    toast.info('登录后才能回复')
    return
  }
  replying.value = !replying.value
}

async function submitReply() {
  const body = replyBody.value.trim()
  if (!body) return
  submitting.value = true
  try {
    await createComment(props.slug, { body, parent_id: props.comment.id })
    replyBody.value = ''
    replying.value = false
    toast.success('回复已发布')
    emit('changed')
  } catch (error) {
    toast.error(apiError(error, '回复失败'))
  } finally {
    submitting.value = false
  }
}

async function remove() {
  if (!window.confirm('确定删除这条评论吗？')) return
  try {
    await deleteComment(props.comment.id)
    toast.success('评论已删除')
    emit('changed')
  } catch (error) {
    toast.error(apiError(error, '删除失败'))
  }
}
</script>

<template>
  <div class="comment-item">
    <div class="comment-head">
      <UserAvatar :name="comment.user?.username" :avatar="comment.user?.avatar" :size="30" />
      <span class="comment-user">{{ comment.user?.username || '匿名' }}</span>
      <span class="comment-time">{{ formatDateTime(comment.created) }}</span>
    </div>
    <div class="comment-body">{{ comment.body }}</div>
    <div class="comment-actions">
      <button type="button" @click="toggleReply">回复</button>
      <button v-if="canDelete" type="button" @click="remove">删除</button>
    </div>

    <form v-if="replying" class="comment-form comment-reply-form" @submit.prevent="submitReply">
      <textarea v-model="replyBody" class="form-control" rows="3" :placeholder="`回复 @${comment.user?.username}`"></textarea>
      <div class="d-flex justify-content-end gap-2 mt-2">
        <button class="btn btn-sm btn-ghost" type="button" @click="replying = false">取消</button>
        <button class="btn btn-sm btn-accent" type="submit" :disabled="submitting || !replyBody.trim()">
          {{ submitting ? '发送中…' : '发送' }}
        </button>
      </div>
    </form>

    <div v-if="children.length" class="comment-children">
      <CommentNode
        v-for="child in children"
        :key="child.id"
        :comment="child"
        :slug="slug"
        :depth="depth + 1"
        @changed="emit('changed')"
      />
    </div>
  </div>
</template>
