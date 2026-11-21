# Starter kit agente - AGENTHON

Scheletro riusabile per un **agente AI che porta a termine un lavoro**: riceve una richiesta,
legge i documenti, agisce sui sistemi del cliente **solo dopo l'approvazione di una persona** e
mostra ogni passo che fa.

Dentro c'è uno scenario di prova (uno studio commercialista che riceve email dai clienti) che
gira **senza chiavi API e senza costi**, grazie a un modello finto con risposte registrate.

## Avvio rapido

Serve Python 3.11 o più recente.

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Poi, dalla cartella del repo:

| Comando | A cosa serve |
|---|---|
| `uvicorn api.main:app --port 8000` | avvia il backend (con `LLM_PROVIDER=mock` davanti per non usare il modello vero) |
| `cd web && npm install && npm run dev` | avvia l'interfaccia web: http://localhost:5173 (serve Node 20+) |
| `streamlit run ui/app.py` | interfaccia di ripiego (http://localhost:8501), non richiede il backend |
| `python scripts/demo_check.py` | verifica che il flusso completo funzioni: **da lanciare prima di ogni merge** |
| `pytest` | tutti i test (pochi secondi) |

## Cosa provare nella demo

Nell'interfaccia web la casella parte vuota: premi **Genera richiesta** (a sinistra) per simulare
l'arrivo di una email di un cliente, poi **Avvia l'agente**, guarda i passi al centro (il più
recente in alto) e approva o rifiuta le azioni a destra. In basso vedi cosa è cambiato nei
sistemi dello studio. Dettagli in [docs/frontend.md](docs/frontend.md).

| Email | Cosa mostra |
|---|---|
| email-001 · fattura Rossi | flusso completo: cliente trovato → dati estratti dal PDF → fattura registrata → conferma via email |
| email-002 · 730 | apertura di una pratica e risposta con l'elenco dei documenti |
| email-003 · mittente sconosciuto | l'agente **non inventa**: non manda documenti e chiede chiarimenti |
| email-004 · fattura Verdi | il **controllo automatico** trova un errore di 36 € nel totale: la fattura non viene registrata |

Le email 005-008 non hanno risposte registrate: servono per provare un modello vero
(vedi [docs/guida.md](docs/guida.md#2-usare-un-modello-vero)).

## Mappa del repo

```
core/                 nucleo riusabile, non dipende dal brief
  llm.py              tipi comuni (Message, ToolCall, LLMResponse) e scelta del provider
  llm_mock.py         provider finto con risposte registrate
  llm_openai.py       provider vero (Gemini, Mistral, Ollama, ... con lo stesso codice)
  tools.py            registro dei tool e validazione degli argomenti
  agent.py            ciclo dell'agente con pausa per l'approvazione
  structured.py       output JSON validato con Pydantic, con autocorrezione
  trace.py            traccia dei passi (un file JSONL per run)
  config.py           impostazioni dal file .env
esempio/              scenario di prova: da sostituire con il dominio del brief
  agente.py           prompt di sistema e tool dello studio
  connettori.py       inbox, gestionale (SQLite) e posta in uscita, tutti finti
  documenti.py        estrazione dati dalle fatture PDF + controlli deterministici
  dati/               email, PDF, database iniziale, risposte registrate del mock
api/main.py           backend HTTP (FastAPI): solo traduzione tra web e core, più il simulatore della casella
web/                  interfaccia web React (vedi docs/frontend.md)
ui/app.py             interfaccia Streamlit di ripiego
scripts/demo_check.py verifica end-to-end con il mock
tests/                test automatici
docs/                 documentazione
runs/                 stato generato a runtime (ignorato da git)
```

## Documentazione

- [docs/architettura.md](docs/architettura.md): **inizia da qui**: livelli, flusso, dove sta lo stato, perché è fatto così.
- [docs/frontend.md](docs/frontend.md): l'interfaccia web, tutti i casi d'uso, come adattarla.
- [docs/consegna.md](docs/consegna.md): descrizione per la giuria e checklist di consegna.
- [docs/panoramica.md](docs/panoramica.md):  Cosa c'è, cosa è stato verificato, cosa resta da fare.
- [docs/guida.md](docs/guida.md): come si usa, come si aggiunge un tool, come si adatta al brief.
- [docs/contratto.md](docs/contratto.md): le interfacce condivise tra le parti del team.

## Regole

- Il file `.env` contiene le chiavi: **non si committa mai** (è già in `.gitignore`).
- Prima di ogni merge su `main`: `pytest` e `python scripts/demo_check.py` devono passare.
- Si sviluppa con il mock; il modello vero si usa quando serve davvero (costa).
