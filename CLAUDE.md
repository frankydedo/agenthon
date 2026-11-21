# CLAUDE.md - AGENTHON (GDG Torino) · track "Agentic AI for business"

> File condiviso dal team. Le sezioni marcate **[DA COMPILARE]** vanno aggiornate al kick-off,
> quando esce il brief. Finché non sono compilate, chiedi invece di assumere.

## 1. Contesto

- Hackathon AGENTHON del GDG Torino (Feat. House, Torino), il weekend prima di DevFest Alps.
- Team di 3: un AI engineer junior e due software engineer junior. Tempo molto limitato.
- Track: **Agentic AI for business**, sponsor **Ariete Tech Solutions**. Il tema dichiarato:
  agenti autonomi che smistano le richieste in arrivo, estraggono informazioni dai documenti e
  collegano più strumenti, così che il lavoro vada dall'inizio alla fine senza passaggi manuali.
- Giudizio (regolamento art. 9, 100 punti): innovatività 25, **esecuzione 25**, fattibilità 20,
  aderenza al tema 15, presentazione 15. Spareggio: esecuzione, poi innovatività.
- Prima selezione sul repo **senza** il voto di presentazione; finale: pitch di circa 3 minuti
  con demo dal vivo. Dettagli in `Vault/wiki/analyses/criteri-e-consegna.md`.

### Chi è lo sponsor (da arietetech.com)
- Braccio tecnologico di Ariete Capital Group (Torino): consulenza sugli investimenti,
  real estate, venture capital. Startup innovativa.
- Costruisce automazioni e strumenti AI su misura per **studi professionali** (legali,
  commercialisti), **advisor e wealth manager**, e **PMI**.
- Principi che dichiarano:
  - eliminare la ripetizione manuale, tenendo **le persone in controllo delle decisioni che contano**;
  - usare l'AI solo dove risolve un problema reale, non per moda;
  - soluzioni su **infrastruttura del cliente, ospitata in UE**, senza dipendere da SaaS di terzi.
- Processi interni che hanno già automatizzato: acquisizione dei lead, firma dei documenti,
  monitoraggio dei portafogli clienti, reportistica di compliance, comunicazione interna.
- Prodotti annunciati: AI Advisory (assistente conversazionale per advisor), Stock Selector,
  Alt-Asset Pricer, Real Estate AI, Company Brain (base di conoscenza unica dell'azienda).

> **Decisioni di prodotto e piano di lavoro: leggi `endof.md` nella root prima di scrivere codice.**

## 2. Il brief (uscito alle 10:28 del 21/11; testo in `Vault/raw/2026-11-21-brief-track1.md`)

Tema: *"Build an AI your team would trust"*: un'AI che lavora in background, **chiede prima di agire**
e viene difesa dal vivo davanti alla giuria. Vince la soluzione **corretta, che ammette ciò che non
sa e non agisce mai senza l'approvazione di una persona**, non quella più appariscente.

- **Caso d'uso scelto dal team: Challenge A · Company Brain** ("il collega che sa e parla per primo").
  Uno strumento che osserva il lavoro di un team (email, chat, task, documenti), tiene una **memoria
  condivisa curata dalle persone** e dice a ciascuno cosa richiede la sua attenzione prima che lo chieda.
  *Un chatbot sui documenti non vale.* (L'alternativa scartata era B · Back Office Autopilot.)
- **Sette controlli della demo**, che la giuria segna sì/no:
  1. **Parla per primo**: un brief o un alert generato da solo, senza che nessuno chieda.
  2. **Le persone curano la memoria**: approvare una voce e rifiutarne una, dal vivo; poi una domanda a cui risponde solo la voce approvata.
  3. **Sa chi chiede**: stessa domanda da una persona della finanza e da una tecnica: a una risponde, all'altra no.
  4. **Cita**: ogni risposta mostra da dove viene.
  5. **Ammette le lacune**: su ciò che non è nei dati dice "non lo so".
  6. **Propone soltanto**: un'azione in attesa di approvazione; nulla accade finché una persona non approva.
  7. **Si inserisce nella giornata del team**: dove lo incontrerebbe (chat, email del mattino, mock-up stile Slack). Nessuna connessione reale richiesta.
- **Dati**: li creiamo noi, **sintetici** (nessun dato reale di clienti o persone), oppure partiamo da un dataset open source.
- **Utenti**: le persone di un team aziendale, con ruoli diversi (almeno finanza e tecnica).
- **Giudizio**: innovatività, aderenza, **fattibilità oltre il prototipo**, esecuzione tecnica, pitch (pesi in §1).
- **Pitch**: circa 3 minuti con demo dal vivo, davanti alla giuria, che può fare domande. Il team
  può essere "attaccato" da giuria e squadre rivali: **la demo deve reggere a domande fuori copione**.
- **Premio extra**: "Best use of ElevenLabs" (facoltativo, solo se ha senso nel prodotto).
- **Ancora da chiarire**: orario di consegna; strumenti e crediti dei partner; metrica per il pitch
  (proposta: i 7 controlli superati, più numeri su pertinenza e "non lo so" corretti).

## 3. Team e responsabilità **[ruoli decisi; cartelle da confermare dopo il brief]**

- **Mauro** e **Pietro**: software (integrazioni, backend, interfaccia). **Franky**: studia l'AI
  (agente, prompt, valutazione). Nella pratica tutti fanno un po' di tutto: i ruoli sotto
  indicano chi decide, non chi è l'unico a toccare quei file.

| Ruolo | Cosa possiede |
|---|---|
| AI engineer | logica dell'agente: prompt, tool, orchestrazione, output strutturati, valutazione |
| SWE 1 - integrazioni | connettori verso i sistemi (email, documenti, CRM, fogli), dati di prova, API backend |
| SWE 2 - prodotto e demo | interfaccia, traccia visibile dei passi dell'agente, deploy, video di riserva, pitch |

Regole:
- Modifica solo la parte che appartiene a chi ti sta usando. Se serve cambiare un'interfaccia
  condivisa (formato dei dati, endpoint, schema di un tool), fermati e dillo: va concordata.
- Le interfacce condivise si scrivono in un file di contratto del repo, da creare dopo il brief.

## 4. Principi di prodotto (vengono dal brief e dallo sponsor)

1. **Una demo end-to-end che funziona** batte dieci funzioni a metà.
2. **Human-in-the-loop**: ogni azione verso l'esterno (inviare, firmare, pagare, modificare
   dati di un cliente) passa da un'approvazione esplicita.
3. **Trasparenza**: ogni passo dell'agente (cosa ha letto, quale tool, con che input, quale
   risultato) deve essere visibile e registrato. Serve alla demo e alla fiducia.
