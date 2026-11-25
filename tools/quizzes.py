#!/usr/bin/env python3
"""Quiz data loader and page renderer for Verilog Academy."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "quizzes.json"
DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))
CATEGORIES = DATA["categories"]
ALLOWED_TYPES = {
    "Multiple choice",
    "Code output",
    "Truth-table interpretation",
    "Boolean expression",
    "Verilog syntax",
    "Identify the error",
    "Practical viva",
}
ALLOWED_ICONS = {"book", "flask", "circuit", "code"}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def validate() -> None:
    if DATA.get("version") != 1:
        raise RuntimeError("data/quizzes.json version must be 1")
    if DATA.get("storageKey") != "va.quizzes":
        raise RuntimeError("data/quizzes.json storageKey must be va.quizzes")
    if not isinstance(CATEGORIES, list) or len(CATEGORIES) != 4:
        raise RuntimeError("Expected exactly four quiz categories")

    ids: set[str] = set()
    prompts: set[str] = set()
    for category in CATEGORIES:
        cid = category.get("id")
        if not isinstance(cid, str) or not cid:
            raise RuntimeError("Every quiz category needs an id")
        if category.get("icon") not in ALLOWED_ICONS:
            raise RuntimeError(f"{cid}: unsupported icon")
        questions = category.get("questions")
        if not isinstance(questions, list) or len(questions) < 10:
            raise RuntimeError(f"{cid}: needs at least ten questions")
        for question in questions:
            qid = question.get("id")
            if not isinstance(qid, str) or not qid:
                raise RuntimeError(f"{cid}: question without id")
            if qid in ids:
                raise RuntimeError(f"Duplicate question id: {qid}")
            ids.add(qid)
            prompt = str(question.get("prompt", "")).strip()
            key = " ".join(prompt.lower().split())
            if not prompt or key in prompts:
                raise RuntimeError(f"{qid}: empty or duplicate prompt")
            prompts.add(key)
            if question.get("type") not in ALLOWED_TYPES:
                raise RuntimeError(f"{qid}: unsupported type {question.get('type')!r}")
            options = question.get("options")
            if not isinstance(options, list) or len(options) != 4:
                raise RuntimeError(f"{qid}: needs four options")
            if len({str(option).strip().lower() for option in options}) != 4:
                raise RuntimeError(f"{qid}: options are not unique")
            answer = question.get("answer")
            if not isinstance(answer, int) or answer < 0 or answer > 3:
                raise RuntimeError(f"{qid}: answer must be an index from 0 to 3")
            explanation = str(question.get("explanation", "")).strip()
            if len(explanation) < 20:
                raise RuntimeError(f"{qid}: explanation is too short")
            table = question.get("table")
            if table is not None:
                headers = table.get("headers")
                rows = table.get("rows")
                if not isinstance(headers, list) or not headers:
                    raise RuntimeError(f"{qid}: table headers are missing")
                if not isinstance(rows, list) or not rows:
                    raise RuntimeError(f"{qid}: table rows are missing")
                for row in rows:
                    if not isinstance(row, list) or len(row) != len(headers):
                        raise RuntimeError(f"{qid}: table row width mismatch")

    if len(ids) < 40:
        raise RuntimeError("The quiz bank should contain at least 40 questions")


def counts() -> dict[str, int]:
    return {
        "categories": len(CATEGORIES),
        "questions": sum(len(category["questions"]) for category in CATEGORIES),
        "types": len({q["type"] for c in CATEGORIES for q in c["questions"]}),
    }


def render_category_cards() -> str:
    cards = []
    for category in CATEGORIES:
        cid = category["id"]
        count = len(category["questions"])
        cards.append(
            f'<button class="quiz-category-card panel" type="button" '
            f'data-quiz-category="{esc(cid)}" aria-pressed="false">'
            '<span class="quiz-category-card__top">'
            f'<span class="quiz-category-card__icon"><svg class="icon" aria-hidden="true"><use href="#icon-{esc(category["icon"])}"></use></svg></span>'
            f'<span class="badge badge-cyan">{esc(category["kicker"])}</span>'
            "</span>"
            f'<span class="quiz-category-card__title">{esc(category["title"])}</span>'
            f'<span class="quiz-category-card__text">{esc(category["description"])}</span>'
            '<span class="quiz-category-card__foot">'
            f'<span>{count} questions</span>'
            f'<span data-quiz-best="{esc(cid)}">No attempts yet</span>'
            '<span class="quiz-category-card__open">Open bank'
            '<svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>'
            "</span>"
            "</span>"
            "</button>"
        )
    return "\n        ".join(cards)


def render_page() -> str:
    validate()
    stats = counts()
    payload = json.dumps(DATA, separators=(",", ":")).replace("</", "<\\/")
    return f"""<script type="application/json" id="quiz-data">{payload}</script>

