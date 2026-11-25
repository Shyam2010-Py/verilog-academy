#!/usr/bin/env python3
"""Zero-dependency static builder for Verilog Academy.

Source content lives in content/ and is wrapped by templates/shell.html.
Generated HTML is written to the project root so the result works directly
on GitHub Pages, including project sites served from a subpath.
"""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import circuits as circuit_lab
import playground as playground_page
import quizzes as quiz_page

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
CURRICULUM = json.loads((ROOT / "data" / "curriculum.json").read_text(encoding="utf-8"))
THEORY = json.loads((ROOT / "data" / "theory.json").read_text(encoding="utf-8"))
LABS = json.loads((ROOT / "data" / "labs.json").read_text(encoding="utf-8"))
SHELL = (ROOT / "templates" / "shell.html").read_text(encoding="utf-8")
LESSON_SHELL = (ROOT / "templates" / "lesson.html").read_text(encoding="utf-8")
LAB_SHELL = (ROOT / "templates" / "experiment.html").read_text(encoding="utf-8")
ICON_SPRITE = (ROOT / "templates" / "icons.svg").read_text(encoding="utf-8")



def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def relative_prefix(out_path: str) -> str:
    """Return the path prefix needed to reach the project root."""
    depth = len(Path(out_path).parent.parts)
    return "../" * depth


def relative_href(out_path: str, href: str) -> str:
    if href.startswith(("http://", "https://", "#", "mailto:", "tel:")):
        return href
    return relative_prefix(out_path) + href


def render_nav(items: list[dict], out_path: str, active_label: str | None = None) -> str:
    links = []
    for item in items:
        label = item["label"]
        href = relative_href(out_path, item["href"])
        is_active = label == active_label
        classes = "nav-link is-active" if is_active else "nav-link"
        current = ' aria-current="page"' if is_active and "#" not in item["href"] else ""
        links.append(
            f'<a class="{classes}" href="{esc(href)}"{current}>{esc(label)}</a>'
        )
    return "\n          ".join(links)


def render_mobile_nav(items: list[dict], out_path: str, active_label: str | None = None) -> str:
    links = []
    for index, item in enumerate(items, start=1):
        label = item["label"]
        href = relative_href(out_path, item["href"])
        is_active = label == active_label and "#" not in item["href"]
        current = ' aria-current="page"' if is_active else ""
        classes = "mobile-nav-link is-active" if is_active else "mobile-nav-link"
        links.append(
            f'<a class="{classes}" href="{esc(href)}"{current}>'
            f'{esc(label)}<span>{index:02d}</span></a>'
        )
    return "\n        ".join(links)


def render_footer(out_path: str) -> str:
    footer = SITE["footer"]
    columns = []

    for column in footer["columns"]:
        links = "\n              ".join(
            f'<a class="footer-link" href="{esc(relative_href(out_path, link["href"]))}">{esc(link["label"])}</a>'
            for link in column["links"]
        )
        columns.append(
            f"""<div class="footer-column">
            <span class="footer-title">{esc(column["title"])}</span>
            <div class="footer-links">
              {links}
            </div>
          </div>"""
        )

    columns_html = "\n          ".join(columns)
    year = date.today().year

    return f"""<div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <a class="brand" href="{esc(relative_href(out_path, "index.html"))}" aria-label="Verilog Academy home">
              <img class="brand-mark" src="{esc(relative_href(out_path, "assets/svg/logo-mark.svg"))}" alt="" width="40" height="40">
              <span class="brand-copy">
                <span class="brand-name">VERILOG</span>
                <span class="brand-sub">ACADEMY</span>
              </span>
            </a>
            <p>{esc(footer["tagline"])}</p>
            <span class="badge badge-cyan"><span class="badge-dot"></span> {esc(footer["badge"])}</span>
          </div>
          {columns_html}
        </div>
        <div class="footer-bottom">
          <p>© {year} Verilog Academy</p>
          <p>{esc(footer["note"])}</p>
          <p>Built with HTML, CSS and vanilla JS.</p>
        </div>
      </div>"""


def get_course(course_id: str) -> dict:
    return next(course for course in CURRICULUM["courses"] if course["id"] == course_id)


# ---------------------------------------------------------------------------
# Theory classroom
# ---------------------------------------------------------------------------

def available_theory_units() -> list[dict]:
    return [unit for unit in get_course("ec405")["units"] if unit.get("status") == "available"]


def theory_available_periods() -> int:
    return sum(int(unit["periods"]) for unit in available_theory_units())


def flat_theory_topics() -> list[tuple[dict, dict]]:
    items = []
    for unit in available_theory_units():
        for topic in unit.get("topics", []):
            items.append((unit, topic))
    return items


def topic_summary(topic_id: str) -> str:
    return THEORY.get("topics", {}).get(topic_id, {}).get("summary", "")


