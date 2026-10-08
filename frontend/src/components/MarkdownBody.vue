<script setup>
import { computed } from 'vue'
import { sanitizeHtml } from '../utils/markdown'

const props = defineProps({ html: { type: String, default: '' } })
const safeHtml = computed(() => sanitizeHtml(props.html))
</script>

<template>
  <div class="prose" v-html="safeHtml"></div>
</template>