<section class="quiz-hero">
  <div class="quiz-hero__atmosphere" aria-hidden="true"></div>
  <div class="container quiz-hero__grid">
    <div class="quiz-hero__copy" data-reveal>
      <span class="eyebrow">Practice quizzes</span>
      <h1 class="display">Test the circuit<br><span class="gradient-text">in your head.</span></h1>
      <p class="lede">Four independent question banks for the published curriculum: EC-405 theory, EC-410 laboratory, the 18 Circuit Lab demonstrations and the Playground workflow. Every answer has an explanation, and nothing is revealed until you submit.</p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="#quiz-runner" data-quiz-start="theory">
          Start with Theory
          <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
        </a>
        <a class="btn btn-secondary btn-lg" href="#quiz-categories">
          Choose a category
          <svg class="icon" aria-hidden="true"><use href="#icon-chevron-down"></use></svg>
        </a>
      </div>
      <div class="hero-facts theory-facts" aria-label="Quiz scope">
        <div><strong>{stats["categories"]:02d}</strong><span>Question banks</span></div>
        <div><strong>{stats["questions"]}</strong><span>Questions</span></div>
        <div><strong>{stats["types"]}</strong><span>Question types</span></div>
        <div><strong>0</strong><span>Progress changes</span></div>
      </div>
    </div>

    <aside class="quiz-boundary panel" data-reveal style="--reveal-delay: 100ms">
      <div class="quiz-boundary__head">
        <span class="panel-kicker">Honest practice</span>
        <span class="badge badge-warning">Local only</span>
      </div>
      <h2>No grades. No fake streaks.</h2>
      <ul class="quiz-boundary__list">
        <li><strong>Answers stay hidden</strong> until you press Submit answers.</li>
        <li><strong>Results are yours.</strong> Attempts are stored under <code>va.quizzes</code> in this browser.</li>
        <li><strong>Progress is separate.</strong> A quiz attempt never marks a theory topic or experiment complete.</li>
        <li><strong>Retry is free.</strong> Keep the attempt history and review any saved result.</li>
      </ul>
      <p class="quiz-boundary__note">These questions check understanding of the published Units 1–3 and Experiments 1–6. They do not include locked Units 4–5 or Experiments 7–15.</p>
    </aside>
  </div>
</section>

<section class="section-tight quiz-categories" id="quiz-categories">
  <div class="container">
    <div class="section-header" data-reveal>
      <div>
        <span class="eyebrow">01 / Choose a bank</span>
        <h2>Practise one area at a time.</h2>
      </div>
      <p>Each bank has its own questions, score and attempt history. Switching banks never mixes one result with another.</p>
    </div>
    <div class="quiz-category-grid">
      {render_category_cards()}
    </div>
  </div>
</section>

