# Phase 08 — Practice quizzes and platform guides

**Status:** release candidate, awaiting owner review  
**Date:** 25 November 2026  
**Site version:** Phase 08  
**Publication state:** not published, not deployed, no public repository created

> **Post-audit update (2026-11-25):** the font-licensing gap noted in section 6
> has been closed. `assets/fonts/OFL-1.1.txt` now carries the three copyright
> notices and the full SIL OFL 1.1 text, and `assets/fonts/README.md` records
> each file's embedded version and provenance. See
> [`../final-audit/REPORT.md`](../final-audit/REPORT.md).

---

## 1. Outcome

Phase 08 adds two connected pieces to the existing Academy without changing the
curriculum or the progress model:

1. **Four practice quiz banks** with 46 explained questions, one-question
   navigation, submit/review, retry and independent local attempt history.
2. **A guide hub plus separate Windows and Android guides**, written against
   the software that is actually installed here and explicit about what is
   optional, absent or impossible on a phone.

The Phase 1–7 pages, EC-405 Units 1–3, EC-410 Experiments 1–6, Circuit Lab and
Playground behaviour were preserved. EC-405 Units 4–5 and EC-410 Experiments
7–15 remain locked and page-less. Quiz attempts do not write `va.progress` and
do not mark any lesson or experiment complete.

---

## 2. Quiz coverage and behaviour

### 2.1 Banks

| Bank | Scope | Questions |
|---|---|---:|
| `theory` | EC-405 Units 1–3: HDL role, nets, data types, operators, gate primitives, delays, dataflow, modules, testbenches | 12 |
| `laboratory` | EC-410 Experiments 1–6: gates, adders, subtractors, ripple carry, multiplexers, demultiplexers | 12 |
| `circuit-lab` | The 18 Circuit Lab demonstrations and ideal-logic limits | 11 |
| `playground` | Playground files, editing, drafts, downloads and the local Icarus workflow | 11 |
| **Total** | | **46** |

### 2.2 Question types

| Type | Count |
|---|---:|
| Multiple choice | 20 |
| Code-output prediction | 6 |
| Truth-table interpretation | 5 |
| Boolean expression | 4 |
| Verilog syntax | 4 |
| Identify the error | 3 |
| Practical viva | 4 |
| **Total** | **46** |

All 46 question ids and prompts are unique. Every question has exactly four
distinct options, one valid answer index and a substantive explanation. No
question refers to EC-405 Units 4–5 or EC-410 Experiments 7–15. Truth-table
questions carry explicit headers and rows whose widths are validated at build
and verification time.

### 2.3 Learner flow

- A category card states the scope and question count before starting.
- Each question is numbered (`Question n of N`) and labelled with its type.
- Options are buttons, so they work with mouse, touch and keyboard.
- Previous/Next move through the bank; answers can be changed until submit.
- A question palette shows answered, current, correct and incorrect state.
- The first submit with unanswered questions warns and does **not** save an
  attempt; a second submit is required to confirm.
- Answers, correct-option styling and explanations are never present in the DOM
  before submission. Verification checks this for all four banks.
- The result shows raw score, percentage, answered count and per-question
  review. Unanswered questions are reported as unanswered, not silently wrong.
- Retry clears answers and the current result but keeps saved history.
- Saved attempts can be reopened in an explicit review mode.
- An empty state appears when a bank has no history.

### 2.4 Storage

| Key | Schema | Purpose |
|---|---|---|
| `va.quizzes` | `verilog-academy.quizzes`, version 1 | Quiz attempt history only |
| `va.progress` | `verilog-academy.progress`, version 1 | Lesson/experiment completion, untouched by quizzes |
| `va.playground.drafts` | existing Playground schema | Editor drafts, untouched by quizzes |
| `va.theme` | existing theme value | Theme choice |

Attempts are capped per bank, normalised on read, and invalid JSON, an
unsupported version or a malformed attempt falls back to an empty history with
a visible recovery message. Verification seeds `va.progress` and
`va.playground.drafts` with sentinels, runs every quiz flow, and confirms both
are byte-identical afterwards.

---

## 3. Guides

### 3.1 Hub

`guides/index.html` explains the two paths and links to both platform pages. It
is reachable from the footer, the homepage toolchain section, the quiz page and
the Playground guidance, without adding a second crowded header group on every
page.

### 3.2 Windows guide

`guides/windows.html` covers:

- the whole workflow in six commands;
- the separate roles of Icarus Verilog (`iverilog`), the runtime (`vvp`) and
  GTKWave;
- installation/version checks and the GTKWave version quirk;
- one project folder and the correct `.v` extensions;
- saving `design.v` and `tb.v`;
- compile, run and transcript reading;
- `$dumpfile` / `$dumpvars`, VCD generation and opening the wave;
- troubleshooting in tool order;
- an explicit installed/optional/absent table;
- a real Academy example with captured output.

