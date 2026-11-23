<script setup lang="ts">
import { computed, useId } from 'vue'
import type { CurrencyCode } from '@/models/exchange'
import { currencySymbol } from '@/models/money'

const props = withDefaults(
  defineProps<{
    /** The typed value, e.g. `100,00`. */
    amount: string
    label?: string
    /** When set, the symbol of the currency shows after the amount. */
    currencyCode?: CurrencyCode
    /** Fraction digits the amount accepts; `0` is for currencies without decimals (JPY). */
    decimals?: 0 | 2
    disabled?: boolean
    /** Text for the user, already in Catalan. It turns the field red. */
    error?: string | null
  }>(),
  { label: 'Import', currencyCode: undefined, decimals: 2, disabled: false, error: null },
)

const emit = defineEmits<{ 'update:amount': [string] }>()

const inputId = useId()
const errorId = `${inputId}-error`

/** The keypad stops growing the integer part here, so a typo cannot overflow the amount. */
const MAX_INTEGER_DIGITS = 9

interface Key {
  text: string
  action: 'digit' | 'comma' | 'backspace'
  /** Accessible name for the keys that are not a digit. */
  ariaLabel?: string
}

const keys = computed<Key[]>(() => {
  const digits: Key[] = ['1', '2', '3', '4', '5', '6', '7', '8', '9'].map((digit): Key => ({
    text: digit,
    action: 'digit',
  }))
  const comma: Key[] = props.decimals > 0 ? [{ text: ',', action: 'comma', ariaLabel: 'Coma decimal' }] : []
  return [
    ...digits,
    ...comma,
    { text: '0', action: 'digit' },
    { text: '⌫', action: 'backspace', ariaLabel: 'Esborra un caràcter' },
  ]
})

/**
 * Keeps only what a decimal amount can hold: digits, one comma and at most
 * `decimals` fraction digits. It fixes both the keypad and a pasted value, so
 * the component never needs to validate anything.
 */
function sanitize(text: string): string {
  const cleaned = text.replace(/\./g, ',').replace(/[^\d,]/g, '')

  // With `decimals 0` the comma starts a fraction, and a whole-unit currency has
  // none: cut at it (`'5,5'` → `'5'`). Dropping just the comma would read it as `'55'`.
  if (props.decimals === 0) return (cleaned.split(',')[0] ?? '').slice(0, MAX_INTEGER_DIGITS)

  const [integerPart = '', ...fractionParts] = cleaned.split(',')
  const integer = integerPart.slice(0, MAX_INTEGER_DIGITS)
  if (fractionParts.length === 0) return integer

  // Several commas collapse into the first one.
  return `${integer},${fractionParts.join('').slice(0, props.decimals)}`
}

function update(value: string): void {
  if (value !== props.amount) emit('update:amount', value)
}

function onKey(key: Key): void {
  if (key.action === 'backspace') {
    update(props.amount.slice(0, -1))
    return
  }
  if (key.action === 'comma') {
    if (!props.amount.includes(',')) update(`${props.amount},`)
    return
  }
  update(sanitize(`${props.amount}${key.text}`))
}

function onInput(event: Event): void {
  const input = event.target as HTMLInputElement
  const value = sanitize(input.value)

  // A letter or a third decimal leaves `amount` unchanged, so Vue would not
  // repaint the input: clean it here or the user keeps seeing the rejected text.
  input.value = value
  update(value)
}
</script>

<template>
  <div class="amount-keypad">
    <label class="label" :for="inputId">{{ label }}</label>
    <div class="field" :class="{ invalid: error }">
      <input
        :id="inputId"
        type="text"
        inputmode="numeric"
        autocomplete="off"
        class="input"
        :value="amount"
        :disabled="disabled"
        :aria-invalid="error !== null"
        :aria-describedby="error ? errorId : undefined"
        @input="onInput"
      />
      <span v-if="currencyCode" class="currency" aria-hidden="true">{{ currencySymbol(currencyCode) }}</span>
    </div>

    <div v-if="$slots.hint" class="hint"><slot name="hint" /></div>

    <div class="keypad">
      <button
        v-for="key in keys"
        :key="key.text"
        type="button"
        class="key"
        :disabled="disabled"
        :aria-label="key.ariaLabel"
        @click="onKey(key)"
      >
        {{ key.text }}
      </button>
    </div>

    <p v-if="error" :id="errorId" class="error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.field {
  display: flex;
  align-items: center;
  margin: 0.5rem 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.field:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.field.invalid {
  border-color: var(--color-error);
}

.field.invalid:focus-within {
  box-shadow: 0 0 0 1px var(--color-error);
}

.input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-text);
  font: inherit;
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.input:focus {
  outline: none;
}

.currency {
  padding-right: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-muted);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin: 0.75rem 0;
}

.key {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 54px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: 20px;
  font-weight: 500;
  cursor: pointer;
}

.key:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  margin: 0.25rem 0 0;
  font-size: 14px;
  color: var(--color-expense);
}
</style>
