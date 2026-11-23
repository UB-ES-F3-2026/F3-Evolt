import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { messageForCode } from '@/models/errorMessages'
import { REQUEST_AMOUNT_OVER_LIMIT_MESSAGE, type MoneyRequest } from '@/models/moneyRequest'
import type { UserSummary } from '@/models/user'
import { useNewMoneyRequestViewModel, type NewMoneyRequestDependencies } from './useNewMoneyRequestViewModel'

const alicia: UserSummary = { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' }
const created: MoneyRequest = {
  id: 'req-03',
  to: alicia,
  amount: 2500,
  concept: 'El sopar de divendres',
  status: 'pending',
  createdAt: '2026-11-23T21:15:00+01:00',
  expiresAt: '2026-11-30T00:00:00+01:00',
}

function setUp(overrides: Partial<NewMoneyRequestDependencies> = {}) {
  const dependencies = {
    searchUsers: vi.fn((_q: string) => Promise.resolve([alicia])),
    wait: vi.fn(() => Promise.resolve()),
    createMoneyRequest: vi.fn(() => Promise.resolve(created)),
    goToRequests: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useNewMoneyRequestViewModel(dependencies), dependencies }
}

async function fill(viewModel: ReturnType<typeof useNewMoneyRequestViewModel>, amount: string, concept: string) {
  viewModel.choose(alicia)
  viewModel.amount.value = amount
  viewModel.concept.value = concept
  await nextTick()
}

describe('useNewMoneyRequestViewModel', () => {
  it('SOP-03: «Enviar sol·licitud» stays disabled without recipient, amount and concept', async () => {
    const { viewModel } = setUp()
    expect(viewModel.canSend.value).toBe(false)

    viewModel.choose(alicia)
    viewModel.amount.value = '25'
    await nextTick()
    expect(viewModel.canSend.value).toBe(false)

    viewModel.concept.value = '   '
    await nextTick()
    expect(viewModel.canSend.value).toBe(false)
  })

  it('SOP-05: the recipient comes from the search of US-13', async () => {
    const { viewModel, dependencies } = setUp()

    await viewModel.search()

    expect(dependencies.searchUsers).toHaveBeenCalledWith('')
    expect(viewModel.users.value).toEqual([alicia])
  })

  it.each([
    ['0', messageForCode('INVALID_AMOUNT')],
    ['-5', messageForCode('INVALID_AMOUNT')],
    ['1000000,01', REQUEST_AMOUNT_OVER_LIMIT_MESSAGE],
  ])('reads the amount %j as «%s» and keeps the button disabled', async (amount, message) => {
    const { viewModel } = setUp()

    await fill(viewModel, amount, 'Sopar')

    expect(viewModel.amountError.value).toBe(message)
    expect(viewModel.canSend.value).toBe(false)
  })

  it('allows exactly 1.000.000,00 € (SO-10)', async () => {
    const { viewModel } = setUp()

    await fill(viewModel, '1000000', 'Sopar')

    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canSend.value).toBe(true)
  })

  it('SOP-04: sends it, says «Sol·licitud enviada a Alicia.» and opens the list after 1,5 s', async () => {
    const { viewModel, dependencies } = setUp()
    await fill(viewModel, '25', '  El sopar de divendres ')

    const sent = await viewModel.send()

    expect(sent).toBe(true)
    expect(dependencies.createMoneyRequest).toHaveBeenCalledWith({
      toUserId: 'usr-03',
      amount: 2500,
      concept: 'El sopar de divendres',
    })
    expect(viewModel.confirmation.value).toBe('Sol·licitud enviada a Alicia.')
    expect(dependencies.wait).toHaveBeenCalledWith(1500)
    expect(dependencies.goToRequests).toHaveBeenCalledOnce()
  })

  it.each(['INTERNAL_ERROR', 'SELF_REQUEST', 'RECIPIENT_NOT_FOUND'] as const)(
    'SOP-06: %s shows its text and keeps recipient, amount and concept',
    async (code) => {
      const { viewModel, dependencies } = setUp({
        createMoneyRequest: vi.fn(() => Promise.reject({ code, message: 'x' })),
      })
      await fill(viewModel, '25', 'Sopar')

      const sent = await viewModel.send()

      expect(sent).toBe(false)
      expect(viewModel.submitError.value).toBe(messageForCode(code))
      expect(viewModel.recipient.value).toEqual(alicia)
      expect(viewModel.amount.value).toBe('25')
      expect(viewModel.concept.value).toBe('Sopar')
      expect(dependencies.goToRequests).not.toHaveBeenCalled()
    },
  )
})
