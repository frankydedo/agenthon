import importlib.util
from pathlib import Path


def test_demo_end_to_end_con_mock():
    percorso = Path(__file__).resolve().parent.parent / "scripts" / "demo_check.py"
    spec = importlib.util.spec_from_file_location("demo_check", percorso)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    assert modulo.main() is True
