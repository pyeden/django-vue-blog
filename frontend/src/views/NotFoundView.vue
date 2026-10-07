<template>
  <section class="auth-page">
    <div class="auth-card text-center">
      <div class="hero-kicker justify-content-center">404</div>
      <h1 class="auth-title">这一页不存在</h1>
      <p class="auth-sub mb-4">可能是链接过期，或者文章已经被删除。</p>
      <router-link class="btn btn-accent" :to="{ name: 'home' }">回到首页</router-link>
    </div>
  </section>
</template>
