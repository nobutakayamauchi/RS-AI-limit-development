#!/usr/bin/env python3
"""Generate a single-file visual navigation map from a JSON manifest.

The output intentionally uses only Python's standard library and embedded
HTML/CSS/JavaScript so it can run in constrained limit-development setups.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

CARD_WIDTH = 300
CARD_HEIGHT = 300
IMAGE_HEIGHT = 190
PADDING = 40

STATUS_STYLE = {
    "confirmed": {"color": "#18864b", "dash": "", "label": "確認済み"},
    "mismatch": {"color": "#d32626", "dash": "", "label": "接続不一致"},
    "unknown": {"color": "#d29a00", "dash": "8 7", "label": "未確認"},
    "blocked": {"color": "#666666", "dash": "3 7", "label": "操作不能"},
}


def _load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data.get("screens"), list):
        raise ValueError("manifest must contain a screens array")
    if not isinstance(data.get("actions"), list):
        raise ValueError("manifest must contain an actions array")
    return data


def _validate(data: dict[str, Any]) -> None:
    ids = [str(screen.get("id", "")) for screen in data["screens"]]
    if any(not item for item in ids):
        raise ValueError("every screen requires a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("screen ids must be unique")

    id_set = set(ids)
    for action in data["actions"]:
        source = action.get("source")
        if source not in id_set:
            raise ValueError(f"unknown action source: {source}")
        for key in ("expected_target", "observed_target"):
            target = action.get(key)
            if target is not None and target not in id_set:
                raise ValueError(f"unknown {key}: {target}")
        status = action.get("status", "unknown")
        if status not in STATUS_STYLE:
            raise ValueError(f"unsupported action status: {status}")


def _screen_positions(data: dict[str, Any]) -> dict[str, tuple[int, int]]:
    positions: dict[str, tuple[int, int]] = {}
    for index, screen in enumerate(data["screens"]):
        fallback_x = PADDING + (index % 4) * 380
        fallback_y = PADDING + (index // 4) * 370
        positions[str(screen["id"])] = (
            int(screen.get("x", fallback_x)),
            int(screen.get("y", fallback_y)),
        )
    return positions


def _target_for_line(action: dict[str, Any]) -> str | None:
    status = action.get("status", "unknown")
    if status in {"mismatch", "blocked"}:
        return action.get("observed_target") or action.get("expected_target")
    return action.get("observed_target") or action.get("expected_target")


def _edge_path(source: tuple[int, int], target: tuple[int, int]) -> tuple[str, int, int]:
    sx = source[0] + CARD_WIDTH
    sy = source[1] + CARD_HEIGHT // 2
    tx = target[0]
    ty = target[1] + CARD_HEIGHT // 2

    if tx >= sx:
        distance = max(50, (tx - sx) // 2)
        path = f"M {sx} {sy} C {sx + distance} {sy}, {tx - distance} {ty}, {tx} {ty}"
    else:
        sx = source[0] + CARD_WIDTH // 2
        sy = source[1] + CARD_HEIGHT
        tx = target[0] + CARD_WIDTH // 2
        ty = target[1]
        bend = max(sy, ty) + 70
        path = f"M {sx} {sy} C {sx} {bend}, {tx} {bend}, {tx} {ty}"
    return path, (sx + tx) // 2, (sy + ty) // 2


def _safe_json(value: Any) -> str:
    return html.escape(json.dumps(value, ensure_ascii=False), quote=True)


def _render(data: dict[str, Any], manifest_path: Path) -> str:
    positions = _screen_positions(data)
    max_x = max((x for x, _ in positions.values()), default=0) + CARD_WIDTH + PADDING
    max_y = max((y for _, y in positions.values()), default=0) + CARD_HEIGHT + PADDING
    title = html.escape(str(data.get("title", "Navigation Map")))

    cards: list[str] = []
    for screen in data["screens"]:
        screen_id = str(screen["id"])
        x, y = positions[screen_id]
        label = html.escape(str(screen.get("label", screen_id)))
        section = html.escape(str(screen.get("section", "")))
        screenshot = str(screen.get("screenshot", "")).strip()
        if screenshot:
            # Keep source relative to the manifest's directory where possible.
            image_html = (
                f'<img src="{html.escape(screenshot, quote=True)}" '
                f'alt="{label} screenshot" loading="lazy">'
            )
        else:
            image_html = '<div class="missing">NO SCREENSHOT</div>'
        cards.append(
            f'''<article class="screen-card" id="screen-{html.escape(screen_id)}"
                style="left:{x}px;top:{y}px" data-screen-id="{html.escape(screen_id)}">
                <header><span>{section}</span><strong>{label}</strong></header>
                <div class="shot">{image_html}</div>
                <footer><code>{html.escape(screen_id)}</code></footer>
            </article>'''
        )

    edges: list[str] = []
    labels: list[str] = []
    action_rows: list[str] = []
    for action in data["actions"]:
        action_id = str(action.get("id", "unnamed-action"))
        source_id = str(action["source"])
        target_id = _target_for_line(action)
        status = str(action.get("status", "unknown"))
        style = STATUS_STYLE[status]
        kind = str(action.get("kind", "forward"))
        if kind == "return" and status == "confirmed":
            color = "#1769aa"
            dash = "8 6"
        else:
            color = style["color"]
            dash = style["dash"]

        detail = {
            "id": action_id,
            "label": action.get("label", action_id),
            "source": source_id,
            "expected_target": action.get("expected_target"),
            "observed_target": action.get("observed_target"),
            "status": status,
            "status_label": style["label"],
            "note": action.get("note", ""),
        }
        action_rows.append(
            "<tr data-status=\"{}\"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(status),
                html.escape(str(action.get("label", action_id))),
                html.escape(source_id),
                html.escape(str(action.get("expected_target") or "—")),
                html.escape(str(action.get("observed_target") or "—")),
                html.escape(style["label"]),
            )
        )

        if target_id is None:
            sx, sy = positions[source_id]
            start_x = sx + CARD_WIDTH
            start_y = sy + CARD_HEIGHT // 2
            end_x = start_x + 130
            end_y = start_y
            path = f"M {start_x} {start_y} L {end_x} {end_y}"
            mid_x, mid_y = (start_x + end_x) // 2, start_y
        else:
            path, mid_x, mid_y = _edge_path(positions[source_id], positions[target_id])

        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker = "arrow-blue" if kind == "return" and status == "confirmed" else f"arrow-{status}"
        edges.append(
            f'''<path class="edge edge-{html.escape(status)}" d="{path}"
                stroke="{color}"{dash_attr} marker-end="url(#{marker})"
                data-action="{_safe_json(detail)}" tabindex="0"/>'''
        )
        labels.append(
            f'''<g class="edge-label" transform="translate({mid_x},{mid_y})"
                data-action="{_safe_json(detail)}" tabindex="0">
                <rect x="-65" y="-15" width="130" height="30" rx="7"></rect>
                <text text-anchor="middle" dominant-baseline="central">{html.escape(str(action.get("label", action_id)))}</text>
            </g>'''
        )

    legend = "".join(
        f'<span><i style="background:{value["color"]}"></i>{value["label"]}</span>'
        for value in STATUS_STYLE.values()
    ) + '<span><i style="background:#1769aa"></i>戻る・復帰</span>'

    source_note = html.escape(str(manifest_path))
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light dark; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#101317; color:#eef2f5; }}
.topbar {{ position:sticky; top:0; z-index:20; background:#151a20ee; backdrop-filter:blur(12px); padding:14px 18px; border-bottom:1px solid #303741; }}
h1 {{ font-size:20px; margin:0 0 10px; }}
.controls {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
.controls button {{ border:1px solid #47515d; border-radius:8px; background:#202731; color:#fff; padding:8px 12px; }}
.legend {{ display:flex; gap:14px; flex-wrap:wrap; font-size:12px; }}
.legend span {{ display:flex; align-items:center; gap:5px; }}
.legend i {{ width:18px; height:4px; border-radius:3px; display:inline-block; }}
.viewport {{ overflow:auto; min-height:70vh; background-image:linear-gradient(#252a31 1px,transparent 1px),linear-gradient(90deg,#252a31 1px,transparent 1px); background-size:24px 24px; }}
.canvas {{ position:relative; width:{max_x}px; height:{max_y}px; transform-origin:0 0; }}
svg {{ position:absolute; inset:0; width:100%; height:100%; overflow:visible; z-index:2; pointer-events:none; }}
.edge {{ fill:none; stroke-width:4; pointer-events:stroke; cursor:pointer; opacity:.92; }}
.edge:hover,.edge:focus {{ stroke-width:8; outline:none; }}
.edge-label {{ cursor:pointer; pointer-events:all; }}
.edge-label rect {{ fill:#151a20; stroke:#596474; }}
.edge-label text {{ fill:#eef2f5; font-size:11px; }}
.screen-card {{ position:absolute; width:{CARD_WIDTH}px; height:{CARD_HEIGHT}px; background:#1b2129; border:2px solid #47515d; border-radius:14px; overflow:hidden; z-index:5; box-shadow:0 12px 30px #0008; }}
.screen-card header {{ height:58px; display:flex; flex-direction:column; justify-content:center; padding:8px 12px; border-bottom:1px solid #343d48; }}
.screen-card header span {{ font-size:11px; color:#9ba8b7; }}
.screen-card header strong {{ font-size:17px; }}
.shot {{ height:{IMAGE_HEIGHT}px; background:#0d0f12; display:grid; place-items:center; overflow:hidden; }}
.shot img {{ width:100%; height:100%; object-fit:contain; }}
.missing {{ color:#697381; font-size:13px; letter-spacing:.12em; }}
.screen-card footer {{ padding:8px 12px; color:#a8b4c2; }}
.details {{ display:grid; grid-template-columns:minmax(260px,420px) 1fr; border-top:1px solid #303741; min-height:260px; }}
.inspector {{ padding:16px; border-right:1px solid #303741; white-space:pre-wrap; }}
.inspector h2,.table-wrap h2 {{ margin:0 0 10px; font-size:16px; }}
.inspector pre {{ font-size:12px; line-height:1.55; overflow:auto; }}
.table-wrap {{ padding:16px; overflow:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:12px; }}
th,td {{ text-align:left; padding:8px; border-bottom:1px solid #303741; }}
tr[data-status="mismatch"] {{ background:#5a151555; }}
tr[data-status="unknown"] {{ background:#5a450d55; }}
tr[data-status="blocked"] {{ background:#4446; }}
.meta {{ color:#9ba8b7; font-size:11px; margin-top:8px; }}
@media (max-width:800px) {{ .details {{ grid-template-columns:1fr; }} .inspector {{ border-right:0; border-bottom:1px solid #303741; }} }}
</style>
</head>
<body>
<section class="topbar">
  <h1>{title}</h1>
  <div class="controls">
    <button id="zoom-out">−</button><button id="zoom-reset">100%</button><button id="zoom-in">＋</button>
    <div class="legend">{legend}</div>
  </div>
  <div class="meta">source: {source_note}</div>
</section>
<div class="viewport" id="viewport"><div class="canvas" id="canvas">
<svg viewBox="0 0 {max_x} {max_y}" aria-label="navigation links">
<defs>
  <marker id="arrow-confirmed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#18864b"/></marker>
  <marker id="arrow-mismatch" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#d32626"/></marker>
  <marker id="arrow-unknown" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#d29a00"/></marker>
  <marker id="arrow-blocked" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#666"/></marker>
  <marker id="arrow-blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#1769aa"/></marker>
</defs>
{''.join(edges)}
{''.join(labels)}
</svg>
{''.join(cards)}
</div></div>
<section class="details">
  <aside class="inspector"><h2>選択した接続</h2><pre id="inspector">線または操作ラベルを選択してください。</pre></aside>
  <div class="table-wrap"><h2>接続一覧</h2><table><thead><tr><th>操作</th><th>起点</th><th>期待</th><th>実測</th><th>状態</th></tr></thead><tbody>{''.join(action_rows)}</tbody></table></div>
</section>
<script>
const canvas = document.getElementById('canvas');
const inspector = document.getElementById('inspector');
let zoom = 1;
function applyZoom() {{ canvas.style.transform = `scale(${{zoom}})`; canvas.parentElement.style.height = `${{canvas.offsetHeight * zoom}}px`; document.getElementById('zoom-reset').textContent = `${{Math.round(zoom*100)}}%`; }}
document.getElementById('zoom-in').onclick = () => {{ zoom = Math.min(2, zoom + .1); applyZoom(); }};
document.getElementById('zoom-out').onclick = () => {{ zoom = Math.max(.3, zoom - .1); applyZoom(); }};
document.getElementById('zoom-reset').onclick = () => {{ zoom = 1; applyZoom(); }};
function inspect(element) {{
  const raw = element.dataset.action;
  if (!raw) return;
  const value = JSON.parse(raw);
  inspector.textContent = [
    `操作: ${{value.label}}`,
    `起点: ${{value.source}}`,
    `期待接続先: ${{value.expected_target ?? '未定義'}}`,
    `実測接続先: ${{value.observed_target ?? '未確認'}}`,
    `状態: ${{value.status_label}} (${{value.status}})`,
    value.note ? `メモ: ${{value.note}}` : ''
  ].filter(Boolean).join('\n');
}}
document.querySelectorAll('[data-action]').forEach(el => {{
  el.addEventListener('click', () => inspect(el));
  el.addEventListener('keydown', event => {{ if (event.key === 'Enter' || event.key === ' ') inspect(el); }});
}});
applyZoom();
</script>
</body>
</html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="input JSON manifest")
    parser.add_argument("--output", type=Path, default=Path("navigation-map.html"))
    args = parser.parse_args()

    data = _load_manifest(args.manifest)
    _validate(data)
    output = _render(data, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
