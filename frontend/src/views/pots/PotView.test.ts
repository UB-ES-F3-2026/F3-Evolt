// @vitest-environment jsdom
import { flushPromises, mount, RouterLinkStub, type VueWrapper } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Pot } from '@/models/pot'
import { getPotMovements, getPots } from '@/services/pots/potsService'
import PotView from './PotView.vue'

// The view is thin over usePotViewModel, so the services it talks to are mocked and
// the real viewmodel runs: mount triggers `load` onMounted (US-20).
vi.mock('@/services/pots/potsService', () => ({ getPots: vi.fn(), getPotMovements: vi.fn() }))

const vacances: Pot = {
  id: 'pot-01',
  name: 'Vacances',
  balance: 15000,
  target: 100000,
  color: 'blue',
  percentage: 15,
  goalStatus: 'in_progress',
}
const emergencies: Pot = {
  id: 'pot-02',
  name: 'Emergències',
  balance: 42000,
  target: null,
  color: 'blue',
  percentage: null,
  goalStatus: null,
}

beforeEach(() => {
  vi.mocked(getPots).mockReset()
  vi.mocked(getPotMovements).mockReset()
  vi.mocked(getPotMovements).mockResolvedValue([])
})

async function mountView(pot: Pot): Promise<VueWrapper> {
  vi.mocked(getPots).mockResolvedValue([pot])
  const wrapper = mount(PotView, {
    props: { potId: pot.id },
    global: {
      stubs: {
        // The shell only provides layout; its slot is what the view renders.
        AppShell: { template: '<div><slot /></div>' },
        RouterLink: RouterLinkStub,
      },
    },
  })
  await flushPromises()
  return wrapper
}

describe('PotView', () => {
  it('shows the goal progress for a pot with a target (OP-01)', async () => {
    const wrapper = await mountView(vacances)

    expect(wrapper.find('[role="progressbar"]').exists()).toBe(true)
    expect(wrapper.find('.progress-percent').text()).toContain('15\u00A0%')
    expect(wrapper.text()).toContain('Objectiu:')
    expect(wrapper.text()).toContain('Aportar')
  })

  it('shows no progress for a pot without a target, but keeps «Aportar» (OP-02)', async () => {
    const wrapper = await mountView(emergencies)

    expect(wrapper.find('[role="progressbar"]').exists()).toBe(false)
    expect(wrapper.find('.progress-percent').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Objectiu:')
    expect(wrapper.text()).toContain('Aportar')
  })
})
