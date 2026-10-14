/**
 * Movement mapper: API JSON (docs/api.md §3) → app object.
 *
 * Contract invariants worth remembering:
 * - `amount` is always a positive integer in cents; direction comes from `type`.
 * - `icon` is a closed list; unknown values fall back to `other`.
 */

const ICONS = ['topup', 'salary', 'transfer', 'shopping', 'food', 'transport', 'other']
const TYPES = ['income', 'expense']

export function fromApiMovement(json) {
  return {
    id: json.id,
    amount: json.amount,
    concept: json.concept,
    date: json.date,
    type: TYPES.includes(json.type) ? json.type : 'expense',
    icon: ICONS.includes(json.icon) ? json.icon : 'other',
  }
}

export function fromApiMovements(jsonList) {
  return (jsonList ?? []).map(fromApiMovement)
}
