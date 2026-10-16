<script setup lang="ts">
import AppShell from '@/components/AppShell.vue'
</script>

<template>
  <AppShell title="Inici">
    <section class="card">
      <h2 class="label">Saldo</h2>
      <p class="value">—</p>
    </section>

    <section class="card">
      <h2 class="label">Total estalviat</h2>
      <p class="value">—</p>
    </section>

    <section class="card">
      <div class="section-header">
        <h2 class="label">Últims moviments</h2>
        <router-link to="/movements" class="see-all">Veure tots</router-link>
      </div>
      <p class="value">Encara no hi ha moviments</p>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.label {
  margin: 0 0 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.value {
  margin: 0;
  font-size: 1.125rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.see-all {
  font-size: 0.875rem;
}
</style>
