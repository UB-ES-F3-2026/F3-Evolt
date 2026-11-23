/** /api/pots — the user's pots (US-17, US-18, US-19). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockContribute, mockCreatePot, mockPotMovements, mockPots, mockWithdraw } from '@/mocks/pots'
import {
  fromApiContribution,
  fromApiPot,
  fromApiPotMovements,
  fromApiPots,
  fromApiWithdrawal,
  type Contribution,
  type ContributionJson,
  type CreatePotRequest,
  type Pot,
  type PotJson,
  type PotMovement,
  type PotMovementsJson,
  type PotsJson,
  type Withdrawal,
  type WithdrawalJson,
} from '@/models/pot'

export async function getPots(): Promise<Pot[]> {
  const json = useMocks() ? mockPots() : await apiGet<PotsJson>('/api/pots')
  return fromApiPots(json.items)
}

export async function createPot(request: CreatePotRequest): Promise<Pot> {
  const json = useMocks() ? mockCreatePot(request) : await apiPost<PotJson>('/api/pots', request)
  return fromApiPot(json)
}

export async function getPotMovements(potId: string): Promise<PotMovement[]> {
  const json = useMocks()
    ? mockPotMovements(potId)
    : await apiGet<PotMovementsJson>(`/api/pots/${encodeURIComponent(potId)}/movements`)
  return fromApiPotMovements(json.items)
}

export async function contribute(potId: string, amountCents: number): Promise<Contribution> {
  const json = useMocks()
    ? mockContribute(potId, { amount: amountCents })
    : await apiPost<ContributionJson>(`/api/pots/${encodeURIComponent(potId)}/contributions`, {
        amount: amountCents,
      })
  return fromApiContribution(json)
}

export async function withdraw(potId: string, amountCents: number): Promise<Withdrawal> {
  const json = useMocks()
    ? mockWithdraw(potId, { amount: amountCents })
    : await apiPost<WithdrawalJson>(`/api/pots/${encodeURIComponent(potId)}/withdrawals`, {
        amount: amountCents,
      })
  return fromApiWithdrawal(json)
}
