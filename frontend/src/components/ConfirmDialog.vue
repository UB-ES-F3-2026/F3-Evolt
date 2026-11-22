<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'

// Modal window over the screen (US-26: the two windows of «Eliminar subcompte").
// Without `cancelLabel` it is a notice with a single button; with it, a question
// whose confirm button is red when `danger`. Esc and a click on the backdrop
// cancel, like the cancel button (or close the notice).
const props = withDefaults(
  defineProps<{
    title: string
    /** Optional line under the title. */
    message?: string
    confirmLabel: string
    /** Without it there is only one button, and every way out emits `confirm`. */
    cancelLabel?: string
    /** Red confirm button, for an action that cannot be undone. */
    danger?: boolean
    /** While the action runs: both buttons are disabled and nothing closes the window. */
    busy?: boolean
  }>(),
  { message: undefined, cancelLabel: undefined, danger: false, busy: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()

const confirmButton = ref<HTMLButtonElement | null>(null)

function dismiss(): void {
  if (props.busy) return
  if (props.cancelLabel === undefined) emit('confirm')
  else emit('cancel')
}

// The focus goes into the window, so the keyboard (and a screen reader) starts there.
onMounted(async () => {
  await nextTick()
  confirmButton.value?.focus()
})
</script>

<template>
  <div class="backdrop" @click.self="dismiss" @keydown.esc="dismiss">
    <div
      class="dialog"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      :aria-describedby="message ? 'confirm-dialog-message' : undefined"
    >
      <h2 id="confirm-dialog-title" class="title" :class="{ centered: cancelLabel === undefined }">{{ title }}</h2>
      <p v-if="message" id="confirm-dialog-message" class="message">{{ message }}</p>
      <div class="buttons">
        <button v-if="cancelLabel !== undefined" type="button" class="cancel" :disabled="busy" @click="emit('cancel')">
          {{ cancelLabel }}
        </button>
        <button
          ref="confirmButton"
          type="button"
          class="confirm"
          :class="{ danger }"
          :disabled="busy"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 10;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgb(26 34 51 / 50%);
}

.dialog {
  width: 100%;
  max-width: 24rem;
  padding: 1.5rem;
  border-radius: calc(var(--radius) * 1.5);
  background: var(--color-surface);
}

.title {
  margin: 0;
  font-size: 1.125rem;
}

.title.centered {
  text-align: center;
}

.message {
  margin: 0.75rem 0 0;
  color: var(--color-text);
}

.buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.cancel,
.confirm {
  flex: 1;
  padding: 0.75rem;
  border-radius: var(--radius);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.cancel {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}

.confirm {
  border: none;
  background: var(--color-primary);
  color: var(--color-surface);
}

.confirm.danger {
  background: var(--color-expense);
}

.cancel:disabled,
.confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
