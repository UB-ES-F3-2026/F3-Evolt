// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { Pot } from '@/models/pot'
import PotProgress from './PotProgress.vue'

function pot(overrides: Partial<Pot> = {}): Pot {
  return {
    id: 'pot-01',
    name: 'Vacances',
    balance: 15000,
    target: 100000,
    color: 'blue',
    ...overrides,
  }
}

describe('PotProgress', () => {
  it('shows amounts, track and badge while in progress (detail)', () => {
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

  it('clamps the bar at 100 % and marks the goal as achieved when over 100 %', () => {
    const wrapper = mount(PotProgress, {
      props: { pot: pot({ balance: 115000 }) },
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

  it('renders the compact variant with a mini track and no amounts or badge', () => {
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

  it('renders nothing when the pot has no goal', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot({ target: null }) } })

    expect(wrapper.find('[role="progressbar"]').exists()).toBe(false)
    expect(wrapper.find('.progress-amounts').exists()).toBe(false)
    expect(wrapper.find('.badge-status').exists()).toBe(false)
    expect(wrapper.find('.mini-percent').exists()).toBe(false)
    expect(wrapper.text()).toBe('')
  })

  it('marks the goal as achieved on exact equality', () => {
    const wrapper = mount(PotProgress, { props: { pot: pot({ balance: 100000 }) } })

    expect(wrapper.find('.progress-track').attributes('aria-valuenow')).toBe('100')
    expect(wrapper.find('.badge-status').text()).toBe('Objectiu assolit')
    expect(wrapper.find('.badge-status').classes()).toContain('achieved')
  })
})
