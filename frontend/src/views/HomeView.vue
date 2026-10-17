<script setup lang="ts">
import { onMounted } from 'vue'
import { Eye, EyeOff } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import MovementRow from '@/components/MovementRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useHomeViewModel } from '@/viewmodels/useHomeViewModel'

const { balance, totalSaved, lastMovements, hasMovements, isLoading, error, load } = useHomeViewModel()
const { isHidden, toggle } = useBalanceVisibility()

// Every visit reloads, so a top-up made on another screen shows up (US-07 AC 4).
onMounted(load)
</script>

<template>
  <AppShell title="Inici">
    <section v-if="error" class="card state">
      <p class="state-text" role="alert">{{ error }}</p>
      <button type="button" class="retry" @click="load">Reintentar</button>
    </section>

    <section v-else-if="isLoading" class="card state">
      <p class="state-text">Carregant…</p>
    </section>

    <template v-else>
      <section class="card">
        <div class="section-header">
          <h2 class="label">Saldo disponible</h2>
          <button
            type="button"
            class="eye"
            :aria-label="isHidden ? 'Mostrar els imports' : 'Amagar els imports'"
            :title="isHidden ? 'Mostrar els imports' : 'Amagar els imports'"
            @click="toggle"
          >
            <EyeOff v-if="isHidden" :size="20" />
            <Eye v-else :size="20" />
          </button>
        </div>
        <MoneyAmount class="balance" :cents="balance" :hidden="isHidden" />
        <p class="saved">
          Total estalviat a guardioles:
          <MoneyAmount class="saved-amount" :cents="totalSaved" :hidden="isHidden" />
        </p>
      </section>

      <section class="card">
        <div class="section-header">
          <h2 class="label">Últims moviments</h2>
          <router-link to="/movements" class="see-all">Veure tots</router-link>
        </div>
        <ul v-if="hasMovements" class="movements">
          <MovementRow
            v-for="movement in lastMovements"
            :key="movement.id"
            :movement="movement"
            :hidden="isHidden"
          />
        </ul>
        <p v-else class="state-text">Encara no tens moviments</p>
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.label {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.eye {
  display: grid;
  place-items: center;
  padding: 0.375rem;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
}

.eye:hover {
  background: var(--color-bg);
}

.balance {
  display: block;
  margin: 0.25rem 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
}

.saved {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.saved-amount {
  color: var(--color-text);
  font-weight: 600;
}

.see-all {
  font-size: 0.875rem;
}

.movements {
  margin: 0.5rem 0 0;
  padding: 0;
}

.state {
  text-align: center;
}

.state-text {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
}

.retry {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-primary);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}
</style>
