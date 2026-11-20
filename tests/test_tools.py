from typing import Annotated

from pydantic import Field

from core import trace
from core.llm import ToolCall
from core.tools import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def somma(a: int, b: Annotated[int, Field(description="secondo addendo")] = 0) -> int:
    """Somma due numeri."""
    return a + b


@registry.tool(external=True)
def invia(destinatario: str) -> dict:
    """Invia qualcosa."""
    return {"inviato_a": destinatario}


@registry.tool()
def rotto() -> None:
    """Solleva sempre un errore."""
    raise RuntimeError("guasto")


def test_schema_generato_dalla_firma():
    schema = registry.get("somma").schema()
    assert schema["name"] == "somma"
    assert schema["description"] == "Somma due numeri."
    assert schema["parameters"]["required"] == ["a"]
    assert schema["parameters"]["properties"]["b"]["description"] == "secondo addendo"
    assert "title" not in schema["parameters"]


def test_flag_external():
    assert registry.get("invia").external is True
    assert registry.get("somma").external is False


def test_esegue_e_converte_i_tipi():
    # "2" come stringa viene convertito in int da Pydantic
    assert registry.esegui(ToolCall(name="somma", arguments={"a": "2", "b": 3})) == {"risultato": 5}


def test_argomenti_non_validi_tornano_come_errore():
    risultato = registry.esegui(ToolCall(name="somma", arguments={"a": "due"}))
    assert risultato["errore"] == "Argomenti non validi"
    assert risultato["dettagli"][0]["campo"] == "a"


def test_argomenti_inventati_sono_rifiutati():
    risultato = registry.esegui(ToolCall(name="somma", arguments={"a": 1, "c": 2}))
    assert risultato["dettagli"][0]["campo"] == "c"


def test_tool_sconosciuto_ed_eccezioni_non_crashano():
    assert "Tool sconosciuto" in registry.esegui(ToolCall(name="boh"))["errore"]
    assert registry.esegui(ToolCall(name="rotto")) == {"errore": "RuntimeError: guasto"}


def test_traccia_scrive_e_rilegge():
    trace.registra("r1", "inizio", input="ciao")
    trace.registra("r1", "fine", testo="ok")
    eventi = trace.leggi("r1")
    assert [e["tipo"] for e in eventi] == ["inizio", "fine"]
    trace.cancella("r1")
    assert trace.leggi("r1") == []
