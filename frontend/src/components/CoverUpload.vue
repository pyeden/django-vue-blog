<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { mediaUrl } from '../utils/format'

const props = defineProps({
  modelValue: { type: Object, default: null },
  existing: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
const objectUrl = ref('')
const input = ref(null)

const preview = computed(() => objectUrl.value || mediaUrl(props.existing))

function revoke() {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
}

function onChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) return
  revoke()
  objectUrl.value = URL.createObjectURL(file)
  emit('update:modelValue', file)
}

function clear() {
  revoke()
  emit('update:modelValue', null)
  if (input.value) input.value.value = ''
}

onBeforeUnmount(revoke)
</script>

<template>
  <div class="cover-drop">
    <img v-if="preview" class="cover-preview" :src="preview" alt="封面预览" />
    <div class="d-flex justify-content-center gap-2 align-items-center">
      <button class="btn btn-sm btn-ghost" type="button" @click="input?.click()">
        {{ preview ? '更换封面' : '选择封面' }}
      </button>
      <button v-if="preview" class="btn btn-sm btn-quiet" type="button" @click="clear">移除</button>
    </div>
    <div class="mt-1">JPG / PNG，建议横图 1200×800</div>
    <input ref="input" class="d-none" type="file" accept="image/*" @change="onChange" />
  </div>
</template>
