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


def genera(client, email_id=None):
    return client.post("/api/simulazione/genera", json={"id": email_id})


def test_la_casella_parte_vuota_e_si_riempie_solo_con_genera(client):
    assert client.get("/api/richieste").json() == []
    assert client.get("/api/stato").json()["provider"] == "mock"
    sim = client.get("/api/simulazione").json()
    assert sim["sorgente"] and len(sim["disponibili"]) == sim["totale"] == 8

    assert genera(client).json()["id"] == "email-001"          # la prossima dell'elenco
    assert genera(client, "email-004").json()["id"] == "email-004"  # una scelta
    assert [r["id"] for r in client.get("/api/richieste").json()] == ["email-004", "email-001"]  # recente prima
    assert genera(client, "email-004").status_code == 409       # già arrivata
    assert len(client.get("/api/simulazione").json()["disponibili"]) == 6


def test_una_richiesta_non_arrivata_non_si_puo_elaborare(client):
    assert client.post("/api/richieste/email-001/elabora").status_code == 404
    assert client.get("/api/richieste/email-001").status_code == 404


def test_flusso_completo_con_approvazioni(client):
    genera(client, "email-001")
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
    genera(client, "email-003")
    client.post("/api/richieste/email-003/elabora")
    assert client.post("/api/richieste/email-003/rifiuta", json={"motivo": "no"}).status_code == 200
    # il run non è più in attesa: approvare ora è un conflitto
    assert client.post("/api/richieste/email-003/approva", json={}).status_code == 409
    assert client.get("/api/sistemi").json()["email_inviate"] == []


def test_richiesta_inesistente_e_reset(client):
    assert client.get("/api/richieste/email-999").status_code == 404
    genera(client, "email-001")
    client.post("/api/richieste/email-001/elabora")
    client.post("/api/reset")
    assert client.get("/api/richieste").json() == []  # la casella è di nuovo vuota


def test_info_agente_e_allegati(client):
    info = client.get("/api/agente").json()
    assert info["provider"] == "mock" and "Studio Esempio" in info["istruzioni"]
    esterni = {t["nome"] for t in info["strumenti"] if t["esterno"]}
    assert esterni == {"registra_fattura", "crea_pratica", "invia_email"}

    genera(client, "email-001")
    allegati = client.get("/api/richieste/email-001/allegati").json()
    assert allegati[0]["nome"] == "fattura_rossi_ottobre.pdf" and "2026/0457" in allegati[0]["testo"]
