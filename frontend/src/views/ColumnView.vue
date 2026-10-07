<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleFeed from '../components/ArticleFeed.vue'
import { useMetaStore } from '../stores/meta'

const route = useRoute()
const meta = useMetaStore()
const slug = computed(() => String(route.params.slug || ''))
const column = computed(() => meta.columnBySlug(slug.value))
const filters = computed(() => ({ column: slug.value }))

onMounted(() => meta.load())
</script>

<template>
  <section class="section">
    <div class="container-narrow">
      <ArticleFeed
        kicker="Column"
        :title="column?.title || '栏目'"
        :description="column ? `这个栏目下共有 ${column.article_count ?? 0} 篇文章。` : '按栏目归档的文章。'"
        :filters="filters"
      />
    </div>
  </section>
</template>
