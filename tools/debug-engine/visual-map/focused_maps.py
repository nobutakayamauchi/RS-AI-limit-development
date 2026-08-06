#!/usr/bin/env python3
"""Generate an overview map plus one focused map per source screen.

The focused maps are the readability fallback for dense navigation graphs. Each
page contains exactly one source screen and only the screens directly connected
to it, so overlapping lines cannot hide which button reaches which target.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import visual_map

DEFAULT_ACTION_THRESHOLD = 8
DEFAULT_OUTGOING_THRESHOLD = 3
DEFAULT_CROSSING_THRESHOLD = 2


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned or "screen"


def _target(action: dict[str, Any]) -> str | None:
    return action.get("observed_target") or action.get("expected_target")


def _segments(data: dict[str, Any]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    positions = visual_map._screen_positions(data)
    result: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for action in data["actions"]:
        target = _target(action)
        if target is None or target == action["source"]:
            continue
        sx, sy = positions[str(action["source"])]
        tx, ty = positions[str(target)]
        result.append(((sx, sy), (tx, ty)))
    return result


def _orientation(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> int:
    value = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    return 0 if value == 0 else (1 if value > 0 else 2)


def _crosses(first: tuple[tuple[int, int], tuple[int, int]], second: tuple[tuple[int, int], tuple[int, int]]) -> bool:
    a, b = first
    c, d = second
    if len({a, b, c, d}) < 4:
        return False
    return _orientation(a, b, c) != _orientation(a, b, d) and _orientation(c, d, a) != _orientation(c, d, b)


def _crossing_count(data: dict[str, Any]) -> int:
    segments = _segments(data)
    return sum(
        1
        for index, first in enumerate(segments)
        for second in segments[index + 1 :]
        if _crosses(first, second)
    )


def complexity(data: dict[str, Any]) -> dict[str, Any]:
    outgoing = Counter(str(action["source"]) for action in data["actions"])
    return {
        "action_count": len(data["actions"]),
        "max_outgoing": max(outgoing.values(), default=0),
        "crossing_count": _crossing_count(data),
        "outgoing_by_screen": dict(outgoing),
    }


def should_split(
    data: dict[str, Any],
    action_threshold: int = DEFAULT_ACTION_THRESHOLD,
    outgoing_threshold: int = DEFAULT_OUTGOING_THRESHOLD,
    crossing_threshold: int = DEFAULT_CROSSING_THRESHOLD,
) -> tuple[bool, list[str]]:
    score = complexity(data)
    reasons: list[str] = []
    if score["action_count"] >= action_threshold:
        reasons.append(f"接続総数 {score['action_count']} >= {action_threshold}")
    if score["max_outgoing"] >= outgoing_threshold:
        reasons.append(f"単一画面の最大接続数 {score['max_outgoing']} >= {outgoing_threshold}")
    if score["crossing_count"] >= crossing_threshold:
        reasons.append(f"推定交差数 {score['crossing_count']} >= {crossing_threshold}")
    return bool(reasons), reasons


def _focused_manifest(data: dict[str, Any], source_id: str) -> dict[str, Any]:
    screen_lookup = {str(screen["id"]): dict(screen) for screen in data["screens"]}
    actions = [dict(action) for action in data["actions"] if str(action["source"]) == source_id]
    target_ids: list[str] = []
    for action in actions:
        target = _target(action)
        if target is not None and str(target) != source_id and str(target) not in target_ids:
            target_ids.append(str(target))

    source = screen_lookup[source_id]
    source["x"] = 60
    source["y"] = 80 + max(0, len(target_ids) - 1) * 120
    screens = [source]
    for index, target_id in enumerate(target_ids):
        target = screen_lookup[target_id]
        target["x"] = 500
        target["y"] = 40 + index * 350
        screens.append(target)

    return {
        "title": f"{data.get('title', 'Navigation Map')} — {source.get('label', source_id)} の接続",
        "screens": screens,
        "actions": actions,
        "focus_source": source_id,
    }


def _index_html(title: str, overview_name: str, pages: list[tuple[str, str, int]], reasons: list[str]) -> str:
    reason_html = "".join(f"<li>{reason}</li>" for reason in reasons) or "<li>手動指定</li>"
    rows = "".join(
        f'<li><a href="{filename}">{label}</a><span>{count} connections</span></li>'
        for filename, label, count in pages
    )
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#101317;color:#eef2f5;margin:0;padding:24px;line-height:1.6}}a{{color:#70b7ff}}.card{{max-width:900px;margin:auto;background:#1b2129;border:1px solid #3b4653;border-radius:14px;padding:22px}}li{{margin:10px 0}}li span{{margin-left:12px;color:#9ba8b7;font-size:12px}}
</style></head><body><main class="card"><h1>{title}</h1><p><a href="{overview_name}">全体マップを開く</a></p><h2>分割理由</h2><ul>{reason_html}</ul><h2>画面別マップ</h2><ul>{rows}</ul></main></body></html>'''


def generate(
    manifest_path: Path,
    output_dir: Path,
    force_focused: bool = False,
    action_threshold: int = DEFAULT_ACTION_THRESHOLD,
    outgoing_threshold: int = DEFAULT_OUTGOING_THRESHOLD,
    crossing_threshold: int = DEFAULT_CROSSING_THRESHOLD,
) -> dict[str, Any]:
    data = visual_map._load_manifest(manifest_path)
    visual_map._validate(data)
    output_dir.mkdir(parents=True, exist_ok=True)

    overview = output_dir / "navigation-map-overview.html"
    overview.write_text(visual_map._render(data, manifest_path), encoding="utf-8")

    split, reasons = should_split(data, action_threshold, outgoing_threshold, crossing_threshold)
    pages: list[tuple[str, str, int]] = []
    if split or force_focused:
        screens = {str(screen["id"]): screen for screen in data["screens"]}
        sources = sorted({str(action["source"]) for action in data["actions"]})
        for source_id in sources:
            focused = _focused_manifest(data, source_id)
            filename = f"navigation-map-{_slug(source_id)}.html"
            (output_dir / filename).write_text(visual_map._render(focused, manifest_path), encoding="utf-8")
            label = str(screens[source_id].get("label", source_id))
            pages.append((filename, label, len(focused["actions"])))

    index = output_dir / "index.html"
    index.write_text(
        _index_html(str(data.get("title", "Navigation Map")), overview.name, pages, reasons),
        encoding="utf-8",
    )
    return {
        "split": split or force_focused,
        "reasons": reasons,
        "overview": str(overview),
        "index": str(index),
        "focused_pages": [str(output_dir / item[0]) for item in pages],
        "complexity": complexity(data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/navigation-maps"))
    parser.add_argument("--focused", action="store_true", help="always generate per-screen maps")
    parser.add_argument("--action-threshold", type=int, default=DEFAULT_ACTION_THRESHOLD)
    parser.add_argument("--outgoing-threshold", type=int, default=DEFAULT_OUTGOING_THRESHOLD)
    parser.add_argument("--crossing-threshold", type=int, default=DEFAULT_CROSSING_THRESHOLD)
    args = parser.parse_args()
    result = generate(
        args.manifest,
        args.output_dir,
        force_focused=args.focused,
        action_threshold=args.action_threshold,
        outgoing_threshold=args.outgoing_threshold,
        crossing_threshold=args.crossing_threshold,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
