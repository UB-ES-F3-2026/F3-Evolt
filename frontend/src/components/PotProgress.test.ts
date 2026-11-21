// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { Pot } from '@/models/pot'
import PotProgress from './PotProgress.vue'

// The API sends `percentage` and `goalStatus` (docs/api.md §11.1); the fixtures carry
// them too, because the component paints them and never derives them.

// The ids below are the US-20 rows of docs/proves-estalvi.md (added by PR #177):
// OP-01…OP-05 and OP-07/OP-08 are covered here; OP-06 (withdrawal) belongs to US-19
// and cannot be tested in this PR.
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

describe('PotProgress', () => {
  it('shows amounts, track and badge while in progress (OP-01)', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot() } })

    expect(wrapper.find('.progress-amounts').text()).toMatch(/150,00\s€ de 1\.000,00\s€/)

    const track = wrapper.find('.progress-track')
    expect(track.attributes('role')).toBe('progressbar')
    expect(track.attributes('aria-label')).toBe("Progrés de Vacances cap a l'objectiu")
    expect(track.attributes('aria-valuemin')).toBe('0')
    expect(track.attributes('aria-valuemax')).toBe('100')
    expect(track.attributes('aria-valuenow')).toBe('15')
    expect(track.attributes('aria-valuetext')).toBe(`15 % de l'objectiu`)

    expect(wrapper.find('.progress-percent').text()).toContain(`15\u00A0%`)
    expect(wrapper.find('.progress-fill').attributes('style')).toContain('width: 15%')

    const badge = wrapper.find('.badge-status')
    expect(badge.text()).toBe('En progrés')
    expect(badge.classes()).not.toContain('achieved')
  })

  it('clamps the bar at 100 % and marks the goal as achieved when over 100 % (OP-05)', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ balance: 115000, percentage: 115, goalStatus: 'achieved' }) },
    })

    expect(wrapper.find('.progress-percent').text()).toContain(`115\u00A0%`)
    expect(wrapper.find('.progress-track').attributes('aria-valuenow')).toBe('100')
    expect(wrapper.find('.progress-track').attributes('aria-valuetext')).toBe(`115 % de l'objectiu`)
    expect(wrapper.find('.progress-fill').attributes('style')).toContain('width: 100%')
    expect(wrapper.find('.progress-fill').classes()).toContain('achieved')
    expect(wrapper.find('.badge-status').classes()).toContain('achieved')
    expect(wrapper.find('.badge-status').text()).toBe('Objectiu assolit')
  })

  it('masks the amounts when hidden, but keeps the percent visible', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot(), hidden: true } })

    expect(wrapper.find('.progress-amounts').text()).not.toContain('150,00')
    expect(wrapper.text()).toContain('••••')
    expect(wrapper.find('.progress-percent').text()).toContain(`15\u00A0%`)
  })

  it('renders the compact variant with a mini track and no amounts or badge (OP-07)', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot(), compact: true } })

    const track = wrapper.find('.mini-track[role="progressbar"]')
    expect(track.exists()).toBe(true)
    expect(track.attributes('aria-label')).toBe("Progrés de Vacances cap a l'objectiu")
    expect(track.attributes('aria-valuemin')).toBe('0')
    expect(track.attributes('aria-valuemax')).toBe('100')
    expect(track.attributes('aria-valuenow')).toBe('15')
    expect(track.attributes('aria-valuetext')).toBe(`15 % de l'objectiu`)
    expect(wrapper.find('.mini-percent').text()).toContain(`15\u00A0%`)
    expect(wrapper.find('.progress-amounts').exists()).toBe(false)
    expect(wrapper.find('.badge-status').exists()).toBe(false)
  })

  it('renders nothing when the pot has no goal (OP-02)', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ target: null, percentage: null, goalStatus: null }) },
    })

    expect(wrapper.find('[role="progressbar"]').exists()).toBe(false)
    expect(wrapper.find('.progress-amounts').exists()).toBe(false)
    expect(wrapper.find('.badge-status').exists()).toBe(false)
    expect(wrapper.find('.mini-percent').exists()).toBe(false)
    expect(wrapper.text()).toBe('')
  })

  it('marks the goal as achieved on exact equality (OP-04)', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ balance: 100000, percentage: 100, goalStatus: 'achieved' }) },
    })

    expect(wrapper.find('.progress-track').attributes('aria-valuenow')).toBe('100')
    expect(wrapper.find('.badge-status').text()).toBe('Objectiu assolit')
    expect(wrapper.find('.badge-status').classes()).toContain('achieved')
  })

  it('paints the 63 % the API sends for 5000 of 8000 (OP-03)', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ balance: 5000, target: 8000, percentage: 63, goalStatus: 'in_progress' }) },
    })

    expect(wrapper.find('.progress-amounts').text()).toMatch(/50,00\s€ de 80,00\s€/)
    expect(wrapper.find('.progress-percent').text()).toContain(`63\u00A0%`)
    expect(wrapper.find('.badge-status').text()).toBe('En progrés')
  })

  it('paints 99 % and «En progrés» for 79,99 € of 80,00 €, as the API sends it (US-20)', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ balance: 7999, target: 8000, percentage: 99, goalStatus: 'in_progress' }) },
    })

    expect(wrapper.find('.progress-amounts').text()).toMatch(/79,99\s€ de 80,00\s€/)
    expect(wrapper.find('.progress-percent').text()).toContain(`99\u00A0%`)
    expect(wrapper.find('.progress-track').attributes('aria-valuenow')).toBe('99')
    expect(wrapper.find('.progress-fill').attributes('style')).toContain('width: 99%')
    expect(wrapper.find('.badge-status').text()).toBe('En progrés')
  })

  it('renders nothing when the API omits the goal progress (US-20)', () => {
    // An answer from before US-20 sends no fields at all; a pot without a goal sends null.
    const answers: Partial<Pot>[] = [
      { percentage: undefined, goalStatus: undefined },
      { percentage: null, goalStatus: null },
    ]

    for (const overrides of answers) {
      const detail = mount(PotProgress, { props: { pot: pot(overrides) } })
      expect(detail.find('[role="progressbar"]').exists()).toBe(false)
      expect(detail.find('.progress-percent').exists()).toBe(false)
      expect(detail.find('.badge-status').exists()).toBe(false)
      expect(detail.text()).toBe('')

      const compact = mount(PotProgress, { props: { pot: pot(overrides), compact: true } })
      expect(compact.find('[role="progressbar"]').exists()).toBe(false)
      expect(compact.find('.progress-percent').exists()).toBe(false)
      expect(compact.find('.badge-status').exists()).toBe(false)
      expect(compact.find('.mini-percent').exists()).toBe(false)
      expect(compact.text()).toBe('')
    }
  })

  it('renders nothing when a malformed answer carries the fields but no target (US-20)', () => {
    // §11.1 sends both fields null without a goal: fields without a target are not trusted.
    const malformed = pot({ target: null, percentage: 63, goalStatus: 'achieved' })

    const detail = mount(PotProgress, { props: { pot: malformed } })
    expect(detail.find('[role="progressbar"]').exists()).toBe(false)
    expect(detail.find('.progress-percent').exists()).toBe(false)
    expect(detail.find('.badge-status').exists()).toBe(false)
    expect(detail.text()).toBe('')

    const compact = mount(PotProgress, { props: { pot: malformed, compact: true } })
    expect(compact.find('[role="progressbar"]').exists()).toBe(false)
    expect(compact.find('.progress-percent').exists()).toBe(false)
    expect(compact.find('.badge-status').exists()).toBe(false)
    expect(compact.find('.mini-percent').exists()).toBe(false)
    expect(compact.text()).toBe('')
  })

  it('exposes the value as ARIA and visible text, not only as colour (OP-08)', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot() } })

    const track = wrapper.find('[role="progressbar"]')
    expect(track.exists()).toBe(true)
    expect(track.attributes('aria-valuenow')).toBe('15')
    expect(track.attributes('aria-valuetext')).toBe(`15 % de l'objectiu`)
    expect(wrapper.find('.progress-percent').text()).toContain(`15\u00A0%`)
    expect(wrapper.find('.badge-status').text()).toBe('En progrés')
  })
})
