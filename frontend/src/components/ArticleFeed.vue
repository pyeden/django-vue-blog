<script setup>
import { computed, ref, watch } from 'vue'
import ArticleCard from './ArticleCard.vue'
import EmptyState from './EmptyState.vue'
import PaginationBar from './PaginationBar.vue'
import SidebarPanel from './SidebarPanel.vue'
import { listArticles } from '../api'
import { apiError } from '../api/client'
import { useToastStore } from '../stores/toast'

const props = defineProps({
  kicker: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  filters: { type: Object, default: () => ({}) },
  showSidebar: { type: Boolean, default: true },
  emptyTitle: { type: String, default: '还没有文章' },
})

const toast = useToastStore()
const items = ref([])
const page = ref(1)
const count = ref(0)
const totalPages = ref(1)
const loading = ref(true)
const error = ref('')

const filterKey = computed(() => JSON.stringify(props.filters || {}))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await listArticles({ page: page.value, page_size: 6, ...props.filters })
    items.value = data.results
    count.value = data.count
    totalPages.value = Math.max(1, Math.ceil(data.count / 6))
    if (page.value > totalPages.value) {
      page.value = totalPages.value
    }
  } catch (err) {
    error.value = apiError(err, '文章加载失败')
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}

watch(
  filterKey,
  () => {
    page.value = 1
    load()
  },
  { immediate: true }
)
watch(page, load)
</script>

<template>
  <div class="layout-grid">
    <div class="layout-main">
      <div v-if="kicker || title" class="section-head">
        <div>
          <div v-if="kicker" class="hero-kicker">{{ kicker }}</div>
          <h1 v-if="title" class="section-title mt-2">{{ title }}</h1>
          <p v-if="description" class="text-muted-ink mb-0 mt-2">{{ description }}</p>
        </div>
        <span class="section-note">{{ count }} 篇</span>
      </div>

      <div v-if="loading" class="article-list">
        <div v-for="n in 3" :key="n" class="article-card no-cover">
          <div class="article-card-body">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-line"></div>
            <div class="skeleton skeleton-line" style="width: 84%"></div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="empty-state">
        <i class="bi bi-cloud-slash"></i>
        <div class="empty-title">加载失败</div>
        <div>{{ error }}</div>
        <button class="btn btn-sm btn-ghost mt-3" type="button" @click="load">重试</button>
      </div>

      <div v-else-if="items.length" class="article-list">
        <ArticleCard v-for="article in items" :key="article.id" :article="article" />
      </div>

      <EmptyState v-else :title="emptyTitle" text="换个关键词，或稍后再来看看。" />

      <PaginationBar
        v-if="items.length"
        :page="page"
        :total-pages="totalPages"
        :total-count="count"
        @update:page="page = $event"
      />
    </div>

    <SidebarPanel v-if="showSidebar" />
  </div>
</template>