def render_theory_unit_cards() -> str:
    cards = []
    for unit in available_theory_units():
        meta = THEORY.get("units", {}).get(unit["id"], {})
        topics = unit.get("topics", [])
        objectives = "".join(f"<li>{esc(item)}</li>" for item in meta.get("objectives", []))
        rows = []
        for topic in topics:
            rows.append(
                f'<li class="unit-lesson" data-topic-row="{esc(topic["id"])}">'
                f'<a class="unit-lesson__link" href="{esc(topic["id"])}.html">'
                f'<span class="unit-lesson__num">{topic["number"]:02d}</span>'
                f'<span class="unit-lesson__title">{esc(topic["title"])}</span>'
                f'<span class="unit-lesson__state" data-topic-state>—</span>'
                '<svg class="icon icon-sm unit-lesson__arrow" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
                "</a></li>"
            )
        first_topic = topics[0]["id"] if topics else None
        start_href = f"{first_topic}.html" if first_topic else "index.html"
        cards.append(
            f'<article class="unit-card panel" id="{esc(unit["id"])}" data-unit-card="{esc(unit["id"])}" data-reveal>'
            '<header class="unit-card__head">'
            '<div class="unit-card__id">'
            f'<span class="unit-index">Unit {unit["number"]:02d}</span>'
            f'<span class="badge badge-cyan">{unit["periods"]} periods · {len(topics)} topics</span>'
            "</div>"
            f'<h2>{esc(unit["title"])}</h2>'
            f'<p class="unit-card__desc">{esc(meta.get("description", ""))}</p>'
            "</header>"
            '<div class="unit-card__objective">'
            '<h3>Learning objectives</h3>'
            f'<ul class="objective-list objective-list--compact">{objectives}</ul>'
            "</div>"
            '<div class="unit-card__progress">'
            '<div class="unit-card__progress-row">'
            f'<span data-unit-count="{esc(unit["id"])}">0 / {len(topics)}</span>'
            f'<span data-unit-percent="{esc(unit["id"])}">0%</span>'
            "</div>"
            f'<div class="progress" role="progressbar" aria-label="Unit {unit["number"]} progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-unit-bar="{esc(unit["id"])}">'
            f'<span class="progress-fill" data-unit-fill="{esc(unit["id"])}" style="--progress: 0%"></span>'
            "</div>"
            "</div>"
            f'<ol class="unit-lesson-list" aria-label="Unit {unit["number"]} topics">'
            + "".join(rows)
            + "</ol>"
            '<div class="unit-card__foot">'
            f'<a class="btn btn-secondary btn-sm" href="{esc(start_href)}" data-unit-start="{esc(unit["id"])}">'
            '<span data-unit-start-label>Start unit</span>'
            '<svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
            "</a>"
            '<a class="text-link" href="index.html#roadmap">Release scope</a>'
            "</div>"
            "</article>"
        )
    return "\n      ".join(cards)


def render_theory_roadmap() -> str:
    cards = []
    for unit in get_course("ec405")["units"]:
        if unit.get("status") != "locked":
            continue
        cards.append(
            '<article class="theory-roadmap-card panel">'
            '<div class="theory-roadmap-card__head">'
            f'<span class="unit-index">Unit {unit["number"]:02d}</span>'
            '<span class="badge badge-violet"><svg class="icon icon-sm" aria-hidden="true"><use href="#icon-lock"></use></svg> Locked</span>'
            "</div>"
            f'<h3>{esc(unit["title"])}</h3>'
            "<p>Part of the official EC-405 syllabus. Lessons, verified examples and completion controls will be published in a later release.</p>"
            f'<span class="theory-roadmap-card__meta">{unit["periods"]} periods · not published</span>'
            "</article>"
        )
    return "\n      ".join(cards)


# ---------------------------------------------------------------------------
# Verilog code rendering
# ---------------------------------------------------------------------------

VERILOG_KEYWORDS = {
    "always", "and", "assign", "automatic", "begin", "buf", "bufif0", "bufif1",
    "case", "casex", "casez", "cell", "cmos", "config", "deassign", "default",
    "defparam", "design", "disable", "edge", "else", "end", "endcase", "endconfig",
    "endfunction", "endgenerate", "endmodule", "endprimitive", "endspecify",
    "endtable", "endtask", "event", "for", "force", "forever", "fork", "function",
    "generate", "genvar", "highz0", "highz1", "if", "ifnone", "incdir", "include",
    "initial", "inout", "input", "instance", "integer", "join", "large", "liblist",
    "library", "localparam", "macromodule", "medium", "module", "nand", "negedge",
    "nmos", "nor", "noshowcancelled", "not", "notif0", "notif1", "or", "output",
    "parameter", "pmos", "posedge", "primitive", "pull0", "pull1", "pulldown",
    "pullup", "pulsestyle_onevent", "pulsestyle_ondetect", "rcmos", "real",
    "realtime", "reg", "release", "repeat", "rnmos", "rpmos", "rtran", "rtranif0",
    "rtranif1", "scalared", "showcancelled", "signed", "small", "specify",
    "specparam", "strong0", "strong1", "supply0", "supply1", "table", "task",
    "time", "tran", "tranif0", "tranif1", "tri", "tri0", "tri1", "triand", "trior",
    "trireg", "unsigned", "use", "vectored", "wait", "wand", "weak0", "weak1",
    "while", "wire", "wor", "xnor", "xor",
}

_VERILOG_TOKEN_RE = re.compile(
    r"(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)"
    r'|(?P<string>"(?:\\.|[^"\\])*")'
    r"|(?P<directive>`[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<system>\$[A-Za-z_][A-Za-z0-9_$]*)"
    r"|(?P<number>(?:\d[\d_]*)?'[sS]?[bBoOdDhH][0-9a-fA-FxXzZ?_]+|\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?\b)"
    r"|(?P<keyword>\b(?:" + "|".join(sorted(map(re.escape, VERILOG_KEYWORDS))) + r")\b)"
)


def highlight_verilog(source: str) -> str:
    output: list[str] = []
    position = 0
    for match in _VERILOG_TOKEN_RE.finditer(source):
        if match.start() > position:
            output.append(esc(source[position:match.start()]))
        kind = match.lastgroup
        output.append(f'<span class="tok-{kind}">{esc(match.group())}</span>')
        position = match.end()
    output.append(esc(source[position:]))
    return "".join(output)


