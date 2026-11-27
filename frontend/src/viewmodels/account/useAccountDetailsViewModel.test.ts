import { describe, expect, it, vi } from 'vitest'
import type { AccountDetails } from '@/models/account'
import { NOTICE_MS, useAccountDetailsViewModel, type AccountDetailsDependencies } from './useAccountDetailsViewModel'

const demo: AccountDetails = { iban: 'ES9121000418450200051332', bic: 'EVOLESB1XXX', holder: 'Usuari demo' }
const SHARE_TEXT = 'IBAN: ES91 2100 0418 4502 0005 1332 · BIC: EVOLESB1XXX · Titular: Usuari demo'

function setUp(overrides: Partial<AccountDetailsDependencies> = {}) {
  // `later` keeps the callbacks so each test decides when the 2 s have passed.
  const pending: (() => void)[] = []
  const dependencies: AccountDetailsDependencies = {
    getAccountDetails: vi.fn(() => Promise.resolve(demo)),
    copyText: vi.fn((_text: string) => Promise.resolve()),
    shareText: null,
    later: vi.fn((done: () => void, _ms: number) => {
      pending.push(done)
    }),
    ...overrides,
  }
  const passTime = () => pending.splice(0).forEach((done) => done())
  return { viewModel: useAccountDetailsViewModel(dependencies), dependencies, passTime }
}

describe('useAccountDetailsViewModel', () => {
  it('IBP-02: loads the details and groups the IBAN in fours', async () => {
    const { viewModel } = setUp()

    await viewModel.load()

    expect(viewModel.details.value).toEqual(demo)
    expect(viewModel.groupedIban.value).toBe('ES91 2100 0418 4502 0005 1332')
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('IBP-07: an error shows the generic text', async () => {
    const { viewModel } = setUp({
      getAccountDetails: vi.fn(() => Promise.reject({ code: 'INTERNAL_ERROR', message: 'x' })),
    })

    await viewModel.load()

    expect(viewModel.loadError.value).toBe("S'ha produït un error inesperat. Torna-ho a provar més tard.")
    expect(viewModel.details.value).toBeNull()
  })

  it('IBP-07: «Reintentar» loads again and clears the error', async () => {
    const getAccountDetails = vi
      .fn<() => Promise<AccountDetails>>()
      .mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' })
      .mockResolvedValueOnce(demo)
    const { viewModel } = setUp({ getAccountDetails })
    await viewModel.load()

    await viewModel.load()

    expect(viewModel.loadError.value).toBeNull()
    expect(viewModel.details.value).toEqual(demo)
  })

  it('IBP-03: touching the IBAN copies it without spaces and says «IBAN copiat» for 2 s', async () => {
    const { viewModel, dependencies, passTime } = setUp()
    await viewModel.load()

    await viewModel.copyIban()

    expect(dependencies.copyText).toHaveBeenCalledWith('ES9121000418450200051332')
    expect(viewModel.notice.value).toBe('IBAN copiat')
    expect(dependencies.later).toHaveBeenCalledWith(expect.any(Function), NOTICE_MS)
    passTime()
    expect(viewModel.notice.value).toBeNull()
  })

  it('IBP-04: «Compartir» opens the share menu with the text, and copies nothing', async () => {
    const shareText = vi.fn((_text: string) => Promise.resolve())
    const { viewModel, dependencies } = setUp({ shareText })
    await viewModel.load()

    await viewModel.share()

    expect(shareText).toHaveBeenCalledWith(SHARE_TEXT)
    expect(dependencies.copyText).not.toHaveBeenCalled()
    expect(viewModel.notice.value).toBeNull()
  })

  it('IBP-05: without a share menu, «Compartir» copies the same text and says «Dades copiades»', async () => {
    const { viewModel, dependencies } = setUp({ shareText: null })
    await viewModel.load()

    await viewModel.share()

    expect(dependencies.copyText).toHaveBeenCalledWith(SHARE_TEXT)
    expect(viewModel.notice.value).toBe('Dades copiades')
  })

  it('IBP-05: a browser that refuses to share also falls back to copying', async () => {
    const refused = vi.fn((_text: string) => Promise.reject(new DOMException('no', 'NotAllowedError')))
    const { viewModel, dependencies } = setUp({ shareText: refused })
    await viewModel.load()

    await viewModel.share()

    expect(dependencies.copyText).toHaveBeenCalledWith(SHARE_TEXT)
    expect(viewModel.notice.value).toBe('Dades copiades')
  })

  it('closing the share menu without choosing does nothing else', async () => {
    const cancelled = vi.fn((_text: string) => Promise.reject(new DOMException('closed', 'AbortError')))
    const { viewModel, dependencies } = setUp({ shareText: cancelled })
    await viewModel.load()

    await viewModel.share()

    expect(dependencies.copyText).not.toHaveBeenCalled()
    expect(viewModel.notice.value).toBeNull()
  })

  it('a newer notice is not cleared by the timer of an older one', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    await viewModel.copyIban()
    const firstTimer = vi.mocked(dependencies.later).mock.calls[0][0]

    await viewModel.share()
    firstTimer()

    expect(viewModel.notice.value).toBe('Dades copiades')
  })
})
