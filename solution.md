# endof.md: allineamento per gli agenti del team

> **Leggi questo file prima di scrivere codice.** Riassume le decisioni prese dal team il
> 21/11/2026 durante AGENTHON (Track 1, Agentic AI for business). Le regole generali di lavoro
> restano in `CLAUDE.md`; il brief originale è in `Vault/raw/2026-11-21-brief-track1.md`;
> il regolamento in `Vault/raw/regulation.pdf`. Se qualcosa qui contraddice `CLAUDE.md`, vale
> questo file per il prodotto e `CLAUDE.md` per il modo di lavorare.
>
> Legenda: **[DECISO]** = scelto dal team, non rimetterlo in discussione senza chiedere ·
> **[PROPOSTO]** = piano di lavoro adottato come base, si può aggiustare parlandone ·
> **[APERTO]** = da decidere, chiedi all'umano invece di assumere.

---

## 0. Decisioni prese insieme (21/11, dopo il brief)

| Tema | Decisione |
|---|---|
| Repo | **[DECISO]** si continua su **questa repo**, branch `develop` (non se ne crea una nuova) |
| PMI fittizia | **[DECISO]** azienda di **automazione industriale**, circa 8 persone |
| Voce (ElevenLabs) | **[DECISO]** **P1**: dopo che i 7 controlli passano con minute di testo |
| Modello in demo | **[DECISO]** **locale** (Qwen sul server Ollama del team) con **cloud di riserva**; il mock resta per sviluppo e test |
| Divisione del lavoro | **[DECISO]** Franky: cervello AI · Pietro: backend, dati, to-do, voce · Mauro: interfaccia, docs, pitch (§7) |
| Permessi | **[DECISO]** per **competenza**: ognuno vede ciò che rientra nelle sue competenze (§3) |
| Approvazioni in giornata | **[DECISO]** la persona accetta e modifica **la propria** to-do del giorno; ciò che cambia **la lista del progetto** è una proposta che approva **il manager** |
| Riunioni sintetiche | **[DECISO]** **5 riunioni** dello stesso progetto (es. kick-off, avanzamento, costi, fine giornata, evento esterno), con le trappole di §7 |
| Widget | **[DECISO]** **layout fisso** per ruolo, con i pezzi già scritti come widget separati; trascinamento/ridimensionamento in P2 |

---

## 1. Cosa stiamo costruendo

**[DECISO] Challenge A · Company Brain**, declinato sulle **riunioni di progetto**.

Il Brain è un **membro attivo del team**: legge riunioni (minute, trascrizioni, registrazioni
audio), capisce i task e a chi assegnarli, tiene una memoria del progetto curata dalle persone,
**trova incongruenze e criticità tra riunioni diverse**, segnala ciò che non conosce, e prepara
le to-do list di ciascuno. **Non agisce mai senza l'approvazione di una persona.**

Frase guida del brief: *"Build an AI your team would trust."* Vince chi è corretto, ammette ciò
che non sa e non agisce senza approvazione. *Un chatbot sui documenti non vale.*

### Il flusso del prodotto [DECISO]

1. **Il manager crea il progetto**: dati, persone coinvolte (anche di reparti diversi), account,
   scadenza. Lo scope è **per progetto**.
2. **Riunione**: il Brain legge la minuta o la registrazione (o, come estensione, ascolta dal vivo).
3. **Analisi**: estrae task, assegnatari, scadenze, decisioni, fatti, criticità.
   - Se un task o il suo assegnatario **non è chiaro**, lo dice esplicitamente (punto oscuro).
   - Se si parla di una **persona o di un contesto che non conosce** (assente da questa riunione,
     dalle precedenti e dalla knowledge base), **avvisa in modo proattivo**.
   - Confronta con le riunioni precedenti e segnala **incongruenze** (es. una scadenza che cambia).
4. **Il Brain aggiorna la to-do list generica del progetto** come proposta: cose fatte, nuove
   cose da fare, criticità.
5. **Il manager approva** (voce per voce). **Solo dopo** la lista viene smistata alle persone.
6. **To-do personale giornaliera**, derivata da quella generica: la persona la **accetta al
   mattino** e la può **modificare durante il giorno** (decide lei, senza il manager).
   Se una modifica tocca la lista del progetto (task chiuso, nuovo task, criticità), diventa una
   **proposta per il manager**. Si aggiorna anche per **eventi esterni**
   (errori nel codice, problemi di colleghi) e con la **riunione di fine giornata** ("ho fatto questo").
   Tra le liste di persone diverse possono esistere **dipendenze**.
7. **Citazioni**: ogni task, fatto o risposta cita **la riunione da cui viene** (con orario e
   frase esatta).

### Voce [DECISO, come bonus]
Si usa **ElevenLabs** (trascrizione con riconoscimento di chi parla, sintesi vocale) per puntare al
premio "Best use of ElevenLabs". È un **bonus**: i 7 controlli vengono prima.

