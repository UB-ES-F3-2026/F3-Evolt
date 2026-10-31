<script setup lang="ts">
import { nextTick, onMounted, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    /** How many boxes, one per digit. */
    length: number
    label: string
    invalid?: boolean
    disabled?: boolean
  }>(),
  { invalid: false, disabled: false },
)

const code = defineModel<string>({ required: true })

// Not `useTemplateRef`: a ref array inside v-for does not keep the order of the boxes.
const boxes: (HTMLInputElement | null)[] = []

function focusBox(index: number): void {
  const box = boxes[Math.min(index, props.length - 1)]
  box?.focus()
  box?.select()
}

function onInput(index: number, event: Event): void {
  const box = event.target as HTMLInputElement
  const digits = box.value.replace(/\D/g, '')

  // A paste brings all the digits at once, so they go on filling the next boxes.
  const before = code.value.slice(0, index)
  const after = code.value.slice(index + Math.max(digits.length, 1))
  code.value = `${before}${digits}${after}`.slice(0, props.length)

  // `code` may not change (a letter was typed), and then Vue would leave the letter there.
  box.value = code.value[index] ?? ''
  if (digits !== '') focusBox(before.length + digits.length)
}

function onBackspace(index: number, event: KeyboardEvent): void {
  if ((code.value[index] ?? '') !== '' || index === 0) return
  event.preventDefault()
  code.value = code.value.slice(0, index - 1) + code.value.slice(index)
  focusBox(index - 1)
}

onMounted(() => focusBox(0))

// After a wrong code or after unlocking, the next digit goes in the first box.
watch([code, () => props.disabled], async ([typed, disabled]) => {
  if (typed !== '' || disabled) return
  await nextTick()
  focusBox(0)
})
</script>

<template>
  <div class="code-input" role="group" :aria-label="label">
    <input
      v-for="(_, index) in length"
      :key="index"
      :ref="(box) => (boxes[index] = box as HTMLInputElement | null)"
      class="box"
      :class="{ invalid }"
      :value="code[index] ?? ''"
      type="text"
      inputmode="numeric"
      autocomplete="one-time-code"
      :aria-label="`${label}: número ${index + 1}`"
      :aria-invalid="invalid"
      :disabled="disabled"
      @input="onInput(index, $event)"
      @keydown.backspace="onBackspace(index, $event)"
      @focus="($event.target as HTMLInputElement).select()"
    />
  </div>
</template>

<style scoped>
.code-input {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.box {
  width: 2.75rem;
  min-width: 0;
  padding: 0.75rem 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}

.box:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.box.invalid {
  border-color: var(--color-error);
}

.box.invalid:focus {
  box-shadow: 0 0 0 1px var(--color-error);
}

.box:disabled {
  background: var(--color-bg);
  cursor: not-allowed;
}
</style>
