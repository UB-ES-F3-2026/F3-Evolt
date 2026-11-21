<script setup lang="ts">
import { computed } from 'vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { potGoalStatus, potPercentage } from '@/models/potGoal'
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

const percent = computed(() => potPercentage(props.pot))
const clampedPercent = computed(() => Math.max(0, Math.min(100, percent.value ?? 0)))
// Only shown when `percent` is non-null, which already means a valid target.
const targetCents = computed((): number => (percent.value === null ? 0 : (props.pot.target ?? 0)))
const isAchieved = computed(() => potGoalStatus(props.pot) === 'achieved')
const badgeText = computed(() => (isAchieved.value ? 'Objectiu assolit' : 'En progrés'))
</script>

<template>
  <!-- Sense objectiu no es renderitza res: ni barra, ni percentatge, ni etiqueta.
       `percent` és null quan no hi ha objectiu, així que el helper decideix. -->
  <div v-if="!compact && percent !== null" class="progress">
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

  <div v-else-if="compact && percent !== null" class="mini">
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
