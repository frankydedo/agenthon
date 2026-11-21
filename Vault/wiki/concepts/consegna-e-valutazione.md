---
type: concept
updated: 2026-11-21
sources: [raw/regulation.pdf, raw/regulation.md]
confidence: alta
tags: [regole, consegna, giuria, pitch]
---
# Consegna e valutazione

Cosa consegnare, entro quando, e come la giuria assegna i 100 punti. Tutto dal regolamento
ufficiale (versione del 20/11/2026, [fonte](../../raw/regulation.md)), salvo le righe *(deduzione)*.

## Cosa si costruisce (Categoria 1)
- Un **prototipo funzionante** di sistema AI che risponde al brief del track; può essere
  parziale ma **deve essere dimostrabile**, non serve che sia pronto per la produzione (art. 7.2).
- Va sviluppato **durante l'Evento**; librerie, framework, API e servizi AI di terzi sono
  ammessi nel rispetto delle licenze (art. 7.1).

## Cosa si consegna, tramite il portale (art. 7.3)
1. **Link al repository** del codice, accessibile alla giuria, con un file che descrive il
   progetto, le tecnologie e le istruzioni essenziali di avvio.
2. **Descrizione di massimo 1.000 caratteri**, che indica gli **eventuali componenti
   preesistenti** usati.
3. Facoltativo: link a una cartella Google Drive con presentazione e altri materiali.
- I link devono funzionare anche da un account **esterno** al team.
- Portale: `agenthon-portal.gdgtorino.it`; al primo login si accetta questa versione del
  regolamento (art. 6.6).

## Scadenza (art. 7.5)
- Orario di consegna comunicato durante l'Evento; oltre quell'orario il progetto non è valutato.
- All'orario di consegna il portale **registra l'ultimo commit** del repository: i commit
  successivi non contano. La demo del pitch deve riguardare **quella** versione (art. 7.4).

## Come si arriva in finale (art. 7.4)
- La giuria valuta tutti i progetti consegnati con i criteri sotto, **esclusa la presentazione**,
  e sceglie da 8 a 12 finalisti.
- I finalisti fanno un **pitch di circa 3 minuti, demo dal vivo inclusa**, in ordine alfabetico
  inverso del nome del progetto; la giuria può fare domande.

## Criteri e punteggi (art. 9.1)
| Criterio | Punti |
|---|---|
| Innovatività (originalità rispetto alle soluzioni esistenti) | 25 |
| Qualità dell'esecuzione (quanto realizzato durante l'Evento) | 25 |
| Fattibilità (adozione in un contesto reale) | 20 |
| Aderenza al tema della categoria | 15 |
| Qualità della presentazione (problema, soluzione, demo) | 15 |

- Voto finale: media dei totali dei 5 giurati, a due decimali (art. 9.2).
- Parità: vince chi ha più punti in **esecuzione**, poi in **innovatività**, poi decide la
  giuria (art. 9.3).
- Giuria del track: un rappresentante di Ariete, uno di GDG Torino, tre esperti esterni;
  giudizio insindacabile (art. 8).

## Cosa ne segue per noi *(deduzione)*
- La selezione dei finalisti si fa **senza pitch**: repo, README e descrizione da 1.000
  caratteri devono reggersi da soli (istruzioni di avvio chiare, demo riproducibile).
- Esecuzione + innovatività = 50 punti e decidono anche le parità: meglio una demo
  end-to-end solida e originale che tante funzioni.
- Fare il merge su `main` (testato) **prima** della scadenza e verificare quale branch legge il
  portale; dopo la scadenza niente commit che servano alla demo.
- Repo pubblico o condiviso con la giuria: provare il link da un browser non loggato.
- 3 minuti con demo dal vivo sono pochissimi: script del pitch cronometrato e video di riserva.

## Da verificare
- Lo starter kit (`core/`) è stato scritto **prima** dell'Evento, mentre l'art. 7.1 chiede che il
  progetto sia sviluppato durante l'Evento e l'art. 7.3 c) chiede di dichiarare i componenti
  preesistenti. *(deduzione)* Va dichiarato esplicitamente nella descrizione; chiedere agli
  organizzatori se è ammesso e in che misura.
- Orario esatto di consegna e quale branch registra il portale.

## Collegamenti
- [AGENTHON](../entities/agenthon.md)
- [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)
- [Overview](../overview.md)
