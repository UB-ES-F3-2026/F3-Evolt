<script setup lang="ts">
withDefaults(defineProps<{ title: string; back?: boolean }>(), { back: false })
</script>

<template>
  <div class="shell">
    <header class="header">
      <router-link v-if="back" to="/" class="back">← Inici</router-link>
      <h1 class="title">{{ title }}</h1>
    </header>
    <main class="content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  border-bottom: 1px solid #e6ebf4;
}

.title {
  margin: 0;
  font-size: 1.25rem;
}

.back {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  color: var(--color-primary);
  font-size: 0.875rem;
}

.content {
  padding: 1.25rem;
  max-width: 48rem;
  margin: 0 auto;
}
</style>
