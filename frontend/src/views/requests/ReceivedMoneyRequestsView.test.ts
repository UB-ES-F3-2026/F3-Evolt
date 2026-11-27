// @vitest-environment jsdom
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { formatDateTime } from '@/models/date'
import type { ReceivedMoneyRequest } from '@/models/moneyRequest'
import { getReceivedMoneyRequests } from '@/services/requests/moneyRequestsService'
import ReceivedMoneyRequestsView from './ReceivedMoneyRequestsView.vue'

// The view is thin over useReceivedMoneyRequestsViewModel, so only the service is mocked and the
// real ViewModel runs: mounting triggers `load` (US-16).
vi.mock('@/services/requests/moneyRequestsService', () => ({ getReceivedMoneyRequests: vi.fn() }))

function received(
  id: string,
  name: string,
  username: string,
  amount: number,
  status: ReceivedMoneyRequest['status'],
): ReceivedMoneyRequest {
  return {
    id,
    from: { id: `usr-${id.slice(-2)}`, name, username },
    amount,
    concept: `Concepte ${id}`,
    status,
    createdAt: '2026-11-23T19:30:00+01:00',
    expiresAt: '2026-11-30T00:00:00+01:00',
  }
}

// The four of the seed (docs/api.md §15.8), in the order the server sends them.
const seed = [
  received('req-06', 'Alicia', 'aliciaa415', 2500, 'pending'),
  received('req-05', 'Junhao', 'junhaozhang', 1200, 'paid'),
  received('req-04', 'Izan', 'izanfarreny47', 1800, 'rejected'),
  received('req-03', 'Jiajun', 'yayuuun', 4200, 'expired'),
]

beforeEach(() => {
  vi.mocked(getReceivedMoneyRequests).mockReset()
})

async function mountView(): Promise<VueWrapper> {
  const wrapper = mount(ReceivedMoneyRequestsView, {
    // The shell only provides the header and the menu; its slot is what this view renders.
    global: { stubs: { AppShell: { template: '<div><slot /></div>' } } },
  })
  await flushPromises()
  return wrapper
}

describe('ReceivedMoneyRequestsView', () => {
  it('SRP-02: one card per received request, in the order the server sends them', async () => {
    vi.mocked(getReceivedMoneyRequests).mockResolvedValue(seed)

    const wrapper = await mountView()

    expect(wrapper.findAll('.request .name').map((name) => name.text())).toEqual(['Alicia', 'Junhao', 'Izan', 'Jiajun'])
  })

  it('SRP-03: the name, then the @username, the concept and the date in grey, and the amount on the right', async () => {
    vi.mocked(getReceivedMoneyRequests).mockResolvedValue([seed[0]])

    const wrapper = await mountView()

    expect(wrapper.findAll('.request .muted').map((line) => line.text())).toEqual([
      '@aliciaa415',
      'Concepte req-06',
      formatDateTime('2026-11-23T19:30:00+01:00'),
    ])
    expect(wrapper.find('.request .amount').text()).toContain('25,00')
  })

  it('SRP-03: «Pendent», «Pagada», «Rebutjada» and «Caducada», each with the class that gives its colour', async () => {
    vi.mocked(getReceivedMoneyRequests).mockResolvedValue(seed)

    const wrapper = await mountView()

    expect(wrapper.findAll('.status').map((label) => [label.text(), label.classes()])).toEqual([
      ['Pendent', ['status', 'pending']],
      ['Pagada', ['status', 'paid']],
      ['Rebutjada', ['status', 'rejected']],
      ['Caducada', ['status', 'expired']],
    ])
  })

  it('SRP-04 (until US-39 and US-40): no card has any button yet', async () => {
    vi.mocked(getReceivedMoneyRequests).mockResolvedValue(seed)

    const wrapper = await mountView()

    expect(wrapper.findAll('.request button')).toHaveLength(0)
  })

  it('SRP-05: with no received request, «Encara no has rebut cap sol·licitud.»', async () => {
    vi.mocked(getReceivedMoneyRequests).mockResolvedValue([])

    const wrapper = await mountView()

    expect(wrapper.text()).toContain('Encara no has rebut cap sol·licitud.')
    expect(wrapper.findAll('.request')).toHaveLength(0)
  })

  it('SRP-06: an error shows the generic text and «Reintentar», which loads the list', async () => {
    vi.mocked(getReceivedMoneyRequests)
      .mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' })
      .mockResolvedValueOnce(seed)
    const wrapper = await mountView()
    expect(wrapper.text()).toContain("S'ha produït un error inesperat. Torna-ho a provar més tard.")

    await wrapper.find('button.retry').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.request')).toHaveLength(4)
  })
})