4. **Privacy e sovranità dei dati**: dati personali minimi e sintetici; il modello deve essere
   sostituibile (nessun lock-in su un fornitore); pensare a GDPR e hosting UE.
5. **AI dove serve**: se una regola deterministica basta, usa la regola. Il modello serve per
   capire testo libero, estrarre dati da documenti, decidere il prossimo passo.
6. **Testi per l'utente in italiano**, dati di prova realistici per uno studio o una PMI italiana.

## 5. Come lavorare (per l'agente di coding)

- Task piccoli e verificabili. Dopo ogni modifica, esegui il test o lo script che la dimostra.
- Codice semplice e leggibile; niente astrazioni per esigenze future.
- Se il brief, un contratto o un requisito è ambiguo, chiedi invece di inventare.
- Non chiamare API a pagamento (LLM o altro) senza che l'umano lo chieda. Preferisci un
  provider finto o dati registrati per sviluppo e test.
- Mai leggere, stampare o committare segreti (`.env`, chiavi, token).
- Risparmia contesto: leggi solo i file necessari, non lanciare subagent se non richiesto,
  risposte brevi.
- Alla fine di ogni task scrivi in 3 righe: cosa è cambiato, come si prova, cosa resta aperto.

## 6. Stack e comandi

Starter kit già pronto: vedi `README.md` e `docs/` (architettura, guida, contratto).

- Linguaggi e framework: Python 3.11+, Pydantic, Streamlit (UI), pdfplumber (PDF), SQLite (gestionale finto).
  Nessun framework per agenti: il ciclo è in `core/agent.py`.
- Provider LLM: `mock` di default; `openai_compat` per Gemini / Mistral / Ollama (config in `.env`).
  **[DA DECIDERE al kick-off: provider e modello vero, e alternativa di riserva]**
- Avvio in locale: backend `uvicorn api.main:app --port 8000` + frontend `cd web && npm run dev`
  (http://localhost:5173); ripiego: `streamlit run ui/app.py`. Architettura: `docs/architettura.md`.
- Test: `pytest` e, prima di ogni merge, `python scripts/demo_check.py`
- Struttura: `core/` è riusabile e non si tocca per il brief; il dominio sta in `esempio/` (da sostituire).
- Interfacce condivise: `docs/contratto.md`.
- Deploy / URL della demo: **[DA COMPILARE]**

## 7. Git

- Un solo repo condiviso. **Si lavora tutti su `develop`** (`git pull` prima, commit piccoli).
- Su `main` si porta **solo ciò che è testato e funziona**: `pytest` e `python scripts/demo_check.py`
  passano e la demo parte.
- Mai push forzati né riscrittura della history di `main`.

## 8. Fasi della giornata

1. Kick-off: compilare §2 e §3, scegliere **un** caso d'uso, scrivere i contratti.
2. Prima versione end-to-end, anche grezza.
3. Rendere tutto reale: modello vero, dati realistici, misura della metrica.
4. Blocco delle funzionalità: solo bug, stabilità, video di riserva.
5. **Consegna** (orario comunicato all'apertura): repo accessibile alla giuria, README con
   descrizione, tecnologie e avvio, descrizione ≤ 1.000 caratteri con lo starter kit dichiarato
   come preesistente, versione finale su `main`. Dopo l'orario non si committa più.
6. Pitch: problema in € o in ore → demo → come funziona → risultati → impatto per i clienti
   dello sponsor.

## 9. Base di conoscenza (`Vault/`)

- È una LLM Wiki: le fonti originali stanno in `Vault/raw/` (immutabili), la sintesi
  scritta dall'agente in `Vault/wiki/`. Le regole sono in `Vault/CLAUDE.md`.
- Al kick-off si mettono in `raw/` brief, regolamento, slide e dati, e si fa l'ingest.
- Prima di decisioni di prodotto o tecniche, leggi `Vault/wiki/index.md` e le pagine
  rilevanti. Le decisioni del team sono registrate in `Vault/wiki/log.md`.
