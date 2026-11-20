// @vitest-environment jsdom
import { mount, RouterLinkStub } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import UserRow from './UserRow.vue'

const stubs = { global: { stubs: { RouterLink: RouterLinkStub } } }

describe('UserRow', () => {
  it('CUP-02: shows the initials, the name and the @username, and never an amount', () => {
    const row = mount(UserRow, { props: { user: { id: 'usr-02', name: 'Usuari nou', username: 'buit' } } })

    expect(row.find('.avatar').text()).toBe('UN')
    expect(row.find('.name').text()).toBe('Usuari nou')
    expect(row.find('.username').text()).toBe('@buit')
    expect(row.text()).not.toMatch(/€|\d+,\d{2}/)
  })

  it('CUP-11: a user without a name shows the @username as the name', () => {
    const row = mount(UserRow, { props: { user: { id: 'usr-09', name: null, username: 'anna' } } })

    expect(row.find('.name').text()).toBe('@anna')
  })

  it('CUP-08: with `to`, the whole row goes there', () => {
    const to = { name: 'send-payment', query: { to: 'usr-04' } }
    const row = mount(UserRow, {
      props: { user: { id: 'usr-04', name: 'Huabin', username: '123huabin123' }, to },
      ...stubs,
    })

    expect(row.findComponent(RouterLinkStub).props('to')).toEqual(to)
  })
})
