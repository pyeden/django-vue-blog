<script setup>
defineProps({
  icon: { type: String, default: 'bi-journal-text' },
  title: { type: String, default: '这里还没有内容' },
  text: { type: String, default: '' },
})
</script>

<template>
  <div class="empty-state">
    <i :class="['bi', icon]"></i>
    <div class="empty-title">{{ title }}</div>
    <div v-if="text">{{ text }}</div>
    <slot />
  </div>
</template>
