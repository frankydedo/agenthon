# Guida pratica

Ricette per usare e modificare lo starter kit. Per capire come funziona dentro, vedi
[architettura.md](architettura.md). Tutti i comandi si lanciano dalla cartella del repo, con il
virtualenv attivo (`.venv\Scripts\activate` su Windows, `source .venv/bin/activate` su macOS/Linux).

## 1. Avviare e presentare la demo

```
streamlit run ui/app.py
```

1. Barra laterale → **Reset demo** per partire puliti.
2. Clicca **Elabora** su una email: al centro compaiono i passi dell'agente.
3. A destra c'è l'azione da approvare: puoi correggere gli argomenti (è JSON), poi **Approva** o **Rifiuta**.
4. In basso, nelle schede, vedi le pratiche aperte, le fatture registrate e le email "inviate".

Ordine consigliato per la demo: **email-001** (flusso completo) → **email-004** (il controllo trova
l'errore: è il momento più forte) → **email-003** (l'agente non inventa).

## 2. Usare un modello vero

1. Copia `.env.example` in `.env` (il file `.env` **non si committa mai**).
2. Scegli un blocco (Gemini, Mistral od Ollama), togli i commenti e inserisci chiave e modello.
3. Imposta `LLM_PROVIDER=openai_compat` e riavvia Streamlit.
4. Nella barra laterale deve comparire `Provider LLM: openai_compat`.

Prima prova consigliata: **email-008** (spam: non deve fare niente) e **email-001**.
Se qualcosa va storto, l'errore compare nella colonna di destra e nella traccia.

> Ogni elaborazione con un modello vero costa (poco, ma costa). Sviluppate con il mock e usate il
> modello vero per provare i prompt e per la demo finale.

**Ollama (tutto in locale):** installa Ollama, scarica un modello che supporti i tool
(`ollama pull qwen2.5:7b`) e usa il blocco Ollama del `.env`. È più lento e meno preciso dei
modelli in cloud, ma nel pitch dimostra che i dati possono non uscire dallo studio.

## 3. Aggiungere un tool

In `esempio/agente.py`, dentro `crea_registry`:

```python
@registry.tool()                              # lettura: eseguito subito
def scadenze_cliente(cliente_id: int) -> list[dict]:
    """Elenca le prossime scadenze fiscali del cliente."""   # la legge il modello: siate chiari
    return connettori.scadenze(cliente_id)

@registry.tool(external=True)                 # azione esterna: passa dall'approvazione
def fissa_appuntamento(
    cliente_id: int,
    data_ora: Annotated[str, Field(description="AAAA-MM-GG HH:MM")],
) -> dict:
    """Fissa un appuntamento in agenda con il cliente."""
    return connettori.fissa_appuntamento(cliente_id, data_ora)
```

Regole: tipi semplici, docstring chiara, valore restituito serializzabile in JSON, errori come
eccezioni con un messaggio in italiano. Se il tool cambia qualcosa fuori dal programma, va
`external=True`. Ricordatevi di citarlo nel `SYSTEM_PROMPT`, se serve spiegare quando usarlo.

## 4. Registrare uno scenario per il mock

In `esempio/dati/mock/scenari.json` aggiungi un oggetto:

```json
{
  "quando": "id=email-005",
  "risposte": [
    {"text": "Cerco la cliente.", "tool_calls": [{"name": "cerca_cliente", "arguments": {"testo": "elena.russo@example.it"}}]},
    {"text": "Riepilogo finale."}
  ]
}
```

- `quando` è un testo cercato nel **primo** messaggio dell'utente (per le email: `id=email-XXX`;
  per l'estrazione di un PDF: `DOCUMENTO: nome_file.pdf`).
- C'è una risposta per ogni chiamata al modello, in ordine. Ogni azione approvata o rifiutata
  porta alla risposta successiva.
- L'ultima risposta non ha `tool_calls`: chiude il run.

Il `text` delle risposte intermedie compare nella timeline: scrivetelo come il "ragionamento ad
alta voce" che volete far vedere in demo.

## 5. Aggiungere dati di prova

- **Email:** `esempio/dati/inbox.json`. Gli allegati vanno in `esempio/dati/documenti/`.
- **Clienti, pratiche, fatture iniziali:** `esempio/dati/gestionale_seed.sql`, poi **Reset demo**.
- **PDF:** aggiungete la fattura in `esempio/dati/genera_pdf.py` e lanciate
  `python esempio/dati/genera_pdf.py`, oppure copiate un PDF in `documenti/`.
- Solo dati **sintetici**: email `@example.it`, nessun dato di persone reali.

## 6. Al kick-off: adattare il kit al brief

`core/` non si tocca; si sostituisce il dominio. Circa un'ora di lavoro, divisibile in tre.

1. **Copiate** `esempio/` in una cartella nuova (es. `dominio/`) e lasciate `esempio/` com'è, come riferimento.
2. **Prompt** (`agente.py` → `SYSTEM_PROMPT`): chi è l'agente, per chi lavora, i passi, cosa non deve fare mai.
3. **Tool** (`agente.py` → `crea_registry`): quelli del brief, con `external=True` sulle azioni.
4. **Connettori** (`connettori.py`): finti all'inizio, con la stessa forma di quelli veri.
5. **Dati** (`dati/`): richieste, documenti e database realistici per il caso del brief.
6. **Mock** (`dati/mock/scenari.json`): registrate 2-3 scenari per la demo.
7. **Import**: in `ui/app.py` e `scripts/demo_check.py` sostituite `esempio` con il nuovo
   nome, poi aggiornate `ATTESE` in `demo_check.py`.
8. Aggiornate [contratto.md](contratto.md) e i testi della UI (titolo, etichette).

Prima versione end-to-end con il mock, poi il modello vero, poi la misura della metrica.

## 7. Prima di ogni merge su `main`

```
pytest
python scripts/demo_check.py
```

Entrambi devono passare. `demo_check` stampa `DEMO OK` oppure l'elenco di cosa si è rotto.

## 8. Problemi comuni

| Sintomo | Causa probabile |
|---|---|
| `ModuleNotFoundError: core` | non sei nella cartella del repo, o il virtualenv non è attivo |
| La timeline dice `[mock] Nessuno scenario registrato` | quella email non ha risposte registrate: aggiungile (§4) o usa un modello vero (§2) |
| Run in `errore` con `HTTPStatusError 401` | chiave sbagliata o scaduta nel `.env` |
| Run in `errore` con `404` | `LLM_BASE_URL` o `LLM_MODEL` sbagliati |
| `Raggiunto il limite di 12 passi` | il modello gira in tondo: rendete più chiaro il prompt o la descrizione dei tool |
| Il modello passa argomenti sbagliati | migliorate docstring e `Field(description=...)`: è l'unica cosa che legge |
| Dati della demo "sporchi" | barra laterale → **Reset demo** |
