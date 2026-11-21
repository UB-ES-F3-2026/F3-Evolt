// @vitest-environment jsdom
import { mount, RouterLinkStub } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { Pot } from '@/models/pot'
import PotRow from './PotRow.vue'

function pot(overrides: Partial<Pot> = {}): Pot {
  return {
    id: 'pot-01',
    name: 'Vacances',
    balance: 15000,
    target: 100000,
    color: 'blue',
    percentage: 15,
    goalStatus: 'in_progress',
    ...overrides,
  }
}

describe('PotRow', () => {
  it('shows a mini progress bar under the name when the pot has a goal (OP-07)', () => {
    const row = mount(PotRow, {
      props: { pot: pot() },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

    expect(row.find('[role="progressbar"]').exists()).toBe(true)
    expect(row.find('.mini-percent').text()).toMatch(/^15\s%$/)
    expect(row.text()).toContain('Vacances')
    expect(row.find('.balance').text()).toContain('150')
    expect(row.getComponent(RouterLinkStub).props('to')).toEqual({
      name: 'pot',
      params: { potId: 'pot-01' },
    })
  })

  it('renders no progress bar when the pot has no goal (OP-07)', () => {
    const row = mount(PotRow, {
      props: {
        pot: pot({ id: 'pot-02', name: 'Emergències', target: null, percentage: null, goalStatus: null }),
      },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

    expect(row.find('[role="progressbar"]').exists()).toBe(false)
    expect(row.text()).not.toMatch(/\d+\s?%/)
    expect(row.text()).toContain('Emergències')
    expect(row.find('.balance').text()).toContain('150')
  })
})
