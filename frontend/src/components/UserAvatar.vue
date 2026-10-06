<script setup>
import { computed } from 'vue'
import { avatarTone, initials, mediaUrl } from '../utils/format'

const props = defineProps({
  name: { type: String, default: '' },
  avatar: { type: String, default: '' },
  size: { type: Number, default: 34 },
})

const src = computed(() => mediaUrl(props.avatar))
const tone = computed(() => avatarTone(props.name))
const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  background: `hsl(${tone.value} 34% 88%)`,
  color: `hsl(${tone.value} 42% 30%)`,
  fontSize: `${Math.max(11, props.size * 0.38)}px`,
}))
</script>

<template>
  <span class="user-avatar" :style="style" :title="name">
    <img v-if="src" :src="src" :alt="name" loading="lazy" />
    <template v-else>{{ initials(name) }}</template>
  </span>
</template>

<style scoped>
.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  overflow: hidden;
  border-radius: 50%;
  font-family: var(--serif);
  line-height: 1;
  user-select: none;
}
.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
