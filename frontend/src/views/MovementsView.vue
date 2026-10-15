<script setup>
import AppShell from '@/components/AppShell.vue'
</script>

<template>
  <AppShell title="Moviments" back>
    <section class="card">
      <p class="placeholder">Encara no hi ha moviments</p>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.placeholder {
  margin: 0;
  color: var(--color-muted);
}
</style>