def repo_file(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise RuntimeError(f"Refusing to read outside the project: {relative}")
    if not path.is_file():
        raise RuntimeError(f"Missing source file: {relative}")
    return path


def render_code_block(relative: str) -> str:
    path = repo_file(relative)
    source = path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"
    name = path.name
    return f"""<div class="code-block" data-copy-root>
  <div class="code-block__header">
    <span class="code-block__dots" aria-hidden="true"><span></span><span></span><span></span></span>
    <span class="code-block__file">{esc(name)}</span>
    <button class="copy-btn" type="button" aria-label="Copy {esc(name)}">
      <svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>
      <span class="copy-label">Copy</span>
    </button>
  </div>
  <div class="code-block__body">
    <pre><code>{highlight_verilog(source)}</code></pre>
  </div>
</div>"""


def render_output_block(relative: str) -> str:
    path = repo_file(relative)
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"
    return f"""<div class="code-block code-block--output" data-copy-root>
  <div class="code-block__header">
    <span class="code-block__file">Simulator output</span>
    <span class="output-tag">actual run · Icarus 13.0</span>
    <button class="copy-btn" type="button" aria-label="Copy simulator output">
      <svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>
      <span class="copy-label">Copy</span>
    </button>
  </div>
  <div class="code-block__body">
    <pre><code>{esc(text)}</code></pre>
  </div>
</div>"""


def render_snippet(relative: str) -> str:
    """A language-reference fragment that is deliberately not executed."""
    path = repo_file(relative)
    source = path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"
    return f"""<div class="code-block code-block--snippet" data-copy-root>
  <div class="code-block__header">
    <span class="code-block__file">{esc(path.name)}</span>
    <span class="snippet-tag">language reference · not executed here</span>
    <button class="copy-btn" type="button" aria-label="Copy {esc(path.name)}">
      <svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>
      <span class="copy-label">Copy</span>
    </button>
  </div>
  <div class="code-block__body">
    <pre><code>{highlight_verilog(source)}</code></pre>
  </div>
</div>"""


def render_commands(example_id: str) -> str:
    directory = None
    for group in ("labs", "verilog"):
        candidate = ROOT / "examples" / group / example_id
        if candidate.is_dir():
            directory = candidate
            break
    if directory is None:
        raise RuntimeError(f"No runnable example found for {example_id}")
    sources = [
        name
        for name in ("design.v", "example.v", "tb.v")
        if (directory / name).is_file()
    ]
    if not sources:
        raise RuntimeError(f"No runnable source found for {example_id}")
    build_line = f"iverilog -g2001 -o {example_id}.out {' '.join(sources)}"
    run_line = f"vvp {example_id}.out"
    return f"""<div class="code-block code-block--commands" data-copy-root>
  <div class="code-block__header">
    <span class="code-block__file">Terminal</span>
    <button class="copy-btn" type="button" aria-label="Copy build commands">
      <svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>
      <span class="copy-label">Copy</span>
    </button>
  </div>
  <div class="code-block__body">
    <pre><code>{esc(build_line)}
{esc(run_line)}</code></pre>
  </div>
</div>"""


_CODE_RE = re.compile(r"\{\{CODE:([^{}]+)\}\}")
_OUTPUT_RE = re.compile(r"\{\{OUTPUT:([^{}]+)\}\}")
_COMMANDS_RE = re.compile(r"\{\{COMMANDS:([^{}]+)\}\}")
_SNIPPET_RE = re.compile(r"\{\{SNIPPET:([^{}]+)\}\}")


_SNIPPET_HEAD_RE = re.compile(
    r'(<div class="code-block code-block--snippet" data-copy-root>\s*'
    r'<div class="code-block__header">)(.*?)(</div>)',
    re.S,
)


def decorate_snippet_header(match: re.Match) -> str:
    """Give hand-written fragments the same tag and copy control as built ones."""
    head, inner, close = match.group(1), match.group(2), match.group(3)
    if "copy-btn" in inner:
        return match.group(0)

    name = re.sub(r"<[^>]+>", " ", inner)
    name = html.unescape(re.sub(r"\s+", " ", name)).strip() or "code"
    tag = "" if "snippet-tag" in inner else (
        '<span class="snippet-tag">illustrative fragment · not a complete module</span>'
    )
    button = (
        f'<button class="copy-btn" type="button" aria-label="Copy {esc(name)}">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-copy"></use></svg>'
        '<span class="copy-label">Copy</span>'
        "</button>"
    )
    return f"{head}{inner}{tag}{button}{close}"


def expand_content_tokens(content: str) -> str:
    content = _CODE_RE.sub(lambda match: render_code_block(match.group(1).strip()), content)
    content = _OUTPUT_RE.sub(lambda match: render_output_block(match.group(1).strip()), content)
    content = _COMMANDS_RE.sub(lambda match: render_commands(match.group(1).strip()), content)
    content = _SNIPPET_RE.sub(lambda match: render_snippet(match.group(1).strip()), content)
    content = _SNIPPET_HEAD_RE.sub(decorate_snippet_header, content)
    return content


def reading_minutes(content: str) -> int:
    text = re.sub(r"<pre.*?</pre>", " ", content, flags=re.S | re.I)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’._-]*", text))
    return max(4, round(words / 190))


def extract_sections(content: str) -> list[tuple[str, str]]:
    sections = []
    for match in re.finditer(
        r'<h2\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h2>', content, flags=re.S
    ):
        title = re.sub(r"<[^>]+>", "", match.group(2))
        sections.append((match.group(1), html.unescape(title).strip()))
    return sections


def number_lesson_sections(content: str) -> str:
    counter = {"value": 0}

    def replace(match: re.Match) -> str:
        counter["value"] += 1
        return f'<h2 data-index="{counter["value"]:02d}" id="'

    return re.sub(r'<h2\s+id="', replace, content, flags=re.I)


def render_lesson_toc(sections: list[tuple[str, str]]) -> str:
    rows = []
    for index, (anchor, title) in enumerate(sections, start=1):
        rows.append(
            f'<li><a href="#{esc(anchor)}"><span class="toc-num">{index:02d}</span>'
            f'<span>{esc(title)}</span></a></li>'
        )
    return "\n            ".join(rows)


def render_pager(
    unit: dict, topic: dict, previous: tuple[dict, dict] | None, following: tuple[dict, dict] | None
) -> tuple[str, str]:
    def card(direction: str, item: tuple[dict, dict] | None) -> str:
        if item is None:
            return (
                f'<a class="pager-card pager-card--{direction}" href="index.html">'
                f'<span class="pager-kicker">← Theory overview</span>'
                "<strong>All units</strong>"
                "</a>"
            )
        item_unit, item_topic = item
        arrow = "←" if direction == "prev" else "→"
        kicker = f"{arrow} {'Previous' if direction == 'prev' else 'Next'} · Unit {item_unit['number']} · Topic {item_topic['number']:02d}"
        return (
            f'<a class="pager-card pager-card--{direction}" href="{esc(item_topic["id"])}.html">'
            f'<span class="pager-kicker">{kicker}</span>'
            f"<strong>{esc(item_topic['title'])}</strong>"
            "</a>"
        )

    return card("prev", previous), card("next", following)


