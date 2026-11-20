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
