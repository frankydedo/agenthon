"""Output strutturato: chiedere al modello un JSON che rispetti uno schema Pydantic.

    fattura = chiedi_strutturato(provider, "Estrai i dati della fattura.", testo_pdf, Fattura)

Se la risposta non è valida (JSON rotto, data nel formato sbagliato, campo mancante...),
l'errore viene rimandato al modello, che ha un altro tentativo per correggersi.
Funziona con qualsiasi provider perché usa solo testo (niente funzioni specifiche di un fornitore).
"""
import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from core.llm import LLMProvider, Message

M = TypeVar("M", bound=BaseModel)


def chiedi_strutturato(provider: LLMProvider, istruzioni: str, testo: str, schema: type[M], tentativi: int = 2) -> M:
    sistema = (
        f"{istruzioni}\n\nRispondi SOLO con un oggetto JSON valido (senza testo prima o dopo) "
        f"che rispetti questo JSON Schema:\n{json.dumps(schema.model_json_schema(), ensure_ascii=False)}"
    )
    messaggi = [Message(role="system", content=sistema), Message(role="user", content=testo)]
    ultimo_errore = ""
    for _ in range(tentativi):
        risposta = provider.chat(messaggi, tools=[])
        try:
            return schema.model_validate_json(_estrai_json(risposta.text))
        except ValidationError as e:
            ultimo_errore = str(e)
            messaggi.append(Message(role="assistant", content=risposta.text))
            messaggi.append(
                Message(role="user", content=f"La risposta non è valida:\n{e}\nCorreggi e rispondi solo con il JSON.")
            )
    raise ValueError(f"Il modello non ha prodotto un JSON valido dopo {tentativi} tentativi: {ultimo_errore}")


def _estrai_json(testo: str) -> str:
    """Toglie eventuali ```json ... ``` o frasi attorno all'oggetto JSON."""
    inizio, fine = testo.find("{"), testo.rfind("}")
    return testo[inizio : fine + 1] if inizio != -1 and fine > inizio else testo
