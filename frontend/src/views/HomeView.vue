<script setup>
import ArticleFeed from '../components/ArticleFeed.vue'
const title = import.meta.env.VITE_BLOG_TITLE || '纸上集'
</script>

<template>
  <div>
    <section class="hero">
      <div class="container-narrow hero-grid">
        <div>
          <div class="hero-kicker">Django × Vue · 个人博客</div>
          <h1 class="hero-title">把想法写成<br /><em>可以慢慢读</em>的页面。</h1>
          <p class="hero-sub">
            这是我在 MacBook 上按《Django 博客教程》的功能路线重做的一站：
            Django 负责文章、评论与权限，Vue 负责阅读与写作的界面。
            不追求信息密度，只希望每一篇都值得停留。
          </p>
        </div>
        <div class="hero-side">
          <strong>43</strong>
          <span>章重写教程</span>
          <div class="side-line">从创建 app 到子路径部署，每一步都在 macOS 上实际跑过。</div>
          <div class="side-line">源码：<a href="https://github.com/pyeden/django-vue-blog" target="_blank" rel="noopener">pyeden/django-vue-blog</a></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container-narrow">
        <ArticleFeed kicker="Latest" title="最近写了什么" :show-sidebar="true" />
      </div>
    </section>
  </div>
</template>
