import importlib
import json
import sqlite3
import sys
import types
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def load_module(monkeypatch, tmp_path):
    monkeypatch.setenv("WEB_AI_CONFIG_DIR", str(ROOT / "apps"))
    monkeypatch.setenv("WEB_AI_PRICING_FILE", str(ROOT / "pricing.json"))
    monkeypatch.setenv("WEB_AI_LEDGER_PATH", str(tmp_path / "ledger.sqlite3"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MIGRATION_FIXTURE_BUDGET_ID", raising=False)
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def install_fake_openai(
    monkeypatch,
    captured,
    *,
    output_text="fixture response",
    input_tokens=100,
    output_tokens=20,
    fail=False,
):
    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            if fail:
                raise RuntimeError("boom")
            usage = types.SimpleNamespace(
                input_tokens=input_tokens, output_tokens=output_tokens
            )
            return types.SimpleNamespace(output_text=output_text, usage=usage)

    class FakeOpenAI:
        def __init__(self, api_key):
            captured["api_key_received"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=FakeOpenAI))


def test_health_and_public_config_do_not_expose_secret(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    client = TestClient(module.app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["pricing_version"] == "openai-2026-07-30"

    res = client.get("/apps/migration-fixture-ai/public-config")
    assert res.status_code == 200
    body = res.json()
    assert body["default_payer_mode"] == "BYOK"
    assert set(body["allowed_payer_modes"]) == {"BYOK", "PLATFORM_CREDIT"}
    assert "BRIDGE-DOGFOOD-001" not in res.text
    assert "OPENAI_API_KEY" not in res.text


def test_unknown_slug_is_explicit(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    client = TestClient(module.app)
    assert client.get("/apps/nope/public-config").status_code == 404


def test_byok_requires_user_key(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "BYOK",
        },
    )
    assert res.status_code == 402
    assert "BYOK" in res.json()["detail"]


def test_byok_uses_user_key_without_platform_debit(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    captured = {}
    install_fake_openai(monkeypatch, captured)
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        headers={"X-Provider-API-Key": "user-key"},
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "BYOK",
        },
    )
    assert res.status_code == 200
    assert captured["api_key_received"] == "user-key"
    assert captured["model"] == "gpt-5.6-luna"
    assert captured["store"] is False
    assert "BRIDGE-DOGFOOD-001" in captured["instructions"]
    meter = res.json()["meter"]
    assert meter["payer_mode"] == "BYOK"
    assert meter["charged_cost_usd_micros"] is None


def test_platform_credit_requires_budget_identity(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "platform-key")
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert res.status_code == 503
    assert "budget" in res.json()["detail"].lower()


def test_platform_credit_settles_usage_and_blocks_exhausted_budget(
    monkeypatch, tmp_path
):
    module = load_module(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "platform-key")
    monkeypatch.setenv("MIGRATION_FIXTURE_BUDGET_ID", "budget-1")
    module.registry.apps["migration-fixture-ai"]["billing"]["platform_credit"][
        "hard_limit_usd_micros"
    ] = 5000
    module.registry.apps["migration-fixture-ai"]["usage"]["max_output_tokens"] = 1000

    captured = {}
    install_fake_openai(monkeypatch, captured, input_tokens=100, output_tokens=20)
    client = TestClient(module.app)
    first = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert first.status_code == 200, first.text
    meter = first.json()["meter"]
    assert meter["payer_mode"] == "PLATFORM_CREDIT"
    assert meter["charged_cost_usd_micros"] > 0

    db = sqlite3.connect(tmp_path / "ledger.sqlite3")
    db.execute(
        "UPDATE budgets SET spent_micros=hard_limit_micros WHERE budget_id='budget-1'"
    )
    db.commit()
    db.close()

    second = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert second.status_code == 402
    assert "exhausted" in second.json()["detail"].lower()


def test_provider_failure_releases_platform_reservation(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "platform-key")
    monkeypatch.setenv("MIGRATION_FIXTURE_BUDGET_ID", "budget-2")
    captured = {}
    install_fake_openai(monkeypatch, captured, fail=True)
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert res.status_code == 502

    db = sqlite3.connect(tmp_path / "ledger.sqlite3")
    spent, reserved = db.execute(
        "SELECT spent_micros, reserved_micros FROM budgets WHERE budget_id='budget-2'"
    ).fetchone()
    db.close()
    assert spent == 0
    assert reserved == 0


def test_platform_credit_blocks_unknown_model_price(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "platform-key")
    monkeypatch.setenv("MIGRATION_FIXTURE_BUDGET_ID", "budget-3")
    app_cfg = module.registry.apps["migration-fixture-ai"]
    app_cfg["routing"]["default_model"] = "unknown-model"
    app_cfg["routing"]["allowed_models"].append("unknown-model")
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "hello",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert res.status_code == 503
    assert "price" in res.json()["detail"].lower()


def test_platform_credit_blocks_knowledge_without_cost_policy(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "platform-key")
    monkeypatch.setenv("MIGRATION_FIXTURE_BUDGET_ID", "budget-4")
    monkeypatch.setenv("MIGRATION_FIXTURE_VECTOR_STORE_ID", "vs-test")
    module.registry.apps["migration-fixture-ai"]["knowledge"]["enabled"] = True
    client = TestClient(module.app)
    res = client.post(
        "/api/chat",
        json={
            "slug": "migration-fixture-ai",
            "message": "knowledge question",
            "history": [],
            "payer_mode": "PLATFORM_CREDIT",
        },
    )
    assert res.status_code == 503
    assert "knowledge cost policy" in res.json()["detail"].lower()


def test_input_and_history_limits_still_apply_before_execution(monkeypatch, tmp_path):
    module = load_module(monkeypatch, tmp_path)
    client = TestClient(module.app)
    too_long = "x" * 12001
    res = client.post(
        "/api/chat",
        headers={"X-Provider-API-Key": "user-key"},
        json={
            "slug": "migration-fixture-ai",
            "message": too_long,
            "history": [],
            "payer_mode": "BYOK",
        },
    )
    assert res.status_code == 413

    history = [{"role": "user", "content": "x"}] * 13
    res = client.post(
        "/api/chat",
        headers={"X-Provider-API-Key": "user-key"},
        json={
            "slug": "migration-fixture-ai",
            "message": "ok",
            "history": history,
            "payer_mode": "BYOK",
        },
    )
    assert res.status_code == 413
