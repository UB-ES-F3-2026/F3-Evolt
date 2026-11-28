<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { CircleCheck, Search, X } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import UserRow from '@/components/UserRow.vue'
import { AMOUNT_FORMAT_MESSAGE } from '@/models/errorMessages'
import { formatCents } from '@/models/money'
import { atUsername, displayName, initials } from '@/models/user'
import { useNewMoneyRequestViewModel } from '@/viewmodels/requests/useNewMoneyRequestViewModel'
import { useSplitExpenseViewModel } from '@/viewmodels/requests/useSplitExpenseViewModel'

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

// «A una persona» (US-15) or «Dividir una despesa» (US-30); each keeps what was typed in it.
const mode = ref<'single' | 'split'>('single')
const split = useSplitExpenseViewModel()
const {
  query: splitQuery,
  users: splitUsers,
  isSearching: splitIsSearching,
  showLoading: splitShowLoading,
  showNoResults: splitShowNoResults,
  error: splitSearchError,
  search: splitSearch,
  total,
  concept: splitConcept,
  participants,
  shareMode,
  myTyped,
  totalError,
  shares,
  sharesError,
  isFull,
  hasNoParticipants,
  canSend: canSendSplit,
  isSubmitting: isSubmittingSplit,
  submitError: splitSubmitError,
  confirmation: splitConfirmation,
} = split

// The initial list of people is there before typing anything, as in «Enviar diners».
onMounted(search)

/** A part with «Parts iguals»: nothing to show until there is a total. */
function shareText(cents: number | null): string {
  return cents === null ? '—' : formatCents(cents)
}
</script>

