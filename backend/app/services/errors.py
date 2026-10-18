"""Codis d'error del contracte i excepció del servei (T07.2).

Aquest mòdul és pur Python: no importa FastAPI ni cap HTTP. La taula de la
secció 5 de docs/api.md viu aquí una sola vegada (codis, estat HTTP i missatge
per defecte en català). Els serveis aixequen `ApiError` amb un codi estable,
i `app/main.py` el converteix a la resposta `{ code, message, details? }`.

Es permet substituir el missatge perquè els missatges del contracte són
orientatius: p. ex. T09 pot dir "Avui encara pots recarregar X €" en lloc del
missatge per defecte del `DAILY_LIMIT_EXCEEDED`.
"""

INVALID_AMOUNT = "INVALID_AMOUNT"
AMOUNT_OVER_LIMIT = "AMOUNT_OVER_LIMIT"
DAILY_LIMIT_EXCEEDED = "DAILY_LIMIT_EXCEEDED"
VALIDATION_ERROR = "VALIDATION_ERROR"
INTERNAL_ERROR = "INTERNAL_ERROR"

# Codi d'error → estat HTTP de la resposta.
ERROR_STATUS: dict[str, int] = {
    INVALID_AMOUNT: 422,
    AMOUNT_OVER_LIMIT: 422,
    DAILY_LIMIT_EXCEEDED: 422,
    VALIDATION_ERROR: 422,
    INTERNAL_ERROR: 500,
}

# Missatge per defecte de cada codi (docs/api.md §5). El contracte els marca
# com a orientatius, així que un servei pot passar-ne un de propi.
ERROR_MESSAGES: dict[str, str] = {
    INVALID_AMOUNT: "L'import ha de ser més gran que 0.",
    AMOUNT_OVER_LIMIT: "L'import màxim per recàrrega és de 500,00 €.",
    DAILY_LIMIT_EXCEEDED: "Has superat el límit diari de recàrrega.",
    VALIDATION_ERROR: "Les dades de la petició no són vàlides.",
    INTERNAL_ERROR: "S'ha produït un error inesperat. Torna-ho a provar més tard.",
}


def error_body(
    code: str,
    message: str,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    """Construeix el cos d'error del contracte `{ code, message, details? }`.

    P6 (docs/api.md §5): la clau `details` mai no apareix buida ni null.
    """
    body: dict[str, object] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return body


class ApiError(Exception):
    """Error de negoci amb el codi del contracte (docs/api.md §5).

    Els serveis la llencen amb un codi estable; `message` i `details` són
    opcionals. Sense `message` es fa servir el per defecte d'`ERROR_MESSAGES`.
    """

    def __init__(
        self,
        code: str,
        message: str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        if code not in ERROR_STATUS:
            raise ValueError(f"Codi d'error fora del contracte: {code!r}")
        self.code = code
        self.message = message or ERROR_MESSAGES[code]
        self.details = details
        super().__init__(self.message)
