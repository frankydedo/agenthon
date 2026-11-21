# Log

## [2026-11-20 12:47] ingest | Pagina Luma dell'evento e note sullo sponsor
- Fonti: `raw/2026-11-20-luma-evento.md`, `raw/2026-11-20-arietetech.md`.
- Create: `overview.md`, `index.md`, `entities/agenthon.md`, `entities/ariete-tech-solutions.md`.
- Ingest volutamente minimo prima del kick-off: niente analisi su possibili casi d'uso.

## [2026-11-20 12:47] decisione | Starter kit su `develop`
- Il lavoro di Mauro (`mauro's-branch`) è stato portato sul nuovo branch `develop`, creato da
  `main`; il vecchio branch è stato cancellato.
- `core/` è considerato riusabile; `esempio/` è solo uno scenario di prova da sostituire dopo il brief.
- Divisione dei file in `docs/contratto.md`: è una proposta, da confermare al kick-off.
- Aperto: provider e modello veri, alternativa di riserva, prova con un modello vero.

## [2026-11-20 12:52] decisione | LLM locale per lo sviluppo
- Modello `qwen/qwen3-30b-a3b-2507` su LM Studio nel MacBook Air (24 GB), usato come server;
  si lavora dal MacBook Pro (16 GB) via Wi-Fi con `LLM_PROVIDER=openai_compat`.
- Verificati: `/v1/models`, tool calling tramite `core/llm_openai.py`, streaming SSE con curl.
- Cavo Thunderbolt Bridge scartato (cavo non adatto); riserva: hotspot del telefono, poi `mock`.
- Creata `analyses/llm-locale.md`; aggiornati `index.md` e `overview.md`.
- Aperto: provider cloud di riserva, prova del flusso completo nella UI.

## [2026-11-20 13:00] decisione | Impostazioni di LM Studio per Qwen3-30B-A3B
- Context 16k (non 262k: limite di memoria dell'Air), GPU offload massimo, flash attention,
  auto-unload disattivato, nessun system prompt nel preset, temperature 0.3.
- Il token di LM Studio resta fuori dalla wiki (regola di `CLAUDE.md` §5 sui segreti).
- Aggiornata `analyses/llm-locale.md`.

## [2026-11-21 10:30] ingest | Regolamento dell'hackathon
- Fonte: `raw/regulation.pdf` (+ trascrizione `.md`), versione del 20 novembre.
- Creata `analyses/criteri-e-consegna.md`; aggiornati `entities/agenthon.md`, `overview.md`, `index.md`.
- Novità rispetto alla pagina Luma: pesi dei criteri, selezione senza voto di presentazione,
  pitch di 3 minuti con demo, ultimo commit registrato dal portale, descrizione ≤ 1.000 caratteri.
- Contraddizioni: nessuna. Resta da verificare orario di consegna e branch registrato.

## [2026-11-21 10:30] decisione | Repo ricreata allo start
- Si crea una repo nuova all'inizio della gara, così storia e orari dei commit combaciano con
  l'evento. Lo starter kit va dichiarato come componente preesistente.
- Flusso git: tutti su `develop`; su `main` solo roba testata (CLAUDE.md §7).

## [2026-11-21 11:30] decisione | Interfaccia: simulatore, flusso e approvazione leggibili
- Le richieste arrivano solo con «Genera richiesta» (simulatore della casella); la casella parte vuota.
- Flusso delle operazioni con l'ultimo passo in alto; approvazione descritta in italiano, con il
  JSON dietro un pulsante. Documentazione: `docs/architettura.md`, `docs/frontend.md`, `docs/consegna.md`.
- Test: `conftest.py` forza il provider `mock` (i test non chiamano mai il modello vero).

## [2026-11-21 12:20] decisione | Seconda schermata «Come ragiona l'agente»
- La schermata operativa resta com'è; si aggiunge una vista che racconta la richiesta in 5 capitoli
  (arrivo, agente e strumenti, ragionamento passo-passo, approvazione, esito).
- Il «perché» viene dal testo del modello: `SYSTEM_PROMPT` ora chiede una frase prima di ogni
  strumento. Nuove rotte: `GET /api/agente`, `GET /api/richieste/{id}/allegati`.

## [2026-11-21 12:10] ingest | Brief ufficiale della Track 1
- Fonte: `raw/2026-11-21-brief-track1.md` (rivelato alle 10:28). Due sfide: A Company Brain, B Back Office Autopilot.
- Sette controlli sì/no per la sfida A, difesa dal vivo contro giuria e squadre rivali.

## [2026-11-21 12:10] decisione | Sviluppiamo la Challenge A · Company Brain
- Scelta del team: **A**. Aggiornato CLAUDE.md §2.
- Conseguenza: lo starter kit (`core/`, `api/`, `web/`) resta valido per ciclo agente, approvazioni, traccia
  e provider; `esempio/` (studio commercialista, fatture) **non** è il dominio giusto e va sostituito.
  Mancano da costruire: memoria condivisa curata, permessi per ruolo, citazioni, "non lo so", brief proattivi.
- Aperto: dati sintetici (che azienda, che fonti), dove incontra il team (chat / email del mattino), ruolo di ElevenLabs.

## [2026-11-21 12:20] decisione | Prodotto: Company Brain sulle riunioni di progetto
- Il Brain legge riunioni (minute, trascrizioni, audio), estrae task e assegnatari, segnala punti
  oscuri, persone/contesti sconosciuti e incongruenze tra riunioni; aggiorna la to-do di progetto
  come proposta; il manager approva e solo dopo si smista; to-do giornaliere personali.
- Voce con ElevenLabs come bonus; interfaccia a widget come app unica (non microfrontend veri).
- Riepilogo completo per gli agenti del team in `endof.md` (root, poi rinominato `solution.md`). Piano e contratti: proposti.

## [2026-11-21 12:25] decisione | Decisioni comuni dopo il brief
- Si continua su questa repo (`develop`), non se ne crea una nuova.
- PMI di automazione industriale (~8 persone); voce ElevenLabs in P1; demo con modello locale e cloud di riserva.
- Divisione: Franky AI, Pietro backend/dati/to-do/voce, Mauro interfaccia/docs/pitch.
- Permessi **per competenza** (aree; competenze per persona, es. senior dev anche `budget`); il modello
  propone l'area, il manager la conferma, il codice filtra.
- To-do del giorno: decide la persona; modifiche alla lista di progetto: proposta al manager.
- Widget: layout fisso, componibile in P2. Dettagli in `solution.md` §0.
- Aggiunto: aree `sviluppo, budget, commerciale, fornitori, personale, generale`; per vedere un'informazione
  basta **una** delle sue aree (corretto alle 12:30); **5 riunioni** sintetiche.

## [2026-11-21 12:30] decisione | Consegna alle 17:00, permessi in OR
- Orario di consegna: **17:00** (ultimo commit entro le 16:50). Tappe ricalcolate in `solution.md` §8.
- Permessi: basta **una** delle aree dell'informazione per vederla.
- `endof.md` rinominato in `solution.md` dal team.