def lesson_page(topic_id: str) -> dict:
    items = flat_theory_topics()
    index = next((i for i, (_, topic) in enumerate(items) if topic["id"] == topic_id), None)
    if index is None:
        raise RuntimeError(f"Unknown theory topic: {topic_id}")
    unit, topic = items[index]
    previous = items[index - 1] if index > 0 else None
    following = items[index + 1] if index + 1 < len(items) else None

    fragment_path = ROOT / "content" / "lessons" / f"{topic_id}.html"
    if not fragment_path.is_file():
        raise RuntimeError(f"Missing lesson fragment: {fragment_path.relative_to(ROOT)}")
    body = expand_content_tokens(fragment_path.read_text(encoding="utf-8"))
    body = number_lesson_sections(body)
    sections = extract_sections(body)
    if not sections:
        raise RuntimeError(f"Lesson {topic_id} has no h2 sections with ids")

    previous_html, next_html = render_pager(unit, topic, previous, following)
    summary = topic_summary(topic_id)
    replacements = {
        "{{LESSON_ID}}": esc(topic_id),
        "{{LESSON_TITLE}}": esc(topic["title"]),
        "{{LESSON_SUMMARY}}": esc(summary),
        "{{LESSON_UNIT_ID}}": esc(unit["id"]),
        "{{LESSON_UNIT_NUMBER}}": str(unit["number"]),
        "{{LESSON_UNIT_TITLE}}": esc(unit["title"]),
        "{{LESSON_UNIT_TOPICS}}": str(len(unit.get("topics", []))),
        "{{LESSON_UNIT_TOTAL}}": str(len(unit.get("topics", []))),
        "{{LESSON_TOPIC_NUMBER}}": f'{topic["number"]:02d}',
        "{{LESSON_MINUTES}}": str(reading_minutes(body)),
        "{{LESSON_TOC}}": render_lesson_toc(sections),
        "{{LESSON_BODY}}": body,
        "{{LESSON_PREV}}": previous_html,
        "{{LESSON_NEXT}}": next_html,
    }

    rendered = LESSON_SHELL
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)

    return {
        "out": f"theory/{topic_id}.html",
        "content": None,
        "content_html": rendered,
        "title": f'{topic["title"]} — EC-405 Unit {unit["number"]} | Verilog Academy',
        "description": summary,
        "page_class": "page-theory page-lesson",
        "robots": "index, follow",
        "nav": "theory",
        "active": "Theory",
        "extra_head": '<link rel="stylesheet" href="{{ROOT}}css/theory.css">',
        "extra_scripts": '<script type="module" src="{{ROOT}}js/theory.js"></script>',
    }


def theory_pages() -> list[dict]:
    pages = [
        {
            "out": "theory/index.html",
            "content": "content/theory.html",
            "title": "EC-405 Theory Classroom — Verilog Academy",
            "description": "A complete Verilog-2001 classroom for EC-405 Units 1–3: design flow, language rules, gate and dataflow modelling, and behavioural modelling, with verified Icarus Verilog examples.",
            "page_class": "page-theory page-theory-index",
            "robots": "index, follow",
            "nav": "theory",
            "active": "Theory",
            "extra_head": '<link rel="stylesheet" href="{{ROOT}}css/theory.css">',
            "extra_scripts": '<script type="module" src="{{ROOT}}js/theory.js"></script>',
        }
    ]
    pages.extend(lesson_page(topic["id"]) for _, topic in flat_theory_topics())
    return pages


# ---------------------------------------------------------------------------
# EC-410 practical laboratory
# ---------------------------------------------------------------------------

def available_experiments() -> list[dict]:
    return [
        experiment
        for experiment in get_course("ec410")["experiments"]
        if experiment.get("status") == "available"
    ]


def locked_experiments() -> list[dict]:
    return [
        experiment
        for experiment in get_course("ec410")["experiments"]
        if experiment.get("status") == "locked"
    ]


def experiment_meta(experiment_id: str) -> dict:
    return LABS.get("experiments", {}).get(experiment_id, {})


def lab_check_total() -> int:
    return sum(int(experiment_meta(item["id"]).get("vectors", 0)) for item in available_experiments())


def render_lab_cards() -> str:
    cards = []
    for experiment in available_experiments():
        meta = experiment_meta(experiment["id"])
        cards.append(
            f'<a class="lab-card panel" href="{esc(experiment["id"])}.html" '
            f'data-lab-card="{esc(experiment["id"])}" data-reveal>'
            '<span class="lab-card__head">'
            f'<span class="lab-card__num">Experiment {experiment["number"]:02d}</span>'
            '<span class="badge badge-violet" data-lab-state>Not started</span>'
            "</span>"
            f'<h3 class="lab-card__title">{esc(experiment["title"])}</h3>'
            f'<p class="lab-card__summary">{esc(meta.get("summary", ""))}</p>'
            '<span class="lab-card__foot">'
            f'<span class="lab-card__meta">{esc(meta.get("scope", ""))}</span>'
            '<span class="lab-card__open">Open experiment'
            '<svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
            "</span>"
            "</span>"
            "</a>"
        )
    return "\n      ".join(cards)


def render_lab_roadmap() -> str:
    rows = []
    for experiment in locked_experiments():
        rows.append(
            '<li class="lab-roadmap-row">'
            f'<span class="lab-roadmap-num">{experiment["number"]:02d}</span>'
            f'<span class="lab-roadmap-title">{esc(experiment["title"])}</span>'
            '<span class="lab-roadmap-meta">Not published</span>'
            "</li>"
        )
    return "\n        ".join(rows)


def render_experiment_pager(
    experiment: dict, previous: dict | None, following: dict | None
) -> tuple[str, str]:
    def card(direction: str, item: dict | None) -> str:
        if item is None:
            return (
                f'<a class="pager-card pager-card--{direction}" href="index.html">'
                f'<span class="pager-kicker">← Laboratory overview</span>'
                "<strong>All experiments</strong>"
                "</a>"
            )
        arrow = "←" if direction == "prev" else "→"
        word = "Previous" if direction == "prev" else "Next"
        return (
            f'<a class="pager-card pager-card--{direction}" href="{esc(item["id"])}.html">'
            f'<span class="pager-kicker">{arrow} {word} · Experiment {item["number"]:02d}</span>'
            f"<strong>{esc(item['title'])}</strong>"
            "</a>"
        )

    return card("prev", previous), card("next", following)


