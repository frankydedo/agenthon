# Consegna all'hackathon

Tutto ciò che il regolamento chiede per la **Categoria 1** (art. 7.3, 7.5) e come lo prepariamo.
Fonte: `Vault/raw/regulation.pdf`; sintesi in `Vault/wiki/analyses/criteri-e-consegna.md`.

> **Bozza provvisoria.** Il brief esce all'apertura dell'evento: i campi `[DA COMPILARE]` si
> riempiono allora. La repo di consegna si ricrea allo start (decisione del team).

## 1. Cosa chiede il regolamento

| Richiesta | Dove sta | Stato |
|---|---|---|
| Link al repository, accessibile alla giuria **da un altro account** | repo nuova, pubblica o con la giuria invitata | [ ] |
| File con **descrizione, tecnologie, istruzioni di avvio** | `README.md` (già scritto, da adattare al brief) | [ ] |
| **Descrizione ≤ 1.000 caratteri** con i componenti preesistenti | sezione 2 di questo file, da incollare nel portale | [ ] |
| Facoltativo: cartella Google Drive con presentazione e materiali | da creare, link accessibile a tutti | [ ] |
| Versione finale come **ultimo commit** prima dell'orario di consegna | `main`, con `pytest` e `demo_check.py` verdi | [ ] |

Dopo l'orario di consegna il portale non considera più alcuna modifica: **niente commit dopo**.
L'orario preciso verrà comunicato durante l'evento.

## 2. Descrizione per il portale (≤ 1.000 caratteri)

Bozza (691 caratteri, da completare con il caso d'uso scelto):

```text
Agente AI che gestisce le richieste in arrivo di uno studio professionale dall'inizio alla fine: legge l'email, identifica il cliente, estrae i dati dai PDF allegati con controlli deterministici (somme, partita IVA), prepara le azioni (registrare fatture, aprire pratiche, rispondere) e le esegue solo dopo l'approvazione esplicita di una persona. Ogni passo è visibile in una timeline in diretta. Il modello è sostituibile (locale con Ollama o cloud) e i dati restano sull'infrastruttura del cliente. Componenti preesistenti, preparati prima dell'evento: starter kit di agente (core/, api/, web/, scenario di prova) da noi scritto. Sviluppato durante l'evento: [DA COMPILARE dopo il brief].
```

Regole per la versione finale:
- contare i caratteri (incollare in un contatore) e restare sotto i 1.000;
- **dichiarare i componenti preesistenti**: lo starter kit (nucleo dell'agente, API, interfaccia web, scenario di prova) è stato scritto prima dell'evento; librerie open source (FastAPI, React, Tailwind, Pydantic, …) sono di terzi;
- dire cosa è stato fatto **durante** l'evento: dominio, prompt, tool, connettori, dati, adattamento dell'interfaccia.

## 3. Tecnologie (per il README)

| Livello | Tecnologie |
|---|---|
| Agente | Python 3.11+, ciclo scritto da noi (nessun framework per agenti), Pydantic, pdfplumber |
| Modello | sostituibile: mock (risposte registrate), server locale compatibile OpenAI (Ollama / LM Studio), cloud (Gemini, Mistral, …) |
| API | FastAPI, Server-Sent Events per i passi in diretta |
| Interfaccia | React 19, TypeScript, Vite, Tailwind v4, Motion, React Flow, TanStack Query |
| Dati | SQLite e file JSON su disco (nessun servizio esterno) |

## 4. Prima di consegnare

- [ ] `pytest` e `python scripts/demo_check.py` passano.
- [ ] Da una cartella pulita: clone, `pip install -r requirements.txt`, `npm install`, avvio dalle sole istruzioni del README.
- [ ] Nessun segreto nella repo (`.env` ignorato, nessuna chiave nei file o nella storia dei commit).
- [ ] La giuria può aprire il repository da un altro account (provare in una finestra anonima).
- [ ] README aggiornato al caso d'uso reale, con istruzioni di avvio **verificate**.
- [ ] Descrizione di ≤ 1.000 caratteri incollata nel portale.
- [ ] La versione che mostriamo in demo è **quella dell'ultimo commit** consegnato.
- [ ] Piano B pronto: provider `mock` con scenari registrati, se rete o modello cadono.

## 5. Pitch (circa 3 minuti, demo dal vivo inclusa)

Il punteggio di presentazione vale 15 punti su 100, ma conta solo in finale; per arrivarci
contano repository e README. Scaletta proposta:

1. **Problema** (20 s): quanto tempo o denaro costa oggi il processo, con un numero.
2. **Demo** (100 s): genera una richiesta → l'agente lavora (flusso in diretta) → la persona
   approva un'azione → si vede cosa è cambiato nei sistemi. Includere un caso in cui l'agente
   **non** agisce (errore trovato, mittente sconosciuto): è il momento più convincente.
3. **Come funziona** (30 s): agente + approvazione umana + modello sostituibile, dati sull'infrastruttura del cliente.
4. **Risultato** (20 s): la metrica misurata.
5. **Impatto** (10 s): cosa cambia per i clienti dello sponsor.

Criteri da toccare apertamente (art. 9): innovatività (25), esecuzione (25), fattibilità (20), aderenza (15).
