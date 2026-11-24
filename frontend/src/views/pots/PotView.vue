<script setup lang="ts">
import { onMounted } from 'vue'
import { PiggyBank } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import MovementRow from '@/components/MovementRow.vue'
import PotProgress from '@/components/PotProgress.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { usePotViewModel } from '@/viewmodels/pots/usePotViewModel'

const props = defineProps<{ potId: string }>()

const { pot, history, title, hasHistory, canWithdraw, isLoading, error, load } = usePotViewModel(props.potId)
const { isHidden } = useBalanceVisibility()

// Every visit reloads, so a contribution or a withdrawal shows up when coming back.
onMounted(load)
</script>

<template>
  <AppShell :title="title">
    <router-link :to="{ name: 'pots' }" class="back-link">← Guardioles</router-link>

    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <template v-else-if="pot">
      <section class="card summary" :style="{ '--pot-color': `var(--color-pot-${pot.color})` }">
        <span class="icon">
          <PiggyBank :size="24" />
        </span>
        <h2 class="label">Saldo de la guardiola</h2>
        <MoneyAmount class="balance" :cents="pot.balance" :hidden="isHidden" />
        <p v-if="pot.target !== null" class="target">
          Objectiu:
          <MoneyAmount :cents="pot.target" :hidden="isHidden" />
        </p>
        <PotProgress :pot="pot" :hidden="isHidden" />
        <div class="actions">
          <router-link :to="{ name: 'contribute', params: { potId: pot.id } }" class="action contribute">
            Aportar
          </router-link>
          <router-link
            v-if="canWithdraw"
            :to="{ name: 'withdraw', params: { potId: pot.id } }"
            class="action withdraw"
          >
            Retirar
          </router-link>
          <!-- A real disabled button: an empty pot has nothing to take out and it cannot get focus. -->
          <button v-else type="button" class="action withdraw" disabled>Retirar</button>
        </div>
      </section>

      <section class="card">
        <h2 class="label">Historial</h2>
        <ul v-if="hasHistory" class="history">
          <MovementRow v-for="entry in history" :key="entry.id" :movement="entry" :hidden="isHidden" />
        </ul>
        <EmptyState v-else message="Encara no hi has aportat diners" />
      </section>
    </template>
  </AppShell>
</template>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.summary {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.icon {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  margin-bottom: 0.75rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--pot-color) 14%, var(--color-surface));
  color: var(--pot-color);
}

.label {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.balance {
  display: block;
  margin: 0.25rem 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
}

.target {
  /* The progress bar below brings its own top margin, so no extra gap here. */
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  width: 100%;
}

.action {
  padding: 0.625rem 1rem;
  border: 1px solid transparent;
  border-radius: var(--radius);
  font: inherit;
  font-weight: 600;
  text-align: center;
}

.contribute {
  background: var(--color-primary);
  color: var(--color-surface);
}

.withdraw {
  border-color: var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}

.withdraw:disabled {
  background: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
}

.history {
  margin: 0.5rem 0 0;
  padding: 0;
}
</style>
