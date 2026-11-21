---
type: overview
updated: 2026-11-21
sources: [raw/2026-11-20-luma-evento.md, raw/2026-11-20-arietetech.md, raw/regulation.md]
confidence: media
tags: [stato]
---
# Overview

**Il brief non è ancora noto**: esce al kick-off. Fino ad allora il caso d'uso non è scelto.

## Cosa sappiamo
- Regolamento noto: criteri con pesi, regole di consegna e pitch di 3 minuti con demo. Vedi
  [Criteri e consegna](analyses/criteri-e-consegna.md).
- Evento, track e criteri di giudizio: vedi [AGENTHON](entities/agenthon.md).
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
- Provider cloud di riserva per la demo dal vivo (il modello locale è deciso, vedi sopra).
- Come misurare la metrica del pitch (accuratezza dello smistamento, tempo risparmiato...).
- Tutto ciò che è in "Da verificare" nelle pagine delle entità.
