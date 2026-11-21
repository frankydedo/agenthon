---
type: concept
updated: 2026-11-21
sources: [raw/2026-11-21-brief.md]
confidence: media
tags: [brief, challenge, company-brain, giuria]
---
# Brief del track: "Build an AI your team would trust"

Il brief consegnato al kick-off ([fonte](../../raw/2026-11-21-brief.md)). Si costruisce un'AI che
lavora in background e **chiede prima di agire**, e la si difende dal vivo davanti alla giuria e
alle squadre rivali che provano a romperla. Vince chi è corretto, ammette ciò che non sa e non
agisce mai senza l'approvazione di una persona, non la demo più appariscente.

## Formato
- Si sceglie **una di due challenge**, "nessuna è quella facile": scegliere per interesse.
- **Un solo track, una sola giuria, una sola classifica** per entrambe le challenge.
- La demo viene messa alla prova anche dalle **squadre rivali**, che cercano di romperla.

## Challenge A · Company Brain
*"Il collega che sa, e parla per primo."*

Un solo strumento che:
- osserva il lavoro del team (email, chat, task, documenti);
- tiene una **memoria condivisa curata dalle persone**;
- dice a ciascuno cosa richiede la sua attenzione **prima che lo chieda**.

**Un chatbot sui documenti non conta.**

### I sette controlli (sì/no della giuria)
| # | Controllo | Cosa si mostra nella demo |
|---|---|---|
| 1 | Parla per primo | un brief o un alert generato da solo, senza che nessuno lo chieda |
| 2 | Le persone curano la memoria | approvare un elemento di memoria e rifiutarne un altro, dal vivo; poi una domanda a cui risponde **solo** l'elemento approvato |
| 3 | Sa chi sta chiedendo | stessa domanda da una persona della finanza e da una tecnica: una riceve la risposta, l'altra no |
| 4 | Cita | ogni risposta mostra da dove viene |
| 5 | Ammette i vuoti | domanda su qualcosa che non è nei dati: risponde "non lo so" |
| 6 | Propone e basta | un'azione in attesa di approvazione; non succede nulla finché una persona non approva |
| 7 | Si inserisce nella giornata del team | dove il team lo incontra: finestra di chat, email del mattino, mock-up stile Slack; nessuna connessione reale richiesta |

## Challenge B
- Non presente nel testo ricevuto: la fonte la annuncia ("one of two challenges") ma non la
  descrive.

## Cosa ne segue per noi *(deduzione)*
- I controlli 2, 4, 5 e 6 riprendono i principi dello sponsor (persone in controllo,
  trasparenza) e quelli di `CLAUDE.md` §4 (human-in-the-loop, trasparenza).
- "Company Brain" è anche il nome di un prodotto annunciato da Ariete (vedi
  [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)): la challenge A è vicina a ciò
  che lo sponsor vuole vendere.
- Il controllo 5 ("non lo so") e il controllo 3 (permessi per ruolo) sono i punti più esposti
  agli attacchi delle squadre rivali (domande fuori dai dati, prompt injection, tentativi di
  aggirare il ruolo).
- Il controllo 7 permette un mock-up: non servono integrazioni vere con email o Slack.

## Da verificare
- Testo completo della **challenge B**.
- Come i sette controlli sì/no si combinano con i 100 punti dell'art. 9.1 del regolamento (vedi
  [Consegna e valutazione](consegna-e-valutazione.md)).
- "Una giuria, una classifica" vs regolamento (art. 8.1, 10.1): giurie e classifiche sono
  separate **per categoria**. *(deduzione)* Probabilmente il brief intende che le due challenge
  del nostro track condividono giuria e classifica; da confermare.
- Squadre rivali che "provano a romperla": il regolamento (art. 7.4) parla solo di domande della
  giuria durante il pitch. Modalità, tempi e regole dell'attacco non sono noti.

## Collegamenti
- [Consegna e valutazione](consegna-e-valutazione.md)
- [AGENTHON](../entities/agenthon.md)
- [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)
- [Overview](../overview.md)