Verified on this machine:

| Tool | Evidence |
|---|---|
| Icarus Verilog | 13.0 stable, `iverilog -V` |
| `vvp` | 13.0 |
| GTKWave | package `3.3.128-1` (`pacman -Q` and `where.exe`; `--version` prints nothing on this UCRT64 build) |
| Python | 3.14.7 at `C:\msys64\ucrt64\bin\python.exe` |
| VS Code | installed |

Explicitly **not installed**: Verilator, Vivado, Xilinx ISE, ModelSim,
Notepad++. The guide does not claim any of them is present. A real demo run
produced a VCD and the expected transcript, including
`VCD info: dumpfile and-gate.vcd opened for output.` and
`tb.v:20: $finish called at 4000 (1ps)`.

### 3.3 Android guide

`guides/android.html` covers browsing and course navigation, the Circuit Lab,
Playground editing/copy/download, the four quiz banks, local progress and
backups, the mobile layout, phone-specific troubleshooting, and the real
compilation boundary.

It states plainly that the static site has no server-side compiler, no
WebAssembly Verilog engine and no bundled simulator, that Icarus is installed
here as a Windows UCRT64 program, that this release does not ship an Android
build, and that an unverified Termux installation is not documented. It also
records the evidence limit: the phone layout was verified in Chrome device
emulation at 360–412 px, not on a physical Android handset.

---

## 4. Files

### Added

| File | Purpose |
|---|---|
| `data/quizzes.json` | 46-question bank, answers and explanations |
| `tools/quizzes.py` | Validation, counts and quiz page renderer |
| `js/quizzes.js` | Quiz runner, scoring, review, retry, `va.quizzes` storage |
| `css/quizzes.css` | Quiz hero, cards, runner, palette, history, responsive rules |
| `css/guides.css` | Guide hero, status, sticky contents, code, tables, cards, limits |
| `content/guides/index.html` | Guide hub |
| `content/guides/windows.html` | Windows setup guide |
| `content/guides/android.html` | Android usage and limits guide |
| `tools/browser_audit.py` | Dependency-free Chrome DevTools Protocol helper |
| `tools/verify_phase8.py` | Static, browser, responsive, quiz, UI and screenshot audit |
| `.gitignore` | Python, simulation, OS and scratch-file hygiene |
| `docs/phase8/screenshots/` | 16 verification screenshots |
| `docs/phase8/REPORT.md` | This report |

### Modified

| File | Change |
|---|---|
| `tools/build.py` | Registers quiz and guide pages; adds counts/tokens; build-time count checks |
| `data/site.json` | Quizzes and Guides navigation, footer links, quiz counts |
| `css/components.css` | Added the danger badge variant used by guides |
| `css/home.css` | Toolchain action row for the two guides |
| `css/layout.css` | Header collapses below 1080 px; compact 1081–1240 px nav; wordmark no longer shrinks |
| `content/index.html` | Guide links in the toolchain section; removed a duplicate `id="top"` |
| `content/dashboard.html` | Removed a duplicate `id="top"` |
| `README.md` | Phase 08 status, quiz/guide sections, verification commands, layout, storage and scope |

Generated output: `quizzes/index.html`, `guides/index.html`,
`guides/windows.html`, `guides/android.html`, plus rebuilt homepage,
dashboard and shared pages.

---

## 5. Verification results

All commands below were run from the project root with
`C:\msys64\ucrt64\bin\python.exe`.

### 5.1 Build and curriculum

- Build completed with **40 generated HTML pages**:
  23 theory topics + 1 theory index, 6 experiments + 1 lab index, 1 Circuit
  Lab, 1 Playground, 1 quiz page, 3 guide pages, homepage, dashboard and
  styleguide.
- Counts: 23 EC-405 topics, 3 available units, 6 available EC-410 experiments,
  9 locked experiments, 18 circuits, 14 Playground projects, 46 quiz questions
  in 4 banks, 43 verified examples.
- Build-time assertions confirm `data/site.json` counts match
  `data/quizzes.json`, `data/playground.json` and `data/circuits.json`.
- EC-405 Units 4–5 and EC-410 Experiments 7–15 remain `locked` with no pages
  and no completion records.

### 5.2 Verilog and interactive content

| Audit | Result |
|---|---|
| `tools/verify_examples.py --check` | **43/43 examples passed** |
| `tools/verify_circuits.py` | **PASS** — 18 circuits, 17 combinational, 914 vectors, 5,901 checks |
| `tools/verify_playground.py` | **PASS** — 14 examples, 510 checks, 660 recorded comparisons |

