---
type: analysis
updated: 2026-11-21
sources: [raw/regulation.md, raw/regulation.pdf]
confidence: alta
tags: [regolamento, valutazione, consegna, pitch]
---
# Criteri di valutazione e regole di consegna (Categoria 1)

Dal regolamento del 20 novembre 2026: come ci valutano, cosa dobbiamo consegnare e cosa ne
segue per il lavoro. Gli articoli citati sono quelli del regolamento.

## Punteggi (art. 9.1, totale 100)
| Criterio | Punti |
|---|---|
| Innovatività (originalità rispetto alle soluzioni esistenti) | 25 |
| Qualità dell'esecuzione (ciò che è **realmente realizzato** nell'evento) | 25 |
| Fattibilità (adozione concreta in un contesto reale) | 20 |
| Aderenza al tema della categoria | 15 |
| Qualità della presentazione (problema, soluzione, demo) | 15 |

- Punteggio finale = media dei totali dei giurati (art. 9.2). Spareggio: prima "esecuzione",
  poi "innovatività", poi voto della giuria (art. 9.3).
- Giuria di 5: sponsor (Ariete), organizzatore, tre esperti esterni (art. 8.1).
- *(deduzione)* Esecuzione e innovatività valgono metà del punteggio e fanno da spareggio:
  meglio una demo solida e originale che molte funzioni a metà.

## Due fasi (art. 7.4)
1. **Selezione**: dopo la consegna la giuria valuta **tutti** i progetti con i criteri sopra,
   **esclusa la presentazione**, e sceglie 8-12 finaliste. Qui contano repository, README e
   descrizione.
2. **Finale**: pitch di circa **3 minuti** (Cat. 1) **comprensivo della demo dal vivo**, con
   domande della giuria. La demo è sulla versione consegnata (art. 7.5).

## Cosa si consegna (art. 7.3)
- Link al **repository** accessibile alla giuria **da un account diverso** dai nostri, con un
  file che descrive progetto, tecnologie e istruzioni essenziali di avvio.
- Descrizione del progetto di **massimo 1.000 caratteri**, con i **componenti preesistenti**
  usati (qui va dichiarato lo starter kit).
- Facoltativo: link a una cartella Google Drive con presentazione e altri materiali (anche
  questo accessibile alla giuria).
- Il portale registra l'**ultimo commit** all'orario di consegna: dopo, niente modifiche
  (art. 7.5). Oltre l'orario il progetto non è ammesso.

## Vincoli sul progetto
- Sviluppato **durante l'evento**; librerie, framework, API e servizi AI di terzi sono ammessi
  nel rispetto delle licenze (art. 7.1).
- Può essere **parziale ma dimostrabile**; non serve una soluzione pronta per la produzione
  (art. 7.2).
- Originale, senza violare diritti di terzi (art. 7.6). Il codice resta nostro; Organizzatore e
  sponsor possono citarlo e mostrarne immagini solo per comunicare l'evento (art. 12).
- Team al massimo di 3, un solo progetto (art. 6.2).

## Premi
- Cat. 1 (Ariete): 1.250 € al primo, 500 € al secondo, divisi in parti uguali nel team
  (art. 10.1-10.2); fino a 3 premi extra (un libro) a squadre fuori dal podio (art. 10.3).
- Premio speciale **"Best use of ElevenLabs"** (qualsiasi categoria, piano Scale) e codice
  piano Pro ai primi di ogni categoria (art. 10.7).

## Cosa ne segue (checklist)
- [ ] Repo nuova creata allo start (decisione del team, vedi [log](../log.md)), con accesso
      per la giuria.
- [ ] README di progetto: descrizione, tecnologie, avvio rapido.
- [ ] Descrizione ≤ 1.000 caratteri con lo starter kit dichiarato come preesistente.
- [ ] Versione finale su `main`, testata, prima dell'orario di consegna.
- [ ] Demo preparata su quella versione; pitch di 3 minuti con demo dentro.
- [ ] Piano B per la demo (modello `mock` registrato) se rete o modello cadono.

## Da verificare
- Orario di consegna e brief: comunicati all'apertura (art. 7.2, 7.5).
- Quale branch registra il portale (il regolamento dice solo "ultimo commit").
- Crediti gratuiti dei partner tecnologici: previsti (art. 7.7) ma non elencati.

## Collegamenti
- [AGENTHON](../entities/agenthon.md)
- [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)
- [LLM locale](llm-locale.md)
