import json

import httpx

from core.llm import Message, ToolCall
from core.llm_mock import MockProvider
from core.llm_openai import OpenAICompatProvider

SCENARI = [
    {
        "quando": "id=email-001",
        "risposte": [
            {"text": "Cerco.", "tool_calls": [{"name": "cerca_cliente", "arguments": {"testo": "Bianchi"}}]},
            {"text": "Fatto."},
        ],
    }
]


def test_mock_segue_lo_scenario_in_base_ai_messaggi_assistant():
    mock = MockProvider(SCENARI)
    conversazione = [Message(role="user", content="EMAIL id=email-001 ...")]

    prima = mock.chat(conversazione, tools=[])
    assert prima.tool_calls[0].name == "cerca_cliente"

    conversazione.append(Message(role="assistant", content=prima.text, tool_calls=prima.tool_calls))
    conversazione.append(Message(role="tool", tool_call_id=prima.tool_calls[0].id, content="[]"))
    assert mock.chat(conversazione, tools=[]).text == "Fatto."


def test_mock_senza_scenario_risponde_senza_errori():
    risposta = MockProvider(SCENARI).chat([Message(role="user", content="altro")], tools=[])
    assert risposta.text.startswith("[mock]")
    assert risposta.tool_calls == []


def test_adapter_openai_converte_richiesta_e_risposta():
    richieste = []

    def server_finto(request: httpx.Request) -> httpx.Response:
        richieste.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "abc",
                                    "type": "function",
                                    "function": {"name": "cerca_cliente", "arguments": '{"testo": "Rossi"}'},
                                }
                            ],
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatProvider(
        "https://esempio.invalid/v1", "chiave-finta", "modello-x",
        client=httpx.Client(transport=httpx.MockTransport(server_finto)),
    )
    storia = [
        Message(role="system", content="sei un assistente"),
        Message(role="user", content="ciao"),
        Message(role="assistant", tool_calls=[ToolCall(id="t1", name="f", arguments={"a": 1})]),
        Message(role="tool", tool_call_id="t1", content='{"risultato": 1}'),
    ]
    tools = [{"name": "cerca_cliente", "description": "d", "parameters": {"type": "object"}}]

    risposta = provider.chat(storia, tools)

    inviato = richieste[0]
    assert inviato["model"] == "modello-x"
    assert inviato["tools"][0] == {"type": "function", "function": tools[0]}
    assert inviato["messages"][2]["tool_calls"][0]["function"] == {"name": "f", "arguments": '{"a": 1}'}
    assert inviato["messages"][3] == {"role": "tool", "tool_call_id": "t1", "content": '{"risultato": 1}'}
    assert risposta.tool_calls == [ToolCall(id="abc", name="cerca_cliente", arguments={"testo": "Rossi"})]


def test_adapter_openai_non_crasha_con_argomenti_non_json():
    def server_finto(request):
        chiamata = {"id": "x", "type": "function", "function": {"name": "f", "arguments": "non json"}}
        return httpx.Response(200, json={"choices": [{"message": {"content": "", "tool_calls": [chiamata]}}]})

    provider = OpenAICompatProvider(
        "https://esempio.invalid/v1", "", "m", client=httpx.Client(transport=httpx.MockTransport(server_finto))
    )
    risposta = provider.chat([Message(role="user", content="x")], [])
    assert risposta.tool_calls[0].arguments == {"_json_non_valido": "non json"}
