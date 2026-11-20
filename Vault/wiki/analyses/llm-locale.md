---
type: analysis
updated: 2026-11-20
sources: []
confidence: alta
tags: [llm, infrastruttura, lm-studio, provider]
---
# LLM locale: Qwen3-30B-A3B su LM Studio (MacBook Air come server)

Per lo sviluppo il modello vero gira in locale su un MacBook Air da 24 GB con LM Studio, e il
MacBook Pro da 16 GB ci si collega via Wi-Fi tramite il provider `openai_compat` già presente in
`core/llm_openai.py`. Nessun dato esce dalla rete locale, il che è coerente con il principio di
sovranità dei dati dello sponsor (vedi [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)).
Tutto ciò che è scritto qui è stato provato in sessione il 2026-11-20 e non viene da una fonte in `raw/`.

## Configurazione
- **Server (Air 24 GB)**: LM Studio, modello `qwen/qwen3-30b-a3b-2507` (MoE, circa 3B parametri
  attivi), circa 50-60 token/s in locale. Nella scheda Developer: server avviato, **Serve on
  Local Network** attivo, autenticazione con token attiva. Context length consigliato di almeno 16k
  *(deduzione: il default di 4k è stretto per un agente con i tool)*.
- **Air sempre sveglio**: alimentatore collegato, coperchio aperto, `caffeinate -dimsu` in un terminale.
- **Client (Pro 16 GB)**: nel file `.env`, che non va mai committato:
  ```
  LLM_PROVIDER=openai_compat
  LLM_BASE_URL=http://<IP-dell-Air>:1234/v1
  LLM_MODEL=qwen/qwen3-30b-a3b-2507
  LLM_API_KEY=<token generato in LM Studio sull'Air>
  ```
  L'IP si legge sull'Air con `ipconfig getifaddr en0` e **cambia a ogni rete**: il 2026-11-20 a
  casa era `192.168.1.12`. Il token non si scrive mai nella wiki né nel repo.

## Cosa è stato verificato
- `GET /v1/models` dal Pro risponde e mostra il modello (oltre a `text-embedding-nomic-embed-text-v1.5`).
- **Tool calling tramite il provider del progetto**: alla domanda "Che tempo fa a Torino?" il
  modello ha risposto con `meteo(citta="Torino")` in 12 s, includendo il caricamento iniziale.
- Lo streaming SSE funziona con `curl -N` e `"stream": true`. Il provider del progetto **non** usa
  lo streaming: aspetta la risposta completa, che per l'agente va bene.
- **Non ancora provato**: il flusso completo dell'agente nella UI su un'email di esempio.

## Problemi noti e piani di riserva
1. **Il Wi-Fi della sede può isolare i dispositivi** (client isolation). Ci si accorge che
   `curl http://<IP>:1234/v1/models` non risponde mentre il server sull'Air è attivo.
   Soluzione: collegare entrambi i Mac all'hotspot di un telefono.
2. **Cavo diretto Thunderbolt Bridge**: provato e **non funzionante** con il cavo che avevamo, perché
   il Pro risultava "No device connected" su tutte le porte. Serve un cavo Thunderbolt 3/4 o USB4,
   non basta un USB-C da ricarica. Con il cavo giusto si usano gli IP manuali `10.0.0.1` (Air) e
   `10.0.0.2` (Pro).
3. **Ultima risorsa**: `LLM_PROVIDER=mock` nel `.env`, così la demo gira con le risposte registrate.

## Comandi utili (dalla root del repo, sul Pro)
```bash
KEY=$(grep '^LLM_API_KEY=' .env | cut -d= -f2-)
curl -s http://<IP>:1234/v1/models -H "Authorization: Bearer $KEY"
curl -N -s http://<IP>:1234/v1/chat/completions -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen/qwen3-30b-a3b-2507","stream":true,"messages":[{"role":"user","content":"Ciao"}]}'
```

## Da verificare
- Provider cloud di riserva (UE, per esempio Mistral API) per la demo dal vivo: non ancora deciso.
- Tenuta dell'Air sotto carico prolungato, visto che non ha ventola *(deduzione: rischio di rallentamenti per il calore)*.
- Il modello va bene sul caso d'uso vero solo una volta noto il brief.

## Collegamenti
- [Overview](../overview.md)
- [Ariete Tech Solutions](../entities/ariete-tech-solutions.md)