### 5.3 Phase 08 audit

`tools/verify_phase8.py` is split into stages so it can be run independently.
The full audit totals **582/582 checks passed**:

| Stage | Checks | Result |
|---|---:|---|
| `static` — quiz data, guide claims, links, ids, icons | 333 | 333/333 |
| `pages` — 12 key pages × 8 browser checks | 96 | 96/96 |
| `responsive` — 11 widths × 5 pages | 55 | 55/55 |
| `quiz` — full flow, unanswered flow, storage recovery | 67 | 67/67 |
| `ui` — theme, mobile dialog, keyboard skip link | 16 | 16/16 |
| `screenshots` — capture and size check | 15 | 15/15 |

Run one stage with, for example:

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_phase8.py --stage quiz
```

The verifier starts its own preview server when one is not already listening.

### 5.4 Links, ids and assets

- **40 pages** scanned.
- **2,243 local file references** resolved, **0 broken**.
- **1,208 in-page anchors** resolved, **0 broken**.
- **0 duplicate element ids**.
- **0 missing SVG icon references**.
- Relative paths verified throughout; no root-absolute asset paths were added.

### 5.5 Browser and responsive behaviour

Twelve pages were checked in headless Chrome 148:
homepage, dashboard, theory index, a lesson, laboratory index, an experiment,
Circuit Lab, Playground, quizzes, guide hub, Windows guide and Android guide.
Each had exactly one `h1`, a main landmark, a document title, named buttons and
links, alt text on every image, no horizontal overflow at 1440 px, and **no
console, page or network errors**.

Horizontal overflow was tested at **360, 390, 412, 768, 901, 960, 1024, 1080,
1280, 1440 and 1920 px** on the homepage, quizzes, Windows guide, Android guide
and dashboard. All 55 combinations passed.

The header now has eight destinations on secondary pages. It collapses to the
mobile dialog below **1080 px**, and uses a compact one-line nav from
**1081–1240 px**. The wordmark no longer shrinks to zero width. At 1081 px the
last nav item ends before the theme control, with no overlap.

### 5.6 Storage and recovery

- `va.progress` sentinel unchanged after all quiz flows.
- `va.playground.drafts` sentinel unchanged.
- `va.quizzes` written with version 1 and one attempt per bank.
- Full-score submissions produce the expected raw score, 100%, correct dots,
  history row, submitted status, explanation and best-score card.
- Retry resets status and answers while keeping history.
- Reload persists history and best score.
- A saved attempt reopens in explicit review mode.
- Invalid JSON, an unsupported schema version and a malformed attempt each
  produce an empty history, the empty state and working questions, with no
  console errors.

### 5.7 Accessibility and keyboard

- Exactly one `h1` and one `main` landmark per checked page.
- Every button and link has an accessible name; every image has `alt`.
- The first Tab reaches the visible **Skip to content** link; Enter moves focus
  to `#main-content`.
- The mobile dialog opens from the menu button, reports
  `aria-expanded="true"`, closes from its close button and closes on Escape.
- The theme toggle changes to Daylight, stores `va.theme`, exposes
  `aria-pressed="true"` and persists after reload.
- Reduced-motion rules disable the new guide card transforms and transitions.
- Focus-visible styling is reused from the existing design system.

### 5.8 Lighthouse

Lighthouse was **not run**. This machine has no Node.js, npm, npx or Lighthouse
CLI, and the project must not be exposed through a public URL for PageSpeed
Insights. Instead, the Phase 08 audit used headless Chrome directly: console
and network error capture, layout/overflow checks, landmark and name checks,
keyboard checks and screenshot review. Lighthouse remains a pre-publication
task for the owner.

---

## 6. Licensing audit

Files inspected: `LICENSE`, `LICENSE-CONTENT`, `THIRD-PARTY-NOTICES.md`,
`README.md`, `assets/fonts/`, `css/fonts.css` and the generated pages.

### Findings

| Item | Finding |
|---|---|
| Original code and Verilog examples | MIT, `LICENSE`; scope note matches the repository |
| Original educational prose, diagrams, tables | CC BY-NC-SA 4.0, `LICENSE-CONTENT`; full legal code included |
| Fonts | Nine local WOFF2 files: Space Grotesk (500/600/700), Inter (400–700), JetBrains Mono (400/500) |
| Font licence | THIRD-PARTY-NOTICES declares SIL OFL 1.1 and links each upstream project |
| Icarus Verilog | GPL-2.0-or-later, used as a build/verification tool and not distributed |
| Python | PSF licence, build/preview only, not distributed |
| Course codes | EC-405/EC-410 used descriptively; no official syllabus reproduced |

