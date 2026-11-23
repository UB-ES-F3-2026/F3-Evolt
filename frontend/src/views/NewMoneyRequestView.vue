<script setup lang="ts">
import { onMounted } from 'vue'
import { CircleCheck, Search } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import UserRow from '@/components/UserRow.vue'
import { AMOUNT_FORMAT_MESSAGE } from '@/models/errorMessages'
import { useNewMoneyRequestViewModel } from '@/viewmodels/useNewMoneyRequestViewModel'

const {
  query,
  users,
  showLoading,
  showNoResults,
  error,
  search,
  recipient,
  amount,
  concept,
  maxConceptLength,
  amountError,
  canSend,
  isSubmitting,
  submitError,
  confirmation,
  choose,
  send,
} = useNewMoneyRequestViewModel()

// The initial list of people is there before typing anything, as in «Enviar diners».
onMounted(search)
</script>

<template>
  <AppShell title="Demanar diners" back>
    <section v-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
    </section>

    <form v-else class="form" novalidate @submit.prevent="send">
      <span class="label">Destinatari</span>
      <label class="search">
        <Search class="search-icon" :size="20" aria-hidden="true" />
        <span class="visually-hidden">Cerca el destinatari</span>
        <input
          v-model="query"
          class="search-input"
          type="search"
          placeholder="@usuari, telèfon o email"
          autocomplete="off"
          autocapitalize="off"
          spellcheck="false"
        />
      </label>

      <LoadingIndicator v-if="showLoading" />
      <section v-else-if="error" class="card">
        <ErrorState :message="error" @retry="search" />
      </section>
      <section v-else-if="showNoResults" class="card">
        <EmptyState message="No hi ha resultats" />
      </section>
      <section v-else class="card list">
        <ul class="users">
          <UserRow
            v-for="user in users"
            :key="user.id"
            :user="user"
            :selected="recipient?.id === user.id"
            @select="choose(user)"
          />
        </ul>
      </section>

      <label class="label" for="request-amount">Import</label>
      <div class="field" :class="{ invalid: amountError }">
        <input
          id="request-amount"
          v-model="amount"
          class="input"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0,00"
          :aria-invalid="amountError !== null"
          aria-describedby="request-amount-hint"
        />
        <span class="currency" aria-hidden="true">€</span>
      </div>
      <p v-if="amountError" class="error" role="alert">{{ amountError }}</p>
      <p v-else id="request-amount-hint" class="hint">{{ AMOUNT_FORMAT_MESSAGE }}</p>

      <label class="label" for="request-concept">Concepte</label>
      <input
        id="request-concept"
        v-model="concept"
        class="field input concept"
        type="text"
        autocomplete="off"
        :maxlength="maxConceptLength"
      />

      <button type="submit" class="button" :disabled="!canSend">
        {{ isSubmitting ? 'Enviant…' : 'Enviar sol·licitud' }}
      </button>
      <p v-if="submitError" class="error submit-error" role="alert">{{ submitError }}</p>
      <router-link :to="{ name: 'money-requests' }" class="secondary">Cancel·lar</router-link>
    </form>
  </AppShell>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
}

.label {
  margin: 0.75rem 0 0.375rem;
  color: var(--color-muted);
}

.search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 0 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.search:focus-within,
.field:focus-within {
  border-color: var(--color-primary);
}

.search-icon {
  flex: none;
  color: var(--color-muted);
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem 0;
  border: none;
  background: transparent;
  color: var(--color-text);
  font: inherit;
}

.search-input:focus,
.input:focus {
  outline: none;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.list {
  overflow: hidden;
}

.users {
  margin: 0;
  padding: 0;
}

.field {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.field.invalid {
  border-color: var(--color-error);
}

.input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-text);
  font: inherit;
}

.concept {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.currency {
  padding-right: 1rem;
  color: var(--color-muted);
}

.hint,
.error {
  margin: 0.375rem 0 0;
  font-size: 0.875rem;
}

.hint {
  color: var(--color-muted);
}

.error {
  color: var(--color-error);
}

.submit-error {
  text-align: center;
}

.button {
  margin-top: 1.5rem;
  padding: 0.875rem;
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

.secondary {
  margin-top: 1rem;
  padding: 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font-weight: 600;
  text-align: center;
}

.success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1.25rem;
  text-align: center;
}

.success-icon {
  color: var(--color-income);
}

.success-text {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}
</style>