<template>
  <AppShell title="Demanar diners" back>
    <section v-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
    </section>

    <section v-else-if="splitConfirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ splitConfirmation.title }}</p>
      <p class="success-detail">{{ splitConfirmation.pending }}</p>
    </section>

    <template v-else>
      <div class="chips" role="group" aria-label="Tipus de sol·licitud">
        <button type="button" class="chip" :aria-pressed="mode === 'single'" @click="mode = 'single'">A una persona</button>
        <button type="button" class="chip" :aria-pressed="mode === 'split'" @click="mode = 'split'">Dividir una despesa</button>
      </div>

      <form v-if="mode === 'single'" class="form" novalidate @submit.prevent="send">
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

      <form v-else class="form" novalidate @submit.prevent="split.send">
        <label class="label" for="split-total">Import total</label>
        <div class="field" :class="{ invalid: totalError }">
          <input
            id="split-total"
            v-model="total"
            class="input"
            type="text"
            inputmode="decimal"
            autocomplete="off"
            placeholder="0,00"
            :aria-invalid="totalError !== null"
            aria-describedby="split-total-hint"
          />
          <span class="currency" aria-hidden="true">€</span>
        </div>
        <p v-if="totalError" class="error" role="alert">{{ totalError }}</p>
        <p v-else id="split-total-hint" class="hint">{{ AMOUNT_FORMAT_MESSAGE }}</p>

        <label class="label" for="split-concept">Concepte</label>
        <input
          id="split-concept"
          v-model="splitConcept"
          class="field input concept"
          type="text"
          autocomplete="off"
          :maxlength="maxConceptLength"
        />

        <section class="card participants">
          <span class="label first">Participants</span>
          <label class="search">
            <Search class="search-icon" :size="20" aria-hidden="true" />
            <span class="visually-hidden">Cerca un participant</span>
            <input
              v-model="splitQuery"
              class="search-input"
              type="search"
              :placeholder="isFull ? 'Màxim 9 participants' : '@usuari, telèfon o email'"
              :disabled="isFull"
              autocomplete="off"
              autocapitalize="off"
              spellcheck="false"
            />
          </label>
          <p v-if="isFull" class="hint">Màxim 9 participants</p>
          <p v-else-if="hasNoParticipants && !splitIsSearching" class="hint">Afegeix almenys un participant.</p>

          <template v-if="splitIsSearching && !isFull">
            <LoadingIndicator v-if="splitShowLoading" />
            <ErrorState v-else-if="splitSearchError" :message="splitSearchError" @retry="splitSearch" />
            <EmptyState v-else-if="splitShowNoResults" message="No hi ha resultats" />
            <ul v-else class="results">
              <li v-for="user in splitUsers" :key="user.id">
                <button
                  type="button"
                  class="person result"
                  :disabled="split.isChosen(user)"
                  @click="split.add(user)"
                >
                  <span class="avatar" aria-hidden="true">{{ initials(user) }}</span>
                  <span class="who">
                    <span class="name">{{ displayName(user) }}</span>
                    <span class="username">{{ atUsername(user) }}</span>
                  </span>
                  <span v-if="split.isChosen(user)" class="already">Ja hi és</span>
                </button>
              </li>
            </ul>
          </template>

          <template v-if="!hasNoParticipants">
            <div class="chips" role="group" aria-label="Com es reparteix">
              <button type="button" class="chip" :aria-pressed="shareMode === 'equal'" @click="split.setShareMode('equal')">
                Parts iguals
              </button>
              <button
                type="button"
                class="chip"
                :aria-pressed="shareMode === 'custom'"
                @click="split.setShareMode('custom')"
              >
                Imports personalitzats
              </button>
            </div>

            <ul class="shares">
              <li v-for="(participant, index) in participants" :key="participant.user.id" class="person share">
                <span class="avatar" aria-hidden="true">{{ initials(participant.user) }}</span>
                <span class="who">
                  <span class="name">{{ displayName(participant.user) }}</span>
                  <span class="username">{{ atUsername(participant.user) }}</span>
                </span>
                <span v-if="shareMode === 'equal'" class="amount">{{ shareText(shares.parts[index]) }}</span>
                <span v-else class="part-field">
                  <input
                    v-model="participant.typed"
                    class="part-input"
                    type="text"
                    inputmode="decimal"
                    autocomplete="off"
                    placeholder="0,00"
                    :aria-label="`Part de ${displayName(participant.user)}`"
                  />
                  <span aria-hidden="true">€</span>
                </span>
                <button
                  type="button"
                  class="remove"
                  :aria-label="`Treure ${displayName(participant.user)}`"
                  @click="split.remove(participant.user.id)"
                >
                  <X :size="16" />
                </button>
              </li>
              <!-- My part makes no request, but it counts in the total (US-30, criterion 3). -->
              <li class="person share me">
                <span class="avatar" aria-hidden="true">JO</span>
                <span class="who">
                  <span class="name">Jo</span>
                </span>
                <span v-if="shareMode === 'equal'" class="amount">{{ shareText(shares.mine) }}</span>
                <span v-else class="part-field">
                  <input
                    v-model="myTyped"
                    class="part-input"
                    type="text"
                    inputmode="decimal"
                    autocomplete="off"
                    placeholder="0,00"
                    aria-label="La meva part"
                  />
                  <span aria-hidden="true">€</span>
                </span>
              </li>
            </ul>
          </template>
        </section>

        <p v-if="sharesError" class="error shares-error" role="alert">{{ sharesError }}</p>
        <button type="submit" class="button" :disabled="!canSendSplit">
          {{ isSubmittingSplit ? 'Enviant…' : 'Enviar sol·licituds' }}
        </button>
        <p v-if="splitSubmitError" class="error submit-error" role="alert">{{ splitSubmitError }}</p>
      </form>
    </template>
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

.success-detail {
  margin: 0;
  color: var(--color-muted);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  padding: 0.375rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}

.chip[aria-pressed='true'] {
  border-color: var(--color-primary);
  background: var(--color-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.participants {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 1rem;
}

.participants .search {
  margin-bottom: 0;
}

.label.first {
  margin-top: 0;
}

.search-input:disabled {
  cursor: not-allowed;
}

.results,
.shares {
  margin: 0;
  padding: 0;
  list-style: none;
}

.person {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.625rem 0;
  border: none;
  background: transparent;
  color: var(--color-text);
  font: inherit;
  text-align: left;
}

.result {
  cursor: pointer;
}

.result:disabled {
  color: var(--color-muted);
  cursor: not-allowed;
}

.avatar {
  display: grid;
  flex: none;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--color-bg);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 700;
}

.who {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.name,
.username {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.username {
  color: var(--color-muted);
  font-size: 0.875rem;
}

.already {
  color: var(--color-muted);
  font-size: 0.875rem;
}

.amount {
  font-weight: 700;
}

.part-field {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 700;
}

.part-input {
  width: 5.5rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-weight: 700;
  text-align: right;
}

.part-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.remove {
  display: grid;
  place-items: center;
  padding: 0.25rem;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
}

.me .amount,
.me .part-field {
  margin-right: 1.5rem;
}

.shares-error {
  margin-top: 1rem;
}
</style>
