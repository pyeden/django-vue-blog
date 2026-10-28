<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({ toc: { type: Array, default: () => [] } })
const active = ref('')
let observer = null

function scrollTo(anchor) {
  const el = document.getElementById(anchor)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  active.value = anchor
}

onMounted(() => {
  const headings = Array.from(document.querySelectorAll('.article-body .prose h1[id], .article-body .prose h2[id], .article-body .prose h3[id], .article-body .prose h4[id], .article-body .prose h5[id], .article-body .prose h6[id]'))
  if (!headings.length) return
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      if (visible[0]) active.value = visible[0].target.id
    },
    { rootMargin: '-90px 0px -70% 0px', threshold: [0, 1] }
  )
  headings.forEach((heading) => observer.observe(heading))
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <aside v-if="toc.length" class="toc-rail">
    <h3 class="toc-title">本文目录</h3>
    <nav class="toc-list">
      <a
        v-for="item in toc"
        :key="item.anchor || item.text"
        class="toc-link"
        :class="[`level-${item.level}`, { active: active === item.anchor }]"
        :href="`#${item.anchor}`"
        @click.prevent="scrollTo(item.anchor)"
      >
        {{ item.text }}
      </a>
    </nav>
  </aside>
</template>
