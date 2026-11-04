<script setup>
const year = new Date().getFullYear()
const title = import.meta.env.VITE_BLOG_TITLE || '纸上集'
</script>

<template>
  <footer class="site-footer">
    <div class="container-narrow footer-inner">
      <div class="footer-brand">{{ title }} · Django + Vue 个人博客</div>
      <div class="footer-links">
        <router-link :to="{ name: 'home' }">首页</router-link>
        <router-link :to="{ name: 'search' }">搜索</router-link>
        <a href="https://github.com/pyeden/django-vue-blog" target="_blank" rel="noopener">源码</a>
        <span>© {{ year }}</span>
      </div>
    </div>
  </footer>
</template>
