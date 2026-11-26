/**
 * The details of the person's account: IBAN, BIC and holder (docs/api.md §16.1, US-12).
 *
 * The server sends the IBAN without spaces; the screen groups it in fours and copies it
 * without spaces. The text of «Compartir» carries the grouped IBAN (PO decision, 26/11).
 */

export interface AccountDetails {
  iban: string
  bic: string
  holder: string
}

/** GET /api/account. */
export type AccountDetailsJson = AccountDetails

export function fromApiAccountDetails(json: AccountDetailsJson): AccountDetails {
  return { iban: json.iban, bic: json.bic, holder: json.holder }
}

/** `"ES9121000418450200051332"` → `"ES91 2100 0418 4502 0005 1332"`. */
export function groupIban(iban: string): string {
  return iban.replace(/\s+/g, '').replace(/(.{4})(?=.)/g, '$1 ')
}

/** «IBAN: ES91 2100 0418 4502 0005 1332 · BIC: EVOLESB1XXX · Titular: Usuari demo» (US-12, criterion 5). */
export function shareText(details: AccountDetails): string {
  return `IBAN: ${groupIban(details.iban)} · BIC: ${details.bic} · Titular: ${details.holder}`
}
