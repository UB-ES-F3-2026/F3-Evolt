<script setup lang="ts">
import { computed } from 'vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import type { Pot } from '@/models/pot'

const props = withDefaults(
  defineProps<{
    /** Guardiola amb (o sense) objectiu. */
    pot: Pot
    /** Masks the amounts line like every other amount (T07.10). Detail variant only. */
    hidden?: boolean
    /** Compact list variant: mini track + percent only. */
    compact?: boolean
  }>(),
  { hidden: false, compact: false },
)

// docs/api.md §11.1: the backend owns the rule, so the component paints its values
// and never recomputes them from `balance` and `target`.
const percent = computed(() => props.pot.percentage ?? null)
const goalStatus = computed(() => props.pot.goalStatus ?? null)
// Only an answer that carries both fields has progress to paint (absent before US-20).
// §11.1 sends both `null` without a goal, so a malformed answer with fields but no
// target is not trusted either: it would paint «X de 0,00 €».
const showProgress = computed(
  () =>
    props.pot.target !== null &&
    props.pot.target > 0 &&
    percent.value !== null &&
    goalStatus.value !== null,
)
const clampedPercent = computed(() => Math.max(0, Math.min(100, percent.value ?? 0)))
// Only rendered when `showProgress`, which means the API sent a pot with a goal.
const targetCents = computed((): number => props.pot.target ?? 0)
const isAchieved = computed(() => goalStatus.value === 'achieved')
const badgeText = computed(() => (isAchieved.value ? 'Objectiu assolit' : 'En progrés'))
</script>

<template>
  <!-- Sense objectiu, o quan l'API encara no envia el progrés, no es renderitza res:
       ni barra, ni percentatge, ni etiqueta. Només es pinten els valors de l'API. -->
  <div v-if="!compact && showProgress" class="progress">
    <p class="progress-amounts">
      <MoneyAmount :cents="pot.balance" :hidden="hidden" /> de
      <MoneyAmount :cents="targetCents" :hidden="hidden" />
    </p>
    <div
      class="progress-track"
      role="progressbar"
      :aria-label="`Progrés de ${pot.name} cap a l'objectiu`"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="clampedPercent"
      :aria-valuetext="`${percent} % de l'objectiu`"
    >
      <div
        class="progress-fill"
        :class="{ achieved: isAchieved }"
        :style="{ width: clampedPercent + '%' }"
      ></div>
    </div>
    <div class="progress-meta">
      <span class="progress-percent">{{ percent }}&nbsp;%</span>
      <span class="badge-status" :class="{ achieved: isAchieved }">{{ badgeText }}</span>
    </div>
  </div>

  <div v-else-if="compact && showProgress" class="mini">
    <div
      class="mini-track"
      role="progressbar"
      :aria-label="`Progrés de ${pot.name} cap a l'objectiu`"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="clampedPercent"
      :aria-valuetext="`${percent} % de l'objectiu`"
    >
      <div
        class="mini-fill"
        :class="{ achieved: isAchieved }"
        :style="{ width: clampedPercent + '%' }"
      ></div>
    </div>
    <span class="mini-percent">{{ percent }}&nbsp;%</span>
  </div>
</template>

<style scoped>
.progress {
  /* Own top gap (next to .target, which carries none) and bottom gap before «Aportar». */
  margin-top: 14px;
  margin-bottom: 14px;
  padding-top: 14px;
  /* Full width inside the flex-column card of PotView (align-items: flex-start). */
  width: 100%;
  border-top: 1px solid var(--color-border);
}
.progress-amounts {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.progress-track {
  width: 100%;
  margin-top: 8px;
  height: 10px;
  border-radius: 999px;
  background: var(--color-border);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--color-primary);
}
.progress-fill.achieved {
  background: var(--color-income);
}
.progress-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.progress-percent {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.badge-status {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--color-border);
  color: var(--color-text);
  white-space: nowrap;
}
.badge-status.achieved {
  background: var(--color-goal-badge-bg);
  color: var(--color-goal-badge-text);
}
.mini {
  /* Full width inside PotRow's flex-column name cell. */
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}
.mini-track {
  width: 100%;
  max-width: 150px;
  height: 4px;
  border-radius: 999px;
  background: var(--color-border);
  overflow: hidden;
}
.mini-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--color-primary);
}
.mini-fill.achieved {
  background: var(--color-income);
}
.mini-percent {
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
