# Cosa c'è in questo branch

> Branch `mauro's-branch`, creato da `main` (commit `6470fea`) il 20 novembre 2026.
> Questo documento basta da solo per capire cosa contiene il branch e cosa fare dopo.
> I dettagli sono in [architettura.md](architettura.md), [guida.md](guida.md) e [contratto.md](contratto.md).

## In breve

Il branch aggiunge uno **starter kit per l'agente**: lo scheletro che servirà qualunque sia il
brief della track "Agentic AI for business". C'è un agente che riceve una richiesta, usa dei
tool, estrae dati dai PDF, **chiede l'approvazione di una persona prima di ogni azione verso
l'esterno** e registra ogni passo. Una UI mostra tutto questo in demo.

Funziona subito, **senza chiavi API e senza costi**, grazie a un modello finto con risposte
registrate, su uno scenario di prova: uno studio commercialista che riceve email dai clienti.

## Perché

Il tema della track ("smistare le richieste, estrarre informazioni dai documenti, collegare
strumenti") vuol dire che ogni soluzione possibile ha la stessa struttura: cambiano solo prompt,
tool e dati. Costruirla adesso ci risparmia le prime 4-6 ore dell'hackathon. Il kit è
volutamente **generico**: la soluzione vera la scriviamo sul brief, e lo scenario di prova si
butta via.

## Provarlo in 5 minuti

```powershell
python -m venv .venv
.venv\Scripts\activate              # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run ui/app.py             # si apre http://localhost:8501
```

Nella UI clicca **Elabora** su una email, guarda i passi al centro, approva o rifiuta a destra e
controlla in basso cosa è cambiato. Le quattro email da provare:

| Email | Cosa mostra |
|---|---|
| email-001 · fattura Rossi | flusso completo: cliente → dati dal PDF → fattura registrata → email di conferma |
| email-002 · 730 | apre una pratica e risponde con l'elenco dei documenti |
| email-003 · mittente sconosciuto | non inventa: non manda documenti e chiede chiarimenti |
| email-004 · fattura Verdi | il controllo automatico trova 36 € di errore nel totale e blocca la registrazione |

## Cosa contiene

**Nucleo riusabile (`core/`), da non modificare per il brief**

| File | Cosa fa |
|---|---|
| `llm.py` | tipi neutri (`Message`, `ToolCall`, `LLMResponse`) e scelta del provider dal `.env` |
| `llm_mock.py` | modello finto: risposte registrate, gratis e sempre uguali |
| `llm_openai.py` | modello vero via API compatibile con il formato OpenAI (Gemini, Mistral, Ollama, ...) |
| `tools.py` | registro dei tool: schema generato dalla firma, argomenti validati con Pydantic |
| `agent.py` | ciclo dell'agente con pausa per l'approvazione, limite di passi, stato salvato su file |
| `structured.py` | JSON validato con uno schema Pydantic; se è sbagliato il modello riceve l'errore e riprova |
| `trace.py` | traccia di ogni passo in `runs/<id>.trace.jsonl` |
| `config.py` | impostazioni dal file `.env` |

**Scenario di prova (`esempio/`), da sostituire al kick-off**

| File | Cosa fa |
|---|---|
| `agente.py` | prompt di sistema e 5 tool: `cerca_cliente`, `estrai_fattura` (lettura); `registra_fattura`, `crea_pratica`, `invia_email` (da approvare) |
| `connettori.py` | inbox, gestionale SQLite e posta in uscita, tutti finti, con la stessa forma di quelli veri |
| `documenti.py` | estrazione dalle fatture PDF: testo → modello → controlli su somme, partita IVA e data |
| `dati/` | 8 email, 2 fatture PDF (con il generatore), database iniziale, risposte registrate del mock |

**Demo, verifica, test**

| File | Cosa fa |
|---|---|
| `ui/app.py` | UI Streamlit: richieste, passi dell'agente, approvazione con argomenti modificabili, sistemi simulati, metriche |
| `scripts/demo_check.py` | verifica end-to-end con il mock: **da lanciare prima di ogni merge** |
| `tests/` | 30 test: provider, tool, ciclo e approvazioni, estrazione, connettori, demo, UI |

**Configurazione e documentazione**

- `requirements.txt`, `pytest.ini`, `.env.example` (modello del file `.env`, con esempi per Gemini, Mistral e Ollama).
- `README.md` e `docs/`: architettura, guida pratica, contratto delle interfacce, questa panoramica.
- File esistenti modificati: `.gitignore` (esclude `.venv/` e `runs/`, include `.env.example`) e
  `CLAUDE.md` §6 (stack e comandi).

## Come funziona, in breve

1. La UI passa l'email all'agente (`Agente.avvia`).
2. L'agente manda al modello la conversazione e l'elenco dei tool.
3. Se il modello chiede un tool di lettura, il tool viene eseguito e il risultato torna al modello.
4. Se chiede un'azione esterna, il run si ferma (`in_attesa`) finché una persona approva,
   corregge o rifiuta. Il modello viene informato della decisione.
5. Quando il modello risponde senza tool, il run è `completato`.
6. Ogni passo finisce nella traccia, che la UI mostra come timeline.

## Decisioni prese

| Decisione | Perché |
|---|---|
| Python + Streamlit, senza FastAPI | è il modo più veloce di avere UI e traccia visibile; FastAPI si aggiunge solo se il brief chiede un'API |
| Nessun framework per agenti | il ciclo è di circa 200 righe e lo capiamo tutti; si modifica in fretta sotto pressione |
| Provider neutro (mock + adapter compatibile OpenAI) | il CLAUDE.md chiede un modello sostituibile; lo sponsor vuole evitare il lock-in; si sviluppa senza costi |
| Approvazione su ogni azione esterna | è un principio dello sponsor, risponde a "e se sbaglia?" e copre GDPR e AI Act |
| Stato su file (`runs/`), non su database | basta per una demo con un utente; si azzera con "Reset demo" |
| Solo dati sintetici | email `@example.it`, partite IVA con codice ufficio `000` (non assegnato, quindi non reali) |

## Verifiche fatte

- `pytest`: **30 test passati** (circa 6 secondi).
- `python scripts/demo_check.py`: **DEMO OK** sulle 4 email con risposte registrate.
- Il server Streamlit si avvia e risponde.
- Tutto provato su Windows 11 con Python 3.12.

**Non ancora verificato:** l'adapter per il modello vero (`llm_openai.py`) è testato solo
con un server HTTP finto, **mai con una chiave vera**. Non è provato nemmeno su macOS/Linux.

## Cosa resta da fare

**Prima dell'hackathon**

- [ ] Ognuno: clonare il branch, creare il virtualenv, avviare la demo, leggere la propria parte ([contratto.md](contratto.md)).
- [ ] Scegliere il provider e provare l'adapter con una chiave vera (guida §2): prima email-008, poi email-001.
- [ ] Confermare la divisione dei ruoli proposta in [contratto.md](contratto.md).
- [ ] Chiedere agli organizzatori se il codice preparato prima è ammesso; in ogni caso dichiararlo nel pitch.
- [ ] Fare una prova generale di 2-3 ore con un brief inventato, usando la checklist della guida §6.
- [ ] Rivedere il branch e farne il merge su `main`.

**Al kick-off** (dettagli nella guida §6)

- [ ] Copiare `esempio/` in una nuova cartella del dominio e riscrivere prompt, tool, connettori, dati e scenari del mock.
- [ ] Aggiornare gli import in `ui/app.py` e `scripts/demo_check.py`.
- [ ] Prima versione end-to-end con il mock → modello vero → misura della metrica per il pitch.

**Aggiunte possibili, solo se servono**

- Adapter con l'SDK ufficiale di Anthropic, se scegliamo Claude.
- Un provider che registra le risposte del modello vero per rigiocarle offline: è il video di riserva "vivo".
- Connettori veri (Gmail, Google Sheets) al posto di quelli finti.
- Deploy della demo (Cloud Run nella regione di Milano o Render) e URL in `CLAUDE.md` §6.

## Regole per lavorarci

- Il file `.env` (con le chiavi) non si committa mai.
- Prima di ogni merge su `main`: `pytest` e `python scripts/demo_check.py` devono passare.
- Le interfacce in [contratto.md](contratto.md) si cambiano solo dopo averne parlato, e chi le
  cambia aggiorna il file nello stesso commit.
