<script setup lang="ts">
import { onMounted } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MovementRow from '@/components/MovementRow.vue'
import PrimaryButton from '@/components/PrimaryButton.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useReportProblemViewModel } from '@/viewmodels/useReportProblemViewModel'

const props = defineProps<{ movementId: string }>()

const { movement, isLoading, loadError, description, error, isSubmitting, isSent, load, submit } =
  useReportProblemViewModel(props.movementId)
const { isHidden } = useBalanceVisibility()

onMounted(load)
</script>

<template>
  <AppShell title="Reportar un problema">
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="load" />
    </section>

    <section v-else-if="isSent" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">Hem rebut el teu informe</p>
      <router-link :to="{ name: 'movement', params: { movementId } }">Tornar al moviment</router-link>
    </section>

    <form v-else-if="movement" class="card" novalidate @submit.prevent="submit">
      <ul class="movement">
        <MovementRow :movement="movement" :hidden="isHidden" />
      </ul>

      <label class="label" for="report-description">Què passa amb aquest moviment?</label>
      <textarea
        id="report-description"
        v-model="description"
        class="input"
        :class="{ invalid: error }"
        rows="5"
        :disabled="isSubmitting"
        :aria-invalid="error !== null"
        :aria-describedby="error ? 'report-error' : undefined"
      />
      <p v-if="error" id="report-error" class="error" role="alert">{{ error }}</p>

      <PrimaryButton :disabled="isSubmitting">{{ isSubmitting ? 'Enviant…' : 'Enviar' }}</PrimaryButton>
      <router-link :to="{ name: 'movement', params: { movementId } }" class="cancel">Cancel·lar</router-link>
    </form>
  </AppShell>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.movement {
  margin: 0 0 1rem;
  padding: 0;
}

.label {
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.input {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  resize: vertical;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.input.invalid {
  border-color: var(--color-error);
}

.input.invalid:focus {
  box-shadow: 0 0 0 1px var(--color-error);
}

/* An error replaces the field's bottom space, so the form does not jump. */
.error {
  margin: -0.75rem 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}

.cancel {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  text-align: center;
}

.success {
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
