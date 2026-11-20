from datetime import date

import pytest

from core import config
from core.llm_mock import MockProvider
from esempio import connettori, documenti
from esempio.documenti import Fattura


def test_partita_iva():
    assert documenti.partita_iva_valida("12345670009")
    assert not documenti.partita_iva_valida("12345670008")  # cifra di controllo sbagliata
    assert not documenti.partita_iva_valida("1234")


def test_testo_pdf():
    testo = documenti.testo_pdf(documenti.percorso_documento("fattura_rossi_ottobre.pdf"))
    assert "2026/0457" in testo and "1.525,00" in testo


def test_percorso_documento_non_esce_dalla_cartella():
    with pytest.raises(FileNotFoundError):
        documenti.percorso_documento("../inbox.json")


def test_verifica_fattura_trova_il_totale_sbagliato():
    f = Fattura(numero="1", data=date(2026, 11, 14), fornitore="X", partita_iva_fornitore="76543210009",
                cliente="Y", imponibile=3400, iva=748, totale=4184)
    avvisi = documenti.verifica_fattura(f)
    assert len(avvisi) == 1 and "4148.00" in avvisi[0]


def test_estrai_fattura_con_mock():
    risultato = documenti.estrai_fattura(MockProvider(config.MOCK_SCENARI), "fattura_verdi_novembre.pdf")
    assert risultato["dati"]["numero"] == "V-1182"
    assert risultato["controlli_superati"] is False


def test_gestionale_e_posta():
    assert connettori.cerca_clienti("BIANCHI")[0]["id"] == 1
    assert connettori.cerca_clienti("nessuno@example.it") == []

    pratica = connettori.crea_pratica(2, "dichiarazione 730", "test")
    assert pratica["stato"] == "aperta"
    with pytest.raises(ValueError):
        connettori.crea_pratica(999, "x", "cliente inesistente")

    args = (1, "N1", "2026-11-01", "Forn", "12345670009", 100.0, 22.0, 122.0)
    connettori.registra_fattura(*args)
    with pytest.raises(ValueError, match="già registrata"):
        connettori.registra_fattura(*args)

    connettori.invia_email("a@example.it", "ogg", "testo")
    assert connettori.email_inviate()[0]["destinatario"] == "a@example.it"
