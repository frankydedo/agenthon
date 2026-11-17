# Schema della wiki - AGENTHON

Questa cartella è una **LLM Wiki** secondo il pattern di Andrej Karpathy (descritto in
`llm-wiki-pattern.md`): una base di conoscenza in markdown che l'agente scrive e mantiene, e che
il team legge (si può aprire in Obsidian come vault).

All'inizio è **vuota**: al kick-off facciamo l'ingest di tutti i documenti (brief, regolamento,
slide dello sponsor, dataset). Da lì ogni sessione di Claude parte dallo stesso contesto.

## Livelli

| Cartella | Chi scrive | Regola |
|---|---|---|
| `raw/` | gli umani (o l'agente su richiesta, per salvare una fonte) | **immutabile**: mai modificare una fonte esistente |
| `wiki/` | solo l'agente | pagine sintetiche, collegate, sempre aggiornate |
| `CLAUDE.md` (questo file) | umani e agente insieme | convenzioni e flussi di lavoro |

## Struttura di `wiki/`

- `index.md`: catalogo di tutte le pagine (link + una riga di sintesi), per categoria. Leggerlo
  **per primo** quando rispondi a una domanda. Crealo al primo ingest.
- `log.md`: registro cronologico, solo in aggiunta. Ogni voce inizia con
  `## [AAAA-MM-GG HH:MM] <ingest|query|lint|decisione> | <titolo>`. Crealo al primo ingest.
- `overview.md`: la sintesi corrente (cosa costruiamo, per chi, perché).
- `entities/`: organizzazioni, eventi, persone, prodotti, sistemi del cliente.
- `concepts/`: idee e tecniche (es. processi del dominio, approcci tecnici).
- `analyses/`: ragionamenti e risposte salvate (scelte, confronti, divisione del lavoro).

## Formato delle pagine

```markdown
---
type: entity | concept | analysis | overview
updated: AAAA-MM-GG
sources: [raw/<file>, ...]
confidence: alta | media | bassa
tags: [..]
---
# Titolo

Sintesi in 2-3 righe.

## ... (sezioni)

## Collegamenti
- [Altra pagina](../concepts/altra-pagina.md)
```

- Nomi file in `kebab-case`, in italiano. Link **relativi in markdown** (funzionano su GitHub e
  in Obsidian).
- Ogni affermazione importante cita la fonte (`raw/...`). Ciò che è **dedotto** e non letto in
  una fonte va marcato come *(deduzione)*.
- Le contraddizioni non si cancellano: si annotano in una sezione `## Da verificare` con le
  fonti di entrambe le versioni.
- Lingua: italiano. Termini tecnici in inglese dove è l'uso comune.

## Flussi di lavoro

**Ingest** (nuove fonti in `raw/`):
1. Leggi la fonte e riassumi all'umano i 3-5 punti chiave; chiedi cosa enfatizzare.
2. Crea o aggiorna le pagine toccate (spesso 5-15): entità, concetti, analisi, `overview.md`.
3. Segnala dove la nuova fonte contraddice o rende obsoleto qualcosa.
4. Aggiorna `index.md` e aggiungi una voce in `log.md`.
Con molte fonti insieme (kick-off), fai prima un giro rapido su tutte per costruire
`overview.md` e `index.md`, poi approfondisci fonte per fonte.

**Query** (domanda del team):
1. Leggi `index.md`, poi le pagine rilevanti; rispondi citando pagine e fonti.
2. Se la risposta ha valore duraturo (un confronto, una decisione), salvala in `analyses/`,
   collegala e registrala in `log.md`.

**Decisione** (il team sceglie qualcosa: caso d'uso, stack, ruoli):
- Registrala in `log.md` con il prefisso `decisione` e aggiorna `overview.md` e le analisi
  interessate. Le decisioni valgono finché non vengono cambiate esplicitamente.

**Lint** (su richiesta, es. prima del pitch):
- Cerca contraddizioni, affermazioni superate, pagine orfane, concetti citati senza pagina,
  link rotti, domande aperte. Proponi le correzioni prima di applicarle.

## Fonti in `raw/`

- Nome: `AAAA-MM-GG-<fonte>.<ext>`. Per ogni fonte non testuale (foto del brief, PDF, slide)
  l'ingest può aggiungere accanto un `.md` con la trascrizione, citando l'originale.
- Dataset grandi: non copiarli in `raw/`; salva una descrizione (schema, dimensioni, posizione).
- Lavorando in tre sullo stesso repo: fai `git pull` prima di un ingest e committa subito dopo,
  così le pagine della wiki non vanno in conflitto.
