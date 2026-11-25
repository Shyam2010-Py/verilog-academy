#!/usr/bin/env python3
"""Verify the Verilog Playground without a browser.

Checks the canonical metadata, the source and transcript files, the generated
page, the client data payload and the local-first safety rules. Compilation and
simulation are covered separately by tools/verify_examples.py.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "playground.json"
EXAMPLE_ROOT = ROOT / "examples" / "playground"
PAGE_PATH = ROOT / "playground" / "index.html"
SCRIPT_PATH = ROOT / "js" / "playground.js"
STYLE_PATH = ROOT / "css" / "playground.css"
SITE_PATH = ROOT / "data" / "site.json"

REQUIRED_TEXT = ("id", "title", "category", "level", "summary", "aim", "operation", "revision")
REQUIRED_LISTS = ("statements", "observations", "mistakes")
EXPECTED_COUNT = 14
MAX_EDITOR_BYTES = 60_000

failures: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main() -> int:
    check(DATA_PATH.is_file(), "data/playground.json is missing")
    if not DATA_PATH.is_file():
        report()
        return 1

    data = json.loads(read(DATA_PATH))
    examples = data.get("examples", [])
    check(data.get("version") == 1, "data/playground.json version must be 1")
    check(isinstance(examples, list), "examples must be a list")
    check(len(examples) == EXPECTED_COUNT, f"expected {EXPECTED_COUNT} examples, found {len(examples)}")

    site = json.loads(read(SITE_PATH))
    check(
        site.get("counts", {}).get("playground") == len(examples),
        "site.json counts.playground does not match data/playground.json",
    )

    ids: list[str] = []
    categories: list[str] = []
    total_checks = 0

    for index, item in enumerate(examples, start=1):
        label = item.get("id", f"#{index}")
        check(bool(re.fullmatch(r"[a-z0-9-]+", str(item.get("id", "")))), f"{label}: invalid id")
        check(str(item.get("id")) not in ids, f"{label}: duplicate id")
        ids.append(str(item.get("id")))

        for key in REQUIRED_TEXT:
            value = item.get(key)
            check(isinstance(value, str) and value.strip(), f"{label}: missing {key}")
        for key in REQUIRED_LISTS:
            value = item.get(key)
            check(isinstance(value, list) and len(value) >= 2, f"{label}: {key} needs at least two entries")

        statements = item.get("statements", [])
        for statement in statements:
            check(
                isinstance(statement, dict)
                and isinstance(statement.get("code"), str)
                and isinstance(statement.get("text"), str),
                f"{label}: malformed statement entry",
            )

        categories.append(str(item.get("category")))
        check(item.get("level") in {"Foundation", "Intermediate", "Advanced"}, f"{label}: unknown level")

        directory = EXAMPLE_ROOT / str(item.get("id"))
        design_path = directory / "design.v"
        tb_path = directory / "tb.v"
        expected_path = directory / "expected.txt"
        for path in (design_path, tb_path, expected_path):
            check(path.is_file(), f"{label}: missing {path.relative_to(ROOT)}")

        if not (design_path.is_file() and tb_path.is_file() and expected_path.is_file()):
            continue

        design = read(design_path)
        testbench = read(tb_path)
        expected = read(expected_path)

        check("module " in design, f"{label}: design.v has no module")
        check("endmodule" in design, f"{label}: design.v has no endmodule")
        check("$finish" in testbench, f"{label}: tb.v does not finish the simulation")
        check("PASS" in expected, f"{label}: expected.txt has no PASS line")
        check("FAIL" not in expected, f"{label}: expected.txt reports a failure")
        check("$finish called at" in expected, f"{label}: expected.txt lacks the Icarus finish line")

        match = re.search(r"PASS:\s*(\d+)/(\d+)", expected)
        check(match is not None, f"{label}: expected.txt has no x/y PASS summary")
        if match:
            passed, total = int(match.group(1)), int(match.group(2))
            check(passed == total, f"{label}: PASS summary is not complete ({passed}/{total})")
            total_checks += total

        check(
            len(design.encode("utf-8")) < MAX_EDITOR_BYTES
            and len(testbench.encode("utf-8")) < MAX_EDITOR_BYTES,
            f"{label}: source file is unexpectedly large",
        )

    check(len(set(categories)) >= 4, "examples should cover at least four categories")

    check(PAGE_PATH.is_file(), "playground/index.html is missing")
    if PAGE_PATH.is_file():
        page = read(PAGE_PATH)
        check("{{" not in page, "generated page contains an unreplaced template token")
        check("js/playground.js" in page, "page does not load js/playground.js")
        check("css/playground.css" in page, "page does not load css/playground.css")
        check("id=\"playground-data\"" in page, "page is missing the client data block")
        check("data-example-select" in page, "page is missing the example selector")
        check(page.count('data-brief="') == len(examples), "brief count does not match example count")
        check(page.count('data-select-example="') == len(examples), "library card count does not match")
        check(page.count("<option value=") == len(examples), "selector option count does not match")
        check("va.playground.drafts" in page, "page does not explain the draft storage key")
        check("va.progress" in page, "page does not explain that progress is untouched")
        check("Icarus Verilog 13.0" in page, "page does not name the verified toolchain")
        check("Original only" in page, "page is missing the edited-example notice")
        check("no fake run button" in page.lower(), "page does not state the no-Run-button boundary")
        check("Playground" in page, "page navigation does not include Playground")

        # Each reference transcript must be embedded exactly once, escaped.
        for item in examples:
            label = item.get("id")
            expected_path = EXAMPLE_ROOT / str(label) / "expected.txt"
            if not expected_path.is_file():
                continue
            expected = read(expected_path)
            check(
                html.escape(expected, quote=True) in page,
                f"{label}: reference transcript is not embedded verbatim",
            )

        try:
            payload = re.search(
                r'<script type="application/json" id="playground-data">(.*?)</script>',
                page,
                re.S,
            )
            check(payload is not None, "client data block is not readable")
            client = json.loads(payload.group(1).replace("<\\/", "</")) if payload else []
            check(len(client) == len(examples), "client data does not contain every example")
            for item, source in zip(client, examples):
                label = item.get("id")
                directory = EXAMPLE_ROOT / str(label)
                check(item.get("title") == source.get("title"), f"{label}: client title mismatch")
                check(
                    item.get("design") == read(directory / "design.v"),
                    f"{label}: client design source mismatch",
                )
                check(
                    item.get("testbench") == read(directory / "tb.v"),
                    f"{label}: client testbench source mismatch",
                )
                check(item.get("checks", 0) > 0, f"{label}: client checks are missing")
        except (json.JSONDecodeError, AttributeError) as error:
            check(False, f"client data is not valid JSON: {error}")

    check(SCRIPT_PATH.is_file(), "js/playground.js is missing")
    if SCRIPT_PATH.is_file():
        script = read(SCRIPT_PATH)
        check('const DRAFT_KEY = "va.playground.drafts"' in script, "draft key is not the documented key")
        check("va.progress" not in script, "playground.js must not touch va.progress")
        check("progress.js" not in script, "playground.js must not import the progress engine")
        check("eval(" not in script and "new Function" not in script, "playground.js must not evaluate user code")
        check("innerHTML" not in script, "playground.js must not inject HTML")
        check("document.execCommand(\"copy\")" in script, "copy fallback is missing")
        check("navigator.clipboard" in script, "clipboard API path is missing")
        check("URL.createObjectURL" in script, "download path is missing")
        check('download("design.v"' in script, "design.v download is missing")
        check('download("tb.v"' in script, "tb.v download is missing")
        check("localStorage" in script, "draft persistence is missing")
        check("DRAFT_VERSION" in script, "draft version guard is missing")
        check("isModified" in script, "edited-state tracking is missing")
        check("Original example only" in script, "edited reference label is missing")

    check(STYLE_PATH.is_file(), "css/playground.css is missing")
    if STYLE_PATH.is_file():
        style = read(STYLE_PATH)
        check("prefers-reduced-motion" in style, "reduced-motion handling is missing")
        check("@media (max-width: 420px)" in style, "small-screen layout is missing")
        check(".pg-textarea" in style and ".pg-highlight" in style, "editor layer styles are missing")
        check(".tok-keyword" in style, "syntax highlighting styles are missing")

    print(f"playground checks: {checks}")
    print(f"examples          : {len(examples)}")
    print(f"recorded checks   : {total_checks}")
    report()
    return 0 if not failures else 1


def report() -> None:
    if failures:
        print("\nFAILED")
        for failure in failures:
            print(f"  - {failure}")
    else:
        print("PASS: playground metadata, sources, transcripts and page are consistent")


if __name__ == "__main__":
    sys.exit(main())