### Interfaccia a widget [DECISO come idea, subordinata]
Schermata componibile con widget (servizi diversi affiancati). Si realizza come **un'unica app
React con un registro di widget**, **non** come microfrontend veri (Module Federation/iframe):
stesso effetto per la giuria, molte ore in meno. Prima **layout fisso**; trascinamento e
ridimensionamento (`react-grid-layout`) solo se avanza tempo.

---

## 2. I 7 controlli della demo (la giuria li segna sì/no)

Ogni funzione deve servire a superarne almeno uno. Se non serve, aspetta.

| # | Controllo del brief | Come lo superiamo |
|---|---|---|
| 1 | **Parla per primo** | avvisi proattivi: incongruenze tra riunioni, persone/contesti sconosciuti, dipendenze a rischio. In demo un pulsante «avanza il tempo / nuovo evento» li rende ripetibili |
| 2 | **Le persone curano la memoria** | il manager approva una proposta e ne rifiuta un'altra **dal vivo**; poi una domanda a cui risponde solo la voce approvata. → **serve la funzione "Chiedi al Brain"** |
| 3 | **Sa chi chiede** | stessa domanda da due persone con competenze diverse: es. lo sviluppatore chiede il budget residuo e non riceve risposta; il senior che ha la competenza «budget» sì (§3, permessi per competenza) |
| 4 | **Cita** | ogni risposta/task mostra i tag della riunione (orario e frase); cliccabili |
| 5 | **Ammette le lacune** | «non lo so» se il dato non c'è; «non conosco questa persona/questo contesto» |
| 6 | **Propone soltanto** | proposte e azioni restano *in attesa* finché il manager non approva |
| 7 | **Si inserisce nella giornata** | to-do del mattino, riunione di fine giornata, email del mattino (mock), brief letto a voce |

Attenzione ai controlli **2 e 3**: con un prodotto centrato solo sui task rischiano di saltare.
Le domande con filtro per ruolo sono obbligatorie.

---

## 3. Regola d'oro: cosa decide il codice e cosa il modello [DECISO]

Il modello **capisce il testo e scrive**. Il codice **fa rispettare le regole**.

**Sempre nel codice (deterministico), mai nel modello:**
- ruolo di chi chiede e permessi: il ruolo arriva dalla sessione, **non è mai un argomento che il
  modello può impostare**;
- **permessi per competenza** (vedi sotto);
- abbinamento delle persone (nomi detti → membri del progetto, tramite alias). Se non è univoco
  → **punto oscuro**, mai un'ipotesi;
- **tag e citazioni**: li genera il codice dagli id dei segmenti; il modello indica solo quali
  segmenti ha usato, e il codice verifica che siano tra quelli forniti;
- **«non lo so»** quando la ricerca non trova nulla di pertinente: risposta immediata, senza
  chiamare il modello;
- stati delle proposte e approvazioni;
- calcolo delle dipendenze e dei task bloccati;
- confronto tra fatti strutturati (stesso soggetto e attributo, valore diverso → incongruenza).

### Permessi per competenza [DECISO]

Ognuno vede **ciò che rientra nelle sue competenze**. Esempio: uno sviluppatore conosce le
informazioni sullo sviluppo ma non il budget; un senior, se è di sua competenza, conosce anche il budget.

- **Aree di competenza** [DECISO], lista chiusa: `sviluppo`, `budget`, `commerciale`, `fornitori`,
  `personale`, `generale`. `generale` è visibile a tutti i membri del progetto.
- Ogni **persona** ha un insieme di competenze: quelle tipiche del suo ruolo **più eventuali
  aggiunte personali** (es. senior dev = `sviluppo` + `budget`). Il manager del progetto le ha tutte.
- Ogni **fatto, task o voce di memoria** ha una o più aree. [DECISO] Una persona lo vede solo se ha
  **tutte** quelle aree (es. «il ritardo del fornitore costa 8.000 €» = `fornitori` + `budget`: lo vede
  solo chi ha entrambe). Altrimenti la risposta è «non hai accesso a questa informazione».
- **Chi assegna l'area**: il modello la **propone** in fase di estrazione, **il manager la conferma**
  quando approva la proposta (è parte della curatela). In caso di dubbio il default è l'area **più
  restrittiva** (mai `generale`). Il **filtro** sulle aree lo applica sempre il **codice**, prima di
  passare qualsiasi dato al modello.

**Al modello:** estrarre task/fatti/punti oscuri da testo libero, comporre risposte e brief,
riconoscere incongruenze espresse con parole diverse, scrivere bozze.

**L'analisi delle riunioni è una pipeline a passi fissi**, non un agente libero. Il ciclo
agentico con tool serve per le domande e per approfondire un'incongruenza.

