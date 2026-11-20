from datetime import date

import pytest
from pydantic import BaseModel

from core import trace
from core.agent import Agente, carica_run
from core.llm_mock import MockProvider
from core.structured import chiedi_strutturato
from core.tools import ToolRegistry

eseguiti = []
registry = ToolRegistry()


@registry.tool()
def leggi(chiave: str) -> str:
    """Legge un valore."""
    eseguiti.append(("leggi", chiave))
    return f"valore di {chiave}"


@registry.tool(external=True)
def invia(destinatario: str, testo: str) -> dict:
    """Invia un messaggio."""
    eseguiti.append(("invia", destinatario))
    return {"inviato": True}


def chiamata(nome, **argomenti):
    return {"name": nome, "arguments": argomenti}


def agente_con(risposte, max_passi=12):
    eseguiti.clear()
    return Agente(MockProvider([{"quando": "", "risposte": risposte}]), registry, "sistema", max_passi=max_passi)


def test_lettura_poi_pausa_sull_azione_esterna():
    agente = agente_con([
        {"tool_calls": [chiamata("leggi", chiave="x")]},
        {"tool_calls": [chiamata("invia", destinatario="a@example.it", testo="ciao")]},
        {"text": "Fatto"},
    ])
    run = agente.avvia("richiesta", run_id="r1")

    assert run.stato == "in_attesa"
    assert run.in_attesa_di.name == "invia"
    assert eseguiti == [("leggi", "x")]  # l'invio NON è ancora avvenuto
    assert carica_run("r1").stato == "in_attesa"  # lo stato è salvato su disco


def test_approvazione_esegue_e_completa():
    agente = agente_con([
        {"tool_calls": [chiamata("invia", destinatario="a@example.it", testo="ciao")]},
        {"text": "Fatto"},
    ])
    agente.avvia("richiesta", run_id="r2")
    run = agente.approva("r2")

    assert eseguiti == [("invia", "a@example.it")]
    assert run.stato == "completato"
    assert run.risposta_finale == "Fatto"
    tipi = [e["tipo"] for e in trace.leggi("r2")]
    assert tipi == ["inizio", "llm", "in_attesa", "approvato", "tool", "llm", "fine"]


def test_approvazione_con_argomenti_modificati():
    agente = agente_con([
        {"tool_calls": [chiamata("invia", destinatario="sbagliato@example.it", testo="ciao")]},
        {"text": "Fatto"},
    ])
    agente.avvia("richiesta", run_id="r3")
    run = agente.approva("r3", {"destinatario": "giusto@example.it", "testo": "ciao"})

    assert eseguiti == [("invia", "giusto@example.it")]
    assert "modificato gli argomenti" in run.messaggi[-2].content  # il modello lo sa


def test_rifiuto_non_esegue_e_il_modello_lo_vede():
    agente = agente_con([
        {"tool_calls": [chiamata("invia", destinatario="a@example.it", testo="ciao")]},
        {"text": "Va bene, non invio."},
    ])
    agente.avvia("richiesta", run_id="r4")
    run = agente.rifiuta("r4", "tono sbagliato")

    assert eseguiti == []
    assert run.stato == "completato"
    assert "tono sbagliato" in run.messaggi[-2].content


def test_argomenti_non_validi_per_azione_esterna_non_chiedono_approvazione():
    agente = agente_con([
        {"tool_calls": [chiamata("invia", destinatario="a@example.it")]},  # manca "testo"
        {"text": "Mi correggo"},
    ])
    run = agente.avvia("richiesta", run_id="r5")
    assert run.stato == "completato"
    assert "Argomenti non validi" in run.messaggi[-2].content


def test_limite_di_passi():
    agente = agente_con([{"tool_calls": [chiamata("leggi", chiave="x")]}] * 5, max_passi=3)
    run = agente.avvia("richiesta", run_id="r6")
    assert run.stato == "errore"
    assert "limite" in run.errore


def test_errore_del_provider_non_fa_crashare():
    class ProviderRotto:
        name = "rotto"

        def chat(self, messages, tools):
            raise ConnectionError("rete assente")

    run = Agente(ProviderRotto(), registry, "s").avvia("x", run_id="r7")
    assert run.stato == "errore"
    assert "rete assente" in run.errore


def test_approvare_un_run_non_in_attesa_e_un_errore():
    agente = agente_con([{"text": "Fatto"}])
    agente.avvia("x", run_id="r8")
    with pytest.raises(ValueError):
        agente.approva("r8")


class Evento(BaseModel):
    titolo: str
    data: date


def test_output_strutturato_si_autocorregge():
    mock = MockProvider([{"quando": "", "risposte": [
        {"text": '{"titolo": "Riunione", "data": "15/10/2026"}'},  # formato data sbagliato
        {"text": '```json\n{"titolo": "Riunione", "data": "2026-10-15"}\n```'},
    ]}])
    evento = chiedi_strutturato(mock, "Estrai l'evento.", "Riunione il 15 ottobre", Evento)
    assert evento == Evento(titolo="Riunione", data=date(2026, 10, 15))


def test_output_strutturato_fallisce_dopo_i_tentativi():
    mock = MockProvider([{"quando": "", "risposte": [{"text": "boh"}, {"text": "boh"}]}])
    with pytest.raises(ValueError):
        chiedi_strutturato(mock, "Estrai.", "testo", Evento)
