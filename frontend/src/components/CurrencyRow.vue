<script setup lang="ts">
import { computed } from 'vue'
import { ChevronRight } from '@lucide/vue'

// Presentational row reused by Home, /divises and /divises/afegir.
// The root element is an <li>: render rows inside a <ul>.
const props = withDefaults(
  defineProps<{
    /** ISO code, e.g. 'USD'. */
    code: string
    /** Localized name, e.g. 'Dòlar nord-americà'. */
    name: string
    /** Symbol inside the circle, e.g. '$'. */
    symbol: string
    /** Pre-formatted amount, e.g. '427,16 $'; when absent no amount is rendered. */
    amountText?: string
    /** Masks the amount, like every other amount (T07.10). */
    hidden?: boolean
    /** The user already owns this currency: greyed with a badge, never clickable. */
    owned?: boolean
    /** The whole row is a button that emits `select`, with a chevron. */
    selectable?: boolean
    /** Busy state: greyed like `owned` but without the badge. */
    disabled?: boolean
  }>(),
  { amountText: undefined, hidden: false, owned: false, selectable: false, disabled: false },
)

const emit = defineEmits<{ select: [] }>()

// An owned row shows the badge instead of the chevron and never acts as a button.
const isButton = computed(() => props.selectable && !props.owned)

function onRowClick() {
  if (isButton.value && !props.disabled) emit('select')
}
</script>

<template>
  <li class="currency-row" :class="{ 'row-disabled': owned || disabled }">
    <component
      :is="isButton ? 'button' : 'div'"
      class="row"
      :type="isButton ? 'button' : undefined"
      :disabled="isButton ? disabled : undefined"
      @click="onRowClick"
    >
      <span class="icon">{{ symbol }}</span>
      <span class="name">{{ code }} · {{ name }}</span>
      <span v-if="owned" class="badge">ja la tens</span>
      <ChevronRight v-else-if="selectable" class="chevron" :size="18" />
      <span v-if="amountText !== undefined" class="amount">{{ hidden ? '••••' : amountText }}</span>
    </component>
  </li>
</template>

<style scoped>
.currency-row {
  list-style: none;
}

.row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  min-height: 3.5rem;
  padding: 0.375rem 0;
  border: none;
  border-bottom: 1px solid var(--color-border);
  color: inherit;
  font: inherit;
  text-align: left;
  background: none;
}

button.row {
  cursor: pointer;
}

.currency-row:last-child .row {
  border-bottom: none;
}

.icon {
  flex: none;
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--color-bg);
  color: var(--color-primary);
  font-size: 0.75rem;
  font-weight: 600;
}

.name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  flex: none;
  padding: 0.1875rem 0.5625rem;
  border-radius: 999px;
  background: var(--color-bg);
  color: var(--color-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: nowrap;
}

.chevron {
  flex: none;
  color: var(--color-muted);
}

.amount {
  flex: none;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.row-disabled .icon {
  background: var(--color-border);
  color: var(--color-muted);
}

.row-disabled .name,
.row-disabled .amount {
  color: var(--color-muted);
}
</style>
