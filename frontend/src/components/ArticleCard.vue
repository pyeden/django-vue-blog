<script setup>
import { computed } from 'vue'
import UserAvatar from './UserAvatar.vue'
import { formatDate, mediaUrl, pluralCount } from '../utils/format'

const props = defineProps({
  article: { type: Object, required: true },
})

const cover = computed(() => mediaUrl(props.article.cover))
const author = computed(() => props.article.author || { username: '', avatar: '' })
const tags = computed(() => (props.article.tags || []).map((tag) => (typeof tag === 'string' ? tag : tag.name)))
const column = computed(() => props.article.column || null)
</script>

<template>
  <article class="article-card" :class="{ 'no-cover': !cover }">
    <router-link v-if="cover" :to="{ name: 'article', params: { slug: article.slug } }">
      <img class="article-card-cover" :src="cover" :alt="article.title" loading="lazy" />
    </router-link>

    <div class="article-card-body">
      <div class="article-card-meta">
        <router-link v-if="column" :to="{ name: 'column', params: { slug: column.slug } }">
          {{ column.title }}
        </router-link>
        <span>{{ formatDate(article.created) }}</span>
        <span>{{ article.total_views || 0 }} 次浏览</span>
      </div>

      <router-link class="article-card-title" :to="{ name: 'article', params: { slug: article.slug } }">
        {{ article.title }}
      </router-link>

      <p class="article-card-excerpt">{{ article.excerpt }}</p>

      <div class="tag-row">
        <router-link
          v-for="tag in tags.slice(0, 4)"
          :key="tag"
          class="tag-chip"
          :to="{ name: 'tag', params: { slug: tag } }"
        >
          # {{ tag }}
        </router-link>
      </div>

      <div class="article-card-foot">
        <span class="d-inline-flex align-items-center gap-2">
          <UserAvatar :name="author.username" :avatar="author.avatar" :size="24" />
          {{ author.username || '匿名' }}
        </span>
        <span><i class="bi bi-chat-square-text me-1"></i>{{ pluralCount(article.comment_count, '条评论') }}</span>
        <span><i class="bi bi-heart me-1"></i>{{ article.likes || 0 }}</span>
      </div>
    </div>
  </article>
</template>
