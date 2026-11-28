/** /api/split-expenses — dividing an expense into money requests (US-30). One function per endpoint. */

import { apiPost } from '@/services/apiClient'
import { useMocks } from '@/mocks'
import { mockCreateSplitExpense } from '@/mocks/splitExpenses'
import { fromApiSplitExpense, type NewSplitExpense, type SplitExpense, type SplitExpenseJson } from '@/models/splitExpense'

/** Creates one request per participant, all or none (docs/api.md §17.2). */
export async function createSplitExpense(expense: NewSplitExpense): Promise<SplitExpense> {
  const json = useMocks()
    ? mockCreateSplitExpense({ ...expense, parts: expense.parts.map((part) => ({ ...part })) })
    : await apiPost<SplitExpenseJson>('/api/split-expenses', expense)
  return fromApiSplitExpense(json)
}
