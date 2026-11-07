/** What a movement's receipt says: the same texts as the «Detall del moviment» screen (docs/api.md §10.5). */
export interface ReceiptContent {
  amount: string
  isIncome: boolean
  concept: string
  rows: { label: string; value: string }[]
}

/** `"EVT-000029"` → `"justificant-EVT-000029.pdf"` */
export function receiptFileName(reference: string): string {
  return `justificant-${reference}.pdf`
}
