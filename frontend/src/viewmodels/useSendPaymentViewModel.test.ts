import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import { messageForCode } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import type { TransferLimit } from '@/models/transfer'
import type { UserSummary } from '@/models/user'
import { useSendPaymentViewModel, type SendPaymentDependencies } from './useSendPaymentViewModel'

const usuariNou: UserSummary = { id: 'usr-02', name: 'Usuari nou', username: 'buit' }
const home: Home = { balance: 379521, totalSaved: 30000, lastMovements: [] }
const fullLimit: TransferLimit = { dailyLimit: 100000, remainingToday: 100000 }

function setUp(overrides: Partial<SendPaymentDependencies> = {}, to: string | undefined = 'usr-02') {
  const dependencies = {
    getUser: vi.fn((_id: string) => Promise.resolve(usuariNou)),
    getHome: vi.fn(() => Promise.resolve(home)),
    getTransferLimit: vi.fn(() => Promise.resolve(fullLimit)),
    goToConfirm: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useSendPaymentViewModel(to, dependencies), dependencies }
}

function typeOnKeypad(viewModel: ReturnType<typeof useSendPaymentViewModel>, keys: string): void {
  for (const key of keys) viewModel.pressKey(key)
}

describe('useSendPaymentViewModel', () => {
  it('CUP-08, CUP-09, ENP-01: asks the recipient of `?to=`, the balance and the limit on opening', async () => {
    const { viewModel, dependencies } = setUp()

    await viewModel.load()

    expect(dependencies.getUser).toHaveBeenCalledWith('usr-02')
    expect(viewModel.recipient.value).toEqual(usuariNou)
    expect(viewModel.balance.value).toBe(379521)
    expect(dependencies.getTransferLimit).toHaveBeenCalledOnce()
  })

  it('CUP-10: an id that is not a user shows «No hem trobat aquest destinatari.» and offers to choose again', async () => {
    const { viewModel } = setUp({ getUser: vi.fn(() => Promise.reject({ code: 'RECIPIENT_NOT_FOUND', message: 'x' })) })

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('RECIPIENT_NOT_FOUND'))
    expect(viewModel.isRecipientMissing.value).toBe(true)
  })

  it('without `?to=` there is nobody to send to, without asking the API', async () => {
    // An empty `?to=` reads like a missing one.
    const { viewModel, dependencies } = setUp({}, '')

    await viewModel.load()

    expect(dependencies.getUser).not.toHaveBeenCalled()
    expect(viewModel.isRecipientMissing.value).toBe(true)
  })

  it('a network error can be tried again: it is not a missing recipient', async () => {
    const { viewModel } = setUp({ getHome: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })) })

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.isRecipientMissing.value).toBe(false)
  })

  it('«Continuar» stays disabled, with no message, while the amount is empty or zero', async () => {
    const { viewModel } = setUp()
    await viewModel.load()

    expect(viewModel.canContinue.value).toBe(false)
    typeOnKeypad(viewModel, '0')
    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canContinue.value).toBe(false)
  })

  it('ENP-02: more than the balance says «No tens prou saldo.» and disables «Continuar»', async () => {
    const { viewModel } = setUp()
    await viewModel.load()

    typeOnKeypad(viewModel, '4000')

    expect(viewModel.amountError.value).toBe('No tens prou saldo.')
    expect(viewModel.canContinue.value).toBe(false)
  })

  it('ENP-03: more than what is left of today\'s limit says the limit and disables «Continuar»', async () => {
    const { viewModel } = setUp({ getTransferLimit: vi.fn(() => Promise.resolve({ dailyLimit: 100000, remainingToday: 98000 })) })
    await viewModel.load()

    typeOnKeypad(viewModel, '981')

    expect(viewModel.amountError.value).toMatch(/^Has superat el límit diari de 1\.000,00\s€\.$/)
    expect(viewModel.canContinue.value).toBe(false)
  })

  it('reaching exactly what is left of the limit is allowed (EN-12)', async () => {
    const { viewModel } = setUp({ getTransferLimit: vi.fn(() => Promise.resolve({ dailyLimit: 100000, remainingToday: 98000 })) })
    await viewModel.load()

    typeOnKeypad(viewModel, '980')

    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canContinue.value).toBe(true)
  })

  it('ENP-04: «Continuar» hands the recipient, the amount in cents and the clean concept to «Confirmar»', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    typeOnKeypad(viewModel, '20')
    viewModel.concept.value = '  El sopar de divendres  '

    const went = await viewModel.continueToConfirm()

    expect(went).toBe(true)
    expect(dependencies.goToConfirm).toHaveBeenCalledWith({ to: 'usr-02', amount: 2000, concept: 'El sopar de divendres' })
  })

  it('ENP-10: a blank concept is no concept', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    typeOnKeypad(viewModel, '20')
    viewModel.concept.value = '   '

    await viewModel.continueToConfirm()

    expect(dependencies.goToConfirm).toHaveBeenCalledWith({ to: 'usr-02', amount: 2000, concept: null })
  })

  it('does not go on while the amount cannot be sent', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()

    expect(await viewModel.continueToConfirm()).toBe(false)
    expect(dependencies.goToConfirm).not.toHaveBeenCalled()
  })

  it('#212: a new `?to=` in the same screen asks the new recipient on the next load', async () => {
    const huabin: UserSummary = { id: 'usr-04', name: 'Huabin', username: '123huabin123' }
    const to = ref('usr-02')
    const getUser = vi.fn((id: string) => Promise.resolve(id === 'usr-04' ? huabin : usuariNou))
    const viewModel = useSendPaymentViewModel(to, {
      getUser,
      getHome: () => Promise.resolve(home),
      getTransferLimit: () => Promise.resolve(fullLimit),
      goToConfirm: () => Promise.resolve(),
    })
    await viewModel.load()

    to.value = 'usr-04'
    await viewModel.load()

    expect(getUser).toHaveBeenLastCalledWith('usr-04')
    expect(viewModel.recipient.value).toEqual(huabin)
  })
})
