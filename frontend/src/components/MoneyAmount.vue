<script setup lang="ts">
import { computed } from 'vue'
import { formatCents } from '@/models/money'

const props = withDefaults(
  defineProps<{
    /** Integer cents, as in the contract. */
    cents: number
    /** Shows a mask instead of the amount (balance visibility, T07.10). */
    hidden?: boolean
    /** Adds `+` or `−` in front, for amounts with a direction (income / expense). */
    sign?: 'positive' | 'negative'
  }>(),
  { hidden: false, sign: undefined },
)

const SIGN_TEXT = { positive: '+', negative: '−' } as const

const text = computed(() => `${props.sign ? SIGN_TEXT[props.sign] : ''}${formatCents(props.cents)}`)
</script>

<template>
  <span v-if="hidden" class="money" role="img" aria-label="Import ocult">••••</span>
  <span v-else class="money">{{ text }}</span>
</template>

<style scoped>
.money {
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
</style>
