"""Configurazione: percorsi e impostazioni lette dal file .env (se presente).

Gli altri moduli leggono sempre `config.NOME` al momento dell'uso (non lo copiano all'import),
così i test possono cambiare i valori, per esempio `RUNS_DIR`.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Provider LLM: "mock" (default: gratis e deterministico) oppure "openai_compat".
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

# Risposte registrate usate dal provider mock.
MOCK_SCENARI = Path(os.getenv("MOCK_SCENARI", ROOT / "esempio" / "dati" / "mock" / "scenari.json"))

# Dove finisce tutto lo stato generato: run, tracce, database della demo, email "inviate".
RUNS_DIR = Path(os.getenv("RUNS_DIR", ROOT / "runs"))
