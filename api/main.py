"""Backend HTTP dell'interfaccia web: espone il nucleo dell'agente via JSON e SSE.

    uvicorn api.main:app --reload --port 8000

Il contratto (endpoint e formato degli eventi) è in docs/contratto.md.
Non contiene logica dell'agente: chiama solo `core/` e `esempio/`.
"""
import asyncio
import json
import threading
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core import config, trace
from core.agent import Agente, Run, carica_run
from esempio import connettori, documenti
from esempio.agente import crea_agente

TABELLE = ("pratiche", "fatture", "clienti")

# Cosa simula il pulsante "Genera richiesta". Va cambiato insieme al dominio dopo il brief.
SORGENTE_SIMULATA = (
    "Email di clienti dello Studio Esempio (fatture, 730, richieste di documenti, posta indesiderata). "
    "In produzione arriverebbero dal server di posta dello studio; nella demo le facciamo arrivare noi."
)


class Generazione(BaseModel):
    id: str | None = None  # None = la prossima dell'elenco di prova


def _file_arrivate():
    return config.RUNS_DIR / "inbox_arrivate.json"


def _arrivate() -> list[dict]:
    """Le richieste "arrivate" finora: [{id, arrivata_il}], in ordine di arrivo."""
    f = _file_arrivate()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


class Approvazione(BaseModel):
    argomenti: dict[str, Any] | None = None  # None = approva così com'è


class Rifiuto(BaseModel):
    motivo: str = ""


