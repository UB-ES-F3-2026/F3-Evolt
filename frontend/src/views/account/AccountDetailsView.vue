<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import { useAccountDetailsViewModel } from '@/viewmodels/account/useAccountDetailsViewModel'

const { details, groupedIban, isLoading, loadError, notice, load, copyIban, share } = useAccountDetailsViewModel()

onMounted(load)
</script>

<template>
  <AppShell title="Dades del compte" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="load" />
    </section>

    <template v-else-if="details">
      <dl class="card details">
        <div class="row">
          <dt>IBAN</dt>
          <!-- The whole value is the button: touching it copies the IBAN (US-12, criterion 4). -->
          <dd>
            <button type="button" class="iban mono" aria-label="Copiar l'IBAN" @click="copyIban">{{ groupedIban }}</button>
          </dd>
        </div>
        <div class="row">
          <dt>BIC</dt>
          <dd class="mono">{{ details.bic }}</dd>
        </div>
        <div class="row">
          <dt>Titular</dt>
          <dd>{{ details.holder }}</dd>
        </div>
      </dl>

      <p class="hint">Toca l'IBAN per copiar-lo.</p>
      <button type="button" class="share" @click="share">Compartir</button>
    </template>

    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
  </AppShell>
</template>

<style scoped>
.card {
  margin: 0 0 0.75rem;
  padding: 0.25rem 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 0;
  border-bottom: 1px solid var(--color-border);
}

.row:last-child {
  border-bottom: none;
}

dt {
  color: var(--color-muted);
}

dd {
  margin: 0;
  text-align: right;
}

.mono {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  letter-spacing: 0.03em;
}

/* Two lines of three groups, as in the mockup US-12-dades-compte. */
.iban {
  max-width: 15ch;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-text);
  font-size: 1rem;
  line-height: 1.5;
  text-align: right;
  cursor: pointer;
}

.hint {
  margin: 0 0 0.75rem;
  color: var(--color-muted);
  font-size: 0.875rem;
  text-align: center;
}

.share {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.notice {
  position: fixed;
  right: 1.25rem;
  bottom: 1.75rem;
  left: 1.25rem;
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--color-text);
  color: var(--color-surface);
  text-align: center;
}
</style>
