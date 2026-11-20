"""Connettori FINTI verso i sistemi dello studio: inbox, gestionale, posta in uscita.

Hanno la stessa forma che avrebbero quelli veri: per passare a Gmail o a un gestionale reale
si riscrive il corpo di queste funzioni, senza toccare l'agente né i tool.
Lo stato modificabile (database, email inviate) sta in runs/, così si resetta con un clic.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core import config

DATI = Path(__file__).parent / "dati"


# --- Inbox (sola lettura) -------------------------------------------------------------------

def elenca_email() -> list[dict]:
    return json.loads((DATI / "inbox.json").read_text(encoding="utf-8"))


def leggi_email(email_id: str) -> dict:
    for email in elenca_email():
        if email["id"] == email_id:
            return email
    raise KeyError(f"Email non trovata: {email_id}")


def formatta_email(email: dict) -> str:
    """Il testo che l'agente riceve come richiesta."""
    allegati = ", ".join(email.get("allegati", [])) or "nessuno"
    return (
        f"EMAIL id={email['id']}\nDa: {email['da']}\nData: {email['data']}\n"
        f"Oggetto: {email['oggetto']}\nAllegati: {allegati}\n\n{email['testo']}"
    )


# --- Gestionale (SQLite) --------------------------------------------------------------------

def _db_path() -> Path:
    return config.RUNS_DIR / "gestionale.db"


def reset_gestionale() -> None:
    """Ricrea il database dai dati di esempio."""
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    _db_path().unlink(missing_ok=True)
    with sqlite3.connect(_db_path()) as db:
        db.executescript((DATI / "gestionale_seed.sql").read_text(encoding="utf-8"))


def _db() -> sqlite3.Connection:
    if not _db_path().exists():
        reset_gestionale()
    db = sqlite3.connect(_db_path())
    db.row_factory = sqlite3.Row
    return db


def cerca_clienti(testo: str) -> list[dict]:
    """Cerca per nome, email, referente o partita IVA (ricerca parziale, senza maiuscole)."""
    filtro = f"%{testo.strip().lower()}%"
    with _db() as db:
        righe = db.execute(
            "SELECT * FROM clienti WHERE lower(nome) LIKE ? OR lower(email) LIKE ? "
            "OR lower(referente) LIKE ? OR partita_iva LIKE ?",
            (filtro, filtro, filtro, filtro),
        ).fetchall()
    return [dict(r) for r in righe]


def crea_pratica(cliente_id: int, tipo: str, descrizione: str) -> dict:
    with _db() as db:
        _verifica_cliente(db, cliente_id)
        cur = db.execute(
            "INSERT INTO pratiche (cliente_id, tipo, descrizione) VALUES (?, ?, ?)", (cliente_id, tipo, descrizione)
        )
        return dict(db.execute("SELECT * FROM pratiche WHERE id = ?", (cur.lastrowid,)).fetchone())


def registra_fattura(cliente_id: int, numero: str, data: str, fornitore: str, partita_iva_fornitore: str,
                     imponibile: float, iva: float, totale: float) -> dict:
    with _db() as db:
        _verifica_cliente(db, cliente_id)
        doppione = db.execute(
            "SELECT id FROM fatture WHERE numero = ? AND partita_iva_fornitore = ?", (numero, partita_iva_fornitore)
        ).fetchone()
        if doppione:
            raise ValueError(f"Fattura {numero} di {fornitore} già registrata (id {doppione['id']})")
        cur = db.execute(
            "INSERT INTO fatture (cliente_id, numero, data, fornitore, partita_iva_fornitore, imponibile, iva, totale) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (cliente_id, numero, data, fornitore, partita_iva_fornitore, imponibile, iva, totale),
        )
        return dict(db.execute("SELECT * FROM fatture WHERE id = ?", (cur.lastrowid,)).fetchone())


def tabella(nome: str) -> list[dict]:
    """Per la UI: tutte le righe di una tabella (clienti, pratiche, fatture)."""
    if nome not in {"clienti", "pratiche", "fatture"}:
        raise ValueError(nome)
    with _db() as db:
        return [dict(r) for r in db.execute(f"SELECT * FROM {nome} ORDER BY id DESC").fetchall()]


def _verifica_cliente(db: sqlite3.Connection, cliente_id: int) -> None:
    if not db.execute("SELECT 1 FROM clienti WHERE id = ?", (cliente_id,)).fetchone():
        raise ValueError(f"Cliente {cliente_id} inesistente")


# --- Posta in uscita (finta: scrive su file, non spedisce niente) ---------------------------

def _posta_path() -> Path:
    return config.RUNS_DIR / "posta_inviata.jsonl"


def invia_email(destinatario: str, oggetto: str, testo: str) -> dict:
    email = {"inviata_il": datetime.now().isoformat(timespec="seconds"),
             "destinatario": destinatario, "oggetto": oggetto, "testo": testo}
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    with _posta_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(email, ensure_ascii=False) + "\n")
    return {"esito": "inviata (simulazione)", "destinatario": destinatario}


def email_inviate() -> list[dict]:
    if not _posta_path().exists():
        return []
    with _posta_path().open(encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def reset_posta() -> None:
    _posta_path().unlink(missing_ok=True)