<section class="section quiz-runner-section" id="quiz-runner">
  <div class="container">
    <div class="section-header" data-reveal>
      <div>
        <span class="eyebrow">02 / The quiz</span>
        <h2 data-quiz-heading>EC-405 Theory</h2>
      </div>
      <p data-quiz-intro>Answer every question, then submit to see your score and explanations.</p>
    </div>

    <div class="quiz-shell">
      <div class="quiz-main panel" data-quiz-main>
        <header class="quiz-runner-head">
          <div>
            <span class="panel-kicker" data-quiz-kicker>Units 1–3</span>
            <h3 data-quiz-title>EC-405 Theory</h3>
          </div>
          <span class="badge" data-quiz-status>Ready to start</span>
        </header>

        <div class="quiz-instructions" data-quiz-instructions>
          <svg class="icon" aria-hidden="true"><use href="#icon-info"></use></svg>
          <p>Choose one answer per question. Use Previous and Next to move through the bank. You can change answers until you submit. Each question is worth one mark; unanswered questions are marked incorrect. Correct answers and explanations appear only after submission.</p>
        </div>

        <div class="quiz-meter-row">
          <span data-quiz-position>Question 1 of 12</span>
          <div class="progress quiz-progress" role="progressbar" aria-label="Quiz progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-quiz-progress>
            <span class="progress-fill" data-quiz-progress-fill style="--progress: 0%"></span>
          </div>
          <span data-quiz-answered>0 answered</span>
        </div>

        <div class="quiz-question" data-quiz-question aria-live="polite"></div>

        <div class="quiz-nav">
          <button class="btn btn-secondary btn-sm" type="button" data-quiz-prev>
            <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
            Previous
          </button>
          <div class="quiz-palette" data-quiz-palette aria-label="Question navigation"></div>
          <button class="btn btn-secondary btn-sm" type="button" data-quiz-next>
            Next
            <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
          </button>
        </div>

        <div class="quiz-submit-row">
          <button class="btn btn-primary" type="button" data-quiz-submit>Submit answers</button>
          <button class="btn btn-secondary" type="button" data-quiz-retry hidden>Retry quiz</button>
          <button class="btn btn-ghost" type="button" data-quiz-review hidden>Review answers</button>
          <p class="quiz-warning" data-quiz-warning role="status"></p>
        </div>
      </div>

      <aside class="quiz-rail">
        <section class="panel quiz-result" data-quiz-result aria-live="polite">
          <span class="panel-kicker">Your result</span>
          <h3>No attempt yet.</h3>
          <p>Choose a category, answer the questions and submit. Your score and explanations will appear here.</p>
        </section>

        <section class="panel quiz-history" aria-labelledby="quiz-history-title">
          <div class="quiz-history__head">
            <div>
              <span class="panel-kicker">Saved attempts</span>
              <h3 id="quiz-history-title">History</h3>
            </div>
            <span class="badge" data-quiz-attempt-count>0</span>
          </div>
          <div data-quiz-history>
            <p class="quiz-empty">No saved attempts for this category yet.</p>
          </div>
          <p class="quiz-history__note">Attempts are stored only in this browser. Clear the key with your browser’s site-data controls if you want a fresh history.</p>
        </section>

        <section class="panel quiz-help">
          <span class="panel-kicker">Keep going</span>
          <h3>Need the local toolchain?</h3>
          <p>The Playground prepares files; your computer runs them. Follow the verified Windows workflow for Icarus Verilog and GTKWave.</p>
          <div class="quiz-help__links">
            <a class="text-link" href="{{{{ROOT}}}}guides/windows.html">Windows PC setup guide <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-right"></use></svg></a>
            <a class="text-link" href="{{{{ROOT}}}}guides/android.html">Android guide <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-right"></use></svg></a>
          </div>
        </section>
      </aside>
    </div>
  </div>
</section>

<section class="section-tight quiz-method" id="quiz-method">
  <div class="container">
    <div class="section-header" data-reveal>
      <div>
        <span class="eyebrow">03 / How to use it</span>
        <h2>Answer. Submit. Read the reason.</h2>
      </div>
      <p>The score is a checkpoint, not a completion record. Use the explanation to repair the idea, then retry the bank.</p>
    </div>
    <div class="quiz-method-grid">
      <article class="quiz-method-card panel" data-reveal>
        <span class="quiz-method-card__num">01</span>
        <h3>Choose the bank</h3>
        <p>Theory, Laboratory, Circuit Lab and Playground are independent. Start with the area you are studying now.</p>
      </article>
      <article class="quiz-method-card panel" data-reveal style="--reveal-delay: 60ms">
        <span class="quiz-method-card__num">02</span>
        <h3>Commit to an answer</h3>
        <p>Select one option per question. The page does not mark anything until you submit the whole bank.</p>
      </article>
      <article class="quiz-method-card panel" data-reveal style="--reveal-delay: 120ms">
        <span class="quiz-method-card__num">03</span>
        <h3>Review the explanation</h3>
        <p>Every question explains the correct idea. Review a saved attempt at any time, or retry without losing the history.</p>
      </article>
    </div>
    <div class="quiz-storage-note panel" data-reveal>
      <svg class="icon" aria-hidden="true"><use href="#icon-shield"></use></svg>
      <p><strong>Storage boundary:</strong> quiz attempts live under <code>va.quizzes</code>. Lesson and experiment completion remains under <code>va.progress</code>, and Playground drafts remain under <code>va.playground.drafts</code>. None of these keys overwrite another.</p>
    </div>
  </div>
</section>
"""
