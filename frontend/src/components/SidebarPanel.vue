<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHotArticles } from '../api'
import { useMetaStore } from '../stores/meta'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const meta = useMetaStore()
const toast = useToastStore()
const q = ref('')
const hot = ref([])
const loadingHot = ref(false)

async function loadHot() {
  loadingHot.value = true
  try {
    hot.value = await fetchHotArticles()
  } catch (error) {
    toast.error('最热文章加载失败')
  } finally {
    loadingHot.value = false
  }
}

function search() {
  const value = q.value.trim()
  if (!value) return
  router.push({ name: 'search', query: { q: value } })
}

onMounted(() => {
  meta.load()
  loadHot()
})
</script>

<template>
  <aside class="layout-side">
    <section class="panel">
      <h3 class="panel-title">找点什么</h3>
      <form class="search-row" @submit.prevent="search">
        <input v-model="q" class="form-control form-control-sm" type="search" placeholder="搜索标题或正文" />
        <button class="btn btn-sm btn-accent" type="submit"><i class="bi bi-search"></i></button>
      </form>
    </section>

    <section class="panel">
      <h3 class="panel-title">最热文章</h3>
      <template v-if="loadingHot">
        <div v-for="n in 4" :key="n" class="skeleton skeleton-line"></div>
      </template>
      <div v-else-if="hot.length" class="hot-list">
        <router-link
          v-for="(item, index) in hot"
          :key="item.id"
          class="hot-item"
          :to="{ name: 'article', params: { slug: item.slug } }"
        >
          <span class="hot-index">{{ String(index + 1).padStart(2, '0') }}</span>
          <span>{{ item.title }}</span>
        </router-link>
      </div>
      <p v-else class="about-mini mb-0">还没有足够的数据。</p>
    </section>

    <section class="panel">
      <h3 class="panel-title">栏目</h3>
      <div class="column-list">
        <router-link
          v-for="column in meta.columns"
          :key="column.id || column.slug"
          class="column-item"
          :to="{ name: 'column', params: { slug: column.slug } }"
        >
          <span>{{ column.title }}</span>
          <span class="column-count">{{ column.article_count ?? '' }}</span>
        </router-link>
      </div>
    </section>

    <section class="panel">
      <h3 class="panel-title">标签</h3>
      <div class="tag-cloud">
        <router-link
          v-for="tag in meta.tags.slice(0, 24)"
          :key="tag.slug || tag.name"
          class="tag-chip"
          :to="{ name: 'tag', params: { slug: tag.slug || tag.name } }"
        >
          {{ tag.name }}
        </router-link>
      </div>
    </section>

    <section class="panel">
      <h3 class="panel-title">关于</h3>
      <p class="about-mini mb-0">
        这是一个从零实现的个人博客。
        Django 4.2 负责数据与 API，Vue 3 负责页面。
      </p>
    </section>
  </aside>
</template>
