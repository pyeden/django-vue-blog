<script setup>
import { onMounted } from 'vue'
import EmptyState from '../components/EmptyState.vue'
import { fromNow } from '../utils/format'
import { useNotificationsStore } from '../stores/notifications'
import { useToastStore } from '../stores/toast'

const notifications = useNotificationsStore()
const toast = useToastStore()

async function load() {
  try {
    await notifications.load()
  } catch (error) {
    toast.error('通知加载失败')
  }
}

async function readAll() {
  try {
    await notifications.readAll()
    toast.success('已全部标为已读')
  } catch (error) {
    toast.error('操作失败')
  }
}

onMounted(load)
</script>

<template>
  <section class="section">
    <div class="container-narrow">
      <div class="section-head">
        <div>
          <div class="hero-kicker">Notifications</div>
          <h1 class="section-title mt-2">通知</h1>
        </div>
        <button class="btn btn-sm btn-ghost" type="button" :disabled="!notifications.unreadCount" @click="readAll">
          全部已读
        </button>
      </div>

      <div v-if="notifications.loading" class="skeleton skeleton-line" v-for="n in 5" :key="n"></div>
      <div v-else-if="notifications.items.length" class="notice-list">
        <div
          v-for="item in notifications.items"
          :key="item.id"
          class="notice-item"
          :class="{ unread: item.unread }"
          @click="notifications.readOne(item.id)"
        >
          <span class="notice-dot"></span>
          <div class="notice-text">
            <router-link
              v-if="item.article"
              :to="{ name: 'article', params: { slug: item.article.slug } }"
            >
              {{ item.actor || '有人' }} 评论了《{{ item.article.title }}》
            </router-link>
            <span v-else>{{ item.actor || '有人' }} {{ item.verb }}</span>
          </div>
          <span class="notice-time">{{ fromNow(item.created) }}</span>
        </div>
      </div>
      <EmptyState v-else icon="bi-bell" title="还没有通知" text="有人评论你的文章时，会出现在这里。" />
    </div>
  </section>
</template>