---

## 4. Architettura [PROPOSTO]

```
 Audio / minuta ─► Voce (ElevenLabs | Whisper | mock) ─► trascrizione: segmenti {chi, inizio, fine, testo}
                                                            │
   Pipeline:  1 blocchi (codice) → 2 estrazione (modello) → 3 abbinamento persone (codice)
              → 4 lacune (codice+modello) → 5 incongruenze (codice+modello) → 6 differenze vs lista (codice)
                                                            │
                         Proposte ─► APPROVAZIONE MANAGER ─► Lista del progetto ─► smistamento
                                                                                       │
                                     To-do giornaliere (accettate al mattino) ◄────────┘
                                          ▲ eventi esterni · riunione di fine giornata
   Trasversali: "Chiedi al Brain" con filtro per ruolo · avvisi proattivi (SSE) · registro di tutto
```

- **Riunioni lunghe**: un'ora ≈ 15-20k token, più dei **16k di contesto** del modello locale.
  Si divide in blocchi, si estrae per blocco, si uniscono i risultati.
- **Scalabilità della memoria** (criterio "fattibilità oltre il prototipo"): partizione per ruolo e
  stato → ricerca FTS5 per trovare i punti di ingresso → collegamenti tra elementi. Embedding e
  grafi più ricchi solo dopo.
- **Fornitori sostituibili** (modello e voce), con una modalità **mock** a risposte registrate:
  serve per sviluppare senza costi e come **piano B dal vivo**.

---

## 5. Stack [PROPOSTO]

| Livello | Scelta |
|---|---|
| Backend | Python 3.12, FastAPI, SSE, Pydantic |
| Dati | **SQLite + FTS5** (nessun servizio esterno; dati sul PC, coerente con lo sponsor) |
| Modello | sostituibile via API compatibile OpenAI. **Demo: Qwen3 locale sul server Ollama del team, cloud di riserva** (contesto ampio). Mock a risposte registrate per sviluppo e test. Configurazione in `.env` (mai committato) |
| Voce | ElevenLabs (trascrizione con chi parla e orari; sintesi). Alternativa locale: `faster-whisper`. Crediti/API **da verificare** all'evento |
| Frontend | React 19, TypeScript, Vite, Tailwind v4, Motion, React Flow (dipendenze), lettore audio sincronizzato; `react-grid-layout` in seguito |
| Dati di prova | riunioni **sintetiche in italiano** scritte da noi, trasformate in audio con voci ElevenLabs (una per persona). Nessun dato reale |

---

## 6. Contratti condivisi [PROPOSTO, da fissare insieme in Fase 0]

Vivono in `backend/modelli.py` (Pydantic) e `backend/schema.sql`. **Si cambiano solo dopo averne
parlato**; chi li cambia aggiorna anche i dati finti.

**Riunione**
```json
{"id": "riu-001", "progetto": "prj-01", "data": "2026-11-10", "partecipanti": ["p-01", "p-03"],
 "aree_predefinite": ["sviluppo"],
 "segmenti": [{"id": "riu-001#s12", "chi": "p-03", "inizio": 872.4, "fine": 880.1, "testo": "..."}]}
```
`aree_predefinite`: aree di competenza suggerite per ciò che emerge dalla riunione (es. una
riunione sui costi → `budget`). Il modello può proporne altre per singolo fatto; il manager conferma.

**Output dell'estrazione**
- `task[]`: descrizione, assegnatario_detto, assegnatario_id (o null), scadenza, **aree**, segmento_id, sicurezza
- `fatti[]`: soggetto, attributo, valore, **aree**, segmento_id
- `punti_oscuri[]`: cosa, perché, segmento_id
- `sconosciuti[]`: nome, tipo (persona | contesto), segmento_id

**Tabelle**: progetti, persone (alias, ruolo, reparto, **competenze**), riunioni, segmenti, fatti, task,
dipendenze, proposte (in_attesa | approvata | rifiutata), todo_giornaliere, avvisi, domande,
eventi. Ogni fatto/task/proposta punta al **segmento** da cui nasce (da lì le citazioni).

**API** (prima versione): `POST /riunioni` · `GET /proposte` · `POST /proposte/{id}/approva` ·
`POST /proposte/{id}/rifiuta` · `GET /progetti/{id}/todo` · `GET /persone/{id}/todo-oggi` ·
`POST /todo-oggi/accetta` · `GET /avvisi` (SSE) · `POST /domande` · `POST /eventi/simula` · `GET /registro`.

---

## 7. Divisione del lavoro [PROPOSTO]

Tutti fanno un po' di tutto; la tabella dice **chi decide** su quella parte.