No third-party images, diagrams, lesson text, code samples or curriculum
documents are bundled. The site has no runtime dependencies.

### Uncertainty for owner review

The OFL-1.1 requires the licence text and the font copyright notices to
accompany distributed font files. The repository currently names each upstream
project and links the official OFL text, but does **not** include a local
`OFL.txt` or per-font copyright lines next to the WOFF2 files. Font metadata
could not be inspected because `fontTools` is not installed. This is a
publication-readiness question, not a functional defect.

**No licence file was changed in Phase 08.** Before publishing, the owner
should decide whether to add `assets/fonts/OFL.txt` with the upstream copyright
notices, or to confirm that the existing notices and links are sufficient for
the intended distribution.

---

## 7. Release hygiene

| Check | Result |
|---|---|
| Git repository | None; project remains private and uninitialised |
| `.gitignore` | Added for `__pycache__`, `.pyc`, simulation output, OS/editor files and scratch folders |
| Build caches | `tools/__pycache__` removed |
| `.nojekyll` | Present |
| `robots.txt` | Present, allows crawling |
| Secrets/API keys | None found in HTML, CSS, JS, JSON, Markdown or tools |
| Private paths | None in generated pages; only generic example paths such as `C:\verilog-lab` appear |
| Temporary fixtures | Kept under the session temp directory, not in the project |
| Reproducibility | 43 generated HTML/JSON files hashed, rebuilt, **0 changed** |
| Source preservation | All build sources, data, verification scripts and screenshots retained |
| Naming | Phase 08 files follow existing lower-case, hyphenated conventions |

---

## 8. Limitations

1. **No Lighthouse score.** No Node/npm/Lighthouse CLI is available, and no
   public URL was created.
2. **No physical Android test.** Phone layout was verified in Chrome device
   emulation at 360–412 px. The guide states this explicitly. Android
   compilation was not tested and is not claimed.
3. **GTKWave version quirk.** `gtkwave --version` prints nothing on this UCRT64
   build; the guide documents the package and path checks instead.
4. **Quiz bank is original but not psychometrically validated.** Technical
   answers were reviewed against the lessons, examples and transcripts; no
   learner cohort data exists.
5. **No deployment.** The release candidate has not been uploaded, published or
   served from a public origin. Deployment remains an owner decision.
6. **Guide scope.** The Windows guide documents the verified UCRT64 Icarus
   workflow, not a vendor FPGA flow. Vivado and ISE are named only as absent
   optional tools.

---

## 9. Rebuild and preview

```powershell
# Rebuild every generated page
C:\msys64\ucrt64\bin\python.exe tools\build.py

# Preview at http://127.0.0.1:8000/
C:\msys64\ucrt64\bin\python.exe tools\serve.py
```

Verification:

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_examples.py --check
C:\msys64\ucrt64\bin\python.exe tools\verify_circuits.py
C:\msys64\ucrt64\bin\python.exe tools\verify_playground.py
C:\msys64\ucrt64\bin\python.exe tools\verify_phase8.py
```

The Phase 08 verifier also accepts `--stage static`, `pages`, `responsive`,
`quiz`, `ui` or `screenshots`.

---

## 10. Screenshots

All screenshots are in `docs/phase8/screenshots/`.

| File | View |
|---|---|
| `desktop-home.png` | Homepage |
| `desktop-dashboard.png` | Learning dashboard |
| `desktop-theory.png` | Theory index |
| `desktop-lesson.png` | Theory lesson |
| `desktop-laboratory.png` | Laboratory index |
| `desktop-circuit-lab.png` | Circuit Lab |
| `desktop-playground.png` | Playground |
| `desktop-quizzes.png` | Quiz hub and category cards |
| `desktop-quiz-question.png` | Active quiz question and palette |
| `desktop-guides.png` | Guide hub |
| `desktop-windows-guide.png` | Windows guide |
| `desktop-android-guide.png` | Android guide |
| `mobile-home.png` | Homepage at 390 px |
| `mobile-quizzes.png` | Quizzes at 390 px |
| `mobile-windows-guide.png` | Windows guide at 390 px |
| `mobile-android-guide.png` | Android guide at 390 px |

---

## 11. Owner review checklist

- [ ] Approve the 46-question bank and its explanations.
- [ ] Approve the Windows guide's verified-tool claims and the absent-tool table.
- [ ] Approve the Android guide's emulation-only evidence note.
- [ ] Decide whether to add a local OFL text/copyright notice for the fonts.
- [ ] Approve the 1080 px header breakpoint and compact 1081–1240 px nav.
- [ ] Decide whether to run Lighthouse and a physical Android check before publication.
- [ ] Authorise publication, deployment or repository creation separately.

**Phase 08 stops here for owner review. Nothing has been published or deployed.**
