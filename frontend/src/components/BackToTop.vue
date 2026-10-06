<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 420
}

function toTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <transition name="backtop">
    <button v-if="visible" class="backtop" type="button" aria-label="回到顶部" @click="toTop">
      <i class="bi bi-arrow-up"></i>
    </button>
  </transition>
</template>

<style scoped>
.backtop {
  position: fixed;
  right: 22px;
  bottom: 82px;
  z-index: 1500;
  width: 40px;
  height: 40px;
  border: 1px solid var(--line-strong);
  border-radius: 50%;
  background: rgba(255, 252, 246, .9);
  color: var(--muted);
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}
.backtop:hover { border-color: var(--accent); color: var(--accent); }
.backtop-enter-active, .backtop-leave-active { transition: opacity .18s ease, transform .18s ease; }
.backtop-enter-from, .backtop-leave-to { opacity: 0; transform: translateY(6px); }
@media (max-width: 767.98px) { .backtop { right: 16px; bottom: 76px; } }
</style>