| Persona | Area | File principali |
|---|---|---|
| **Franky** (AI) | il cervello: prompt, estrazione, abbinamento, lacune, incongruenze, domande, valutazione; scrive le **5 riunioni sintetiche** con le trappole e i JSON attesi (prima la riunione 1, che serve subito come dato finto per gli altri) | `backend/analisi/`, `backend/domande.py`, `backend/llm.py`, `dati/riunioni/`, `dati/attese/` |
| **Pietro** (software) | backend, database, dati dell'azienda, logica delle to-do e delle dipendenze, simulatore eventi, ElevenLabs, verifica automatica | `backend/app.py`, `db.py`, `schema.sql`, `todo.py`, `eventi.py`, `voce.py`, `dati/azienda.json`, `scripts/demo_check.py` |
| **Mauro** (software) | interfaccia (selettore ruolo, vista manager, vista membro, chat, email del mattino, citazioni cliccabili), README, descrizione, pitch | `web/`, `docs/`, `README.md` |

**Le trappole da mettere nelle riunioni sintetiche** (fanno passare i controlli): un task chiaro
e assegnato; un task senza responsabile; un nome ambiguo (due «Marco»); una persona o un sistema
mai citati prima; una scadenza che cambia tra due riunioni; un dato di budget visibile solo a chi
ha la competenza `budget` (e un'informazione con due aree, es. `fornitori` + `budget`); una
dipendenza tra task di persone diverse; un «ho fatto questo» nella riunione di fine giornata;
un evento esterno (es. errore nel codice) che rimescola le priorità.

---

## 8. Priorità e tappe [PROPOSTO]

- **P0 (entro M2)**: progetto e persone come dati iniziali; minuta di testo → estrazione con
  citazioni e punti oscuri → approvazione del manager → to-do smistate; un'incongruenza tra due
  riunioni; domande con filtro per ruolo e «non lo so». **= i 7 controlli.**
- **P1**: audio con ElevenLabs; to-do del mattino da accettare/modificare; riunione di fine
  giornata; brief letto a voce.
- **P2**: ascolto dal vivo; eventi esterni (errori nel codice); ricadute a catena delle
  dipendenze; widget trascinabili.

| Ora (consegna ipotizzata 19:00) | Tappa |
|---|---|
| +45 min | Fase 0 chiusa: contratti e repo pronti |
| **15:30** | **M1**: tutto collegato con dati finti (minuta → proposte → approvazione → to-do) |
| **17:00** | **M2**: P0 completo con il modello vero, i 7 controlli passano |
| 18:15 | M3: voce e to-do del giorno |
| 18:15-19:00 | **blocco funzionalità**: solo bug, prova del pitch, video di riserva, merge su `main` |

Se M2 non è chiuso alle 17:00, **la voce si salta**.

---

## 9. Regole operative (da `CLAUDE.md`, ribadite)

- Si lavora su **`develop`**; su `main` solo ciò che è testato e funziona. `git pull` prima,
  commit piccoli.
- Modifica solo la tua area; per cambiare un contratto condiviso fermati e chiedi.
- **Non chiamare API a pagamento** (modello, ElevenLabs) senza che l'umano lo chieda; sviluppa
  con il mock.
- **Mai** leggere, stampare o committare segreti (`.env`, chiavi, token).
- Solo **dati sintetici**; testi per l'utente in **italiano**.
- Il regolamento registra **l'ultimo commit all'orario di consegna**: dopo, niente commit.
- I componenti scritti prima dell'evento (starter kit: provider, output strutturato, SSE, setup
  React) vanno **dichiarati come preesistenti** nella descrizione per la giuria.
- Alla fine di ogni task: cosa è cambiato, come si prova, cosa resta aperto (3 righe).

---

## 10. Aperto

- **[APERTO]** Orario di consegna (verrà comunicato all'evento).
- **[APERTO]** Accesso della giuria alla repo da un altro account (repo pubblica o giuria invitata), da sistemare prima della consegna.
- **[APERTO]** Competenze di ogni persona dell'azienda fittizia (Fase 0, con i dati di `azienda.json`).
- **[APERTO]** Quale modello cloud di riserva; crediti e API disponibili per ElevenLabs.
- **[APERTO]** Raggiungibilità del server Ollama del team (rete dedicata; parametri nel `.env`).

---

## 11. Dove trovare il resto

| Cosa | Dove |
|---|---|
| Regole di lavoro del team | `CLAUDE.md` |
| Brief ufficiale (inglese, originale) | `Vault/raw/2026-11-21-brief-track1.md` |
| Regolamento, criteri e consegna | `Vault/raw/regulation.pdf`, `Vault/wiki/analyses/criteri-e-consegna.md` |
| Storia delle decisioni | `Vault/wiki/log.md` |
| Starter kit esistente (riusabile, dominio da sostituire) | `core/`, `api/`, `web/`, `docs/architettura.md` |
| Modello locale (configurazione) | `Vault/wiki/analyses/llm-locale.md` |
