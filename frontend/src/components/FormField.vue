<script setup lang="ts">
withDefaults(
  defineProps<{
    id: string
    label: string
    type?: 'text' | 'password'
    autocomplete?: string
    /** Text for the user, already in Catalan. It turns the field red. */
    error?: string | null
    disabled?: boolean
  }>(),
  { type: 'text', autocomplete: 'off', error: null, disabled: false },
)

const value = defineModel<string>({ required: true })
</script>

<template>
  <div class="form-field">
    <label class="label" :for="id">{{ label }}</label>
    <input
      :id="id"
      v-model="value"
      class="input"
      :class="{ invalid: error }"
      :type="type"
      :autocomplete="autocomplete"
      :disabled="disabled"
      :aria-invalid="error !== null"
      :aria-describedby="error ? `${id}-error` : undefined"
    />
    <p v-if="error" :id="`${id}-error`" class="error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.form-field {
  margin-bottom: 1rem;
}

.label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
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

.error {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-error);
}
</style>
