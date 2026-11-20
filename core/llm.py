"""Livello LLM sostituibile: tipi comuni e scelta del provider.

Tutto il resto del codice parla con il modello solo tramite `provider.chat(messaggi, tools)`.
Per cambiare modello o fornitore si cambia il file .env, non il codice.
"""
from typing import Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel, Field

from core import config


class ToolCall(BaseModel):
    """Richiesta del modello di eseguire un tool."""

    id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:8]}")
    name: str
    arguments: dict = Field(default_factory=dict)


class Message(BaseModel):
    """Un messaggio della conversazione, in formato neutro (indipendente dal fornitore)."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)  # solo role="assistant"
    tool_call_id: str | None = None  # solo role="tool": a quale chiamata risponde


class LLMResponse(BaseModel):
    """Risposta del modello: testo, richieste di tool, o entrambi."""

    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)


class LLMProvider(Protocol):
    """Interfaccia che ogni provider implementa.

    `tools` è una lista di {"name", "description", "parameters" (JSON Schema)},
    prodotta da `ToolRegistry.schemas()`.
    """

    name: str

    def chat(self, messages: list[Message], tools: list[dict]) -> LLMResponse: ...


def get_provider() -> LLMProvider:
    """Crea il provider indicato da LLM_PROVIDER nel file .env."""
    if config.LLM_PROVIDER == "mock":
        from core.llm_mock import MockProvider

        return MockProvider(config.MOCK_SCENARI)
    if config.LLM_PROVIDER == "openai_compat":
        from core.llm_openai import OpenAICompatProvider

        return OpenAICompatProvider(config.LLM_BASE_URL, config.LLM_API_KEY, config.LLM_MODEL)
    raise ValueError(
        f"LLM_PROVIDER sconosciuto: {config.LLM_PROVIDER!r} (valori ammessi: mock, openai_compat)"
    )
