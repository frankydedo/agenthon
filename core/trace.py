"""Traccia dei passi: ogni azione dell'agente diventa una riga JSON in runs/<run_id>.trace.jsonl.

Serve a tre cose: la timeline nella UI, l'audit (chi ha fatto cosa e perché), il debug.
I tipi di evento sono descritti in docs/contratto.md.
"""
import json
from datetime import datetime

from core import config


def _file(run_id: str):
    return config.RUNS_DIR / f"{run_id}.trace.jsonl"


def registra(run_id: str, tipo: str, **dati) -> dict:
    """Aggiunge un evento alla traccia del run e lo restituisce."""
    evento = {"ts": datetime.now().isoformat(timespec="milliseconds"), "run_id": run_id, "tipo": tipo, **dati}
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    with _file(run_id).open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False, default=str) + "\n")
    return evento


def leggi(run_id: str) -> list[dict]:
    percorso = _file(run_id)
    if not percorso.exists():
        return []
    with percorso.open(encoding="utf-8") as f:
        return [json.loads(riga) for riga in f if riga.strip()]


def cancella(run_id: str) -> None:
    _file(run_id).unlink(missing_ok=True)
