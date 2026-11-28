// @vitest-environment jsdom
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import type { UserSummary } from '@/models/user'
import { searchUsers } from '@/services/usersService'
import NewMoneyRequestView from './NewMoneyRequestView.vue'

// The view is thin over its two ViewModels: only the search is a fake, and the real ViewModels run.
vi.mock('@/services/usersService', () => ({ searchUsers: vi.fn() }))

const izan: UserSummary = { id: 'usr-05', name: 'Izan', username: 'izanfarreny47' }
const alicia: UserSummary = { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' }

beforeEach(() => {
  vi.mocked(searchUsers).mockReset()
  vi.mocked(searchUsers).mockResolvedValue([izan, alicia])
})

async function mountView(): Promise<VueWrapper> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      // The view is mounted below; the route only gives it a current location.
      { path: '/requests/new', name: 'new-money-request', component: { template: '<div />' } },
      { path: '/requests', name: 'money-requests', component: { template: '<div />' } },
    ],
  })
  await router.push('/requests/new')
  const wrapper = mount(NewMoneyRequestView, {
    // The shell only provides the header and the menu; its slot is what this view renders.
    global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' } } },
  })
  await flushPromises()
  return wrapper
}

/** Types in the participants search and waits for the pause after typing (US-13). */
async function searchFor(wrapper: VueWrapper, text: string): Promise<void> {
  await wrapper.find('.participants .search-input').setValue(text)
  await new Promise((resolve) => setTimeout(resolve, 300))
  await flushPromises()
}

function chip(wrapper: VueWrapper, text: string) {
  const found = wrapper.findAll('.chip').find((button) => button.text() === text)
  if (found === undefined) throw new Error(`No chip «${text}»`)
  return found
}

describe('NewMoneyRequestView · Dividir una despesa', () => {
  it('DDP-01: «A una persona» is the default; «Dividir una despesa» shows the total, the concept and the participants', async () => {
    const wrapper = await mountView()
    expect(chip(wrapper, 'A una persona').attributes('aria-pressed')).toBe('true')
    expect(wrapper.text()).toContain('Destinatari')

    await chip(wrapper, 'Dividir una despesa').trigger('click')

    expect(chip(wrapper, 'Dividir una despesa').attributes('aria-pressed')).toBe('true')
    expect(wrapper.findAll('.label').map((label) => label.text())).toEqual(['Import total', 'Concepte', 'Participants'])
    expect(wrapper.text()).not.toContain('Destinatari')
  })

  it('DDP-10: without participants, «Afegeix almenys un participant.» and «Enviar sol·licituds» disabled', async () => {
    const wrapper = await mountView()
    await chip(wrapper, 'Dividir una despesa').trigger('click')

    await wrapper.find('#split-total').setValue('60')
    await wrapper.find('#split-concept').setValue("Sopar d'aniversari")

    expect(wrapper.find('.participants .hint').text()).toBe('Afegeix almenys un participant.')
    expect(wrapper.find('button[type="submit"]').text()).toBe('Enviar sol·licituds')
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })

  it('DDP-02 and DDP-03: a chosen person gets a row with their part and «×», and shows «Ja hi és» in the search', async () => {
    const wrapper = await mountView()
    await chip(wrapper, 'Dividir una despesa').trigger('click')
    await wrapper.find('#split-total').setValue('60')
    await wrapper.find('#split-concept').setValue("Sopar d'aniversari")

    await searchFor(wrapper, 'iz')
    await wrapper.findAll('.result')[0].trigger('click')

    const rows = wrapper.findAll('.share')
    expect(rows.map((row) => row.find('.name').text())).toEqual(['Izan', 'Jo'])
    expect(rows.map((row) => row.find('.amount').text())).toEqual(['30,00 €', '30,00 €'])
    expect(rows[0].find('.remove').attributes('aria-label')).toBe('Treure Izan')

    await searchFor(wrapper, 'iz')
    const izanResult = wrapper.findAll('.result')[0]
    expect(izanResult.text()).toContain('Ja hi és')
    expect(izanResult.attributes('disabled')).toBeDefined()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
  })
})