def crea_app(agente: Agente | None = None) -> FastAPI:
    """Crea l'app. Nei test si passa un agente con provider finto."""
    app = FastAPI(title="Agente Studio - API")
    # Il frontend in sviluppo (Vite) gira su un'altra porta.
    app.add_middleware(
        CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"], allow_headers=["*"],
    )
    stato_app: dict[str, Any] = {"agente": agente}
    blocco = threading.Lock()

    def get_agente() -> Agente:
        with blocco:
            if stato_app["agente"] is None:
                stato_app["agente"] = crea_agente()
            return stato_app["agente"]

    def richiesta(email_id: str) -> dict:
        """Una richiesta esiste solo dopo essere stata generata (arrivata nella casella)."""
        if email_id not in {a["id"] for a in _arrivate()}:
            raise HTTPException(404, f"Richiesta {email_id!r} non ancora arrivata o inesistente")
        return connettori.leggi_email(email_id)

    @app.get("/api/stato")
    def stato() -> dict:
        runs = [carica_run(a["id"]) for a in _arrivate()]
        completati = [r for r in runs if r and r.stato == "completato"]
        tempi = [sum(ev.get("durata_ms", 0) for ev in trace.leggi(r.id)) for r in completati]
        return {
            "provider": get_agente().provider.name,
            "totale": len(runs),
            "disponibili": len(connettori.elenca_email()) - len(runs),
            "completate": len(completati),
            "da_approvare": [r.id for r in runs if r and r.stato == "in_attesa"],
            "tempo_medio_ms": round(sum(tempi) / len(tempi)) if tempi else None,
        }

    @app.get("/api/agente")
    def info_agente() -> dict:
        """Chi è l'agente: modello, istruzioni e strumenti. Serve alla schermata «Come ragiona»."""
        ag = get_agente()
        strumenti = []
        for sch in ag.registry.schemas():
            tool = ag.registry.get(sch["name"])
            strumenti.append({
                "nome": sch["name"], "descrizione": sch["description"], "esterno": bool(tool and tool.external),
                "parametri": list(sch["parameters"].get("properties", {}).keys()),
            })
        return {"provider": ag.provider.name, "istruzioni": ag.system_prompt, "strumenti": strumenti}

    @app.get("/api/richieste")
    def elenco() -> list[dict]:
        """Solo le richieste arrivate, dalla più recente."""
        out = []
        for a in reversed(_arrivate()):
            run = carica_run(a["id"])
            out.append({**connettori.leggi_email(a["id"]), "arrivata_il": a["arrivata_il"],
                        "stato": run.stato if run else None})
        return out

    @app.get("/api/simulazione")
    def simulazione() -> dict:
        """Cosa può ancora "arrivare" con il pulsante Genera richiesta."""
        arrivate = {a["id"] for a in _arrivate()}
        resto = [e for e in connettori.elenca_email() if e["id"] not in arrivate]
        return {
            "sorgente": SORGENTE_SIMULATA,
            "totale": len(connettori.elenca_email()),
            "disponibili": [{"id": e["id"], "da": e["da"], "oggetto": e["oggetto"]} for e in resto],
        }

    @app.post("/api/simulazione/genera")
    def genera(corpo: Generazione) -> dict:
        """Simula l'arrivo di una email nella casella dello studio."""
        arrivate = _arrivate()
        gia = {a["id"] for a in arrivate}
        resto = [e for e in connettori.elenca_email() if e["id"] not in gia]
        if not resto:
            raise HTTPException(409, "Sono già arrivate tutte le richieste di prova")
        scelta = resto[0]
        if corpo.id is not None:
            scelta = next((e for e in resto if e["id"] == corpo.id), None)
            if scelta is None:
                raise HTTPException(409, f"La richiesta {corpo.id!r} è già arrivata o non esiste")
        arrivate.append({"id": scelta["id"], "arrivata_il": datetime.now().isoformat(timespec="seconds")})
        config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
        _file_arrivate().write_text(json.dumps(arrivate, ensure_ascii=False), encoding="utf-8")
        return {**scelta, "arrivata_il": arrivate[-1]["arrivata_il"], "stato": None}

    @app.get("/api/richieste/{email_id}")
    def dettaglio(email_id: str) -> dict:
        return _dettaglio(richiesta(email_id))

    @app.get("/api/richieste/{email_id}/allegati")
    def allegati(email_id: str) -> list[dict]:
        """Il testo contenuto negli allegati PDF: ciò che l'agente legge davvero."""
        out = []
        for nome in richiesta(email_id).get("allegati", []):
            try:
                out.append({"nome": nome, "testo": documenti.testo_pdf(documenti.percorso_documento(nome))})
            except Exception as e:  # noqa: BLE001 - file mancante o non leggibile
                out.append({"nome": nome, "testo": "", "errore": f"{type(e).__name__}: {e}"})
        return out

    @app.post("/api/richieste/{email_id}/elabora")
    def elabora(email_id: str) -> dict:
        """Bloccante: ritorna quando il run finisce o si ferma in attesa di approvazione.
        I passi si seguono in diretta dallo stream mentre questa chiamata è in corso."""
        email = richiesta(email_id)
        get_agente().avvia(connettori.formatta_email(email), run_id=email_id)
        return _dettaglio(email)

    @app.post("/api/richieste/{email_id}/approva")
    def approva(email_id: str, corpo: Approvazione) -> dict:
        email = richiesta(email_id)
        try:
            get_agente().approva(email_id, corpo.argomenti)
        except ValueError as e:
            raise HTTPException(409, str(e)) from None
        return _dettaglio(email)

    @app.post("/api/richieste/{email_id}/rifiuta")
    def rifiuta(email_id: str, corpo: Rifiuto) -> dict:
        email = richiesta(email_id)
        try:
            get_agente().rifiuta(email_id, corpo.motivo)
        except ValueError as e:
            raise HTTPException(409, str(e)) from None
        return _dettaglio(email)

    @app.get("/api/richieste/{email_id}/stream")
    async def stream(email_id: str) -> StreamingResponse:
        """Server-Sent Events: manda la traccia esistente e poi ogni nuovo evento appena nasce.
        Resta aperto finché il client non si disconnette."""
        richiesta(email_id)

        async def eventi():
            inviati = 0
            while True:
                tutti = trace.leggi(email_id)
                if len(tutti) < inviati:  # la traccia è stata cancellata: nuova elaborazione
                    inviati = 0
                    yield "event: reset\ndata: {}\n\n"
                for ev in tutti[inviati:]:
                    yield f"event: passo\ndata: {json.dumps(ev, ensure_ascii=False)}\n\n"
                inviati = len(tutti)
                yield ": ping\n\n"
                await asyncio.sleep(0.3)

        return StreamingResponse(eventi(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/sistemi")
    def sistemi() -> dict:
        return {**{t: connettori.tabella(t) for t in TABELLE}, "email_inviate": connettori.email_inviate()}

    @app.post("/api/reset")
    def reset() -> dict:
        for p in list(config.RUNS_DIR.glob("*.run.json")) + list(config.RUNS_DIR.glob("*.trace.jsonl")):
            p.unlink()
        _file_arrivate().unlink(missing_ok=True)
        connettori.reset_gestionale()
        connettori.reset_posta()
        return {"ok": True}

    return app


def _dettaglio(email: dict) -> dict:
    run = carica_run(email["id"])
    return {"richiesta": email, "run": _run_pubblico(run), "passi": trace.leggi(email["id"])}


def _run_pubblico(run: Run | None) -> dict | None:
    """Solo ciò che serve alla UI: niente messaggi interni (prompt compreso)."""
    if run is None:
        return None
    chiamata = run.in_attesa_di
    return {
        "id": run.id, "stato": run.stato, "risposta_finale": run.risposta_finale, "errore": run.errore,
        "in_attesa_di": chiamata.model_dump() if chiamata else None,
    }


app = crea_app()
