// @vitest-environment jsdom
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { AccountDetails } from '@/models/account'
import { getAccountDetails } from '@/services/account/accountService'
import AccountDetailsView from './AccountDetailsView.vue'

// The view is thin over useAccountDetailsViewModel: only the service and the clipboard are fakes,
// and the real ViewModel runs. jsdom has no share menu, so «Compartir» copies (IBP-05).
vi.mock('@/services/account/accountService', () => ({ getAccountDetails: vi.fn() }))

const demo: AccountDetails = { iban: 'ES9121000418450200051332', bic: 'EVOLESB1XXX', holder: 'Usuari demo' }
const writeText = vi.fn((_text: string) => Promise.resolve())

beforeEach(() => {
  vi.mocked(getAccountDetails).mockReset()
  writeText.mockClear()
  Object.defineProperty(navigator, 'clipboard', { value: { writeText }, configurable: true })
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
})

async function mountView(): Promise<VueWrapper> {
  const wrapper = mount(AccountDetailsView, {
    // The shell only provides the header and the menu; its slot is what this view renders.
    global: { stubs: { AppShell: { template: '<div><slot /></div>' } } },
  })
  await flushPromises()
  return wrapper
}

describe('AccountDetailsView', () => {
  it('IBP-02: «IBAN», «BIC» and «Titular», one under the other, with the IBAN in groups of four', async () => {
    vi.mocked(getAccountDetails).mockResolvedValue(demo)

    const wrapper = await mountView()

    expect(wrapper.findAll('dt').map((label) => label.text())).toEqual(['IBAN', 'BIC', 'Titular'])
    expect(wrapper.findAll('dd').map((value) => value.text())).toEqual([
      'ES91 2100 0418 4502 0005 1332',
      'EVOLESB1XXX',
      'Usuari demo',
    ])
    expect(wrapper.text()).toContain("Toca l'IBAN per copiar-lo.")
  })

  it('IBP-03: touching the IBAN copies it without spaces and «IBAN copiat» goes after 2 s', async () => {
    vi.mocked(getAccountDetails).mockResolvedValue(demo)
    const wrapper = await mountView()

    await wrapper.find('button.iban').trigger('click')
    await flushPromises()

    expect(writeText).toHaveBeenCalledWith('ES9121000418450200051332')
    expect(wrapper.find('.notice').text()).toBe('IBAN copiat')
    await vi.advanceTimersByTimeAsync(2000)
    expect(wrapper.find('.notice').exists()).toBe(false)
  })

  it('IBP-05: without a share menu, «Compartir» copies the text and says «Dades copiades»', async () => {
    vi.mocked(getAccountDetails).mockResolvedValue(demo)
    const wrapper = await mountView()

    await wrapper.find('button.share').trigger('click')
    await flushPromises()

    expect(writeText).toHaveBeenCalledWith('IBAN: ES91 2100 0418 4502 0005 1332 · BIC: EVOLESB1XXX · Titular: Usuari demo')
    expect(wrapper.find('.notice').text()).toBe('Dades copiades')
  })

  it('IBP-07: an error shows the generic text and «Reintentar», which loads the details', async () => {
    vi.mocked(getAccountDetails)
      .mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' })
      .mockResolvedValueOnce(demo)
    const wrapper = await mountView()
    expect(wrapper.text()).toContain("S'ha produït un error inesperat. Torna-ho a provar més tard.")
    expect(wrapper.find('button.share').exists()).toBe(false)

    await wrapper.find('button.retry').trigger('click')
    await flushPromises()

    expect(wrapper.find('button.iban').text()).toBe('ES91 2100 0418 4502 0005 1332')
  })
})
