"""Test del backend HTTP, sempre con il provider finto (mai il modello vero)."""
import pytest
from fastapi.testclient import TestClient

from api.main import crea_app
from core import config
from core.llm_mock import MockProvider
from esempio.agente import crea_agente


@pytest.fixture
def client():
    return TestClient(crea_app(crea_agente(MockProvider(config.MOCK_SCENARI))))


def test_elenco_e_stato(client):
    richieste = client.get("/api/richieste").json()
    assert len(richieste) == 8 and richieste[0]["stato"] is None
    assert client.get("/api/stato").json()["provider"] == "mock"


def test_flusso_completo_con_approvazioni(client):
    r = client.post("/api/richieste/email-001/elabora").json()
    assert r["run"]["stato"] == "in_attesa"
    assert r["run"]["in_attesa_di"]["name"] == "registra_fattura"
    assert "messaggi" not in r["run"]  # il prompt non esce dal backend

    assert client.post("/api/richieste/email-001/approva", json={}).json()["run"]["stato"] == "in_attesa"
    fine = client.post("/api/richieste/email-001/approva", json={}).json()
    assert fine["run"]["stato"] == "completato" and fine["run"]["risposta_finale"]
    assert [p["tipo"] for p in fine["passi"]][0] == "inizio"
    sistemi = client.get("/api/sistemi").json()
    assert len(sistemi["fatture"]) >= 1 and len(sistemi["email_inviate"]) == 1


def test_rifiuto_e_conflitto(client):
    client.post("/api/richieste/email-003/elabora")
    assert client.post("/api/richieste/email-003/rifiuta", json={"motivo": "no"}).status_code == 200
    # il run non è più in attesa: approvare ora è un conflitto
    assert client.post("/api/richieste/email-003/approva", json={}).status_code == 409
    assert client.get("/api/sistemi").json()["email_inviate"] == []


def test_richiesta_inesistente_e_reset(client):
    assert client.get("/api/richieste/email-999").status_code == 404
    client.post("/api/richieste/email-001/elabora")
    client.post("/api/reset")
    assert client.get("/api/richieste/email-001").json()["run"] is None
