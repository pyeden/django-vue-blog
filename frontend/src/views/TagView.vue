<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ArticleFeed from '../components/ArticleFeed.vue'
import { useMetaStore } from '../stores/meta'

const route = useRoute()
const meta = useMetaStore()
const slug = computed(() => String(route.params.slug || ''))
const tag = computed(() => meta.tagBySlug(slug.value))
const filters = computed(() => ({ tag: slug.value }))

onMounted(() => meta.load())
</script>

<template>
  <section class="section">
    <div class="container-narrow">
      <ArticleFeed
        kicker="Tag"
        :title="`# ${tag?.name || slug}`"
        description="带有这个标签的文章。"
        :filters="filters"
      />
    </div>
  </section>
</template>