def experiment_page(experiment_id: str) -> dict:
    experiments = available_experiments()
    index = next(
        (i for i, experiment in enumerate(experiments) if experiment["id"] == experiment_id), None
    )
    if index is None:
        raise RuntimeError(f"Unknown practical experiment: {experiment_id}")
    experiment = experiments[index]
    previous = experiments[index - 1] if index > 0 else None
    following = experiments[index + 1] if index + 1 < len(experiments) else None
    meta = experiment_meta(experiment_id)

    fragment_path = ROOT / "content" / "experiments" / f"{experiment_id}.html"
    if not fragment_path.is_file():
        raise RuntimeError(f"Missing experiment fragment: {fragment_path.relative_to(ROOT)}")
    body = expand_content_tokens(fragment_path.read_text(encoding="utf-8"))
    body = number_lesson_sections(body)
    sections = extract_sections(body)
    if not sections:
        raise RuntimeError(f"Experiment {experiment_id} has no h2 sections with ids")

    previous_html, next_html = render_experiment_pager(experiment, previous, following)
    replacements = {
        "{{EXPERIMENT_ID}}": esc(experiment_id),
        "{{EXPERIMENT_TITLE}}": esc(experiment["title"]),
        "{{EXPERIMENT_SUMMARY}}": esc(meta.get("summary", "")),
        "{{EXPERIMENT_SCOPE}}": esc(meta.get("scope", "")),
        "{{EXPERIMENT_NUMBER}}": f'{experiment["number"]:02d}',
        "{{EXPERIMENT_VECTORS}}": f'{int(meta.get("vectors", 0)):,}',
        "{{EXPERIMENT_TOTAL}}": str(len(experiments)),
        "{{EXPERIMENT_MINUTES}}": str(reading_minutes(body)),
        "{{EXPERIMENT_TOC}}": render_lesson_toc(sections),
        "{{EXPERIMENT_BODY}}": body,
        "{{EXPERIMENT_PREV}}": previous_html,
        "{{EXPERIMENT_NEXT}}": next_html,
    }

    rendered = LAB_SHELL
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)

    return {
        "out": f"labs/{experiment_id}.html",
        "content": None,
        "content_html": rendered,
        "title": f'{experiment["title"]} — EC-410 Experiment {experiment["number"]:02d} | Verilog Academy',
        "description": meta.get("summary", ""),
        "page_class": "page-lab page-lab-lesson",
        "robots": "index, follow",
        "nav": "lab",
        "active": "Laboratory",
        "extra_head": (
            '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
            '<link rel="stylesheet" href="{{ROOT}}css/labs.css">'
        ),
        "extra_scripts": '<script type="module" src="{{ROOT}}js/labs.js"></script>',
    }


def lab_pages() -> list[dict]:
    landing_source = (ROOT / "content" / "labs.html").read_text(encoding="utf-8")
    pages = [
        {
            "out": "labs/index.html",
            "content": None,
            "content_html": expand_content_tokens(landing_source),
            "title": "EC-410 Practical Laboratory — Verilog Academy",
            "description": (
                "Six verified Verilog-2001 experiments for EC-410: basic gates, adders, "
                "subtractors, a four-bit parallel adder, multiplexers and demultiplexers, "
                "each compiled and simulated with Icarus Verilog 13.0."
            ),
            "page_class": "page-lab page-lab-index",
            "robots": "index, follow",
            "nav": "lab",
            "active": "Laboratory",
            "extra_head": (
                '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
                '<link rel="stylesheet" href="{{ROOT}}css/labs.css">'
            ),
            "extra_scripts": '<script type="module" src="{{ROOT}}js/labs.js"></script>',
        }
    ]
    pages.extend(experiment_page(experiment["id"]) for experiment in available_experiments())
    return pages


# ---------------------------------------------------------------------------
# Interactive Circuit Lab
# ---------------------------------------------------------------------------

def circuit_pages() -> list[dict]:
    content = (
        '<script type="application/json" id="circuit-data">'
        + circuit_lab.client_data_json()
        + "</script>\n"
        + circuit_lab.render_lab()
    )
    return [
        {
            "out": "circuit-lab/index.html",
            "content": None,
            "content_html": content,
            "title": "Interactive Circuit Lab — Verilog Academy",
            "description": (
                "Eighteen working digital-logic demonstrations: gates, adders, subtractors, "
                "multiplexers, demultiplexers, encoders, decoders, a comparator and a clocked "
                "D flip-flop, with live SVG diagrams, truth tables and Boolean equations."
            ),
            "page_class": "page-circuit",
            "robots": "index, follow",
            "nav": "circuit",
            "active": "Circuit Lab",
            "extra_head": (
                '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
                '<link rel="stylesheet" href="{{ROOT}}css/circuit-lab.css">'
            ),
            "extra_scripts": '<script type="module" src="{{ROOT}}js/circuit-lab.js"></script>',
        }
    ]


# ---------------------------------------------------------------------------
# Verilog Playground
# ---------------------------------------------------------------------------

def playground_pages() -> list[dict]:
    return [
        {
            "out": "playground/index.html",
            "content": None,
            "content_html": playground_page.render_page(),
            "title": "Verilog Playground — Verilog Academy",
            "description": (
                "A local-first Verilog workbench: edit fourteen verified design and "
                "testbench pairs, download the .v files and compile them with Icarus "
                "Verilog. No browser compiler and no hidden simulation."
            ),
            "page_class": "page-theory page-playground",
            "robots": "index, follow",
            "nav": "site",
            "active": "Playground",
            "extra_head": (
                '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
                '<link rel="stylesheet" href="{{ROOT}}css/playground.css">'
            ),
            "extra_scripts": '<script type="module" src="{{ROOT}}js/playground.js"></script>',
        }
    ]


# ---------------------------------------------------------------------------
# Practice quizzes
# ---------------------------------------------------------------------------

