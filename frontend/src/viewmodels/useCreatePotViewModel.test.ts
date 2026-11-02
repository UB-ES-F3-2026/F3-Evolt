import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { AMOUNT_FORMAT_MESSAGE, messageForCode } from '@/models/errorMessages'
import type { CreatePotRequest, Pot } from '@/models/pot'
import { useCreatePotViewModel, type CreatePotDependencies } from './useCreatePotViewModel'

const created: Pot = { id: 'pot-04', name: 'Viatge', balance: 0, target: 30000, color: 'teal' }

function setUp(overrides: Partial<CreatePotDependencies> = {}) {
  const dependencies = {
    createPot: vi.fn((_request: CreatePotRequest) => Promise.resolve(created)),
    goToPots: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useCreatePotViewModel(dependencies), dependencies }
}

async function type(field: { value: string }, text: string): Promise<void> {
  field.value = text
  await nextTick()
}

describe('useCreatePotViewModel', () => {
  it('starts with "Crear" disabled but nothing in red, because nobody has made a mistake yet', () => {
    const { viewModel } = setUp()

    expect(viewModel.canSubmit.value).toBe(false)
    expect(viewModel.nameError.value).toBeNull()
    expect(viewModel.targetError.value).toBeNull()
    expect(viewModel.color.value).toBe('purple')
  })

  it('offers the six colours of the contract with their names', () => {
    const { viewModel } = setUp()

    expect(viewModel.colorOptions.map((option) => option.label)).toEqual([
      'Lila',
      'Blau',
      'Turquesa',
      'Taronja',
      'Rosa',
      'Groc',
    ])
  })

  it.each(['', '   '])('turns the name red when it is left as %j (US-17, criterion 4)', async (text) => {
    const { viewModel } = setUp()

    await type(viewModel.name, 'Viatge')
    await type(viewModel.name, text)

    expect(viewModel.nameError.value).toBe(messageForCode('INVALID_POT_NAME'))
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it.each([
    ['0', messageForCode('INVALID_TARGET')],
    ['0,00', messageForCode('INVALID_TARGET')],
    ['-5', messageForCode('INVALID_TARGET')],
    ['abc', AMOUNT_FORMAT_MESSAGE],
    ['300,555', AMOUNT_FORMAT_MESSAGE],
  ])('rejects the target %j with its reason and keeps "Crear" disabled', async (text, message) => {
    const { viewModel } = setUp()
    await type(viewModel.name, 'Viatge')

    await type(viewModel.target, text)

    expect(viewModel.targetError.value).toBe(message)
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('sends the name, the target in cents and the chosen colour, then opens the list', async () => {
    const { viewModel, dependencies } = setUp()
    await type(viewModel.name, 'Viatge')
    await type(viewModel.target, '300')
    viewModel.color.value = 'teal'

    const sent = await viewModel.submit()

    expect(sent).toBe(true)
    expect(dependencies.createPot).toHaveBeenCalledWith({ name: 'Viatge', target: 30000, color: 'teal' })
    expect(dependencies.goToPots).toHaveBeenCalledOnce()
  })

  it('creates a pot without target, with the default colour', async () => {
    const { viewModel, dependencies } = setUp()
    await type(viewModel.name, 'Fons')

    await viewModel.submit()

    expect(dependencies.createPot).toHaveBeenCalledWith({ name: 'Fons', target: null, color: 'purple' })
  })

  it('does not send anything while the form is not valid', async () => {
    const { viewModel, dependencies } = setUp()

    const sent = await viewModel.submit()

    expect(sent).toBe(false)
    expect(viewModel.nameError.value).toBe(messageForCode('INVALID_POT_NAME'))
    expect(dependencies.createPot).not.toHaveBeenCalled()
  })

  it('shows a name rejected by the backend under the name, until it changes', async () => {
    const { viewModel, dependencies } = setUp({
      createPot: vi.fn(() => Promise.reject({ code: 'INVALID_POT_NAME', message: 'x' })),
    })
    await type(viewModel.name, 'Viatge')

    await viewModel.submit()
    expect(viewModel.nameError.value).toBe(messageForCode('INVALID_POT_NAME'))
    expect(dependencies.goToPots).not.toHaveBeenCalled()

    await type(viewModel.name, 'Viatge a Roma')
    expect(viewModel.nameError.value).toBeNull()
  })

  it('keeps what was typed when the server fails, so the person only has to try again', async () => {
    const { viewModel, dependencies } = setUp({
      createPot: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })
    await type(viewModel.name, 'Viatge')
    await type(viewModel.target, '300')

    await viewModel.submit()

    expect(viewModel.submitError.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.name.value).toBe('Viatge')
    expect(viewModel.target.value).toBe('300')
    expect(viewModel.canSubmit.value).toBe(true)
    expect(dependencies.goToPots).not.toHaveBeenCalled()
  })

  it('disables "Crear" while the pot is being created', async () => {
    let finish!: (pot: Pot) => void
    const { viewModel } = setUp({
      createPot: vi.fn(() => new Promise<Pot>((resolve) => (finish = resolve))),
    })
    await type(viewModel.name, 'Viatge')

    const sending = viewModel.submit()
    expect(viewModel.isSubmitting.value).toBe(true)
    expect(viewModel.canSubmit.value).toBe(false)

    finish(created)
    await sending
    expect(viewModel.isSubmitting.value).toBe(false)
  })
})
