# CLAUDE.md - AGENTHON (GDG Torino) · track "Agentic AI for business"

> File condiviso dal team. Le sezioni marcate **[DA COMPILARE]** vanno aggiornate al kick-off,
> quando esce il brief. Finché non sono compilate, chiedi invece di assumere.

## 1. Contesto

- Hackathon AGENTHON del GDG Torino (Feat. House, Torino), il weekend prima di DevFest Alps.
- Team di 3: un AI engineer junior e due software engineer junior. Tempo molto limitato.
- Track: **Agentic AI for business**, sponsor **Ariete Tech Solutions**. Il tema dichiarato:
  agenti autonomi che smistano le richieste in arrivo, estraggono informazioni dai documenti e
  collegano più strumenti, così che il lavoro vada dall'inizio alla fine senza passaggi manuali.
- Giudizio su: **innovazione, aderenza al brief, fattibilità, esecuzione, pitch finale**.

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

## 2. Il brief **[in parte compilato dal regolamento; il resto al kick-off]**

Fonte: regolamento ufficiale del 20/11/2026 (`Vault/raw/regulation.md`, sintesi in
`Vault/wiki/concepts/consegna-e-valutazione.md`).

- Problema esatto e utente (chi lo usa, in che ruolo): **[DA COMPILARE]** (il brief si comunica
  all'apertura dell'Evento, art. 7.2). Il tema del track è un prototipo AI che svolge in autonomia
  processi aziendali: gestione di richieste, elaborazione di documenti, coordinamento di più
  applicativi (art. 5.1).
- Dati e documenti forniti (formati, lingua, volume): **[DA COMPILARE]**
- Strumenti o API da integrare, vincoli tecnici e crediti disponibili: **[DA COMPILARE]**. Il
  regolamento ammette librerie, framework, API e servizi AI di terzi, nel rispetto delle licenze
  (art. 7.1). I partner possono fornire crediti gratuiti (art. 7.7), e ElevenLabs ha un premio
  speciale per il miglior uso dei suoi strumenti (art. 10.7).
- Cosa si consegna e quando (art. 7.3-7.5), tramite `agenthon-portal.gdgtorino.it`:
  - link al **repo**, accessibile alla giuria, con un file su progetto, tecnologie e istruzioni di avvio;
  - **descrizione di massimo 1.000 caratteri**, con i componenti preesistenti usati (lo starter kit
    va dichiarato);
  - facoltativo: link a una cartella Google Drive con le slide;
  - i link devono aprirsi anche da un account esterno al team;
  - entro l'orario comunicato durante l'Evento (**[DA COMPILARE]**). Conta l'**ultimo commit** a
    quell'ora, e la demo deve girare su quella versione;
  - finalisti (8-12) scelti senza pitch; in finale **pitch di ~3 minuti con demo dal vivo**.
- Punteggio (art. 9.1, su 100): innovatività 25, esecuzione 25, fattibilità 20, aderenza 15,
  presentazione 15. A parità vince chi ha più punti in esecuzione, poi in innovatività.
- Caso d'uso scelto dal team (uno solo): **[DA COMPILARE]**
- Metrica di successo da mostrare nel pitch (tempo risparmiato, accuratezza, € ...): **[DA COMPILARE]**

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
- Avvio in locale: `streamlit run ui/app.py`
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
5. Pitch: problema in € o in ore → demo → come funziona → risultati → impatto per i clienti
   dello sponsor.

## 9. Base di conoscenza (`Vault/`)

- È una LLM Wiki: le fonti originali stanno in `Vault/raw/` (immutabili), la sintesi
  scritta dall'agente in `Vault/wiki/`. Le regole sono in `Vault/CLAUDE.md`.
- Al kick-off si mettono in `raw/` brief, regolamento, slide e dati, e si fa l'ingest.
- Prima di decisioni di prodotto o tecniche, leggi `Vault/wiki/index.md` e le pagine
  rilevanti. Le decisioni del team sono registrate in `Vault/wiki/log.md`.
