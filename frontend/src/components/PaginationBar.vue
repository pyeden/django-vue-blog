<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  totalCount: { type: Number, default: 0 },
})
const emit = defineEmits(['update:page'])

const pages = computed(() => {
  const total = props.totalPages
  const current = props.page
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const set = new Set([1, total, current, current - 1, current + 1])
  if (current <= 3) [2, 3, 4].forEach((n) => set.add(n))
  if (current >= total - 2) [total - 3, total - 2, total - 1].forEach((n) => set.add(n))
  const ordered = [...set].filter((n) => n >= 1 && n <= total).sort((a, b) => a - b)
  const result = []
  ordered.forEach((n, i) => {
    if (i && n - ordered[i - 1] > 1) result.push('...')
    result.push(n)
  })
  return result
})

function go(page) {
  if (page === props.page || page < 1 || page > props.totalPages) return
  emit('update:page', page)
}
</script>

<template>
  <div v-if="totalPages > 1" class="pagination-bar">
    <button class="page-btn" type="button" :disabled="page <= 1" @click="go(page - 1)">
      <i class="bi bi-chevron-left"></i>
    </button>
    <template v-for="(item, index) in pages" :key="`${item}-${index}`">
      <span v-if="item === '...'" class="page-info">…</span>
      <button
        v-else
        class="page-btn"
        :class="{ active: item === page }"
        type="button"
        @click="go(item)"
      >
        {{ item }}
      </button>
    </template>
    <button class="page-btn" type="button" :disabled="page >= totalPages" @click="go(page + 1)">
      <i class="bi bi-chevron-right"></i>
    </button>
    <span class="page-info">共 {{ totalCount }} 篇</span>
  </div>
</template>
