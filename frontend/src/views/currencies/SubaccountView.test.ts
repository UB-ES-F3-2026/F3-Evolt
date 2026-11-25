// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter, type Router } from 'vue-router'
import { mockAddSubaccount, mockRecordSubaccountMovement, mockSubaccounts } from '@/mocks/currencies'
import SubaccountView from './SubaccountView.vue'

// The screen with the mocks behind it (the default in tests): the literal texts of
// US-26 are fixed here, in the template where they live (PO decision D6).

function makeRouter(): Router {
  const empty = { template: '<div />' }
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: empty },
      { path: '/divises', name: 'currencies', component: empty },
      // The screen is mounted by hand below: the route only has to exist.
      { path: '/divises/:subaccountId', name: 'subaccount', component: empty },
    ],
  })
}

async function open(subaccountId: string) {
  const router = makeRouter()
  await router.push(`/divises/${subaccountId}`)
  await router.isReady()
  const view = mount(SubaccountView, { props: { subaccountId }, global: { plugins: [router] } })
  await flushPromises()
  return { view, router }
}

function usdId(): string {
  const usd = mockSubaccounts().items.find((subaccount) => subaccount.currency === 'USD')
  return usd?.id ?? mockAddSubaccount({ currency: 'USD' }).id
}

function plain(text: string): string {
  return text.replace(/[\u00a0\u202f]/g, ' ')
}

describe('SubaccountView (US-26)', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  it('ELP-01, ELP-07: the USD detail with «Saldo», «Últims moviments», the red «Eliminar subcompte» and no «Aportar»', async () => {
    const { view } = await open(usdId())

    expect(view.text()).toContain('USD · Dòlar nord-americà')
    expect(view.text()).toContain('Saldo')
    expect(plain(view.text())).toContain('0,00 $')
    expect(view.text()).toContain('Últims moviments')
    expect(view.text()).toContain('Encara no tens moviments')
    expect(view.get('button.delete').text()).toBe('Eliminar subcompte')
    expect(view.text()).not.toContain('Aportar')
    expect(view.text()).toContain('← Divises')
  })

  it('ELP-02: the EUR detail has no «Eliminar subcompte»', async () => {
    const { view } = await open('main')

    expect(view.text()).toContain('EUR · Euro')
    expect(view.find('button.delete').exists()).toBe(false)
  })

  it('ELP-03: with 0,01 $, «Abans d\'eliminar-lo has de deixar el saldo a 0» with «D\'acord», and nothing is deleted', async () => {
    const id = usdId()
    mockRecordSubaccountMovement(id, { amount: 1, concept: 'Canvi EUR → USD', date: '2026-11-19T10:00:00+01:00', type: 'income' })
    const { view } = await open(id)

    expect(view.text()).toContain('Canvi EUR → USD')
    expect(plain(view.text())).toContain('+0,01 $')
    await view.get('button.delete').trigger('click')

    const dialog = view.get('[role="dialog"]')
    expect(dialog.get('h2').text()).toBe("Abans d'eliminar-lo has de deixar el saldo a 0")
    expect(dialog.findAll('button').map((button) => button.text())).toEqual(["D'acord"])

    await dialog.get('button').trigger('click')
    expect(view.find('[role="dialog"]').exists()).toBe(false)
    expect(mockSubaccounts().items.some((subaccount) => subaccount.id === id)).toBe(true)

    // Back to 0,00 $ for the next tests, as an exchange to EUR would leave it.
    mockRecordSubaccountMovement(id, { amount: 1, concept: 'Canvi USD → EUR', date: '2026-11-19T11:00:00+01:00', type: 'expense' })
  })

  it('ELP-04: at 0,00 $, «Segur que vols eliminar aquest subcompte?» with «Cancel·lar» and «Eliminar»', async () => {
    const { view } = await open(usdId())
    await view.get('button.delete').trigger('click')

    const dialog = view.get('[role="dialog"]')
    expect(dialog.get('h2').text()).toBe('Segur que vols eliminar aquest subcompte?')
    expect(dialog.text()).toContain('Els moviments en euros dels canvis es queden a «Moviments».')
    expect(dialog.findAll('button').map((button) => button.text())).toEqual(['Cancel·lar', 'Eliminar'])
    expect(dialog.get('.confirm').classes()).toContain('danger')

    await dialog.get('.cancel').trigger('click')
    expect(view.find('[role="dialog"]').exists()).toBe(false)
  })

  it('ELP-05: «Eliminar» shows the tick «Subcompte eliminat» and the USD is gone', async () => {
    const id = usdId()
    const { view } = await open(id)
    await view.get('button.delete').trigger('click')

    await view.get('[role="dialog"] .confirm').trigger('click')
    await flushPromises()

    expect(view.get('[role="status"]').text()).toContain('Subcompte eliminat')
    expect(view.find('[role="dialog"]').exists()).toBe(false)
    expect(mockSubaccounts().items.some((subaccount) => subaccount.id === id)).toBe(false)
  })

  it('an unknown sub-account says «No s\'ha trobat el subcompte.»', async () => {
    const { view } = await open('sub-99')

    expect(view.text()).toContain("No s'ha trobat el subcompte.")
    expect(view.find('button.delete').exists()).toBe(false)
  })
})
