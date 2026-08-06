from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TAG_PATTERNS: dict[str, tuple[str, ...]] = {
    "DESTRUCTIVE_TEST": ("わざと", "意図的", "壊れないか", "破壊", "試した"),
    "ACCIDENTAL_MISUSE": ("間違えて", "意図せず", "うっかり", "誤操作"),
    "RECOVERY_TEST": ("戻る", "戻った", "再入場", "復帰", "再開", "再実行"),
    "STRESS_TEST": ("連打", "何度も", "繰り返", "長時間", "同時"),
    "STATE_MISMATCH": ("表示", "状態", "反映されない", "押せない", "無反応", "一致しない"),
    "DATA_LOSS_RISK": ("消え", "失われ", "保存されない", "飛んだ", "復元できない"),
    "HUMAN_ONLY": ("分かりにくい", "押しにくい", "違和感", "自然", "ストレス", "見苦しい"),
}

PURPOSE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("重複操作で二重実行されないこと", ("連打", "二重", "何度も押")),
    ("離脱・復帰後も状態を保持すること", ("戻る", "復帰", "再入場", "別画面")),
    ("表示と内部状態が一致すること", ("表示", "反映", "状態", "無反応")),
    ("編集内容・保存データを失わないこと", ("消え", "保存", "復元", "飛んだ")),
    ("エラー後に安全に再実行できること", ("エラー", "再実行", "やり直")),
    ("プレビューと最終成果物が一致すること", ("プレビュー", "最終", "書き出し")),
)


@dataclass(frozen=True)
class Classification:
    tags: list[str]
    confidence: dict[str, float]
    evidence: dict[str, list[str]]
    purposes: list[str]
    mixed_intent: bool


def _matches(text: str, patterns: Iterable[str]) -> list[str]:
    return [pattern for pattern in patterns if re.search(re.escape(pattern), text, re.IGNORECASE)]


def classify_report(text: str) -> Classification:
    if not text.strip():
        raise ValueError("report text must not be empty")

    tags: list[str] = []
    confidence: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}

    for tag, patterns in TAG_PATTERNS.items():
        hits = _matches(text, patterns)
        if hits:
            tags.append(tag)
            evidence[tag] = hits
            confidence[tag] = min(0.55 + 0.12 * len(hits), 0.95)

    if not tags:
        tags.append("NORMAL_FLOW")
        evidence["NORMAL_FLOW"] = ["破壊・誤操作を示す語がなく通常報告として扱った"]
        confidence["NORMAL_FLOW"] = 0.55

    purposes: list[str] = []
    for purpose, patterns in PURPOSE_PATTERNS:
        if _matches(text, patterns):
            purposes.append(purpose)

    mixed_intent = "ACCIDENTAL_MISUSE" in tags and "DESTRUCTIVE_TEST" in tags
    return Classification(tags, confidence, evidence, purposes, mixed_intent)


def build_scenario(text: str, result: Classification) -> dict:
    return {
        "source_report": text,
        "classification": asdict(result),
        "preconditions": [],
        "steps": [],
        "expected": result.purposes,
        "actual": [],
        "evidence_to_collect": [
            "operation_history",
            "screenshots_before_after",
            "console_logs",
            "network_logs",
            "visible_ui_state",
            "persistent_state",
        ],
        "automation_status": "NEEDS_SCENARIO_AUTHORING",
        "human_checks": [],
    }


def build_release_gate(project_name: str) -> dict:
    return {
        "project": project_name,
        "gate": "RELEASE_GATE",
        "blocking_automatic_checks": [
            "normal_flow",
            "repeated_input_single_accept",
            "leave_and_return_during_processing",
            "empty_state_guard",
            "save_exit_restore",
            "error_retry_idempotency",
            "preview_final_consistency",
        ],
        "human_test_program": [
            {
                "title": "初見導線",
                "precondition": "対象機能を初めて見る人が操作する",
                "action": "説明なしで主要導線を開始する",
                "observation": "次に押す操作を理解できるか",
                "pass": "重大な迷いなく完走できる",
            },
            {
                "title": "継続操作ストレス",
                "precondition": "同じ導線を3回以上利用する",
                "action": "主要作業を反復する",
                "observation": "毎回強いストレスになる操作がないか",
                "pass": "恒常的な苦痛・誤操作誘発がない",
            },
            {
                "title": "成果物の感覚品質",
                "precondition": "最終成果物が生成済み",
                "action": "実利用環境で最初から最後まで確認する",
                "observation": "見た目、音、同期、自然さ、違和感",
                "pass": "用途を妨げる違和感がない",
            },
        ],
        "decision": "BLOCK_UNTIL_EXECUTED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="限界開発式デバッグエンジン v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify", help="不具合報告を分類してシナリオJSONを作る")
    classify.add_argument("text")
    classify.add_argument("--output", type=Path)

    gate = sub.add_parser("release-gate", help="リリース前テストプログラムを生成する")
    gate.add_argument("project")
    gate.add_argument("--output", type=Path)

    args = parser.parse_args()
    payload = (
        build_scenario(args.text, classify_report(args.text))
        if args.command == "classify"
        else build_release_gate(args.project)
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
