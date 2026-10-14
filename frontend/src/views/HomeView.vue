<script setup>
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import { formatCents } from '@/models/money'
import { useHomeViewModel } from '@/viewmodels/useHomeViewModel'

const { isLoading, error, balance, totalSaved, lastMovements, load } = useHomeViewModel()

onMounted(load)
</script>

<template>
  <AppShell title="Inici">
    <p v-if="isLoading" class="state">Carregant…</p>
    <p v-else-if="error" class="state error" role="alert">{{ error }}</p>

    <template v-else>
      <section class="card">
        <h2 class="label">Saldo</h2>
        <p class="value">{{ formatCents(balance ?? 0) }}</p>
      </section>

      <section class="card">
        <h2 class="label">Total estalviat</h2>
        <p class="value">{{ formatCents(totalSaved ?? 0) }}</p>
      </section>

      <section class="card">
        <h2 class="label">Últims moviments</h2>
        <p v-if="lastMovements.length === 0" class="value">Encara no hi ha moviments</p>
        <ul v-else class="list">
          <li v-for="movement in lastMovements" :key="movement.id" class="row">
            <span>{{ movement.concept }}</span>
            <span :class="['amount', movement.type]">
              {{ movement.type === 'income' ? '+' : '−' }}{{ formatCents(movement.amount) }}
            </span>
          </li>
        </ul>
        <router-link to="/movements" class="link">Veure tots els moviments</router-link>
      </section>
    </template>
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

.row:last-child {
  border-bottom: none;
}

.amount.income {
  color: var(--color-income);
}

.amount.expense {
  color: var(--color-expense);
}

.link {
  display: inline-block;
  margin-top: 0.75rem;
  font-size: 0.875rem;
}
</style>
