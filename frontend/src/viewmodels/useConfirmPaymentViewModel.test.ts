import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import type { Transfer } from '@/models/transfer'
import type { UserSummary } from '@/models/user'
import {
  useConfirmPaymentViewModel,
  type ConfirmPaymentDependencies,
  type ConfirmPaymentQuery,
} from './useConfirmPaymentViewModel'

const usuariNou: UserSummary = { id: 'usr-02', name: 'Usuari nou', username: 'buit' }
const home: Home = { balance: 379521, totalSaved: 30000, lastMovements: [] }
const sent: Transfer = {
  balance: 377521,
  recipient: usuariNou,
  movement: {
    id: 'mov-31',
    amount: 2000,
    concept: 'El sopar de divendres',
    date: '2026-11-15T21:15:00+01:00',
    type: 'expense',
    icon: 'transfer',
  },
}
const draft: ConfirmPaymentQuery = { to: 'usr-02', amount: '2000', concept: 'El sopar de divendres' }

function setUp(overrides: Partial<ConfirmPaymentDependencies> = {}, query: ConfirmPaymentQuery = draft) {
  const dependencies = {
    getUser: vi.fn((_id: string) => Promise.resolve(usuariNou)),
    getHome: vi.fn(() => Promise.resolve(home)),
    getTransferLimit: vi.fn(() => Promise.resolve({ dailyLimit: 100000, remainingToday: 100000 })),
    sendTransfer: vi.fn(() => Promise.resolve(sent)),
    goHome: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useConfirmPaymentViewModel(query, dependencies), dependencies }
}

function rejectWith(code: string, details?: Record<string, unknown>) {
  return vi.fn(() => Promise.reject({ code, message: 'x', details }))
}

describe('useConfirmPaymentViewModel', () => {
  it('ENP-04: shows the recipient, the amount, the concept and the available balance', async () => {
    const { viewModel } = setUp()

    await viewModel.load()

    expect(viewModel.recipient.value).toEqual(usuariNou)
    expect(viewModel.amount).toBe(2000)
    expect(viewModel.concept).toBe('El sopar de divendres')
    expect(viewModel.balance.value).toBe(379521)
    expect(viewModel.canConfirm.value).toBe(true)
  })

  it('ENP-05: sends, shows the green tick with the new balance and goes back to Inici after 1,5 s', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()

    const done = await viewModel.confirm()

    expect(done).toBe(true)
    expect(dependencies.sendTransfer).toHaveBeenCalledWith({
      toUserId: 'usr-02',
      amount: 2000,
      concept: 'El sopar de divendres',
    })
    expect(viewModel.confirmation.value).toMatch(/^Has enviat 20,00\s€ a Usuari nou$/)
    expect(viewModel.balance.value).toBe(377521)
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goHome).toHaveBeenCalledOnce()
  })

  it('ENP-10: without a concept nothing is sent as concept', async () => {
    const { viewModel, dependencies } = setUp({}, { to: 'usr-02', amount: '2000' })
    await viewModel.load()

    await viewModel.confirm()

    expect(dependencies.sendTransfer).toHaveBeenCalledWith({ toUserId: 'usr-02', amount: 2000, concept: null })
  })

  it.each([
    ['ENP-08', 'INSUFFICIENT_BALANCE', 'No tens prou saldo.'],
    ['ENP-09', 'SELF_TRANSFER', 'No et pots enviar diners a tu mateix.'],
    ['ENP-11', 'INTERNAL_ERROR', messageForCode('INTERNAL_ERROR')],
  ])('%s: %s shows «%s» under the button and moves nothing', async (_id, code, text) => {
    const { viewModel, dependencies } = setUp({ sendTransfer: rejectWith(code) })
    await viewModel.load()

    const done = await viewModel.confirm()

    expect(done).toBe(false)
    expect(viewModel.submitError.value).toBe(text)
    expect(viewModel.confirmation.value).toBeNull()
    expect(viewModel.balance.value).toBe(379521)
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('ENP-08: a limit reached in the meantime says the same limit text as «Enviar»', async () => {
    const { viewModel } = setUp({ sendTransfer: rejectWith('TRANSFER_LIMIT_EXCEEDED', { remainingToday: 0 }) })
    await viewModel.load()

    await viewModel.confirm()

    expect(viewModel.submitError.value).toMatch(/^Has superat el límit diari de 1\.000,00\s€\.$/)
  })

  it('a recipient that is gone offers to choose another one', async () => {
    const { viewModel } = setUp({ sendTransfer: rejectWith('RECIPIENT_NOT_FOUND') })
    await viewModel.load()

    await viewModel.confirm()

    expect(viewModel.submitError.value).toBe(messageForCode('RECIPIENT_NOT_FOUND'))
    expect(viewModel.isRecipientMissing.value).toBe(true)
  })

  it.each([{ to: 'usr-02' }, { to: 'usr-02', amount: 'abc' }, { to: 'usr-02', amount: '0' }, { amount: '2000' }])(
    'a URL without a valid recipient or amount (%j) cannot be confirmed',
    async (query) => {
      const { viewModel, dependencies } = setUp({}, query)

      await viewModel.load()

      expect(viewModel.loadError.value).toBe(messageForCode('VALIDATION_ERROR'))
      expect(dependencies.getUser).not.toHaveBeenCalled()
    },
  )
})
