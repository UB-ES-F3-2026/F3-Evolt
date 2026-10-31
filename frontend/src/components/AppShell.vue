<script setup lang="ts">
import { Menu } from '@lucide/vue'
import { useSessionMenuViewModel } from '@/viewmodels/useSessionMenuViewModel'

withDefaults(defineProps<{ title: string; back?: boolean }>(), { back: false })

// The one component with a ViewModel: every screen has this header, so the alternative
// is repeating the same menu and its logout in all of them.
const { isLoggedIn, logOut } = useSessionMenuViewModel()
</script>

<template>
  <div class="shell">
    <header class="header">
      <router-link v-if="back" to="/" class="back">← Inici</router-link>
      <h1 class="title">{{ title }}</h1>
      <details v-if="isLoggedIn" class="menu">
        <summary class="menu-button" aria-label="Menú" title="Menú">
          <Menu :size="20" />
        </summary>
        <button type="button" class="menu-item" @click="logOut">Tancar sessió</button>
      </details>
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

.menu {
  position: relative;
  margin-left: auto;
}

.menu-button {
  display: grid;
  place-items: center;
  padding: 0.375rem;
  border-radius: 50%;
  color: var(--color-muted);
  cursor: pointer;
  list-style: none;
}

.menu-button::-webkit-details-marker {
  display: none;
}

.menu-button:hover {
  background: var(--color-bg);
}

.menu-item {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1;
  margin-top: 0.25rem;
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: 0.875rem;
  white-space: nowrap;
  cursor: pointer;
}

.menu-item:hover {
  background: var(--color-bg);
}

.content {
  padding: 1.25rem;
  max-width: 48rem;
  margin: 0 auto;
}
</style>