def quiz_pages() -> list[dict]:
    stats = quiz_page.counts()
    return [
        {
            "out": "quizzes/index.html",
            "content": None,
            "content_html": quiz_page.render_page(),
            "title": "Practice Quizzes — Verilog Academy",
            "description": (
                f"{stats['questions']} explained questions across four banks: EC-405 theory, "
                "EC-410 laboratory, Circuit Lab and the Playground workflow. Answers and "
                "explanations appear only after submission, and attempts stay in this browser."
            ),
            "page_class": "page-quiz",
            "robots": "index, follow",
            "nav": "quiz",
            "active": "Quizzes",
            "extra_head": (
                '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
                '<link rel="stylesheet" href="{{ROOT}}css/quizzes.css">'
            ),
            "extra_scripts": '<script type="module" src="{{ROOT}}js/quizzes.js"></script>',
        }
    ]


# ---------------------------------------------------------------------------
# Windows and Android setup guides
# ---------------------------------------------------------------------------

def guide_pages() -> list[dict]:
    shared_head = (
        '<link rel="stylesheet" href="{{ROOT}}css/theory.css">'
        '<link rel="stylesheet" href="{{ROOT}}css/guides.css">'
    )
    return [
        {
            "out": "guides/index.html",
            "content": "content/guides/index.html",
            "title": "Setup Guides — Windows and Android | Verilog Academy",
            "description": (
                "Two honest setup guides: the verified Windows Icarus Verilog and GTKWave "
                "workflow, and what Android can really do with the static Academy site."
            ),
            "page_class": "page-guide page-guide-index",
            "robots": "index, follow",
            "nav": "guide",
            "active": "Guides",
            "extra_head": shared_head,
        },
        {
            "out": "guides/windows.html",
            "content": "content/guides/windows.html",
            "title": "Windows Setup — Icarus Verilog and GTKWave | Verilog Academy",
            "description": (
                "A verified Windows workflow for Verilog simulation: check Icarus Verilog 13.0, "
                "save a design and testbench, compile, run, read the transcript and open a "
                "VCD waveform in GTKWave 3.3.128."
            ),
            "page_class": "page-guide page-guide-windows",
            "robots": "index, follow",
            "nav": "guide",
            "active": "Guides",
            "extra_head": shared_head,
        },
        {
            "out": "guides/android.html",
            "content": "content/guides/android.html",
            "title": "Android Guide — Study and Edit on a Phone | Verilog Academy",
            "description": (
                "Use Verilog Academy on Android: browse theory and laboratory pages, run the "
                "Circuit Lab, edit and download Playground files, keep local progress and export "
                "a backup. Compilation stays on the Windows PC."
            ),
            "page_class": "page-guide page-guide-android",
            "robots": "index, follow",
            "nav": "guide",
            "active": "Guides",
            "extra_head": shared_head,
        },
    ]


def render_unit_rows() -> str:
    rows = []
    for unit in get_course("ec405")["units"]:
        if unit.get("status") != "available":
            continue
        topics = len(unit.get("topics", []))
        rows.append(
            '<li class="track-row">'
            f'<span class="track-row__code">Unit {unit["number"]}</span>'
            f'<span class="track-row__title">{esc(unit["title"])}</span>'
            f'<span class="track-row__meta">{topics} topics</span>'
            "</li>"
        )
    return "\n                ".join(rows)


def render_locked_unit_rows() -> str:
    rows = []
    for unit in get_course("ec405")["units"]:
        if unit.get("status") != "locked":
            continue
        rows.append(
            '<li class="track-row is-locked">'
            f'<span class="track-row__code">Unit {unit["number"]}</span>'
            f'<span class="track-row__title">{esc(unit["title"])}</span>'
            '<span class="track-row__meta">Roadmap</span>'
            "</li>"
        )
    return "\n                ".join(rows)


def render_experiment_rows() -> str:
    rows = []
    for experiment in get_course("ec410")["experiments"]:
        if experiment.get("status") != "available":
            continue
        rows.append(
            '<li class="track-row track-row--lab">'
            f'<span class="track-row__code">Exp {experiment["number"]:02d}</span>'
            f'<span class="track-row__title">{esc(experiment["title"])}</span>'
            "</li>"
        )
    return "\n                ".join(rows)


def render_locked_experiment_row() -> str:
    experiments = [experiment for experiment in get_course("ec410")["experiments"] if experiment.get("status") == "locked"]
    if not experiments:
        return ""
    first = experiments[0]["number"]
    last = experiments[-1]["number"]
    return (
        '<li class="track-row is-locked">'
        f'<span class="track-row__code">Exp {first:02d}–{last}</span>'
        '<span class="track-row__title">Reserved for the next release</span>'
        '<span class="track-row__meta">Roadmap</span>'
        "</li>"
    )


def render_dashboard_theory_units() -> str:
    blocks = []
    for unit in get_course("ec405")["units"]:
        if unit.get("status") != "available":
            continue
        topics = unit.get("topics", [])
        rows = []
        for topic in topics:
            rows.append(
                f'<li class="topic-row" id="topic-{esc(topic["id"])}">'
                '<label class="check-row">'
                f'<input class="check-input" type="checkbox" data-kind="theory" data-id="{esc(topic["id"])}" data-unit="{esc(unit["id"])}" disabled>'
                '<span class="check-box" aria-hidden="true">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
                "</span>"
                '<span class="check-text">'
                f'<span class="check-title">{esc(topic["title"])}</span>'
                f'<span class="check-meta">Topic {topic["number"]:02d}</span>'
                "</span>"
                "</label>"
                "</li>"
            )
        blocks.append(
            f'<article class="unit-block" data-unit-block="{esc(unit["id"])}">'
            '<header class="unit-block__head">'
            '<div class="unit-block__id">'
            f'<span class="unit-index">Unit {unit["number"]:02d}</span>'
            f'<h4 class="unit-title">{esc(unit["title"])}</h4>'
            "</div>"
            '<div class="unit-meter">'
            f'<span class="unit-count" data-unit-count="{esc(unit["id"])}">0 / {len(topics)}</span>'
            f'<div class="progress unit-progress" role="progressbar" aria-label="Unit {unit["number"]} progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-unit-bar="{esc(unit["id"])}">'
            f'<span class="progress-fill" data-unit-fill="{esc(unit["id"])}" style="--progress: 0%"></span>'
            "</div>"
            "</div>"
            "</header>"
            '<ul class="topic-list">' + "".join(rows) + "</ul>"
            "</article>"
        )
    return "\n                ".join(blocks)


