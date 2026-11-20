"""Verifica end-to-end della demo con il provider mock. Da lanciare PRIMA DI OGNI MERGE.

    python scripts/demo_check.py

Elabora le email che hanno uno scenario registrato, approva tutte le azioni e controlla che
gestionale, posta inviata e traccia siano come previsto. Usa una cartella temporanea:
non tocca lo stato della UI in runs/. Esce con codice 0 se tutto va bene, 1 altrimenti.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import config, trace  # noqa: E402
from core.llm_mock import MockProvider  # noqa: E402
from esempio import connettori  # noqa: E402
from esempio.agente import crea_agente  # noqa: E402

# email -> (azioni da approvare attese, fatture nuove attese, pratiche nuove attese)
ATTESE = {
    "email-001": (["registra_fattura", "invia_email"], 1, 0),
    "email-002": (["crea_pratica", "invia_email"], 0, 1),
    "email-003": (["invia_email"], 0, 0),
    "email-004": (["crea_pratica", "invia_email"], 0, 1),
}


def main() -> bool:
    config.RUNS_DIR = Path(tempfile.mkdtemp(prefix="demo_check_"))
    connettori.reset_gestionale()
    agente = crea_agente(MockProvider(config.MOCK_SCENARI))
    problemi = []

    for email_id, (azioni_attese, fatture_attese, pratiche_attese) in ATTESE.items():
        fatture_prima = len(connettori.tabella("fatture"))
        pratiche_prima = len(connettori.tabella("pratiche"))

        run = agente.avvia(connettori.formatta_email(connettori.leggi_email(email_id)), run_id=email_id)
        approvate = []
        while run.stato == "in_attesa":
            approvate.append(run.in_attesa_di.name)
            run = agente.approva(run.id)

        eventi = trace.leggi(email_id)
        controlli = {
            "stato completato": run.stato == "completato",
            f"azioni approvate {azioni_attese}": approvate == azioni_attese,
            "fatture nuove": len(connettori.tabella("fatture")) - fatture_prima == fatture_attese,
            "pratiche nuove": len(connettori.tabella("pratiche")) - pratiche_prima == pratiche_attese,
            "nessun errore nei tool": not any("errore" in e["risultato"] for e in eventi if e["tipo"] == "tool"),
            "traccia da inizio a fine": eventi[0]["tipo"] == "inizio" and eventi[-1]["tipo"] == "fine",
        }
        falliti = [nome for nome, ok in controlli.items() if not ok]
        print(f"{'OK ' if not falliti else 'KO '} {email_id}  {run.stato:<11} approvate={approvate}")
        problemi += [f"{email_id}: {nome} (stato={run.stato}, errore={run.errore!r})" for nome in falliti]

    if len(connettori.email_inviate()) != len(ATTESE):
        problemi.append(f"email inviate: {len(connettori.email_inviate())}, attese {len(ATTESE)}")

    print("\nDEMO OK" if not problemi else "\nDEMO ROTTA:\n- " + "\n- ".join(problemi))
    return not problemi


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
