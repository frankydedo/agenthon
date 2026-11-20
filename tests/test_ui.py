"""Smoke test della UI: simula i clic con streamlit.testing (nessun browser)."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

from esempio import connettori

APP = str(Path(__file__).resolve().parent.parent / "ui" / "app.py")


def test_ui_elabora_approva_e_completa():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception

    at.button(key="elabora-email-001").click().run()
    assert "In attesa di approvazione: registra_fattura" in [e.label.split(" ", 1)[1] for e in at.expander]

    at.button(key="approva-email-001").click().run()  # registra la fattura
    at.button(key="approva-email-001").click().run()  # invia l'email
    assert not at.exception
    assert any("Ho registrato la fattura" in s.value for s in at.success)
    assert len(connettori.email_inviate()) == 1


def test_ui_rifiuto():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button(key="elabora-email-003").click().run()
    at.button(key="rifiuta-email-003").click().run()
    assert not at.exception
    assert connettori.email_inviate() == []