def render_dashboard_experiments() -> str:
    rows = []
    for experiment in get_course("ec410")["experiments"]:
        if experiment.get("status") != "available":
            continue
        rows.append(
            f'<li class="topic-row experiment-row" id="lab-{esc(experiment["id"])}">'
            '<label class="check-row">'
            f'<input class="check-input" type="checkbox" data-kind="practical" data-id="{esc(experiment["id"])}" disabled>'
            '<span class="check-box" aria-hidden="true">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
            "</span>"
            '<span class="check-text">'
            f'<span class="check-title">{esc(experiment["title"])}</span>'
            f'<span class="check-meta">Experiment {experiment["number"]:02d} · EC-410</span>'
            "</span>"
            "</label>"
            "</li>"
        )
    return "\n                ".join(rows)


def render_dashboard_locked_units() -> str:
    rows = []
    for unit in get_course("ec405")["units"]:
        if unit.get("status") != "locked":
            continue
        rows.append(
            '<li class="roadmap-item">'
            f'<span class="roadmap-code">Unit {unit["number"]:02d}</span>'
            f'<span class="roadmap-title">{esc(unit["title"])}</span>'
            f'<span class="roadmap-meta">{unit["periods"]} periods</span>'
            "</li>"
        )
    return "\n                ".join(rows)


def render_dashboard_locked_experiments() -> str:
    experiments = [experiment for experiment in get_course("ec410")["experiments"] if experiment.get("status") == "locked"]
    if not experiments:
        return ""
    first = experiments[0]["number"]
    last = experiments[-1]["number"]
    return (
        '<li class="roadmap-item">'
        f'<span class="roadmap-code">Exp {first:02d}–{last}</span>'
        '<span class="roadmap-title">Reserved for the next release</span>'
        f'<span class="roadmap-meta">{len(experiments)} experiments</span>'
        "</li>"
    )


def curriculum_counts() -> dict[str, int]:
    ec405 = get_course("ec405")
    ec410 = get_course("ec410")
    available_units = [unit for unit in ec405["units"] if unit.get("status") == "available"]
    available_labs = [experiment for experiment in ec410["experiments"] if experiment.get("status") == "available"]
    locked_labs = [experiment for experiment in ec410["experiments"] if experiment.get("status") == "locked"]

    return {
        "theory_topics": sum(len(unit.get("topics", [])) for unit in available_units),
        "available_units": len(available_units),
        "labs": len(available_labs),
        "locked_labs": len(locked_labs),
        "ec405_periods": int(ec405["totalPeriods"]),
        "ec410_periods": int(ec410["totalPeriods"]),
        "circuits": int(SITE.get("counts", {}).get("circuits", 0)),
        "playground": int(SITE.get("counts", {}).get("playground", 0)),
        "quizzes": int(SITE.get("counts", {}).get("quizzes", 0)),
        "quiz_categories": int(SITE.get("counts", {}).get("quizCategories", 0)),
    }


PAGES = [
    {
        "out": "index.html",
        "content": "content/index.html",
        "title": "Verilog Academy — Digital Logic and Verilog HDL",
        "description": "A structured engineering course in digital logic and Verilog HDL for SBTET C-23 ECE. Study EC-405 theory and verify designs in the EC-410 laboratory.",
        "page_class": "page-home",
        "robots": "index, follow",
        "nav": "home",
        "active": None,
        "extra_head": '<link rel="stylesheet" href="{{ROOT}}css/home.css">',
    },
    {
        "out": "dashboard.html",
        "content": "content/dashboard.html",
        "title": "Learning Dashboard — Verilog Academy",
        "description": "Your local Verilog Academy workspace: EC-405 theory and EC-410 practical progress, continue-learning, recent activity and validated progress backups.",
        "page_class": "page-dashboard",
        "robots": "index, follow",
        "nav": "dashboard",
        "active": "Dashboard",
        "extra_head": '<link rel="stylesheet" href="{{ROOT}}css/dashboard.css">',
        "extra_scripts": '<script type="module" src="{{ROOT}}js/dashboard.js"></script>',
    },
    {
        "out": "styleguide.html",
        "content": "content/styleguide.html",
        "title": "Component Library — Verilog Academy",
        "description": "The Verilog Academy design system: tokens, typography, components, patterns, motion and implementation notes.",
        "page_class": "page-styleguide",
        "robots": "noindex, nofollow",
        "nav": "design",
        "active": None,
    },
]


