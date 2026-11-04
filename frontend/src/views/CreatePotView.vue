<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import AppShell from '@/components/AppShell.vue'
import { useCreatePotViewModel } from '@/viewmodels/useCreatePotViewModel'

const {
  name,
  target,
  color,
  colorOptions,
  nameError,
  targetError,
  submitError,
  canSubmit,
  isSubmitting,
  touchName,
  submit,
} = useCreatePotViewModel()

const nameInput = useTemplateRef<HTMLInputElement>('nameInput')
onMounted(() => nameInput.value?.focus())
</script>

<template>
  <AppShell title="Crear guardiola">
    <form class="card" novalidate @submit.prevent="submit">
      <label class="label" for="pot-name">Nom</label>
      <input
        id="pot-name"
        ref="nameInput"
        v-model="name"
        class="input"
        :class="{ invalid: nameError }"
        type="text"
        autocomplete="off"
        placeholder="P. ex. Vacances"
        :disabled="isSubmitting"
        :aria-invalid="nameError !== null"
        :aria-describedby="nameError ? 'pot-name-error' : undefined"
        @blur="touchName"
      />
      <p v-if="nameError" id="pot-name-error" class="error" role="alert">{{ nameError }}</p>

      <label class="label" for="pot-target">Objectiu (opcional)</label>
      <div class="amount" :class="{ invalid: targetError }">
        <input
          id="pot-target"
          v-model="target"
          class="amount-input"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0,00"
          :disabled="isSubmitting"
          :aria-invalid="targetError !== null"
          :aria-describedby="targetError ? 'pot-target-error' : undefined"
        />
        <span class="currency" aria-hidden="true">€</span>
      </div>
      <p v-if="targetError" id="pot-target-error" class="error" role="alert">{{ targetError }}</p>

      <fieldset class="colors" :disabled="isSubmitting">
        <legend class="label">Color</legend>
        <label v-for="option in colorOptions" :key="option.value" class="swatch" :title="option.label">
          <input v-model="color" class="swatch-input" type="radio" name="pot-color" :value="option.value" />
          <span
            class="swatch-dot"
            :style="{ background: `var(--color-pot-${option.value})` }"
            aria-hidden="true"
          />
          <span class="visually-hidden">{{ option.label }}</span>
        </label>
      </fieldset>

      <p v-if="submitError" class="error submit-error" role="alert">{{ submitError }}</p>

      <button type="submit" class="button" :disabled="!canSubmit">
        {{ isSubmitting ? 'Creant…' : 'Crear' }}
      </button>
      <router-link :to="{ name: 'pots' }" class="cancel">Cancel·lar</router-link>
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

.label {
  margin-bottom: 0.25rem;
  padding: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.input,
.amount {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.input {
  margin-bottom: 1rem;
  padding: 0.75rem;
  color: var(--color-text);
  font: inherit;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.amount {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.amount:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.amount-input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-text);
  font: inherit;
  font-variant-numeric: tabular-nums;
}

.amount-input:focus {
  outline: none;
}

.currency {
  padding-right: 0.75rem;
  color: var(--color-muted);
}

.input.invalid,
.amount.invalid {
  border-color: var(--color-error);
}

.input.invalid:focus,
.amount.invalid:focus-within {
  box-shadow: 0 0 0 1px var(--color-error);
}

/* An error replaces the field's bottom space, so the form does not jump. */
.error {
  margin: -0.75rem 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}

.submit-error {
  margin-top: 0;
}

.colors {
  display: flex;
  flex-wrap: wrap;
  gap: 0.625rem;
  margin: 0 0 1.25rem;
  padding: 0;
  border: none;
}

.colors .label {
  width: 100%;
}

.swatch {
  position: relative;
  cursor: pointer;
}

.swatch-input {
  position: absolute;
  opacity: 0;
}

.swatch-dot {
  display: block;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-surface);
}

.swatch-input:checked + .swatch-dot {
  box-shadow:
    0 0 0 2px var(--color-surface),
    0 0 0 4px var(--color-text);
}

.swatch-input:focus-visible + .swatch-dot {
  outline: 2px solid var(--color-primary);
  outline-offset: 4px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.button {
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

.cancel {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  text-align: center;
}
</style>
