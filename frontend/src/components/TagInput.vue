<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  placeholder: { type: String, default: '输入标签后回车' },
})
const emit = defineEmits(['update:modelValue'])
const draft = ref('')

function add() {
  const parts = draft.value
    .split(/[,，]/)
    .map((item) => item.trim())
    .filter(Boolean)
  if (!parts.length) return
  const next = [...props.modelValue]
  parts.forEach((part) => {
    if (!next.includes(part)) next.push(part)
  })
  emit('update:modelValue', next.slice(0, 10))
  draft.value = ''
}

function remove(tag) {
  emit('update:modelValue', props.modelValue.filter((item) => item !== tag))
}

function onKeydown(event) {
  if (event.key === 'Enter' || event.key === ',') {
    event.preventDefault()
    add()
  }
  if (event.key === 'Backspace' && !draft.value && props.modelValue.length) {
    remove(props.modelValue[props.modelValue.length - 1])
  }
}
</script>

<template>
  <div>
    <div class="tag-row mb-2">
      <span v-for="tag in modelValue" :key="tag" class="tag-chip">
        # {{ tag }}
        <button class="tag-remove" type="button" @click="remove(tag)" aria-label="移除标签">×</button>
      </span>
    </div>
    <input
      v-model="draft"
      class="form-control"
      :placeholder="placeholder"
      @keydown="onKeydown"
      @blur="add"
    />
  </div>
</template>

<style scoped>
.tag-remove {
  margin-left: 5px;
  border: 0;
  background: transparent;
  color: var(--faint);
  line-height: 1;
  padding: 0;
}
.tag-remove:hover { color: var(--accent); }
</style>
