"""Ciclo dell'agente, con pausa per l'approvazione umana.

    agente = Agente(provider, registry, system_prompt)
    run = agente.avvia("testo della richiesta", run_id="email-001")
    while run.stato == "in_attesa":          # c'è un'azione esterna da approvare
        print(run.in_attesa_di)               # ToolCall: nome del tool e argomenti
        run = agente.approva(run.id)          # oppure agente.rifiuta(run.id, "motivo")
    print(run.stato, run.risposta_finale)

Il ciclo: chiedi al modello → se vuole usare dei tool, eseguili (quelli esterni solo dopo
l'approvazione) → rimanda i risultati al modello → ripeti finché risponde senza tool.
Lo stato del run viene salvato su disco (runs/<id>.run.json) a ogni pausa e alla fine.
"""
import json
import time
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from core import config, trace
from core.llm import LLMProvider, Message, ToolCall
from core.tools import ToolRegistry

Stato = Literal["in_corso", "in_attesa", "completato", "errore"]


class Run(BaseModel):
    """Un'esecuzione dell'agente su una richiesta."""

    id: str
    stato: Stato = "in_corso"
    messaggi: list[Message] = Field(default_factory=list)
    da_eseguire: list[ToolCall] = Field(default_factory=list)  # tool chiesti dal modello, non ancora eseguiti
    passi: int = 0  # chiamate al modello fatte finora
    risposta_finale: str = ""
    errore: str = ""
    creato_il: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def in_attesa_di(self) -> ToolCall | None:
        """L'azione che aspetta l'approvazione (None se il run non è in attesa)."""
        return self.da_eseguire[0] if self.stato == "in_attesa" and self.da_eseguire else None


def salva_run(run: Run) -> None:
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    (config.RUNS_DIR / f"{run.id}.run.json").write_text(run.model_dump_json(indent=2), encoding="utf-8")


def carica_run(run_id: str) -> Run | None:
    percorso = config.RUNS_DIR / f"{run_id}.run.json"
    return Run.model_validate_json(percorso.read_text(encoding="utf-8")) if percorso.exists() else None


