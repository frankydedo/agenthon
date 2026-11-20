"""Provider per qualsiasi API compatibile con il formato OpenAI "Chat Completions".

Con lo stesso codice si collegano, ad esempio: Google Gemini, Mistral (azienda UE),
Ollama o vLLM in locale (anche sul server del cliente, senza che i dati escano).
Cambiare fornitore = cambiare LLM_BASE_URL, LLM_API_KEY e LLM_MODEL nel file .env.
"""
import json

import httpx

from core.llm import LLMResponse, Message, ToolCall


class OpenAICompatProvider:
    name = "openai_compat"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        client: httpx.Client | None = None,
        timeout: float = 120.0,
    ):
        if not base_url or not model:
            raise ValueError("Per openai_compat imposta LLM_BASE_URL e LLM_MODEL nel file .env")
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = client or httpx.Client(timeout=timeout)

    def chat(self, messages: list[Message], tools: list[dict]) -> LLMResponse:
        payload: dict = {"model": self.model, "messages": [_a_formato_api(m) for m in messages]}
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        risposta = self._client.post(self.url, headers=self._headers, json=payload)
        risposta.raise_for_status()
        msg = risposta.json()["choices"][0]["message"]
        chiamate = []
        for c in msg.get("tool_calls") or []:
            dati = {"name": c["function"]["name"], "arguments": _leggi_argomenti(c["function"].get("arguments"))}
            if c.get("id"):
                dati["id"] = c["id"]
            chiamate.append(ToolCall(**dati))
        return LLMResponse(text=msg.get("content") or "", tool_calls=chiamate)


def _a_formato_api(m: Message) -> dict:
    """Converte un Message neutro nel formato atteso dall'API."""
    if m.role == "tool":
        return {"role": "tool", "tool_call_id": m.tool_call_id, "content": m.content}
    if m.tool_calls:
        return {
            "role": m.role,
            "content": m.content or None,
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.name, "arguments": json.dumps(c.arguments, ensure_ascii=False)},
                }
                for c in m.tool_calls
            ],
        }
    return {"role": m.role, "content": m.content}


def _leggi_argomenti(grezzi) -> dict:
    """Gli argomenti arrivano come stringa JSON. Se non è JSON valido, non crasha: l'errore di
    validazione tornerà al modello, che potrà correggersi."""
    if isinstance(grezzi, dict):
        return grezzi
    try:
        valore = json.loads(grezzi or "{}")
    except json.JSONDecodeError:
        return {"_json_non_valido": grezzi}
    return valore if isinstance(valore, dict) else {"_valore_non_oggetto": valore}
