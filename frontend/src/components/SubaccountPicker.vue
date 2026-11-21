<script setup lang="ts">
import { formatMinor } from '@/models/money'
import type { CurrencyCode } from '@/models/exchange'

interface SubaccountPickerOption {
  code: CurrencyCode
  name: string
  balanceMinor: number
}

const props = withDefaults(
  defineProps<{
    /** Caller-provided, used by the label and the select. */
    id: string
    label: string
    /** The selected currency code. */
    modelValue: string
    options: SubaccountPickerOption[]
    /** Option that must not be selectable: the other side of the exchange. */
    disabledCode?: string | null
    disabledTag?: string
  }>(),
  { disabledCode: null, disabledTag: "és l'origen" },
)

const emit = defineEmits<{ 'update:modelValue': [string] }>()

function optionText(option: SubaccountPickerOption): string {
  const text = `${option.code} · ${option.name} — ${formatMinor(option.balanceMinor, option.code)}`
  return option.code === props.disabledCode ? `${text} · ${props.disabledTag}` : text
}

function onChange(event: Event): void {
  emit('update:modelValue', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="subaccount-picker">
    <label class="label" :for="id">{{ label }}</label>
    <select :id="id" class="select" :value="modelValue" @change="onChange">
      <option
        v-for="option in options"
        :key="option.code"
        :value="option.code"
        :disabled="option.code === disabledCode"
      >
        {{ optionText(option) }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
}

.select:focus {
  outline: none;
  box-shadow: 0 0 0 1px var(--color-primary);
}
</style>