def build_page(page: dict, counts: dict[str, int]) -> Path:
    out_path = page["out"]
    if page.get("content_html"):
        content = page["content_html"]
    else:
        content = (ROOT / page["content"]).read_text(encoding="utf-8")
    prefix = relative_prefix(out_path)
    nav_items = SITE["navigation"][page["nav"]]
    active = page.get("active")

    replacements = {
        "{{CONTENT}}": content,
        "{{ROOT}}": prefix,
        "{{TITLE}}": esc(page["title"]),
        "{{DESCRIPTION}}": esc(page["description"]),
        "{{PAGE_CLASS}}": esc(page["page_class"]),
        "{{ROBOTS}}": esc(page["robots"]),
        "{{NAV}}": render_nav(nav_items, out_path, active),
        "{{MOBILE_NAV}}": render_mobile_nav(nav_items, out_path, active),
        "{{FOOTER}}": render_footer(out_path),
        "{{ICON_SPRITE}}": ICON_SPRITE,
        "{{EXTRA_HEAD}}": page.get("extra_head", ""),
        "{{EXTRA_SCRIPTS}}": page.get("extra_scripts", ""),
        "{{THEORY_TOPIC_COUNT}}": str(counts["theory_topics"]),
        "{{EC405_TOPIC_COUNT}}": str(counts["theory_topics"]),
        "{{LAB_COUNT}}": str(counts["labs"]),
        "{{EC410_EXPERIMENT_COUNT}}": str(counts["labs"]),
        "{{EC410_LOCKED_COUNT}}": str(counts["locked_labs"]),
        "{{CIRCUIT_COUNT}}": str(counts["circuits"]),
        "{{PG_EXAMPLE_COUNT}}": str(counts["playground"]),
        "{{QUIZ_CATEGORY_COUNT}}": str(counts["quiz_categories"]),
        "{{QUIZ_QUESTION_COUNT}}": str(counts["quizzes"]),
        "{{UNIT_COUNT}}": str(counts["available_units"]),
        "{{EC405_UNIT_COUNT}}": str(counts["available_units"]),
        "{{EC405_PERIODS}}": str(counts["ec405_periods"]),
        "{{EC410_PERIODS}}": str(counts["ec410_periods"]),
        "{{EC405_UNITS}}": render_unit_rows(),
        "{{EC405_LOCKED_UNITS}}": render_locked_unit_rows(),
        "{{EC410_EXPERIMENTS}}": render_experiment_rows(),
        "{{EC410_LOCKED_EXPERIMENTS}}": render_locked_experiment_row(),
        "{{DASHBOARD_THEORY_TOTAL}}": str(counts["theory_topics"]),
        "{{DASHBOARD_PRACTICAL_TOTAL}}": str(counts["labs"]),
        "{{DASHBOARD_TOTAL_ITEMS}}": str(counts["theory_topics"] + counts["labs"]),
        "{{DASHBOARD_THEORY_UNITS}}": render_dashboard_theory_units(),
        "{{DASHBOARD_EXPERIMENTS}}": render_dashboard_experiments(),
        "{{DASHBOARD_LOCKED_UNITS}}": render_dashboard_locked_units(),
        "{{DASHBOARD_LOCKED_EXPERIMENTS}}": render_dashboard_locked_experiments(),
        "{{THEORY_UNIT_CARDS}}": render_theory_unit_cards(),
        "{{THEORY_ROADMAP}}": render_theory_roadmap(),
        "{{THEORY_AVAILABLE_PERIODS}}": str(theory_available_periods()),
        "{{THEORY_TOTAL_TOPICS}}": str(counts["theory_topics"]),
        "{{LAB_TOTAL}}": str(counts["labs"]),
        "{{LAB_CHECK_TOTAL}}": f"{lab_check_total():,}",
        "{{LAB_PERIODS}}": str(counts["ec410_periods"]),
        "{{LAB_TOOL_VERSION}}": esc(LABS["toolchain"]["version"]),
        "{{LAB_TOOL_MODE}}": esc(LABS["toolchain"]["mode"]),
        "{{LAB_LOCKED_FIRST}}": (
            f'{locked_experiments()[0]["number"]:02d}' if locked_experiments() else ""
        ),
        "{{LAB_LOCKED_LAST}}": (
            f'{locked_experiments()[-1]["number"]:02d}' if locked_experiments() else ""
        ),
        "{{LAB_LOCKED_COUNT}}": str(counts["locked_labs"]),
        "{{LAB_CARDS}}": render_lab_cards(),
        "{{LAB_ROADMAP}}": render_lab_roadmap(),
        "{{CURRICULUM_JSON}}": json.dumps(CURRICULUM, separators=(",", ":")).replace("</", "<\\/"),
        "{{EC405_TITLE}}": esc(get_course("ec405")["title"]),
        "{{EC410_TITLE}}": esc(get_course("ec410")["title"]),
        "{{YEAR}}": str(date.today().year),
        "{{BUILD_DATE}}": date.today().isoformat(),
    }

    rendered = SHELL
    # Two passes let fragments inserted through {{CONTENT}} resolve their own
    # tokens (for example {{ROOT}}) without requiring a second template file.
    for _ in range(2):
        for token, value in replacements.items():
            rendered = rendered.replace(token, value)

    leftover = sorted(set(re.findall(r"\{\{[^{}\n]+\}\}", rendered)))
    if leftover:
        raise RuntimeError(f"Unreplaced template tokens in {out_path}: {leftover}")

    destination = ROOT / out_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8", newline="\n")
    return destination


def main() -> None:
    counts = curriculum_counts()
    if counts["circuits"] != len(circuit_lab.CIRCUITS):
        raise RuntimeError(
            f"site.json says {counts['circuits']} circuits but data/circuits.json has "
            f"{len(circuit_lab.CIRCUITS)}"
        )
    if counts["playground"] != len(playground_page.EXAMPLES):
        raise RuntimeError(
            f"site.json says {counts['playground']} playground projects but "
            f"data/playground.json has {len(playground_page.EXAMPLES)}"
        )
    quiz_stats = quiz_page.counts()
    if counts["quizzes"] != quiz_stats["questions"]:
        raise RuntimeError(
            f"site.json says {counts['quizzes']} quiz questions but "
            f"data/quizzes.json has {quiz_stats['questions']}"
        )
    if counts["quiz_categories"] != quiz_stats["categories"]:
        raise RuntimeError(
            f"site.json says {counts['quiz_categories']} quiz categories but "
            f"data/quizzes.json has {quiz_stats['categories']}"
        )
    pages = (
        PAGES
        + theory_pages()
        + lab_pages()
        + circuit_pages()
        + playground_pages()
        + quiz_pages()
        + guide_pages()
    )
    built = []
    for page in pages:
        built.append(build_page(page, counts))
    truth_tables = circuit_lab.write_truth_tables(ROOT / "circuit-lab" / "data")

    print("Verilog Academy — static build")
    print(f"  Theory topics : {counts['theory_topics']}")
    print(f"  Units         : {counts['available_units']}")
    print(f"  Labs          : {counts['labs']} available, {counts['locked_labs']} roadmap")
    print(f"  Circuit demos : {counts['circuits']} ({len(truth_tables)} truth tables)")
    print(f"  Lesson pages  : {len(flat_theory_topics())}")
    print(f"  Lab pages     : {len(available_experiments()) + 1}")
    print(f"  Circuit pages : 1")
    print(f"  Playground    : {counts['playground']} projects")
    print(f"  Quizzes       : {counts['quizzes']} questions in {counts['quiz_categories']} banks")
    print(f"  Guides        : 2 platform guides + hub")
    for path in built:
        print(f"  built         : {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
