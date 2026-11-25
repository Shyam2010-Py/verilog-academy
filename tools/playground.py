#!/usr/bin/env python3
"""Build the Verilog Playground page from verified example sources.

The page is a static workbench. It ships the original design and testbench
text, the actual Icarus transcript and a local compile/run workflow. It does
not compile or simulate user-entered Verilog in the browser.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "playground.json").read_text(encoding="utf-8"))
LABS = json.loads((ROOT / "data" / "labs.json").read_text(encoding="utf-8"))
EXAMPLE_ROOT = ROOT / "examples" / "playground"
PAGE_SOURCE = ROOT / "content" / "playground.html"

COMMANDS = (
    "# Compile the downloaded files\n"
    "iverilog -g2001 -o simulation.out design.v tb.v\n"
    "\n"
    "# Run the simulation image\n"
    "vvp simulation.out"
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"


def load_examples() -> list[dict]:
    examples = DATA.get("examples", [])
    if not isinstance(examples, list) or not examples:
        raise RuntimeError("data/playground.json must contain a non-empty examples list")

    loaded: list[dict] = []
    seen: set[str] = set()
    for item in examples:
        example_id = item.get("id", "")
        if not isinstance(example_id, str) or not re.fullmatch(r"[a-z0-9-]+", example_id):
            raise RuntimeError(f"Invalid playground example id: {example_id!r}")
        if example_id in seen:
            raise RuntimeError(f"Duplicate playground example id: {example_id}")
        seen.add(example_id)

        directory = EXAMPLE_ROOT / example_id
        design_path = directory / "design.v"
        tb_path = directory / "tb.v"
        expected_path = directory / "expected.txt"
        for path in (design_path, tb_path, expected_path):
            if not path.is_file():
                raise RuntimeError(
                    f"Missing playground file: {path.relative_to(ROOT)}"
                )

        expected = read_text(expected_path)
        match = re.search(r"PASS:\s*(\d+)/(\d+)", expected)
        checks = int(match.group(2)) if match else 0
        if checks <= 0:
            raise RuntimeError(f"No PASS summary found in {expected_path.relative_to(ROOT)}")

        loaded.append(
            {
                **item,
                "design_source": read_text(design_path),
                "tb_source": read_text(tb_path),
                "expected": expected,
                "checks": checks,
            }
        )
    return loaded


EXAMPLES = load_examples()
BY_ID = {item["id"]: item for item in EXAMPLES}
CATEGORIES = list(dict.fromkeys(item["category"] for item in EXAMPLES))
TOTAL_CHECKS = sum(item["checks"] for item in EXAMPLES)


def render_options() -> str:
    rows = []
    for index, item in enumerate(EXAMPLES, start=1):
        rows.append(
            f'<option value="{esc(item["id"])}">{index:02d} · {esc(item["title"])} — {esc(item["category"])}</option>'
        )
    return "\n            ".join(rows)


def render_cards() -> str:
    cards = []
    for index, item in enumerate(EXAMPLES, start=1):
        cards.append(
            f'<a class="pg-example-card panel" href="#workbench" data-select-example="{esc(item["id"])}">'
            '<span class="pg-example-card__head">'
            f'<span class="pg-example-card__num">{index:02d}</span>'
            f'<span class="badge badge-cyan">{esc(item["category"])}</span>'
            "</span>"
            f'<h3>{esc(item["title"])}</h3>'
            f'<p>{esc(item["summary"])}</p>'
            '<span class="pg-example-card__foot">'
            '<span class="pg-example-card__files"><code>design.v</code><span aria-hidden="true"> + </span><code>tb.v</code></span>'
            '<span class="pg-example-card__open">Open project'
            '<svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
            "</span>"
            "</span>"
            "</a>"
        )
    return "\n        ".join(cards)


def render_commands_block() -> str:
    return f"""<div class="code-block code-block--commands" data-copy-root>
                <div class="code-block__header">
                  <span class="code-block__file">Terminal</span>
                  <button class="copy-btn" type="button" aria-label="Copy local compile and run commands">
                    <svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>
                    <span class="copy-label">Copy</span>
                  </button>
                </div>
                <div class="code-block__body">
                  <pre><code>{esc(COMMANDS)}</code></pre>
                </div>
              </div>"""


def render_briefs() -> str:
    briefs = []
    for index, item in enumerate(EXAMPLES, start=1):
        hidden = "" if index == 1 else " hidden"
        statements = "".join(
            f'<li><code>{esc(statement["code"])}</code><span>{esc(statement["text"])}</span></li>'
            for statement in item.get("statements", [])
        )
        observations = "".join(f"<li>{esc(line)}</li>" for line in item.get("observations", []))
        mistakes = "".join(f"<li>{esc(line)}</li>" for line in item.get("mistakes", []))
        briefs.append(
            f'<article class="pg-brief" data-brief="{esc(item["id"])}"{hidden}>'
            '<div class="pg-brief__notes panel">'
            '<div class="pg-brief__head">'
            "<div>"
            f'<span class="eyebrow">{index:02d} / {esc(item["category"])}</span>'
            f'<h3>{esc(item["title"])}</h3>'
            "</div>"
            f'<span class="badge badge-violet">{esc(item["level"])}</span>'
            "</div>"
            f'<p class="pg-aim"><strong>Aim.</strong> {esc(item["aim"])}</p>'
            "<h4>How the circuit behaves</h4>"
            f'<p>{esc(item["operation"])}</p>'
            "<h4>Important statements</h4>"
            f'<ul class="pg-statement-list">{statements}</ul>'
            '<div class="pg-brief__grid">'
            f'<div><h4>What to observe</h4><ul class="pg-list">{observations}</ul></div>'
            f'<div><h4>Common mistakes</h4><ul class="pg-list pg-list--warning">{mistakes}</ul></div>'
            "</div>"
            f'<p class="pg-revision"><strong>Revision.</strong> {esc(item["revision"])}</p>'
            "</div>"
            '<div class="pg-brief__side">'
            '<section class="panel pg-command-panel">'
            '<span class="panel-kicker">Local commands</span>'
            "<h4>Compile and run</h4>"
            "<p>Download both files into one folder, open a terminal in that folder, and run:</p>"
            f"{render_commands_block()}"
            '<p class="pg-command-note">The downloads are always named <code>design.v</code> and <code>tb.v</code>. If you rename them, substitute the new names in both commands.</p>'
            "</section>"
            '<section class="panel pg-reference" data-reference data-copy-root>'
            '<div class="pg-reference__head">'
            '<div><span class="panel-kicker">Reference output</span><h4>Actual Icarus 13.0 transcript</h4></div>'
            '<div class="pg-reference__tools">'
            '<span class="badge badge-success" data-reference-badge>Verified original</span>'
            f'<button class="copy-btn" type="button" data-copy-target="#pg-output-{esc(item["id"])}" aria-label="Copy reference output">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>'
            '<span class="copy-label">Copy</span>'
            "</button>"
            "</div>"
            "</div>"
            '<p class="pg-reference__note" data-reference-note>Produced by compiling and running the original <code>design.v</code> and <code>tb.v</code> with Icarus Verilog 13.0. The output is not regenerated in the browser.</p>'
            f'<pre class="pg-output"><code id="pg-output-{esc(item["id"])}">{esc(item["expected"])}</code></pre>'
            "</section>"
            "</div>"
            "</article>"
        )
    return "\n      ".join(briefs)


def client_data() -> list[dict]:
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "level": item["level"],
            "summary": item["summary"],
            "design": item["design_source"],
            "testbench": item["tb_source"],
            "checks": item["checks"],
        }
        for item in EXAMPLES
    ]


def client_data_json() -> str:
    return json.dumps(client_data(), separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")


def render_page() -> str:
    source = PAGE_SOURCE.read_text(encoding="utf-8")
    replacements = {
        "{{PG_OPTIONS}}": render_options(),
        "{{PG_CARDS}}": render_cards(),
        "{{PG_BRIEFS}}": render_briefs(),
        "{{PG_COMMANDS}}": render_commands_block(),
        "{{PG_EXAMPLE_DATA}}": client_data_json(),
        "{{PG_EXAMPLE_COUNT}}": str(len(EXAMPLES)),
        "{{PG_FILE_COUNT}}": str(len(EXAMPLES) * 2),
        "{{PG_CATEGORY_COUNT}}": str(len(CATEGORIES)),
        "{{PG_CHECK_TOTAL}}": f"{TOTAL_CHECKS:,}",
        "{{PG_TOOL_VERSION}}": esc(LABS["toolchain"]["version"]),
        "{{PG_TOOL_MODE}}": esc(LABS["toolchain"]["mode"]),
    }
    for token, value in replacements.items():
        source = source.replace(token, value)
    return source
