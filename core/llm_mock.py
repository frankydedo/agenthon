"""Provider finto: restituisce risposte registrate. Gratis, veloce e sempre uguale.

Formato degli scenari (file JSON o lista Python):

    [
      {"quando": "id=email-001",        # testo cercato nel PRIMO messaggio dell'utente
       "risposte": [                     # una risposta per ogni chiamata al modello, in ordine
         {"text": "Cerco il cliente.",
          "tool_calls": [{"name": "cerca_cliente", "arguments": {"testo": "Bianchi"}}]},
         {"text": "Fatto: ho registrato la fattura."}
       ]}
    ]

La risposta da dare si ricava dalla conversazione stessa (quanti messaggi "assistant" ci sono già),
quindi il mock non ha stato interno e funziona anche dopo una pausa per l'approvazione.
"""
import json
from pathlib import Path

from core.llm import LLMResponse, Message


class MockProvider:
    name = "mock"

    def __init__(self, scenari: list[dict] | Path | str):
        if isinstance(scenari, (str, Path)):
            scenari = json.loads(Path(scenari).read_text(encoding="utf-8"))
        self.scenari = scenari

    def chat(self, messages: list[Message], tools: list[dict]) -> LLMResponse:
        primo_utente = next((m.content for m in messages if m.role == "user"), "")
        passo = sum(1 for m in messages if m.role == "assistant")
        for scenario in self.scenari:
            if scenario["quando"] in primo_utente:
                risposte = scenario["risposte"]
                if passo < len(risposte):
                    return LLMResponse.model_validate(risposte[passo])
                return LLMResponse(text="[mock] Scenario finito: nessun'altra risposta registrata.")
        return LLMResponse(
            text="[mock] Nessuno scenario registrato per questo input. "
            "Aggiungilo in esempio/dati/mock/scenari.json oppure usa un provider vero."
        )
