<script setup lang="ts">
import { onMounted } from 'vue'
import AmountKeypad from '@/components/AmountKeypad.vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import SubaccountPicker from '@/components/SubaccountPicker.vue'
import { useExchangeViewModel } from '@/viewmodels/exchange/useExchangeViewModel'

const {
  isLoading,
  loadError,
  retry,
  options,
  needsTwoSubaccounts,
  srcCurrency,
  tgtCurrency,
  amount,
  decimals,
  amountError,
  insufficient,
  estimateText,
  canContinue,
  load,
  proceed,
  goToCurrencies,
} = useExchangeViewModel()

// The subaccounts can change on «Divises», so the list is read on every visit.
onMounted(load)
</script>

<template>
  <AppShell title="Canviar" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="retry" />
    </section>

    <section v-else-if="needsTwoSubaccounts" class="card">
      <p class="notice">Necessites dos subcomptes per canviar divises.</p>
      <button type="button" class="button" @click="goToCurrencies()">Divises</button>
    </section>

    <template v-else>
      <section class="card">
        <SubaccountPicker
          id="exchange-src"
          v-model="srcCurrency"
          label="Subcompte d'origen"
          :options="options"
        />
      </section>

      <section class="card">
        <SubaccountPicker
          id="exchange-tgt"
          v-model="tgtCurrency"
          label="Subcompte de destí"
          :options="options"
          :disabled-code="srcCurrency"
        />
      </section>

      <section class="card">
        <AmountKeypad v-model:amount="amount" :currency-code="srcCurrency" :decimals="decimals">
          <template #hint>
            <p v-if="estimateText" class="estimate">{{ estimateText }}</p>
          </template>
        </AmountKeypad>
      </section>

      <!-- «Import massa petit» lives above the button (US-27-error-import-petit); -->
      <!-- «No tens prou saldo» lives under it (US-27 «Saldo insuficient»). -->
      <p v-if="amountError !== null && !insufficient" class="error" role="alert">{{ amountError }}</p>

      <button type="button" class="button" :disabled="!canContinue" @click="proceed()">Continuar</button>

      <p v-if="insufficient" class="error" role="alert">{{ amountError }}</p>
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

.notice {
  margin: 0 0 1rem;
  color: var(--color-muted);
}

.estimate {
  margin: 0 0 1rem;
  font-size: 1.5rem;
  line-height: 1.25;
  color: var(--color-muted);
  font-variant-numeric: tabular-nums;
}

.button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  line-height: 1.4;
  color: var(--color-expense);
}
</style>
