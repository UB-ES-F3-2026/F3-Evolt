<script setup lang="ts">
import AppShell from '@/components/AppShell.vue'
</script>

<template>
  <AppShell title="Recàrrega" back>
    <section class="card">
      <label class="label" for="amount">Import</label>
      <input id="amount" class="input" type="number" placeholder="0,00" disabled />
      <button class="button" type="button" disabled>Recarregar</button>
      <p class="placeholder">La recàrrega encara no està disponible</p>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.input {
  width: 100%;
  margin: 0.5rem 0;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e6ebf4;
  border-radius: var(--radius);
  font-size: 1rem;
}

.button {
  width: 100%;
  padding: 0.625rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: #ffffff;
  font-size: 1rem;
}

.placeholder {
  margin: 0.75rem 0 0;
  color: var(--color-muted);
  font-size: 0.875rem;
}
</style>
