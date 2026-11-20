"""Rigenera i PDF di esempio in esempio/dati/documenti/.

    python esempio/dati/genera_pdf.py

I PDF sono già nel repo: serve solo se volete cambiarli o aggiungerne.
Nota: i font base di fpdf2 non hanno il simbolo dell'euro, quindi si usa "EUR".
"""
from pathlib import Path

from fpdf import FPDF

CARTELLA = Path(__file__).parent / "documenti"

FATTURE = [
    {
        "file": "fattura_rossi_ottobre.pdf",
        "fornitore": ["ROSSI FORNITURE SRL", "Via Garibaldi 12 - 10122 Torino (TO)", "P.IVA 12345670009"],
        "numero": "2026/0457",
        "data": "31/10/2026",
        "cliente": ["Bianchi Impianti di Marco Bianchi", "Via Nizza 88 - 10126 Torino (TO)", "P.IVA 24681350005"],
        "righe": [
            ("Cavo elettrico FG16 3x2,5 mmq (matassa 100 m)", "4", "185,00", "740,00"),
            ("Quadro elettrico IP65 12 moduli", "2", "140,00", "280,00"),
            ("Interruttore magnetotermico 2P 16A", "10", "23,00", "230,00"),
        ],
        "imponibile": "1.250,00",
        "iva": "275,00",
        "totale": "1.525,00",
        "pagamento": "Bonifico bancario a 30 giorni data fattura",
    },
    {
        # ATTENZIONE: totale volutamente sbagliato (3.400 + 748 = 4.148, non 4.184)
        # per mostrare il controllo automatico in demo.
        "file": "fattura_verdi_novembre.pdf",
        "fornitore": ["VERDI NOLEGGI SPA", "Corso Francia 210 - 10146 Torino (TO)", "P.IVA 76543210009"],
        "numero": "V-1182",
        "data": "14/11/2026",
        "cliente": ["Ferraro Costruzioni Srl", "Via Cigna 45 - 10152 Torino (TO)", "P.IVA 13579240006"],
        "righe": [
            ("Noleggio gru a torre 1-14 novembre", "1", "2.900,00", "2.900,00"),
            ("Trasporto e montaggio", "1", "500,00", "500,00"),
        ],
        "imponibile": "3.400,00",
        "iva": "748,00",
        "totale": "4.184,00",
        "pagamento": "RiBa 60 giorni fine mese",
    },
]


def genera(f: dict) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f["fornitore"][0], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    for riga in f["fornitore"][1:]:
        pdf.cell(0, 5, riga, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, f"FATTURA N. {f['numero']} del {f['data']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 5, "Spett.le", new_x="LMARGIN", new_y="NEXT")
    for riga in f["cliente"]:
        pdf.cell(0, 5, riga, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 10)
    larghezze = (100, 20, 35, 35)
    for testo, w in zip(("Descrizione", "Q.ta", "Prezzo unit.", "Importo"), larghezze):
        pdf.cell(w, 7, testo, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    for riga in f["righe"]:
        for testo, w in zip(riga, larghezze):
            pdf.cell(w, 7, testo, border=1)
        pdf.ln()
    pdf.ln(4)
    for etichetta, chiave in (("Imponibile", "imponibile"), ("IVA 22%", "iva"), ("TOTALE DOCUMENTO", "totale")):
        pdf.cell(155, 6, etichetta, align="R")
        pdf.cell(35, 6, f"{f[chiave]} EUR", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.cell(0, 5, f"Pagamento: {f['pagamento']}", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(CARTELLA / f["file"]))


if __name__ == "__main__":
    CARTELLA.mkdir(exist_ok=True)
    for fattura in FATTURE:
        genera(fattura)
        print("creato", CARTELLA / fattura["file"])
