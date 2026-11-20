"""L'agente dello scenario di prova: prompt di sistema + tool + collegamento ai connettori.

    from esempio.agente import crea_agente
    agente = crea_agente()            # usa il provider indicato nel .env (mock di default)
"""
from typing import Annotated

from pydantic import Field

from core.agent import Agente
from core.llm import LLMProvider, get_provider
from core.tools import ToolRegistry
from esempio import connettori, documenti

SYSTEM_PROMPT = """Sei l'assistente operativo dello "Studio Esempio - Commercialisti Associati" di Torino.
Ricevi una email alla volta arrivata nella casella dello studio e la gestisci dall'inizio alla fine.

Come lavori:
1. Capisci che tipo di richiesta è (registrazione fattura, adempimento fiscale, richiesta di
   appuntamento o di documenti, paghe, comunicazione non pertinente come pubblicità o spam).
2. Identifica il cliente con cerca_cliente (cerca per email del mittente, poi per nome).
3. Se ci sono fatture allegate, usa estrai_fattura. Se i controlli automatici segnalano problemi,
   NON registrare la fattura: apri una pratica di verifica e avvisa il cliente.
4. Esegui le azioni necessarie (registra_fattura, crea_pratica) e prepara la risposta con invia_email.
5. Se un'informazione manca o la richiesta è ambigua, non inventare: chiedi chiarimenti via email.
6. Per pubblicità e spam non fare nessuna azione.

Le azioni registra_fattura, crea_pratica e invia_email vengono approvate da una persona dello studio
prima di essere eseguite. Scrivi email cortesi e brevi, in italiano, firmate "Studio Esempio".
Alla fine rispondi con un riepilogo di 1-3 frasi di cosa hai fatto e perché."""


def crea_registry(provider: LLMProvider) -> ToolRegistry:
    registry = ToolRegistry()

    @registry.tool()
    def cerca_cliente(testo: Annotated[str, Field(description="Email, nome, referente o partita IVA")]) -> list[dict]:
        """Cerca un cliente dello studio nel gestionale. Restituisce una lista (vuota se nessun risultato)."""
        return connettori.cerca_clienti(testo)

    @registry.tool()
    def estrai_fattura(nome_file: Annotated[str, Field(description="Nome del file allegato, es. fattura.pdf")]) -> dict:
        """Legge una fattura PDF allegata ed estrae i dati, con controlli automatici su somme e partita IVA."""
        return documenti.estrai_fattura(provider, nome_file)

    @registry.tool(external=True)
    def registra_fattura(
        cliente_id: int,
        numero: str,
        data: Annotated[str, Field(description="AAAA-MM-GG")],
        fornitore: str,
        partita_iva_fornitore: str,
        imponibile: float,
        iva: float,
        totale: float,
    ) -> dict:
        """Registra una fattura passiva nella contabilità del cliente."""
        return connettori.registra_fattura(cliente_id, numero, data, fornitore, partita_iva_fornitore,
                                           imponibile, iva, totale)

    @registry.tool(external=True)
    def crea_pratica(
        cliente_id: int,
        tipo: Annotated[str, Field(description="Es. dichiarazione 730, verifica fattura, paghe, contenzioso")],
        descrizione: str,
    ) -> dict:
        """Apre una nuova pratica per il cliente nel gestionale dello studio."""
        return connettori.crea_pratica(cliente_id, tipo, descrizione)

    @registry.tool(external=True)
    def invia_email(destinatario: str, oggetto: str, testo: str) -> dict:
        """Invia una email dalla casella dello studio."""
        return connettori.invia_email(destinatario, oggetto, testo)

    return registry


def crea_agente(provider: LLMProvider | None = None) -> Agente:
    provider = provider or get_provider()
    return Agente(provider, crea_registry(provider), SYSTEM_PROMPT)
