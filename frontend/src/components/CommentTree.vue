<script setup>
import CommentNode from './CommentNode.vue'
import EmptyState from './EmptyState.vue'

defineProps({
  comments: { type: Array, default: () => [] },
  slug: { type: String, required: true },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['changed'])
</script>

<template>
  <div>
    <div v-if="loading" class="py-3">
      <div class="skeleton skeleton-line" v-for="n in 3" :key="n"></div>
    </div>
    <div v-else-if="comments.length" class="comment-list">
      <CommentNode
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :slug="slug"
        @changed="emit('changed')"
      />
    </div>
    <EmptyState v-else icon="bi-chat-square" title="还没有评论" text="来做第一个留言的人。" />
  </div>
</template>
