<script setup>
import ArticleEditor from '../components/ArticleEditor.vue'
</script>

<template>
  <section class="editor-page">
    <div class="container-narrow">
      <div class="editor-head">
        <div>
          <div class="hero-kicker">New article</div>
          <h1 class="editor-title mt-2">写一篇新文章</h1>
        </div>
      </div>
      <ArticleEditor />
    </div>
  </section>
</template>
