import importlib
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def load_module(monkeypatch, tmp_path=None):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    if tmp_path is not None:
        monkeypatch.setenv("WEB_AI_CONFIG_DIR", str(tmp_path))
    else:
        monkeypatch.setenv("WEB_AI_CONFIG_DIR", str(ROOT / "apps"))
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def test_health_and_public_config(monkeypatch):
    module = load_module(monkeypatch)
    client = TestClient(module.app)
    assert client.get("/health").json()["status"] == "ok"
    public = client.get("/apps/migration-fixture-ai/public-config")
    assert public.status_code == 200
    assert "_instructions" not in public.text
    assert "BRIDGE-DOGFOOD-001" not in public.text


def test_unknown_slug_is_explicit(monkeypatch):
    module = load_module(monkeypatch)
    client = TestClient(module.app)
    assert client.get("/apps/nope/public-config").status_code == 404


def test_missing_api_key_is_bounded(monkeypatch):
    module = load_module(monkeypatch)
    client = TestClient(module.app)
    res = client.post("/api/chat", json={"slug": "migration-fixture-ai", "message": "hello", "history": []})
    assert res.status_code == 503
    assert res.json()["detail"] == "AI service is not configured"


def test_input_and_history_limits(monkeypatch):
    module = load_module(monkeypatch)
    client = TestClient(module.app)
    too_long = "x" * 12001
    res = client.post("/api/chat", json={"slug": "migration-fixture-ai", "message": too_long, "history": []})
    assert res.status_code == 413
    history = [{"role": "user", "content": "x"}] * 13
    res = client.post("/api/chat", json={"slug": "migration-fixture-ai", "message": "ok", "history": history})
    assert res.status_code == 413


def test_duplicate_slug_rejected(monkeypatch, tmp_path):
    instruction = ROOT / "apps" / "migration-fixture-ai.instructions.md"
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps({
            "slug": "same",
            "instructions_file": str(instruction.relative_to(ROOT))
        }), encoding="utf-8")
    monkeypatch.setenv("WEB_AI_CONFIG_DIR", str(tmp_path))
    sys.modules.pop("app", None)
    with pytest.raises(ValueError, match="duplicate slug"):
        importlib.import_module("app")
