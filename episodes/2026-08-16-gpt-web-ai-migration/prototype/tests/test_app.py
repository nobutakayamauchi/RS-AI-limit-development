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


def install_fake_openai(monkeypatch, captured, text="fixture response"):
    import types

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(output_text=text)

    class FakeOpenAI:
        def __init__(self, api_key):
            captured["api_key_received"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeOpenAI))


def test_model_call_path_uses_server_config(monkeypatch):
    module = load_module(monkeypatch)
    captured = {}
    install_fake_openai(monkeypatch, captured)
    monkeypatch.setenv("OPENAI_API_KEY", "server-secret")
    monkeypatch.setenv("WEB_AI_MODEL", "server-model")
    client = TestClient(module.app)
    res = client.post("/api/chat", json={
        "slug": "migration-fixture-ai",
        "message": "hello",
        "history": [{"role": "assistant", "content": "prior"}],
    })
    assert res.status_code == 200
    assert res.json()["text"] == "fixture response"
    assert captured["api_key_received"] == "server-secret"
    assert captured["model"] == "server-model"
    assert "BRIDGE-DOGFOOD-001" in captured["instructions"]
    assert captured["store"] is False
    assert captured["input"][-1] == {"role": "user", "content": "hello"}
    assert "tools" not in captured


def test_knowledge_binding_comes_from_server_env(monkeypatch):
    module = load_module(monkeypatch)
    captured = {}
    install_fake_openai(monkeypatch, captured)
    monkeypatch.setenv("OPENAI_API_KEY", "server-secret")
    monkeypatch.setenv("WEB_AI_MODEL", "server-model")
    monkeypatch.setenv("MIGRATION_FIXTURE_VECTOR_STORE_ID", "vs_server_only")
    module.registry.apps["migration-fixture-ai"]["knowledge"]["enabled"] = True
    client = TestClient(module.app)
    res = client.post("/api/chat", json={
        "slug": "migration-fixture-ai",
        "message": "knowledge question",
        "history": [],
    })
    assert res.status_code == 200
    assert captured["tools"] == [
        {"type": "file_search", "vector_store_ids": ["vs_server_only"]}
    ]
