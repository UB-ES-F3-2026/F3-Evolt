<script setup>
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import { formatCents } from '@/models/money'
import { useMovementsViewModel } from '@/viewmodels/useMovementsViewModel'

const { isLoading, error, items, isEmpty, hasMore, load, loadMore } = useMovementsViewModel()

onMounted(load)
</script>

<template>
  <AppShell title="Moviments" back>
    <p v-if="error" class="state error" role="alert">{{ error }}</p>

    <section class="card">
      <p v-if="isLoading && items.length === 0" class="state">Carregant…</p>
      <p v-else-if="isEmpty" class="state">Encara no hi ha moviments</p>

      <ul v-else class="list">
        <li v-for="movement in items" :key="movement.id" class="row">
          <span class="concept">
            {{ movement.concept }}
            <small class="date">{{ movement.date }}</small>
          </span>
          <span :class="['amount', movement.type]">
            {{ movement.type === 'income' ? '+' : '−' }}{{ formatCents(movement.amount) }}
          </span>
        </li>
      </ul>

      <button v-if="hasMore" class="button" type="button" :disabled="isLoading" @click="loadMore">
        {{ isLoading ? 'Carregant…' : 'Carregar més' }}
      </button>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.state {
  margin: 0;
  color: var(--color-muted);
}

.error {
  color: var(--color-expense);
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eef2f8;
}

.concept {
  display: flex;
  flex-direction: column;
}

.date {
  color: var(--color-muted);
  font-size: 0.75rem;
}

.amount.income {
  color: var(--color-income);
}

.amount.expense {
  color: var(--color-expense);
}

.button {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.625rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-primary);
  font-size: 1rem;
  cursor: pointer;
}

.button:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
