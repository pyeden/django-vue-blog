<script setup>
import { useToastStore } from '../stores/toast'
const toast = useToastStore()
</script>

<template>
  <div class="toast-host" aria-live="polite">
    <transition-group name="toast">
      <div
        v-for="item in toast.items"
        :key="item.id"
        class="toast-item"
        :class="item.type"
        @click="toast.dismiss(item.id)"
      >
        {{ item.message }}
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: opacity .18s ease, transform .18s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(7px); }
</style>
