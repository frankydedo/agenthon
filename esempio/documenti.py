"""Estrazione dei dati dalle fatture PDF: regola → modello → regola.

1. pdfplumber estrae il testo (deterministico, gratis).
2. Il modello capisce quale numero è il totale, quale la data, ecc. e compila lo schema `Fattura`.
3. Controlli deterministici (somme, partita IVA) segnalano gli errori, del documento o del modello.
"""
from datetime import date
from pathlib import Path

import pdfplumber
from pydantic import BaseModel, Field

from core.llm import LLMProvider
from core.structured import chiedi_strutturato

CARTELLA_DOCUMENTI = Path(__file__).parent / "dati" / "documenti"


class Fattura(BaseModel):
    numero: str
    data: date = Field(description="Data della fattura in formato AAAA-MM-GG")
    fornitore: str = Field(description="Ragione sociale di chi emette la fattura")
    partita_iva_fornitore: str = Field(description="Solo le 11 cifre")
    cliente: str = Field(description="Ragione sociale del destinatario")
    imponibile: float = Field(description="Numero con il punto decimale, es. 1250.00")
    iva: float
    totale: float


def percorso_documento(nome_file: str) -> Path:
    """Accetta solo file dentro la cartella dei documenti (niente '../' o percorsi assoluti)."""
    percorso = (CARTELLA_DOCUMENTI / nome_file).resolve()
    if percorso.parent != CARTELLA_DOCUMENTI.resolve() or not percorso.is_file():
        raise FileNotFoundError(f"Documento non trovato: {nome_file}")
    return percorso


def testo_pdf(percorso: Path) -> str:
    with pdfplumber.open(percorso) as pdf:
        return "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)


def partita_iva_valida(piva: str) -> bool:
    """Controllo della cifra di verifica della partita IVA italiana (11 cifre)."""
    if len(piva) != 11 or not piva.isdigit():
        return False
    somma = 0
    for i, c in enumerate(piva[:10]):
        cifra = int(c)
        if i % 2 == 1:  # posizioni pari (contando da 1): si raddoppia
            cifra *= 2
            if cifra > 9:
                cifra -= 9
        somma += cifra
    return (10 - somma % 10) % 10 == int(piva[10])


def verifica_fattura(f: Fattura) -> list[str]:
    """Controlli deterministici: restituisce la lista dei problemi trovati (vuota = tutto ok)."""
    avvisi = []
    if abs(f.imponibile + f.iva - f.totale) > 0.01:
        avvisi.append(
            f"Imponibile + IVA = {f.imponibile + f.iva:.2f} ma il totale indicato è {f.totale:.2f} "
            f"(differenza {f.totale - f.imponibile - f.iva:+.2f})"
        )
    if not partita_iva_valida(f.partita_iva_fornitore):
        avvisi.append(f"Partita IVA del fornitore non valida: {f.partita_iva_fornitore}")
    if f.data > date.today():
        avvisi.append(f"Data della fattura nel futuro: {f.data}")
    return avvisi


def estrai_fattura(provider: LLMProvider, nome_file: str) -> dict:
    testo = testo_pdf(percorso_documento(nome_file))
    fattura = chiedi_strutturato(
        provider,
        "Sei un assistente contabile. Estrai i dati dalla fattura italiana qui sotto. "
        "Converti gli importi dal formato italiano (1.234,56) a numero (1234.56) e la data in AAAA-MM-GG.",
        f"DOCUMENTO: {nome_file}\n\n{testo}",
        Fattura,
    )
    avvisi = verifica_fattura(fattura)
    return {"dati": fattura.model_dump(mode="json"), "controlli_superati": not avvisi, "avvisi": avvisi}
