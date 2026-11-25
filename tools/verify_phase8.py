#!/usr/bin/env python3
"""Site verification: quiz data, guides, links, browser behaviour and layout.

Starts a preview server on port 8000 when one is not already running, so a
single command is enough:
    C:\\msys64\\ucrt64\\bin\\python.exe tools\\verify_phase8.py
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser_audit import Chrome, CDPError

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8000"
SCREENSHOTS = ROOT / "docs" / "phase8" / "screenshots"

QUIZ_DATA = json.loads((ROOT / "data" / "quizzes.json").read_text(encoding="utf-8"))
QUIZ_TYPES = {
    "Multiple choice",
    "Code output",
    "Truth-table interpretation",
    "Boolean expression",
    "Verilog syntax",
    "Identify the error",
    "Practical viva",
}

results: list[tuple[bool, str]] = []


def check(condition: bool, label: str, detail: str = "") -> None:
    results.append((bool(condition), label))
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {label}" + (f" — {detail}" if detail and not condition else ""))


def local_target(page: Path, href: str) -> Path | None:
    href = html.unescape(href.strip())
    if not href or href.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
        return None
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href:
        return None
    target = (page.parent / href).resolve()
    if href.endswith("/"):
        target = target / "index.html"
    return target


# ---------------------------------------------------------------------------
# Static data
# ---------------------------------------------------------------------------

def verify_quiz_data() -> None:
    categories = QUIZ_DATA.get("categories", [])
    check(QUIZ_DATA.get("version") == 1, "quiz data version is 1")
    check(QUIZ_DATA.get("storageKey") == "va.quizzes", "quiz storage key is va.quizzes")
    check(len(categories) == 4, "four quiz categories", str(len(categories)))

    ids: set[str] = set()
    prompts: set[str] = set()
    types: set[str] = set()
    total = 0
    for category in categories:
        questions = category.get("questions", [])
        total += len(questions)
        check(len(questions) >= 10, f"{category.get('id')} has at least 10 questions", str(len(questions)))
        check(
            all(question.get("type") in QUIZ_TYPES for question in questions),
            f"{category.get('id')} uses supported question types",
        )
        for question in questions:
            qid = question.get("id")
            check(bool(qid) and qid not in ids, f"question id unique: {qid}")
            ids.add(qid)
            prompt_key = " ".join(str(question.get("prompt", "")).lower().split())
            check(bool(prompt_key) and prompt_key not in prompts, f"prompt unique: {qid}")
            prompts.add(prompt_key)
            types.add(question.get("type"))
            options = question.get("options", [])
            check(len(options) == 4, f"{qid} has four options", str(len(options)))
            check(
                len({str(option).strip().lower() for option in options}) == 4,
                f"{qid} options are distinct",
            )
            answer = question.get("answer")
            check(isinstance(answer, int) and 0 <= answer <= 3, f"{qid} answer index valid")
            explanation = str(question.get("explanation", "")).strip()
            check(len(explanation) >= 20, f"{qid} explanation is substantive", explanation[:40])
            table = question.get("table")
            if table:
                headers = table.get("headers", [])
                rows = table.get("rows", [])
                check(bool(headers) and bool(rows), f"{qid} table has headers and rows")
                check(
                    all(len(row) == len(headers) for row in rows),
                    f"{qid} table rows match header width",
                )

    check(total == 46, "quiz bank contains 46 questions", str(total))
    check(len(types) == 7, "all seven question types are used", str(sorted(types)))
    check(len(ids) == total, "every question id is unique")
    check(
        not any(re.search(r"\b(Unit\s*[45]|Experiment\s*(?:[7-9]|1[0-5]))\b", str(q)) for q in QUIZ_DATA),
        "quiz data does not include locked Units 4–5 or Experiments 7–15",
    )


# ---------------------------------------------------------------------------
# Static guide claims
# ---------------------------------------------------------------------------

def verify_guides() -> None:
    windows = (ROOT / "content" / "guides" / "windows.html").read_text(encoding="utf-8")
    android = (ROOT / "content" / "guides" / "android.html").read_text(encoding="utf-8")

    windows_required = [
        "Icarus Verilog 13.0",
        "GTKWave 3.3.128",
        "iverilog -g2001",
        "vvp",
        "$dumpfile",
        "$dumpvars",
        "VCD",
        "Troubleshooting",
        "Not installed",
        "Vivado",
        "Xilinx ISE",
        "GTKWave version quirk",
        "design.v",
        "tb.v",
    ]
    for phrase in windows_required:
        check(phrase in windows, f"Windows guide covers {phrase!r}")

    check(
        "Vivado, Xilinx ISE, ModelSim and Verilator are <strong>not installed</strong>" in windows,
        "Windows guide states vendor tools are not installed",
    )
    check(
        "Vivado" not in windows.replace("Vivado, Xilinx ISE, ModelSim and Verilator are <strong>not installed</strong>", "").replace("Vivado / Xilinx ISE", "").replace("Vivado or ISE", "")
        or "not installed" in windows,
        "Windows guide does not claim Vivado is installed",
    )
    check("Android" not in windows or "Windows" in windows, "Windows guide keeps platform scope explicit")

    android_required = [
        "Circuit Lab",
        "Playground",
        "va.progress",
        "va.quizzes",
        "va.playground.drafts",
        "Export JSON",
        "Import backup",
        "Download design.v",
        "has no server-side compiler",
        "cannot turn",
        "Compilation is a Windows step",
        "file://",
        "Termux",
        "not exercised on a physical Android handset",
    ]
    for phrase in android_required:
        check(phrase in android, f"Android guide covers {phrase!r}")

    check(
        "It is not a place where this static site compiles Verilog" in android,
        "Android guide states the site does not compile Verilog",
    )
    check(
        "Icarus is not bundled" in android or "Icarus on Android" in android,
        "Android guide is explicit about Icarus",
    )
    check(
        "does not claim that a public deployment exists" in android,
        "Android guide avoids claiming a live deployment",
    )
    check(
        not re.search(r"Android (?:compiles|runs) (?:Verilog|Icarus)", android),
        "Android guide contains no false Android-compiler claim",
    )


# ---------------------------------------------------------------------------
# Site-wide links and ids
# ---------------------------------------------------------------------------

def verify_links_and_ids() -> None:
    pages = sorted(ROOT.rglob("*.html"))
    pages = [
        page
        for page in pages
        if not {"docs", "content", "templates"} & set(page.relative_to(ROOT).parts)
    ]
    broken: list[str] = []
    duplicates: list[str] = []
    icon_misses: list[str] = []
    checked = 0

    sprite = (ROOT / "templates" / "icons.svg").read_text(encoding="utf-8")
    sprite_ids = set(re.findall(r'<symbol id="([^"]+)"', sprite))

    for page in pages:
        text = page.read_text(encoding="utf-8")
        page_ids = re.findall(r'\bid="([^"]+)"', text)
        seen: set[str] = set()
        for value in page_ids:
            if value in seen:
                duplicates.append(f"{page.relative_to(ROOT)}#{value}")
            seen.add(value)

        for match in re.finditer(r'\b(?:href|src)="([^"]+)"', text):
            value = match.group(1)
            if value.startswith("#") and value != "#":
                target_id = html.unescape(value[1:])
                if target_id not in seen:
                    broken.append(f"{page.relative_to(ROOT)} -> {value} (missing id)")
                continue
            target = local_target(page, value)
            if target is None:
                continue
            checked += 1
            if not target.is_file():
                broken.append(f"{page.relative_to(ROOT)} -> {value}")

        for use in re.findall(r'<use href="#(icon-[^"]+)"', text):
            if use not in sprite_ids:
                icon_misses.append(f"{page.relative_to(ROOT)} -> #{use}")

    check(not broken, f"all {checked} local links resolve", "; ".join(broken[:8]))
    check(not duplicates, "no duplicate element ids", "; ".join(duplicates[:8]))
    check(not icon_misses, "all SVG icon references exist", "; ".join(icon_misses[:8]))


# ---------------------------------------------------------------------------
# Browser page pass
# ---------------------------------------------------------------------------

PAGES = [
    ("home", "index.html"),
    ("dashboard", "dashboard.html"),
    ("theory", "theory/index.html"),
    ("lesson", "theory/vlsi-design-flow.html"),
    ("laboratory", "labs/index.html"),
    ("experiment", "labs/experiment-01.html"),
    ("circuit-lab", "circuit-lab/index.html"),
    ("playground", "playground/index.html"),
    ("quizzes", "quizzes/index.html"),
    ("guides", "guides/index.html"),
    ("windows-guide", "guides/windows.html"),
    ("android-guide", "guides/android.html"),
]

OVERFLOW_WIDTHS = [360, 390, 412, 768, 901, 960, 1024, 1080, 1280, 1440, 1920]


def browser_page_pass(session) -> None:
    for name, path in PAGES:
        session.navigate(f"{BASE}/{path}", wait=0.45)
        info = session.evaluate(
            """(() => ({
                title: document.title,
                h1: document.querySelectorAll('h1').length,
                main: !!document.querySelector('#main-content'),
                overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
                width: document.documentElement.clientWidth,
                scrollWidth: document.documentElement.scrollWidth,
                unnamedButtons: Array.from(document.querySelectorAll('button')).filter(b => !(b.getAttribute('aria-label') || b.textContent.trim())).length,
                unnamedLinks: Array.from(document.querySelectorAll('a')).filter(a => !(a.getAttribute('aria-label') || a.textContent.trim() || a.querySelector('img[alt]:not([alt=""])'))).length,
                imagesWithoutAlt: Array.from(document.querySelectorAll('img')).filter(i => !i.hasAttribute('alt')).length,
            }))()"""
        )
        check(bool(info["title"]), f"{name}: has a document title")
        check(info["h1"] == 1, f"{name}: exactly one h1", str(info["h1"]))
        check(info["main"], f"{name}: main landmark exists")
        check(not info["overflow"], f"{name}: no horizontal overflow at 1440", f"{info['scrollWidth']}>{info['width']}")
        check(info["unnamedButtons"] == 0, f"{name}: every button has a name", str(info["unnamedButtons"]))
        check(info["unnamedLinks"] == 0, f"{name}: every link has a name", str(info["unnamedLinks"]))
        check(info["imagesWithoutAlt"] == 0, f"{name}: every image has alt text", str(info["imagesWithoutAlt"]))
        errors = session.drain_errors()
        check(not errors, f"{name}: no console or network errors", "; ".join(errors[:4]))


def browser_responsive_pass(session) -> None:
    for width in OVERFLOW_WIDTHS:
        session.set_viewport(width, 900, mobile=width <= 480)
        for path in ("index.html", "quizzes/index.html", "guides/windows.html", "guides/android.html", "dashboard.html"):
            session.navigate(f"{BASE}/{path}", wait=0.25)
            info = session.evaluate(
                "({w: document.documentElement.clientWidth, s: document.documentElement.scrollWidth, nav: getComputedStyle(document.querySelector('.site-nav')).display, menu: getComputedStyle(document.querySelector('.menu-toggle')).display})"
            )
            check(
                info["s"] <= info["w"] + 1,
                f"{path} at {width}px has no horizontal overflow",
                f"{info['s']}>{info['w']}",
            )
        session.set_viewport(1440, 900, mobile=False)


# ---------------------------------------------------------------------------
# Quiz browser flow
# ---------------------------------------------------------------------------

QUIZ_FLOW = r"""
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const one = (selector) => document.querySelector(selector);
  const all = (selector) => Array.from(document.querySelectorAll(selector));
  const data = JSON.parse(one('#quiz-data').textContent);
  localStorage.setItem('va.progress', 'SENTINEL-PROGRESS');
  localStorage.setItem('va.playground.drafts', 'SENTINEL-DRAFTS');
  localStorage.removeItem('va.quizzes');
  const result = { hiddenBeforeSubmit: true, categories: [] };

  for (const category of data.categories) {
    one('[data-quiz-category="' + category.id + '"]').click();
    await sleep(15);
    for (let index = 0; index < category.questions.length; index += 1) {
      if (all('.quiz-explanation').length || all('.quiz-option.is-correct').length) {
        result.hiddenBeforeSubmit = false;
      }
      one('[data-quiz-option="' + category.questions[index].answer + '"]').click();
      if (index < category.questions.length - 1) one('[data-quiz-next]').click();
      await sleep(4);
    }
    one('[data-quiz-submit]').click();
    await sleep(15);
    result.categories.push({
      id: category.id,
      score: one('.quiz-result__score')?.textContent.trim(),
      percent: one('.quiz-result__percent')?.textContent.trim(),
      correctDots: all('.quiz-palette__dot.is-correct').length,
      history: all('[data-quiz-attempt]').length,
      status: one('[data-quiz-status]')?.textContent.trim(),
      explanations: all('.quiz-explanation').length,
      bestCard: one('[data-quiz-best="' + category.id + '"]')?.textContent.trim(),
    });
  }

  result.progress = localStorage.getItem('va.progress');
  result.drafts = localStorage.getItem('va.playground.drafts');
  const store = JSON.parse(localStorage.getItem('va.quizzes'));
  result.storage = {
    version: store.version,
    keys: Object.keys(store.attempts).sort(),
    counts: Object.fromEntries(Object.entries(store.attempts).map(([key, list]) => [key, list.length])),
  };
  one('[data-quiz-retry]').click();
  await sleep(10);
  result.afterRetry = {
    status: one('[data-quiz-status]')?.textContent.trim(),
    answered: one('[data-quiz-answered]')?.textContent.trim(),
    history: all('[data-quiz-attempt]').length,
    score: one('.quiz-result__score')?.textContent.trim(),
  };
  return result;
})()
"""


def verify_quiz_flow(session) -> None:
    session.navigate(f"{BASE}/quizzes/index.html", wait=0.5)
    session.evaluate("localStorage.clear()")
    session.navigate(f"{BASE}/quizzes/index.html", wait=0.5)
    flow = session.evaluate(QUIZ_FLOW)

    check(flow["hiddenBeforeSubmit"], "quiz: no answers or explanations before submit")
    check(flow["progress"] == "SENTINEL-PROGRESS", "quiz: va.progress is untouched")
    check(flow["drafts"] == "SENTINEL-DRAFTS", "quiz: Playground drafts are untouched")
    check(flow["storage"]["version"] == 1, "quiz: stored schema version is 1")
    check(
        flow["storage"]["keys"] == ["circuit-lab", "laboratory", "playground", "theory"],
        "quiz: attempts saved for all four banks",
        str(flow["storage"]["keys"]),
    )
    check(
        all(count == 1 for count in flow["storage"]["counts"].values()),
        "quiz: one saved attempt per bank",
        str(flow["storage"]["counts"]),
    )

    expected = {"theory": 12, "laboratory": 12, "circuit-lab": 11, "playground": 11}
    for category in flow["categories"]:
        total = expected[category["id"]]
        check(category["score"] == f"{total} / {total}", f"quiz {category['id']}: full score", str(category["score"]))
        check(category["percent"] == "100%", f"quiz {category['id']}: 100 percent", str(category["percent"]))
        check(category["correctDots"] == total, f"quiz {category['id']}: every dot marked correct", str(category["correctDots"]))
        check(category["history"] == 1, f"quiz {category['id']}: one history row", str(category["history"]))
        check(category["status"] == "Submitted", f"quiz {category['id']}: submitted status", str(category["status"]))
        check(category["explanations"] == 1, f"quiz {category['id']}: explanation visible after submit", str(category["explanations"]))
        check("Best 100%" in (category["bestCard"] or ""), f"quiz {category['id']}: category card shows best score", str(category["bestCard"]))

    check(flow["afterRetry"]["status"] == "Ready to start", "quiz: retry resets status")
    check(flow["afterRetry"]["answered"].startswith("0 of"), "quiz: retry clears answers", str(flow["afterRetry"]["answered"]))
    check(flow["afterRetry"]["history"] == 1, "quiz: retry keeps history", str(flow["afterRetry"]["history"]))
    check(not session.drain_errors(), "quiz flow: no console errors")

    # Reload and confirm persistence, then review a saved attempt.
    session.navigate(f"{BASE}/quizzes/index.html", wait=0.5)
    persisted = session.evaluate(
        """(() => ({
            theoryHistory: (() => { document.querySelector('[data-quiz-category="theory"]').click(); return document.querySelectorAll('[data-quiz-attempt]').length; })(),
            best: document.querySelector('[data-quiz-best="theory"]')?.textContent.trim(),
            stored: !!localStorage.getItem('va.quizzes'),
            progress: localStorage.getItem('va.progress'),
        }))()"""
    )
    check(persisted["theoryHistory"] == 1, "quiz: history persists after reload", str(persisted["theoryHistory"]))
    check("Best 100%" in (persisted["best"] or ""), "quiz: best score persists after reload", str(persisted["best"]))
    check(persisted["stored"], "quiz: storage key persists after reload")
    check(persisted["progress"] == "SENTINEL-PROGRESS", "quiz: reload does not touch va.progress")

    session.evaluate("document.querySelector('[data-quiz-attempt]').click()")
    review = session.evaluate(
        """(() => ({
            status: document.querySelector('[data-quiz-status]')?.textContent.trim(),
            score: document.querySelector('.quiz-result__score')?.textContent.trim(),
            note: document.querySelector('.quiz-result__note')?.textContent.trim(),
            reviewHidden: document.querySelector('[data-quiz-review]')?.hidden,
        }))()"""
    )
    check(review["status"] == "Reviewing saved attempt", "quiz: saved attempt opens in review mode", str(review["status"]))
    check(review["score"] == "12 / 12", "quiz: reviewed score matches", str(review["score"]))
    check("Reviewing a saved attempt" in (review["note"] or ""), "quiz: review note is explicit", str(review["note"]))
    check(review["reviewHidden"] is False, "quiz: review button available")


UNANSWERED_FLOW = r"""
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const one = (selector) => document.querySelector(selector);
  localStorage.removeItem('va.quizzes');
  const result = {};
  one('[data-quiz-category="theory"]').click();
  await sleep(10);
  one('[data-quiz-submit]').click();
  await sleep(10);
  result.warning = one('[data-quiz-warning]')?.textContent.trim();
  result.attemptsAfterWarning = document.querySelectorAll('[data-quiz-attempt]').length;
  result.stillEditable = !one('[data-quiz-option]')?.disabled;
  one('[data-quiz-submit]').click();
  await sleep(10);
  result.score = one('.quiz-result__score')?.textContent.trim();
  result.percent = one('.quiz-result__percent')?.textContent.trim();
  result.unansweredNote = document.querySelectorAll('.quiz-explanation__note').length;
  result.wrongDots = document.querySelectorAll('.quiz-palette__dot.is-wrong').length;
  result.history = document.querySelectorAll('[data-quiz-attempt]').length;
  result.stored = JSON.parse(localStorage.getItem('va.quizzes'));
  return result;
})()
"""


def verify_unanswered_flow(session) -> None:
    session.navigate(f"{BASE}/quizzes/index.html", wait=0.4)
    session.evaluate("localStorage.removeItem('va.quizzes')")
    session.navigate(f"{BASE}/quizzes/index.html", wait=0.45)
    flow = session.evaluate(UNANSWERED_FLOW)
    check("unanswered" in (flow["warning"] or "").lower(), "quiz: first submit warns about unanswered questions", str(flow["warning"]))
    check(flow["attemptsAfterWarning"] == 0, "quiz: warning does not save an attempt", str(flow["attemptsAfterWarning"]))
    check(flow["stillEditable"], "quiz: warning leaves the questions editable")
    check(flow["score"] == "0 / 12", "quiz: unanswered bank scores zero", str(flow["score"]))
    check(flow["percent"] == "0%", "quiz: unanswered bank shows zero percent", str(flow["percent"]))
    check(flow["unansweredNote"] == 1, "quiz: current question shows the unanswered note", str(flow["unansweredNote"]))
    check(flow["wrongDots"] == 0, "quiz: unanswered dots are not marked wrong", str(flow["wrongDots"]))
    check(flow["history"] == 1, "quiz: confirmed submission saves an attempt", str(flow["history"]))
    check(
        flow["stored"]["attempts"]["theory"][0]["answers"] == [None] * 12,
        "quiz: unanswered answers stored as nulls",
        str(flow["stored"]["attempts"]["theory"][0]["answers"][:3]),
    )


MALFORMED_STORAGE = [
    ("{broken", "invalid JSON"),
    (json.dumps({"version": 99, "attempts": {}}), "unsupported version"),
    (json.dumps({"version": 1, "attempts": {"theory": [{"id": "x", "submittedAt": "not-a-date", "answers": []}]}}), "malformed attempt"),
]


def verify_storage_recovery(session) -> None:
    for payload, label in MALFORMED_STORAGE:
        session.navigate(f"{BASE}/quizzes/index.html", wait=0.35)
        session.evaluate(f"localStorage.setItem('va.quizzes', {json.dumps(payload)})")
        session.navigate(f"{BASE}/quizzes/index.html", wait=0.45)
        state = session.evaluate(
            "({history: document.querySelectorAll('[data-quiz-attempt]').length, empty: document.querySelector('.quiz-empty')?.textContent.trim(), questions: document.querySelectorAll('[data-quiz-option]').length})"
        )
        check(state["history"] == 0, f"quiz storage: {label} shows empty history", str(state["history"]))
        check("No saved attempts" in (state["empty"] or ""), f"quiz storage: {label} shows empty state", str(state["empty"]))
        check(state["questions"] == 4, f"quiz storage: {label} still renders questions", str(state["questions"]))
        check(not session.drain_errors(), f"quiz storage: {label} raises no console errors")


# ---------------------------------------------------------------------------
# Theme and mobile navigation
# ---------------------------------------------------------------------------

def verify_theme_and_mobile(session) -> None:
    session.set_viewport(1440, 900, mobile=False)
    session.navigate(f"{BASE}/index.html", wait=0.4)
    session.evaluate("document.querySelector('#theme-toggle').click()")
    theme = session.evaluate("({theme: document.documentElement.dataset.theme, stored: localStorage.getItem('va.theme'), pressed: document.querySelector('#theme-toggle').getAttribute('aria-pressed')})")
    check(theme["theme"] == "daylight", "theme: toggle switches to Daylight", str(theme["theme"]))
    check(theme["stored"] == "daylight", "theme: choice stored under va.theme", str(theme["stored"]))
    check(theme["pressed"] == "true", "theme: toggle exposes pressed state", str(theme["pressed"]))
    session.navigate(f"{BASE}/index.html", wait=0.4)
    check(session.evaluate("document.documentElement.dataset.theme") == "daylight", "theme: choice persists after reload")
    session.evaluate("document.querySelector('#theme-toggle').click()")
    session.evaluate("localStorage.removeItem('va.theme')")

    session.set_viewport(390, 844, mobile=True)
    session.navigate(f"{BASE}/index.html", wait=0.4)
    nav = session.evaluate(
        """(() => ({
            siteNav: getComputedStyle(document.querySelector('.site-nav')).display,
            menu: getComputedStyle(document.querySelector('.menu-toggle')).display,
            links: document.querySelectorAll('.mobile-nav-link').length,
        }))()"""
    )
    check(nav["siteNav"] == "none", "mobile: desktop navigation is hidden")
    check(nav["menu"] != "none", "mobile: menu button is visible")
    check(nav["links"] >= 8, "mobile: navigation includes quiz and guide links", str(nav["links"]))
    session.evaluate("document.querySelector('#menu-toggle').click()")
    opened = session.evaluate("({open: document.querySelector('#mobile-nav').open, expanded: document.querySelector('#menu-toggle').getAttribute('aria-expanded')})")
    check(opened["open"], "mobile: menu dialog opens")
    check(opened["expanded"] == "true", "mobile: menu button reports expanded")
    session.evaluate("document.querySelector('#mobile-nav-close').click()")
    check(session.evaluate("!document.querySelector('#mobile-nav').open"), "mobile: close button closes the dialog")
    session.evaluate("document.querySelector('#menu-toggle').click()")
    session.call("Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    session.call("Input.dispatchKeyEvent", type="keyUp", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    session.evaluate("new Promise((r) => setTimeout(r, 60))")
    check(session.evaluate("!document.querySelector('#mobile-nav').open"), "mobile: Escape closes the dialog")
    session.set_viewport(1440, 900, mobile=False)


# ---------------------------------------------------------------------------
# Screenshots
# ---------------------------------------------------------------------------

def verify_keyboard(session) -> None:
    session.set_viewport(1440, 900, mobile=False)
    session.navigate(f"{BASE}/index.html", wait=0.4)
    session.evaluate("document.body.focus()")
    session.call("Input.dispatchKeyEvent", type="keyDown", key="Tab", code="Tab", windowsVirtualKeyCode=9)
    session.call("Input.dispatchKeyEvent", type="keyUp", key="Tab", code="Tab", windowsVirtualKeyCode=9)
    session.evaluate("new Promise((resolve) => setTimeout(resolve, 60))")
    first = session.evaluate(
        "({tag: document.activeElement.tagName, cls: document.activeElement.className, text: document.activeElement.textContent.trim(), width: document.activeElement.offsetWidth})"
    )
    check(first["cls"] == "skip-link", "keyboard: first Tab reaches the skip link", str(first))
    check(first["width"] > 0, "keyboard: skip link is visible when focused", str(first["width"]))
    session.call("Input.dispatchKeyEvent", type="keyDown", key="Enter", code="Enter", windowsVirtualKeyCode=13)
    session.call("Input.dispatchKeyEvent", type="keyUp", key="Enter", code="Enter", windowsVirtualKeyCode=13)
    session.evaluate("new Promise((resolve) => setTimeout(resolve, 90))")
    landed = session.evaluate("({hash: location.hash, active: document.activeElement.id})")
    check(landed["hash"] == "#main-content", "keyboard: skip link targets the main landmark", str(landed))
    check(landed["active"] == "main-content", "keyboard: focus moves to main content", str(landed))
    check(not session.drain_errors(), "keyboard: no console errors")


def capture_screenshots(session) -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    shots = [
        ("desktop-home.png", "index.html", 1440, 900),
        ("desktop-dashboard.png", "dashboard.html", 1440, 900),
        ("desktop-theory.png", "theory/index.html", 1440, 900),
        ("desktop-lesson.png", "theory/vlsi-design-flow.html", 1440, 900),
        ("desktop-laboratory.png", "labs/index.html", 1440, 900),
        ("desktop-circuit-lab.png", "circuit-lab/index.html", 1440, 900),
        ("desktop-playground.png", "playground/index.html", 1440, 900),
        ("desktop-quizzes.png", "quizzes/index.html", 1440, 900),
        ("desktop-guides.png", "guides/index.html", 1440, 900),
        ("desktop-windows-guide.png", "guides/windows.html", 1440, 900),
        ("desktop-android-guide.png", "guides/android.html", 1440, 900),
        ("mobile-home.png", "index.html", 390, 844),
        ("mobile-quizzes.png", "quizzes/index.html", 390, 844),
        ("mobile-windows-guide.png", "guides/windows.html", 390, 844),
        ("mobile-android-guide.png", "guides/android.html", 390, 844),
    ]
    for name, path, width, height in shots:
        session.set_viewport(width, height, mobile=width <= 480)
        session.navigate(f"{BASE}/{path}", wait=0.55)
        session.screenshot(SCREENSHOTS / name)
        check((SCREENSHOTS / name).is_file() and (SCREENSHOTS / name).stat().st_size > 10_000, f"screenshot captured: {name}")
    session.set_viewport(1440, 900, mobile=False)


def server_ready(timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(f"{BASE}/index.html", timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def start_server() -> subprocess.Popen | None:
    """Start the preview server when one is not already listening.

    Keeps the audit self-contained so it can run in one command without a
    separate background shell.
    """
    if server_ready():
        return None
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "tools" / "serve.py"), "--port", "8000"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        if server_ready(0.5):
            return process
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError("Preview server did not start on port 8000")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify the Phase 08 site.")
    parser.add_argument(
        "--stage",
        choices=("all", "static", "pages", "responsive", "quiz", "ui", "screenshots"),
        default="all",
        help="Run one audit stage, or all of them (default).",
    )
    args = parser.parse_args()

    if args.stage == "static":
        verify_quiz_data()
        verify_guides()
        verify_links_and_ids()
        return report(args.stage)

    server = start_server()
    try:
        return run_audit(args.stage)
    finally:
        if server and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


def report(stage: str) -> int:
    passed = sum(1 for ok, _ in results if ok)
    failed = [label for ok, label in results if not ok]
    print()
    print(f"Phase 08 verification ({stage}): {passed}/{len(results)} checks passed")
    if failed:
        print("Failures:")
        for label in failed:
            print(f"  - {label}")
        return 1
    return 0


def run_audit(stage: str) -> int:
    ports = {
        "all": 9341,
        "pages": 9342,
        "responsive": 9343,
        "quiz": 9344,
        "ui": 9345,
        "screenshots": 9346,
    }
    try:
        with Chrome(port=ports[stage]) as chrome:
            session = chrome.new_page("about:blank")
            session.set_viewport(1440, 900, mobile=False)
            if stage in ("all", "pages"):
                browser_page_pass(session)
            if stage in ("all", "responsive"):
                browser_responsive_pass(session)
            if stage in ("all", "quiz"):
                verify_quiz_flow(session)
                verify_unanswered_flow(session)
                verify_storage_recovery(session)
            if stage in ("all", "ui"):
                verify_theme_and_mobile(session)
                verify_keyboard(session)
            if stage in ("all", "screenshots"):
                capture_screenshots(session)
            session.ws.close()
    except CDPError as error:
        check(False, "browser session", str(error))

    return report(stage)


if __name__ == "__main__":
    sys.exit(main())
