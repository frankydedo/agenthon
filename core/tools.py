"""Registro dei tool: le funzioni Python che l'agente può chiamare.

    registry = ToolRegistry()

    @registry.tool()                    # sola lettura: eseguito subito
    def cerca_cliente(testo: str) -> list[dict]:
        "Cerca un cliente nel gestionale."     # la docstring è la descrizione che legge il modello
        ...

    @registry.tool(external=True)       # azione verso l'esterno: serve l'approvazione umana
    def invia_email(destinatario: str, oggetto: str, testo: str) -> dict:
        ...

Lo schema dei parametri (JSON Schema) viene generato dai type hint della funzione.
Per descrivere un parametro al modello: `testo: Annotated[str, Field(description="...")]`.
"""
import inspect
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, ValidationError, create_model

from core.llm import ToolCall


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., Any]
    params: type[BaseModel]  # modello Pydantic generato dalla firma della funzione
    external: bool  # True = agisce verso l'esterno, richiede approvazione

    def schema(self) -> dict:
        parametri = self.params.model_json_schema()
        _togli_titoli(parametri)
        return {"name": self.name, "description": self.description, "parameters": parametri}


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def tool(self, external: bool = False):
        """Decoratore che registra una funzione come tool."""

        def decoratore(func):
            self._tools[func.__name__] = Tool(
                name=func.__name__,
                description=inspect.getdoc(func) or "",
                func=func,
                params=_modello_parametri(func),
                external=external,
            )
            return func

        return decoratore

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict]:
        return [t.schema() for t in self._tools.values()]

    def controlla(self, call: ToolCall) -> dict | None:
        """Restituisce un errore (dict) se il tool non esiste o gli argomenti non sono validi."""
        tool = self.get(call.name)
        if tool is None:
            return {"errore": f"Tool sconosciuto: {call.name}. Disponibili: {', '.join(self._tools)}"}
        try:
            tool.params.model_validate(call.arguments)
        except ValidationError as e:
            return {"errore": "Argomenti non validi", "dettagli": _errori_leggibili(e)}
        return None

    def esegui(self, call: ToolCall) -> dict:
        """Esegue un tool e restituisce {"risultato": ...} oppure {"errore": ...}.

        Non solleva mai eccezioni: gli errori tornano al modello come dati, così può correggersi.
        """
        errore = self.controlla(call)
        if errore:
            return errore
        tool = self._tools[call.name]
        args = tool.params.model_validate(call.arguments)
        try:
            return {"risultato": tool.func(**{k: getattr(args, k) for k in tool.params.model_fields})}
        except Exception as e:  # noqa: BLE001 - qualsiasi errore del tool va restituito al modello
            return {"errore": f"{type(e).__name__}: {e}"}


def _modello_parametri(func) -> type[BaseModel]:
    """Crea un modello Pydantic dai parametri della funzione (tipi e valori di default)."""
    campi = {}
    for nome, p in inspect.signature(func, eval_str=True).parameters.items():
        tipo = p.annotation if p.annotation is not inspect.Parameter.empty else str
        default = p.default if p.default is not inspect.Parameter.empty else ...
        campi[nome] = (tipo, default)
    # extra="forbid": se il modello inventa un argomento che non esiste, è un errore.
    return create_model(f"{func.__name__}_parametri", __config__=ConfigDict(extra="forbid"), **campi)


def _errori_leggibili(e: ValidationError) -> list[dict]:
    return [{"campo": ".".join(map(str, err["loc"])) or "(input)", "problema": err["msg"]} for err in e.errors()]


def _togli_titoli(schema) -> None:
    """Rimuove i campi "title" generati da Pydantic: rumore inutile per il modello."""
    if isinstance(schema, dict):
        schema.pop("title", None)
        for chiave, valore in schema.items():
            if chiave == "properties":  # qui le chiavi sono nomi di parametri: non toccarle
                for sotto in valore.values():
                    _togli_titoli(sotto)
            else:
                _togli_titoli(valore)
    elif isinstance(schema, list):
        for sotto in schema:
            _togli_titoli(sotto)
