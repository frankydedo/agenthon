import pytest

from core import config


@pytest.fixture(autouse=True)
def runs_temporanei(tmp_path, monkeypatch):
    """Ogni test scrive run, tracce e database in una cartella temporanea, mai in runs/."""
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path / "runs")
    return tmp_path / "runs"
