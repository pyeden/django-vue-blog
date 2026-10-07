<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ArticleFeed from '../components/ArticleFeed.vue'

const route = useRoute()
const q = computed(() => String(route.query.q || '').trim())
const filters = computed(() => (q.value ? { search: q.value } : {}))
</script>

<template>
  <section class="section">
    <div class="container-narrow">
      <ArticleFeed
        kicker="Search"
        :title="q ? `搜索：${q}` : '搜索文章'"
        :description="q ? '在标题和正文中查找。' : '在右上角输入关键词，或直接使用侧栏搜索。'"
        :filters="filters"
        :empty-title="q ? '没有找到匹配的文章' : '输入关键词开始搜索'"
      />
    </div>
  </section>
</template>
