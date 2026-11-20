# Architettura

Cosa c'è nello starter kit, come funziona e perché è fatto così.

## L'idea in una frase

Un agente è un modello linguistico che lavora **in un ciclo**: a ogni giro decide se rispondere o
usare uno strumento (un *tool*: cercare un cliente, leggere un PDF, inviare un'email). Il codice
esegue il tool e gli rimanda il risultato. Le azioni che toccano il mondo esterno si fermano e
aspettano che una persona le approvi.

Il kit è diviso in due:

- **`core/`**: la struttura che serve a qualunque brief (ciclo, tool, approvazioni, traccia, provider).
  Non contiene niente di specifico dello studio commercialista.
- **`esempio/`**: un dominio di prova costruito sopra `core/`. Al kick-off si sostituisce con il
  dominio del brief, mentre `core/` resta com'è.

## Il flusso, su un esempio vero (email-001)

```mermaid
sequenceDiagram
    participant UI as UI (Streamlit)
    participant A as Agente (core/agent.py)
    participant M as Modello (provider)
    participant T as Tool (esempio/agente.py)
    participant U as Persona dello studio

    UI->>A: avvia(email-001)
    A->>M: email + elenco dei tool
    M-->>A: usa cerca_cliente("marco.bianchi@example.it")
    A->>T: cerca_cliente → cliente id 1
    A->>M: risultato
    M-->>A: usa estrai_fattura("fattura_rossi_ottobre.pdf")
    A->>T: PDF → testo → modello → JSON validato → controlli
    A->>M: risultato (controlli superati)
    M-->>A: usa registra_fattura(...)  [azione esterna]
    A-->>UI: stato "in_attesa"
    U->>UI: Approva
    UI->>A: approva(email-001)
    A->>T: registra_fattura → riga nel gestionale
    A->>M: risultato
    M-->>A: usa invia_email(...)  [azione esterna]
    A-->>UI: stato "in_attesa"
    U->>UI: Approva
    A->>T: invia_email
    A->>M: risultato
    M-->>A: riepilogo finale (nessun tool)
    A-->>UI: stato "completato"
```

Ogni freccia che parte dall'agente viene registrata nella traccia: è quello che la UI mostra al centro.

## I pezzi, uno per uno

### 1. Provider LLM sostituibile: `core/llm.py`, `core/llm_mock.py`, `core/llm_openai.py`

Tutto il codice parla con il modello solo tramite `provider.chat(messaggi, tools) -> LLMResponse`.
I messaggi sono in un formato neutro (`Message`, `ToolCall`), quindi nessun file dipende da un
fornitore. Il provider si sceglie con `LLM_PROVIDER` nel file `.env`.

| Provider | Quando |
|---|---|
| `mock` (default) | sviluppo, test, demo offline. Risponde con le risposte registrate in `esempio/dati/mock/scenari.json`. Sceglie la risposta contando i messaggi già presenti nella conversazione, quindi non ha stato e funziona anche dopo una pausa. |
| `openai_compat` | modello vero. Un solo file copre Gemini, Mistral, Ollama/vLLM in locale e qualsiasi API compatibile con il formato OpenAI. |

**Perché:** si sviluppa e si testa senza spendere crediti; la UI e i connettori si costruiscono
senza aspettare i prompt; se l'API cade durante la demo si torna al mock; e nel pitch si può
dire "il modello si cambia, anche con uno open-source sul server del cliente".

### 2. Ciclo dell'agente: `core/agent.py`

`Agente.avvia()` crea un `Run` e lo porta avanti finché il modello risponde senza chiedere tool.
A ogni giro:

1. chiama il modello con la conversazione e l'elenco dei tool;
2. se il modello chiede dei tool, li mette in coda (`run.da_eseguire`);
3. esegue la coda: i tool di lettura subito; davanti a un tool **esterno** si ferma;
4. aggiunge i risultati alla conversazione e ricomincia.

Protezioni: massimo 12 chiamate al modello per run (`max_passi`); qualsiasi errore del
provider (rete, chiave, quota) porta il run in stato `errore` senza far cadere la UI.

**Stati di un run:**

```
in_corso ──► in_attesa ──(approva / rifiuta)──► in_corso ──► completato
    │                                                │
    └──────────────────► errore ◄────────────────────┘
```

Il run viene salvato in `runs/<id>.run.json` a ogni pausa e alla fine. Per questo la UI può
ricaricarsi (Streamlit riesegue lo script a ogni clic) senza perdere niente.

### 3. Registro dei tool: `core/tools.py`

Un tool è una normale funzione Python con il decoratore `@registry.tool()`. Dalla firma viene
generato lo schema JSON che vede il modello; la docstring diventa la descrizione.

- Gli argomenti proposti dal modello sono validati con **Pydantic** prima dell'esecuzione: tipi
  sbagliati o argomenti inventati diventano un errore leggibile che torna al modello, che può
  correggersi.
- `esegui()` non solleva mai eccezioni: anche un errore dentro il tool torna al modello come dato.

### 4. Approvazione umana: `external=True`

`@registry.tool(external=True)` segna un'azione verso l'esterno (inviare, registrare, modificare
dati di un cliente). Quando il modello la chiede:

- se gli argomenti non sono validi, l'errore torna subito al modello (inutile disturbare la persona);
- altrimenti il run va `in_attesa`. La persona può **approvare**, **correggere gli argomenti e
  approvare** (il modello viene avvisato della modifica) oppure **rifiutare** con un motivo (il
  modello lo legge e decide come proseguire).

**Perché:** è un principio dichiarato dallo sponsor ("le persone in controllo delle decisioni che
contano"), risponde alla domanda della giuria "e se sbaglia?" e copre GDPR (art. 22) e la
sorveglianza umana richiesta dall'AI Act.

### 5. Traccia dei passi: `core/trace.py`

Ogni evento (`inizio`, `llm`, `tool`, `in_attesa`, `approvato`, `rifiutato`, `modificato`, `fine`,
`errore`) è una riga JSON in `runs/<id>.trace.jsonl`, con ora e durata. Il formato è in
[contratto.md](contratto.md#traccia).

**Perché:** la UI la mostra come timeline (la giuria *vede* l'agente lavorare); è un registro
di audit; serve per il debug; e con le durate si misura il tempo per pratica, un numero da pitch.

### 6. Output strutturato ed estrazione documenti: `core/structured.py`, `esempio/documenti.py`

`chiedi_strutturato(provider, istruzioni, testo, Schema)` chiede al modello un JSON e lo valida
con uno schema Pydantic. Se non è valido (data nel formato sbagliato, campo mancante, JSON rotto)
rimanda l'errore al modello per un secondo tentativo. Usa solo testo, quindi funziona con ogni provider.

L'estrazione delle fatture segue lo schema **regola → modello → regola**:

1. `pdfplumber` estrae il testo dal PDF (deterministico, gratis);
2. il modello capisce quale numero è il totale, quale la data, ecc. e compila lo schema `Fattura`;
3. controlli deterministici: imponibile + IVA = totale, cifra di controllo della partita IVA,
   data non nel futuro. Trovano gli errori del documento (email-004) e quelli del modello.

### 7. Connettori finti: `esempio/connettori.py`

Inbox (`dati/inbox.json`), gestionale (SQLite, ricreato da `dati/gestionale_seed.sql`) e posta in
uscita (scrive su `runs/posta_inviata.jsonl`, non spedisce niente). Hanno la forma che avrebbero
quelli veri: per collegare Gmail si riscrive il corpo di `invia_email`, senza toccare agente e tool.
Tutti i dati sono sintetici (email `@example.it`, partite IVA con codice ufficio `000`, non assegnato).

### 8. UI e verifica end-to-end: `ui/app.py`, `scripts/demo_check.py`

La UI ha tre colonne (richieste, passi, approvazione) e sotto lo stato dei sistemi simulati.
Nella barra laterale ci sono il provider in uso, le metriche e il reset della demo.

`demo_check.py` fa girare le quattro email con risposte registrate, approva tutto e controlla
stato, azioni, righe nel gestionale, email inviate e traccia. Usa una cartella temporanea, quindi
non tocca lo stato della UI.

## Scelte e limiti consapevoli

- **Niente framework per agenti** (LangChain, ADK, ...): il ciclo sta in circa 200 righe leggibili (commenti compresi),
  e lo si modifica in fretta durante l'hackathon. Se il brief richiede un framework, si sostituisce
  solo `core/agent.py`.
- **Niente database per lo stato dei run**: file JSON in `runs/`. Basta per una demo con un utente.
- **Un tool esterno alla volta**: se il modello chiede più azioni insieme, vengono approvate una
  dopo l'altra.
- **Niente API web (FastAPI)**: la UI chiama l'agente direttamente. Si aggiunge solo se il brief
  richiede un webhook o un frontend separato.
- **L'adapter del modello vero non è ancora stato provato con una chiave**: è testato con un
  server HTTP finto. Va provato appena avete una chiave (vedi la guida).
