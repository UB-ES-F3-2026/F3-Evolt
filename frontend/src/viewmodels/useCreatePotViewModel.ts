import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import { AMOUNT_FORMAT_MESSAGE, messageForCode, toUserMessage } from '@/models/errorMessages'
import { eurosToCents } from '@/models/money'
import {
  DEFAULT_POT_COLOR,
  POT_COLOR_LABELS,
  POT_COLORS,
  type CreatePotRequest,
  type Pot,
  type PotColor,
} from '@/models/pot'
import { createPot } from '@/services/potsService'

export interface CreatePotDependencies {
  createPot: (request: CreatePotRequest) => Promise<Pot>
  goToPots: () => Promise<unknown>
}

/** "Crear guardiola" form (US-17): name, optional target and colour, their checks, and creating it. */
export function useCreatePotViewModel(dependencies: CreatePotDependencies = defaultDependencies()) {
  const name = ref('')
  const target = ref('')
  const color = ref<PotColor>(DEFAULT_POT_COLOR)
  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  // The backend's answer about one field, shown under that field until it changes.
  const serverNameError = ref<string | null>(null)
  const serverTargetError = ref<string | null>(null)
  // An empty name only turns red once the person has written in it or left it: nobody has made a mistake yet.
  const isNameTouched = ref(false)

  const targetCents = computed(() => eurosToCents(target.value))

  // Same rules as the backend (docs/api.md §9.3), checked here only to answer before sending.
  const nameError = computed(() => {
    if (serverNameError.value !== null) return serverNameError.value
    return isNameTouched.value && name.value.trim() === '' ? messageForCode('INVALID_POT_NAME') : null
  })

  const targetError = computed(() => {
    if (serverTargetError.value !== null) return serverTargetError.value
    const typed = target.value.trim()
    if (typed === '') return null // the target is optional
    // eurosToCents only reads digits, so a minus sign would read as a format error: US-17 asks for this text.
    if (typed.startsWith('-')) return messageForCode('INVALID_TARGET')
    if (targetCents.value === null) return AMOUNT_FORMAT_MESSAGE
    if (targetCents.value <= 0) return messageForCode('INVALID_TARGET')
    return null
  })

  const canSubmit = computed(
    () => name.value.trim() !== '' && targetError.value === null && !isSubmitting.value,
  )

  const colorOptions = POT_COLORS.map((value) => ({ value, label: POT_COLOR_LABELS[value] }))

  // New data makes the previous answer from the backend stale.
  watch(name, () => {
    isNameTouched.value = true
    serverNameError.value = null
    submitError.value = null
  })
  watch(target, () => {
    serverTargetError.value = null
    submitError.value = null
  })

  /** Leaving the name empty is a mistake too (US-17, criterion 4), not only clearing it. */
  function touchName(): void {
    isNameTouched.value = true
  }

  async function submit(): Promise<boolean> {
    isNameTouched.value = true
    if (!canSubmit.value) return false
    isSubmitting.value = true
    submitError.value = null

    try {
      await dependencies.createPot({
        name: name.value,
        target: target.value.trim() === '' ? null : targetCents.value,
        color: color.value,
      })
      await dependencies.goToPots()
      return true
    } catch (failure) {
      if (isApiError(failure) && failure.code === 'INVALID_POT_NAME') {
        serverNameError.value = messageForCode('INVALID_POT_NAME')
      } else if (isApiError(failure) && failure.code === 'INVALID_TARGET') {
        serverTargetError.value = messageForCode('INVALID_TARGET')
      } else {
        // The form keeps what was typed, so the person only has to try again.
        submitError.value = toUserMessage(failure)
      }
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return {
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
  }
}

function defaultDependencies(): CreatePotDependencies {
  const router = useRouter()
  return {
    createPot,
    // Replace: going back from the list must not reopen a form that was already sent.
    goToPots: () => router.replace({ name: 'pots' }),
  }
}
