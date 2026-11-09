/** A problem reported on a movement (US-11, docs/api.md §10.4). */

/** The longest description, counted without the spaces at the ends. */
export const MAX_REPORT_LENGTH = 500

/** POST /api/movements/{movementId}/reports answer. */
export interface MovementReport {
  id: string
  movementId: string
  description: string
  createdAt: string
}

export function isValidReportDescription(description: string): boolean {
  const text = description.trim()
  return text !== '' && text.length <= MAX_REPORT_LENGTH
}
