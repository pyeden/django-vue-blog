<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ArticleEditor from '../components/ArticleEditor.vue'
import EmptyState from '../components/EmptyState.vue'
import { fetchArticle } from '../api'
import { apiError } from '../api/client'

const route = useRoute()
const article = ref(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    article.value = await fetchArticle(String(route.params.slug || ''))
  } catch (err) {
    error.value = apiError(err, '文章加载失败')
  } finally {
    loading.value = false
  }
}

watch(() => route.params.slug, load, { immediate: true })
onMounted(load)
</script>

<template>
  <section class="editor-page">
    <div class="container-narrow">
      <div class="editor-head">
        <div>
          <div class="hero-kicker">Edit</div>
          <h1 class="editor-title mt-2">编辑文章</h1>
        </div>
      </div>

      <div v-if="loading" class="py-5">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line" style="width: 70%"></div>
      </div>
      <EmptyState v-else-if="error" icon="bi-exclamation-circle" title="无法打开文章" :text="error" />
      <ArticleEditor v-else-if="article" :article="article" />
    </div>
  </section>
</template>
