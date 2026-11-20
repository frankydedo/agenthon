# Contratto delle interfacce condivise

> **Stato: proposta.** Queste sono le interfacce tra le parti del team (agente, integrazioni, UI).
> Si possono cambiare, ma **solo dopo averlo concordato**, perché ogni modifica rompe il lavoro
> degli altri (CLAUDE.md §3). Chi cambia un'interfaccia aggiorna questo file nello stesso commit.

## Chi possiede cosa (proposta, da confermare al kick-off)

| Parte | File | Ruolo |
|---|---|---|
| Ciclo, provider, tool, output strutturato | `core/agent.py`, `core/llm*.py`, `core/tools.py`, `core/structured.py`, prompt e tool in `esempio/agente.py` | AI engineer |
| Connettori, dati di prova, estrazione documenti | `esempio/connettori.py`, `esempio/documenti.py`, `esempio/dati/` | SWE integrazioni |
| UI, traccia visibile, verifica della demo | `ui/app.py`, `core/trace.py`, `scripts/demo_check.py` | SWE prodotto e demo |

## Messaggi e provider (`core/llm.py`)

```python
class ToolCall:     id: str; name: str; arguments: dict
class Message:      role: "system" | "user" | "assistant" | "tool"
                    content: str
                    tool_calls: list[ToolCall]   # solo assistant
                    tool_call_id: str | None     # solo tool
class LLMResponse:  text: str; tool_calls: list[ToolCall]

class LLMProvider(Protocol):
    name: str
    def chat(self, messages: list[Message], tools: list[dict]) -> LLMResponse: ...
```

`tools` è una lista di `{"name": str, "description": str, "parameters": <JSON Schema>}`.
Un nuovo provider implementa solo `chat` e si aggiunge in `get_provider()`.

## Tool (`core/tools.py`)

- Un tool è una funzione Python registrata con `@registry.tool()` (lettura) o
  `@registry.tool(external=True)` (azione verso l'esterno, da approvare).
- Nome del tool = nome della funzione, in `snake_case` italiano. Descrizione = docstring.
- Parametri con **tipi semplici** (`str`, `int`, `float`, `bool`, `list[str]`): alcuni provider
  gestiscono male gli schemi complessi. Le descrizioni si mettono con `Annotated[str, Field(description=...)]`.
- Il valore restituito deve essere serializzabile in JSON (dict, list, str, numeri).
- Il risultato che arriva al modello ha sempre una di queste forme:

```json
{"risultato": <valore restituito dalla funzione>}
{"errore": "Argomenti non validi", "dettagli": [{"campo": "data", "problema": "..."}]}
{"errore": "ValueError: Cliente 999 inesistente"}
{"esito": "rifiutato dall'utente", "motivo": "..."}
```

Se una persona ha corretto gli argomenti prima di approvare, al risultato si aggiunge `"nota"`.

## Run (`core/agent.py`)

```python
agente.avvia(input_utente: str, run_id: str | None = None) -> Run
agente.approva(run_id: str, argomenti: dict | None = None) -> Run
agente.rifiuta(run_id: str, motivo: str = "") -> Run
carica_run(run_id) -> Run | None
```

| Campo di `Run` | Significato |
|---|---|
| `id` | identificativo (nella demo coincide con l'id dell'email) |
| `stato` | `in_corso`, `in_attesa`, `completato`, `errore` |
| `in_attesa_di` | la `ToolCall` da approvare (solo se `stato == "in_attesa"`) |
| `risposta_finale` | riepilogo del modello (solo se `completato`) |
| `errore` | messaggio (solo se `errore`) |
| `messaggi`, `da_eseguire`, `passi` | stato interno del ciclo |

File: `runs/<id>.run.json`.

## Traccia

File: `runs/<id>.trace.jsonl`, un evento JSON per riga. Campi comuni: `ts` (ISO, ms), `run_id`, `tipo`.

| `tipo` | Campi specifici |
|---|---|
| `inizio` | `input`, `provider` |
| `llm` | `testo`, `tool_calls` (lista di `{id, name, arguments}`), `durata_ms` |
| `tool` | `tool`, `argomenti`, `risultato`, `durata_ms` (assente se gli argomenti erano già non validi) |
| `in_attesa` | `tool`, `argomenti` |
| `modificato` | `tool`, `prima`, `dopo` |
| `approvato` | `tool`, `argomenti` |
| `rifiutato` | `tool`, `argomenti`, `motivo` |
| `fine` | `testo` |
| `errore` | `messaggio` |

## Connettori dell'esempio (`esempio/connettori.py`)

```python
elenca_email() -> list[dict]          # {id, da, data, oggetto, testo, allegati: [nome_file]}
leggi_email(email_id) -> dict
formatta_email(email) -> str          # il testo che riceve l'agente; inizia con "EMAIL id=<id>"
cerca_clienti(testo) -> list[dict]
crea_pratica(cliente_id, tipo, descrizione) -> dict
registra_fattura(cliente_id, numero, data, fornitore, partita_iva_fornitore, imponibile, iva, totale) -> dict
invia_email(destinatario, oggetto, testo) -> dict
tabella(nome) -> list[dict]           # per la UI: clienti, pratiche, fatture
email_inviate() -> list[dict]
reset_gestionale(); reset_posta()
```

Gli errori si segnalano **sollevando un'eccezione** con un messaggio chiaro in italiano
(`ValueError("Cliente 999 inesistente")`): il registro dei tool la trasforma in un risultato
`{"errore": ...}` che il modello legge.
