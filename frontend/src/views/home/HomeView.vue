<script setup lang="ts">
import { onMounted } from 'vue'
import { Coins, Eye, EyeOff, PiggyBank, Plus, Send } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import CurrencyRow from '@/components/CurrencyRow.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import MovementRow from '@/components/MovementRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useCurrenciesViewModel } from '@/viewmodels/currencies/useCurrenciesViewModel'
import { useHomeViewModel } from '@/viewmodels/home/useHomeViewModel'

const { balance, totalSaved, lastMovements, hasMovements, isLoading, error, load } = useHomeViewModel()
const { isHidden, toggle } = useBalanceVisibility()
const {
  rows: currencyRows,
  totalCents: currenciesTotalCents,
  isLoading: currenciesIsLoading,
  error: currenciesError,
  load: loadCurrencies,
} = useCurrenciesViewModel()

// Every visit reloads, so a top-up made on another screen shows up (US-07 AC 4).
onMounted(() => {
  void load()
  void loadCurrencies()
})
</script>

<template>
  <AppShell title="Inici">
    <section v-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <LoadingIndicator v-else-if="isLoading" />

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
        <div class="actions">
          <router-link :to="{ name: 'topup' }" class="add-money">
            <Plus :size="18" />
            Afegir diners
          </router-link>
          <router-link :to="{ name: 'payments' }" class="send-link">
            <Send :size="18" />
            Enviar diners
          </router-link>
          <router-link :to="{ name: 'pots' }" class="pots-link">
            <PiggyBank :size="18" />
            Guardioles
          </router-link>
          <router-link :to="{ name: 'currencies' }" class="currencies-link">
            <Coins :size="18" />
            Divises
          </router-link>
        </div>
      </section>

      <section class="card">
        <div class="section-header">
          <h2 class="label">Divises</h2>
        </div>
        <LoadingIndicator v-if="currenciesIsLoading" />
        <ErrorState v-else-if="currenciesError" :message="currenciesError" @retry="loadCurrencies" />
        <template v-else>
          <ul class="currency-rows">
            <CurrencyRow
              v-for="row in currencyRows" :key="row.code" :code="row.code" :name="row.name"
              :symbol="row.symbol" :amount-text="row.amountText" :hidden="isHidden"
            />
          </ul>
          <p class="total-line">
            Total ≈ <strong><MoneyAmount :cents="currenciesTotalCents" :hidden="isHidden" /></strong>
          </p>
        </template>
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
            :to="{ name: 'movement', params: { movementId: movement.id } }"
          />
        </ul>
        <EmptyState v-else />
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

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.add-money,
.send-link,
.pots-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  font-weight: 600;
}

.add-money {
  background: var(--color-primary);
  color: var(--color-surface);
}

.send-link,
.pots-link {
  background: var(--color-surface);
  color: var(--color-primary);
}

.currencies-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  font-weight: 600;
  background: var(--color-surface);
  color: var(--color-primary);
}

.see-all {
  font-size: 0.875rem;
}

.movements {
  margin: 0.5rem 0 0;
  padding: 0;
}

.currency-rows {
  list-style: none;
  padding: 0;
  margin: 0;
}

.total-line {
  border-top: 1px solid var(--color-border);
  padding-top: 0.75rem;
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  font-weight: 600;
}
</style>