class Agente:
    def __init__(self, provider: LLMProvider, registry: ToolRegistry, system_prompt: str, max_passi: int = 12):
        self.provider = provider
        self.registry = registry
        self.system_prompt = system_prompt
        self.max_passi = max_passi  # protezione contro i loop infiniti

    def avvia(self, input_utente: str, run_id: str | None = None) -> Run:
        """Avvia un nuovo run. Se esiste già un run con lo stesso id, lo sostituisce."""
        run_id = run_id or f"run-{datetime.now():%Y%m%d-%H%M%S}"
        trace.cancella(run_id)
        run = Run(
            id=run_id,
            messaggi=[Message(role="system", content=self.system_prompt), Message(role="user", content=input_utente)],
        )
        trace.registra(run.id, "inizio", input=input_utente, provider=self.provider.name)
        return self._continua(run)

    def approva(self, run_id: str, argomenti: dict | None = None) -> Run:
        """Esegue l'azione in attesa (eventualmente con argomenti corretti dall'umano) e prosegue."""
        run = self._run_in_attesa(run_id)
        chiamata = run.da_eseguire.pop(0)
        nota = None
        if argomenti is not None and argomenti != chiamata.arguments:
            trace.registra(run.id, "modificato", tool=chiamata.name, prima=chiamata.arguments, dopo=argomenti)
            chiamata = chiamata.model_copy(update={"arguments": argomenti})
            nota = "L'utente ha modificato gli argomenti prima di approvare"
        trace.registra(run.id, "approvato", tool=chiamata.name, argomenti=chiamata.arguments)
        self._esegui(run, chiamata, nota=nota)
        run.stato = "in_corso"
        return self._continua(run)

    def rifiuta(self, run_id: str, motivo: str = "") -> Run:
        """Non esegue l'azione in attesa: il modello riceve il rifiuto (e il motivo) e decide come proseguire."""
        run = self._run_in_attesa(run_id)
        chiamata = run.da_eseguire.pop(0)
        trace.registra(run.id, "rifiutato", tool=chiamata.name, argomenti=chiamata.arguments, motivo=motivo)
        self._aggiungi_risultato(
            run, chiamata, {"esito": "rifiutato dall'utente", "motivo": motivo or "nessun motivo indicato"}
        )
        run.stato = "in_corso"
        return self._continua(run)

    # --- interno -------------------------------------------------------------------------

    def _run_in_attesa(self, run_id: str) -> Run:
        run = carica_run(run_id)
        if run is None or run.stato != "in_attesa":
            raise ValueError(f"Il run {run_id!r} non è in attesa di approvazione")
        return run

    def _continua(self, run: Run) -> Run:
        try:
            while True:
                if self._esegui_coda(run):
                    break  # in pausa: serve un'approvazione
                if run.passi >= self.max_passi:
                    run.stato, run.errore = "errore", f"Raggiunto il limite di {self.max_passi} passi"
                    trace.registra(run.id, "errore", messaggio=run.errore)
                    break
                inizio = time.perf_counter()
                risposta = self.provider.chat(run.messaggi, self.registry.schemas())
                run.passi += 1
                trace.registra(
                    run.id, "llm", testo=risposta.text,
                    tool_calls=[c.model_dump() for c in risposta.tool_calls], durata_ms=_ms(inizio),
                )
                run.messaggi.append(Message(role="assistant", content=risposta.text, tool_calls=risposta.tool_calls))
                if not risposta.tool_calls:
                    run.stato, run.risposta_finale = "completato", risposta.text
                    trace.registra(run.id, "fine", testo=risposta.text)
                    break
                run.da_eseguire = list(risposta.tool_calls)
        except Exception as e:  # noqa: BLE001 - errore del provider (rete, chiave, quota): il run si ferma, la UI no
            run.stato, run.errore = "errore", f"{type(e).__name__}: {e}"
            trace.registra(run.id, "errore", messaggio=run.errore)
        salva_run(run)
        return run

    def _esegui_coda(self, run: Run) -> bool:
        """Esegue i tool in coda. Restituisce True se si ferma su un'azione da approvare."""
        while run.da_eseguire:
            chiamata = run.da_eseguire[0]
            tool = self.registry.get(chiamata.name)
            if tool is not None and tool.external:
                errore = self.registry.controlla(chiamata)
                if errore is None:
                    run.stato = "in_attesa"
                    trace.registra(run.id, "in_attesa", tool=chiamata.name, argomenti=chiamata.arguments)
                    return True
                # Argomenti non validi: inutile disturbare l'umano, l'errore torna al modello.
                run.da_eseguire.pop(0)
                trace.registra(run.id, "tool", tool=chiamata.name, argomenti=chiamata.arguments, risultato=errore)
                self._aggiungi_risultato(run, chiamata, errore)
                continue
            run.da_eseguire.pop(0)
            self._esegui(run, chiamata)
        return False

    def _esegui(self, run: Run, chiamata: ToolCall, nota: str | None = None) -> None:
        inizio = time.perf_counter()
        risultato = self.registry.esegui(chiamata)
        if nota:
            risultato["nota"] = nota
        trace.registra(
            run.id, "tool", tool=chiamata.name, argomenti=chiamata.arguments, risultato=risultato, durata_ms=_ms(inizio)
        )
        self._aggiungi_risultato(run, chiamata, risultato)

    @staticmethod
    def _aggiungi_risultato(run: Run, chiamata: ToolCall, risultato: dict) -> None:
        contenuto = json.dumps(risultato, ensure_ascii=False, default=str)
        run.messaggi.append(Message(role="tool", tool_call_id=chiamata.id, content=contenuto))


def _ms(inizio: float) -> int:
    return round((time.perf_counter() - inizio) * 1000)
