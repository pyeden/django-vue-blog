<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommentTree from '../components/CommentTree.vue'
import MarkdownBody from '../components/MarkdownBody.vue'
import TocRail from '../components/TocRail.vue'
import UserAvatar from '../components/UserAvatar.vue'
import EmptyState from '../components/EmptyState.vue'
import { createComment, deleteArticle, fetchArticle, fetchComments, toggleArticleLike } from '../api'
import { apiError } from '../api/client'
import { formatDate, mediaUrl, pluralCount } from '../utils/format'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const article = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')
const loadingComments = ref(false)
const liking = ref(false)
const commentBody = ref('')
const submitting = ref(false)

const slug = computed(() => String(route.params.slug || ''))
const cover = computed(() => mediaUrl(article.value?.cover))
const isAuthor = computed(() => auth.isAuthenticated && auth.username === article.value?.author?.username)
const canManage = computed(() => auth.isStaff || isAuthor.value)
const commentCount = computed(() => {
  const walk = (items) => items.reduce((sum, item) => sum + 1 + walk(item.replies || []), 0)
  return walk(comments.value)
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    article.value = await fetchArticle(slug.value)
    loadComments()
  } catch (err) {
    error.value = apiError(err, '文章加载失败')
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  loadingComments.value = true
  try {
    comments.value = await fetchComments(slug.value)
  } catch (err) {
    toast.error(apiError(err, '评论加载失败'))
  } finally {
    loadingComments.value = false
  }
}

async function toggleLike() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  if (liking.value) return
  liking.value = true
  try {
    const data = await toggleArticleLike(slug.value)
    article.value.liked = data.liked
    article.value.likes = data.likes
  } catch (err) {
    toast.error(apiError(err, '点赞失败'))
  } finally {
    liking.value = false
  }
}

async function submitComment() {
  const body = commentBody.value.trim()
  if (!body) return
  submitting.value = true
  try {
    await createComment(slug.value, { body })
    commentBody.value = ''
    toast.success('评论已发布')
    await loadComments()
  } catch (err) {
    toast.error(apiError(err, '评论失败'))
  } finally {
    submitting.value = false
  }
}

async function removeArticle() {
  if (!window.confirm('确定删除这篇文章吗？删除后不可恢复。')) return
  try {
    await deleteArticle(slug.value)
    toast.success('文章已删除')
    router.push({ name: 'home' })
  } catch (err) {
    toast.error(apiError(err, '删除失败'))
  }
}

watch(slug, load)
onMounted(load)
</script>

<template>
  <section class="article-page">
    <div class="container-narrow">
      <div v-if="loading" class="article-layout">
        <div>
          <div class="skeleton skeleton-title" style="height: 48px; width: 80%"></div>
          <div class="skeleton skeleton-line" style="width: 40%"></div>
          <div class="skeleton skeleton-line mt-4"></div>
          <div class="skeleton skeleton-line"></div>
          <div class="skeleton skeleton-line" style="width: 90%"></div>
        </div>
      </div>

      <EmptyState v-else-if="error" icon="bi-file-earmark-x" title="文章不存在" :text="error">
        <router-link class="btn btn-sm btn-ghost mt-3" :to="{ name: 'home' }">回到首页</router-link>
      </EmptyState>

      <div v-else-if="article" class="article-layout">
        <article>
          <header class="article-head">
            <div class="article-kicker">
              <router-link v-if="article.column" :to="{ name: 'column', params: { slug: article.column.slug } }">
                {{ article.column.title }}
              </router-link>
              <span v-else>随笔</span>
            </div>
            <h1 class="article-title">{{ article.title }}</h1>
            <div class="article-meta">
              <span class="author">
                <UserAvatar :name="article.author?.username" :avatar="article.author?.avatar" :size="30" />
                {{ article.author?.username }}
              </span>
              <span>{{ formatDate(article.created) }}</span>
              <span>{{ article.total_views }} 次浏览</span>
              <span>{{ pluralCount(commentCount, '条评论') }}</span>
            </div>
            <img v-if="cover" class="article-cover mt-4" :src="cover" :alt="article.title" />
            <div v-if="article.tags?.length" class="tag-row">
              <router-link
                v-for="tag in article.tags"
                :key="tag"
                class="tag-chip"
                :to="{ name: 'tag', params: { slug: tag } }"
              >
                # {{ tag }}
              </router-link>
            </div>
          </header>

          <div class="article-body">
            <MarkdownBody :html="article.body_html" />
          </div>

          <div class="article-actions">
            <button class="like-btn" :class="{ liked: article.liked }" type="button" :disabled="liking" @click="toggleLike">
              <i :class="article.liked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
              {{ article.likes }}
            </button>
            <span class="text-muted-ink small">觉得有用，就点个赞。</span>
            <span class="flex-grow-1"></span>
            <template v-if="canManage">
              <router-link class="btn btn-sm btn-ghost" :to="{ name: 'edit', params: { slug: article.slug } }">编辑</router-link>
              <button class="btn btn-sm btn-quiet text-danger" type="button" @click="removeArticle">删除</button>
            </template>
          </div>

          <section class="comment-section">
            <h2 class="comment-title">评论 <span class="comment-count">{{ commentCount }}</span></h2>

            <form v-if="auth.isAuthenticated" class="comment-form" @submit.prevent="submitComment">
              <textarea
                v-model="commentBody"
                class="form-control"
                rows="3"
                placeholder="写下你的想法…"
                maxlength="2000"
              ></textarea>
              <div class="d-flex justify-content-end mt-2">
                <button class="btn btn-sm btn-accent" type="submit" :disabled="submitting || !commentBody.trim()">
                  {{ submitting ? '发送中…' : '发表评论' }}
                </button>
              </div>
            </form>
            <div v-else class="comment-login-hint">
              <router-link :to="{ name: 'login', query: { redirect: route.fullPath } }">登录</router-link>
              后可以发表评论。
            </div>

            <CommentTree :comments="comments" :slug="slug" :loading="loadingComments" @changed="loadComments" />
          </section>
        </article>

        <TocRail :toc="article.toc || []" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.article-cover {
  width: 100%;
  max-height: 430px;
  object-fit: cover;
  border-radius: 4px;
}
</style>
