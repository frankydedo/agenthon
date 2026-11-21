---
type: overview
updated: 2026-11-21
sources: [raw/2026-11-20-luma-evento.md, raw/2026-11-20-arietetech.md, raw/regulation.md, raw/2026-11-21-brief.md]
confidence: media
tags: [stato]
---
# Overview

**Il brief è uscito** (2026-11-21): "Build an AI your team would trust". Si sceglie una di due
challenge; la A è **Company Brain**, con sette controlli sì/no da superare nella demo. La
challenge B non è ancora nel testo ricevuto. **La challenge non è ancora scelta.** Vedi
[Brief del track](concepts/brief-del-track.md).

## Cosa sappiamo
- Brief, challenge A e i sette controlli della giuria: vedi
  [Brief del track](concepts/brief-del-track.md).
- Evento, track, premi e regole: vedi [AGENTHON](entities/agenthon.md).
- Cosa si consegna (repo + README + descrizione da 1.000 caratteri), scadenza (conta l'ultimo
  commit), pesi dei criteri e pitch di ~3 minuti: vedi
  [Consegna e valutazione](concepts/consegna-e-valutazione.md).
- Analisi di dettaglio su punteggi, fasi e checklist: [Criteri e consegna](analyses/criteri-e-consegna.md).
- Sponsor e i suoi principi (persone in controllo, AI dove serve, hosting UE): vedi
  [Ariete Tech Solutions](entities/ariete-tech-solutions.md).

## Stato del codice
- Interfaccia nuova: backend FastAPI (`api/`) e frontend React (`web/`) sopra `core/`, collaudati
  col mock (2026-11-21). Streamlit resta come ripiego.
- Decisione: la repo di consegna si ricrea allo start dell'evento, così i commit coincidono
  con gli orari di gara.
- Sul branch `develop` c'è uno starter kit (vedi `README.md` e `docs/` nel repo):
  - `core/`: ciclo dell'agente, provider LLM sostituibile, tool con approvazione umana, output
    strutturato, traccia dei passi. Pensato per restare valido con qualsiasi brief.
  - `esempio/`: scenario di prova (studio commercialista, email e fatture). **Da sostituire**
    dopo il brief, non è il caso d'uso scelto.
- Verificato il 2026-11-20: test verdi e `scripts/demo_check.py` ok, ma solo con il provider
  finto (mock).
- Modello vero in sviluppo: Qwen3-30B-A3B su LM Studio nel MacBook Air, collegato dal Pro via
  Wi-Fi; tool calling verificato il 2026-11-20, flusso completo nella UI non ancora provato.
  Vedi [LLM locale](analyses/llm-locale.md).

## Domande aperte
- Testo della challenge B e scelta della challenge (decisione del team).
- Come si combinano i sette controlli sì/no con i 100 punti del regolamento; come funziona
  l'attacco delle squadre rivali.
- Lo starter kit scritto prima dell'Evento è ammesso? Va comunque dichiarato come componente
  preesistente (regolamento art. 7.1 e 7.3).
- Provider cloud di riserva per la demo dal vivo (il modello locale è deciso, vedi sopra).
- Come misurare la metrica del pitch (accuratezza dello smistamento, tempo risparmiato...).
- Tutto ciò che è in "Da verificare" nelle pagine delle entità.
