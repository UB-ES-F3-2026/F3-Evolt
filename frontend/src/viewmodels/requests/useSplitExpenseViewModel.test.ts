import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import type { SplitExpense } from '@/models/splitExpense'
import type { UserSummary } from '@/models/user'
import { useSplitExpenseViewModel, type SplitExpenseDependencies } from './useSplitExpenseViewModel'

const izan: UserSummary = { id: 'usr-05', name: 'Izan', username: 'izanfarreny47' }
const alicia: UserSummary = { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' }
const marti: UserSummary = { id: 'usr-08', name: 'Martí', username: 'sudo-itramplay' }

// The answer of POST /api/split-expenses for the expense of docs/proves-despeses.md (D0).
const created: SplitExpense = {
  id: 'split-01',
  concept: "Sopar d'aniversari",
  total: 6000,
  myShare: 1500,
  createdAt: '2026-11-15T21:15:00+01:00',
  status: 'pending',
  people: 4,
  paidCount: 0,
  pendingAmount: 4500,
  parts: [izan, alicia, marti].map((to, index) => ({ requestId: `req-0${index + 7}`, to, amount: 1500, status: 'pending' })),
}

function setUp(overrides: Partial<SplitExpenseDependencies> = {}) {
  const dependencies = {
    searchUsers: vi.fn((_q: string) => Promise.resolve([izan, alicia, marti])),
    wait: vi.fn(() => Promise.resolve()),
    createSplitExpense: vi.fn(() => Promise.resolve(created)),
    goToRequests: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useSplitExpenseViewModel(dependencies), dependencies }
}

type ViewModel = ReturnType<typeof useSplitExpenseViewModel>

async function fill(viewModel: ViewModel, total: string, people: UserSummary[] = [izan, alicia, marti]) {
  viewModel.total.value = total
  viewModel.concept.value = "Sopar d'aniversari"
  people.forEach((user) => viewModel.add(user))
  await nextTick()
}

function user(number: number): UserSummary {
  return { id: `usr-${number}`, name: `Persona ${number}`, username: `persona${number}` }
}

describe('useSplitExpenseViewModel', () => {
  it('DDP-10: without participants, «Afegeix almenys un participant.» and «Enviar sol·licituds» disabled', async () => {
    const { viewModel } = setUp()
    viewModel.total.value = '60'
    viewModel.concept.value = "Sopar d'aniversari"
    await nextTick()

    expect(viewModel.hasNoParticipants.value).toBe(true)
    expect(viewModel.canSend.value).toBe(false)
  })

  it('DDP-02: a chosen user is in the list once, shows as already there in the search, and «×» takes them out', () => {
    const { viewModel } = setUp()
    viewModel.query.value = 'iz'

    viewModel.add(izan)
    viewModel.add(izan)

    expect(viewModel.participants.value.map((one) => one.user.id)).toEqual(['usr-05'])
    expect(viewModel.isChosen(izan)).toBe(true)
    expect(viewModel.query.value).toBe('')
    viewModel.remove('usr-05')
    expect(viewModel.participants.value).toEqual([])
  })

  it('DDP-06: with 9 participants the search is full and a tenth is not added', () => {
    const { viewModel } = setUp()

    for (let number = 1; number <= 10; number++) viewModel.add(user(number))

    expect(viewModel.participants.value).toHaveLength(9)
    expect(viewModel.isFull.value).toBe(true)
  })

  it('DDP-03: «Parts iguals» is the default: 60,00 € among 3 and me → 15,00 € each', async () => {
    const { viewModel } = setUp()

    await fill(viewModel, '60')

    expect(viewModel.shareMode.value).toBe('equal')
    expect(viewModel.shares.value).toEqual({ parts: [1500, 1500, 1500], mine: 1500 })
    expect(viewModel.canSend.value).toBe(true)
  })

  it('DDP-03: 100,00 € among 2 and me → 33,33 € each and 33,34 € for me', async () => {
    const { viewModel } = setUp()

    await fill(viewModel, '100', [izan, alicia])

    expect(viewModel.shares.value).toEqual({ parts: [3333, 3333], mine: 3334 })
  })

  it('DDP-04: «Imports personalitzats» starts from the equal parts; if they do not add up, the message and no sending', async () => {
    const { viewModel } = setUp()
    await fill(viewModel, '60')

    viewModel.setShareMode('custom')
    expect(viewModel.participants.value.map((one) => one.typed)).toEqual(['15,00', '15,00', '15,00'])
    expect(viewModel.myTyped.value).toBe('15,00')

    viewModel.participants.value[0].typed = '20'
    viewModel.participants.value[1].typed = '10'
    viewModel.participants.value[2].typed = '10'
    await nextTick()
    expect(viewModel.sharesError.value).toBe('La suma de les parts ha de ser igual al total.')
    expect(viewModel.canSend.value).toBe(false)

    viewModel.myTyped.value = '20'
    await nextTick()
    expect(viewModel.sharesError.value).toBeNull()
    expect(viewModel.canSend.value).toBe(true)
  })

  it('DDP-04: a part at 0, mine included, says «Cada part ha de ser més gran que 0.»', async () => {
    const { viewModel } = setUp()
    await fill(viewModel, '60')
    viewModel.setShareMode('custom')

    viewModel.myTyped.value = '0'
    await nextTick()

    expect(viewModel.sharesError.value).toBe('Cada part ha de ser més gran que 0.')
    expect(viewModel.canSend.value).toBe(false)
  })

  it('DDP-05: back to «Parts iguals», the parts are worked out again and what was typed is lost', async () => {
    const { viewModel } = setUp()
    await fill(viewModel, '60')
    viewModel.setShareMode('custom')
    viewModel.participants.value[0].typed = '20'

    viewModel.setShareMode('equal')

    expect(viewModel.participants.value[0].typed).toBe('')
    expect(viewModel.shares.value).toEqual({ parts: [1500, 1500, 1500], mine: 1500 })
  })

  it('DDP-07: sends every part in cents, says how many and what is pending, and goes back to the list after 1,5 s', async () => {
    const { viewModel, dependencies } = setUp()
    await fill(viewModel, '60')

    expect(await viewModel.send()).toBe(true)

    expect(dependencies.createSplitExpense).toHaveBeenCalledWith({
      concept: "Sopar d'aniversari",
      total: 6000,
      myShare: 1500,
      parts: [
        { toUserId: 'usr-05', amount: 1500 },
        { toUserId: 'usr-03', amount: 1500 },
        { toUserId: 'usr-08', amount: 1500 },
      ],
    })
    expect(viewModel.confirmation.value).toEqual({
      title: 'Has enviat 3 sol·licituds',
      pending: 'Pendent de cobrar: 45,00 €',
    })
    expect(dependencies.wait).toHaveBeenCalledWith(1500)
    expect(dependencies.goToRequests).toHaveBeenCalled()
  })

  it('DDP-09: an error from the server shows under the button and keeps everything typed', async () => {
    const { viewModel, dependencies } = setUp({
      createSplitExpense: vi.fn(() => Promise.reject({ code: 'INTERNAL_ERROR', message: 'x' })),
    })
    await fill(viewModel, '60')

    expect(await viewModel.send()).toBe(false)

    expect(viewModel.submitError.value).toBe("S'ha produït un error inesperat. Torna-ho a provar més tard.")
    expect(viewModel.participants.value).toHaveLength(3)
    expect(viewModel.total.value).toBe('60')
    expect(viewModel.canSend.value).toBe(true)
    expect(dependencies.goToRequests).not.toHaveBeenCalled()
  })

  it('a total over 1.000.000,00 € is not valid', async () => {
    const { viewModel } = setUp()

    await fill(viewModel, '1000000,01')

    expect(viewModel.totalError.value).toBe("L'import màxim és d'1.000.000,00 €.")
    expect(viewModel.canSend.value).toBe(false)
  })
})
