# VERILOG ACADEMY

**From digital logic to hardware design.**

A premium, static engineering education platform for EC-405 Theory and EC-410
Laboratory. The first release covers EC-405 Units 1–3 (23 topics), EC-410
Experiments 1–6, an 18-demo Interactive Circuit Lab, a 14-project Verilog
Playground, 46 explained practice questions and honest Windows/Android setup
guides. Experiments 7–15 remain locked roadmap items.

## Repository and live site

| | |
|---|---|
| Source code | <https://github.com/Shyam2010-Py/verilog-academy> |
| Live site | <https://shyam2010-py.github.io/verilog-academy/> |
| Releases | <https://github.com/Shyam2010-Py/verilog-academy/releases> |
| Current release | [v1.0.0 — Foundations Release](https://github.com/Shyam2010-Py/verilog-academy/releases/tag/v1.0.0) |

```powershell
git clone https://github.com/Shyam2010-Py/verilog-academy.git
```

## Current status

**Version 1.0.0 — released, public and live.**

The site contains:

- the production homepage and shared Midnight/Daylight design system;
- the local learning dashboard with real progress, recent activity and
  validated JSON export/import;
- 23 EC-405 theory lessons with runnable examples and completion controls;
- a laboratory landing page and six complete EC-410 experiment pages;
- an Interactive Circuit Lab with 18 working demonstrations, live SVG wiring,
  Boolean expressions, highlighted truth tables and a clocked D flip-flop;
- a Verilog Playground with 14 verified starter projects, a highlighted
  two-file editor, `.v` downloads, optional local drafts and an honest local
  Icarus workflow;
- four practice quiz banks with 46 explained questions covering EC-405 theory,
  EC-410 laboratory work, Circuit Lab concepts and the Playground workflow;
- a guide hub plus separate Windows and Android setup guides, with real
  Icarus Verilog 13.0 and GTKWave 3.3.128 evidence on Windows and an honest
  account of the site’s limits on a phone;
- 43 verified Verilog examples (23 theory, 6 laboratory, 14 playground), each
  compiled and run with Icarus Verilog 13.0;
- locked roadmap entries for EC-410 Experiments 7–15, with no pages and no
  completion records.

### Start here

| Document | Purpose |
|---|---|
| [`GUIDE.md`](GUIDE.md) | Build, authoring, verification, storage and deployment guide |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Editing rules, local workflow and contribution licensing |
| [`SECURITY.md`](SECURITY.md) | Supported versions, reporting and data handling |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| [`docs/final-audit/REPORT.md`](docs/final-audit/REPORT.md) | Source cleanup and third-party licensing audit |
| [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) | Font, tool and course-reference notices |

Every laboratory page includes an aim, objectives, tools, working principle,
logic diagram, truth table, Boolean equations, Verilog-2001 design,
testbench, line-by-line explanation, exact commands, captured simulator
transcript, waveform explanation, result, troubleshooting, viva questions,
revision points and an explicit completion control.

## Interactive Circuit Lab

Open `circuit-lab/index.html` (or **Circuit Lab** in the main navigation) for
18 live demonstrations: seven gates, five arithmetic blocks, three routing and
selection circuits, two encoding/comparison blocks and one clocked flip-flop.
Every card has working inputs, a live SVG circuit, output indicators, the
Boolean expression, a truth table, worked notes, common mistakes and a short
revision point. Search, category filters and deep links (`#circuit-<id>`) work
without a page reload.

The lab is a digital-electronics workbench, not a Verilog compiler or
timing-accurate simulator. It evaluates gate-level JavaScript models and shows
ideal logic levels. Sequential behaviour is limited to the D flip-flop, which
has an explicit clock pulse, auto-clock, active-high enable and asynchronous
active-high reset.

The implementation is split into reusable modules:

| File | Role |
|---|---|
| `js/circuit-engine.js` | Gate-level models and the D flip-flop state machine |
| `js/circuit-diagrams.js` | Inline SVG diagrams and live wire/lamp painting |
| `js/circuit-lab.js` | Bench controls, filters, truth-table loading, test API |
| `css/circuit-lab.css` | Bench, card and responsive styling |
| `data/circuits.json` | Canonical demo metadata, prose and Verilog snippets |
| `tools/circuits.py` | Independent Python oracle and page/table generator |

Truth tables are generated at build time by the Python oracle and lazy-loaded
from `circuit-lab/data/<id>.json`. The JavaScript engine is never used as its
own test oracle.

## Verilog Playground

Open `playground/index.html` (or **Playground** in the main navigation) for 14
verified starter projects: three logic gates, five arithmetic blocks, three
routing/selection circuits, two behavioural blocks and one clocked D flip-flop.

Each project pairs a `design.v` with a self-checking `tb.v` and an
Icarus-generated transcript. The workbench lets you switch between the design
and testbench, edit both files with line numbers and Verilog syntax
highlighting, copy the whole file or a selection, reset either file, and
download the exact text as `design.v` and `tb.v`.

The Playground does **not** compile or simulate in the browser. Download the
two files, then run:

```powershell
iverilog -g2001 -o simulation.out design.v tb.v
vvp simulation.out
```

The reference transcript is evidence for the original files only. As soon as
either editor changes, the badge switches to **“Original example only”** and
you must compile your own files locally. Drafts are optional and live under
`va.playground.drafts`; they never touch `va.progress`.

The implementation is split into:

| File | Role |
|---|---|
| `data/playground.json` | Project metadata, aims, explanations and revision points |
| `tools/playground.py` | Loads sources/transcripts and renders the page |
| `js/playground.js` | Editor, highlighting, tabs, drafts, copy/download/reset |
| `css/playground.css` | Workbench, library, workflow and responsive styling |
| `tools/verify_playground.py` | Metadata, page and script-safety checks |

## Practice quizzes

Open `quizzes/index.html` (or **Quizzes** in the main navigation) for four
independent banks:

| Bank | Scope | Questions |
|---|---|---:|
| Theory | EC-405 Units 1–3 | 12 |
| Laboratory | EC-410 Experiments 1–6 | 12 |
| Circuit Lab | The 18 demonstrations | 11 |
| Playground | Editor, drafts and the Icarus workflow | 11 |

The 46 questions use multiple choice, code-output prediction, truth-table
interpretation, Boolean expressions, Verilog syntax, identify-the-error and
viva-style prompts. Every question has an explanation. Answers and
explanations are never rendered or marked before submission; review mode opens
only after a result exists.

Each bank has instructions, numbered questions, previous/next navigation, a
question palette, a confirmation step for unanswered questions, a final score,
per-question review and a retry that clears answers but keeps history.

Attempts are stored under `va.quizzes` in a versioned
`verilog-academy.quizzes` schema. Quiz attempts never write `va.progress`,
never mark a lesson or experiment complete, and malformed or unsupported data
falls back to an empty history with a visible recovery message rather than a
console error.

| File | Role |
|---|---|
| `data/quizzes.json` | Canonical question bank, answers and explanations |
| `tools/quizzes.py` | Validation, counts and page rendering |
| `js/quizzes.js` | Quiz runner, scoring, review, retry and `va.quizzes` storage |
| `css/quizzes.css` | Quiz cards, runner, palette and responsive styling |
| `tools/verify_phase8.py` | Data, guide, link, browser, storage and screenshot audit |

## Windows and Android guides

`guides/index.html` is the shared hub. It links to two platform pages:

- `guides/windows.html` documents the verified toolchain: Icarus Verilog 13.0,
  `vvp` 13.0 and GTKWave 3.3.128, with folder layout, a saved design and
  testbench, `iverilog -g2001` and `vvp` commands, transcript reading, VCD
  waveform generation, the GTKWave version quirk, and troubleshooting.
- `guides/android.html` explains browsing, course navigation, Circuit Lab
  demonstrations, Playground editing and downloads, local progress,
  export/import and the real limits of a phone.

The guides distinguish installed software from optional tools. Vivado, Xilinx
ISE, ModelSim, Verilator and Notepad++ are explicitly **not installed** on the
verification machine. The static site never compiles Verilog in the browser,
and the Android guide does not claim otherwise.

## Preview locally

The site uses native ES modules and `localStorage`, so preview it through a
local server rather than opening the HTML files directly.

```powershell
C:\msys64\ucrt64\bin\python.exe tools\serve.py
```

Open <http://127.0.0.1:8000/>.

## Rebuild generated pages

```powershell
C:\msys64\ucrt64\bin\python.exe tools\build.py
```

Source content lives in `content/`. The shared shell lives in
`templates/shell.html`; laboratory experiment pages share
`templates/experiment.html`. Generated HTML is written to the project root,
`theory/`, `labs/`, `circuit-lab/`, `playground/`, `quizzes/` and `guides/`,
and uses relative paths so it works on GitHub Pages project sites.

Do not edit generated HTML by hand. Edit `content/`, `templates/`, `css/`,
`js/` or `data/`, then rebuild.

## Verify the examples

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_examples.py
```

The verifier scans `examples/verilog/`, `examples/labs/` and
`examples/playground/`, compiles each design and testbench with
`iverilog -g2001`, runs `vvp`, and compares the transcript with the recorded
`expected.txt`. A mismatched transcript is reported rather than silently
accepted. The current run passes 43/43 examples; add `--check` to compare
without rewriting the recorded files.

Laboratory vectors:

| Experiment | Topic | Checks |
|---|---|---:|
| 01 | Basic logic gates | 4 |
| 02 | Half and full adder | 12 |
| 03 | Half and full subtractor | 12 |
| 04 | 4-bit parallel adder | 512 |
| 05 | 2:1, 4:1 and 8:1 multiplexers | 2,132 |
| 06 | 1:2, 1:4 and 1:8 demultiplexers | 28 |

Circuit Lab verification:

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_circuits.py
```

The verifier re-derives every combinational truth table with an independent
integer/priority implementation, compares it with the generated JSON and the
gate-level engine, and checks D flip-flop state sequences, reset/enable
behaviour and truth-table invariants. The current run performs 5,901 checks
across 18 circuits and 914 combinational vectors.

Playground verification:

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_playground.py
```

This checks the 14-project metadata, the design/testbench structure, the PASS
summaries, the generated page, the embedded client data and the editor script’s
safety rules. The current run passes 510 checks and 660 recorded comparisons.

Site verification (starts its own preview server if port 8000 is idle):

```powershell
C:\msys64\ucrt64\bin\python.exe tools\verify_phase8.py
```

This validates the 46-question bank, the guide claims, all local links and
element ids, twelve key pages in headless Chrome, horizontal overflow at 360,
390, 412, 768, 901, 960, 1024, 1080, 1280, 1440 and 1920 px, quiz
submit/review/retry behaviour, storage isolation and recovery from malformed
`va.quizzes` data, the theme toggle, the mobile dialog, the keyboard skip link,
and captures the audit screenshots. The current run passes 582/582 checks
across its six stages.

`tools/browser_audit.py` is a small dependency-free Chrome DevTools Protocol
helper used by the Phase 08 verifier. It needs Google Chrome and the local
preview server; it does not add a runtime dependency to the site.

## Project layout

| Path | Purpose |
|---|---|
| `content/` | Page and lesson source fragments |
| `content/experiments/` | Laboratory experiment fragments |
| `templates/` | Shared page shells |
| `data/` | Curriculum, site navigation, laboratory, circuit, playground and quiz metadata |
| `examples/verilog/` | Theory examples and expected transcripts |
| `examples/labs/` | Laboratory designs, testbenches and transcripts |
| `examples/playground/` | 14 Playground designs, testbenches and transcripts |
| `css/`, `js/` | Design system, pages, circuit engine, diagrams, Playground editor and quizzes |
| `tools/` | Static build, preview, circuit oracle, browser audit and verifiers |
| `theory/`, `labs/` | Generated lesson and laboratory pages |
| `circuit-lab/` | Generated Circuit Lab page and lazy truth-table JSON |
| `playground/` | Generated Playground page |
| `quizzes/` | Generated quiz page and embedded question data |
| `guides/` | Generated guide hub, Windows guide and Android guide |
| `assets/fonts/` | Bundled WOFF2 fonts, provenance notes and the OFL-1.1 text |
| `docs/phase6/` | Phase 6 report and verification screenshots |
| `docs/phase7/` | Phase 7 report and verification screenshots |
| `docs/phase8/` | Phase 8 report and verification screenshots |
| `docs/final-audit/` | Final source-hygiene and licensing audit |
| `LICENSING.md` | Which licence applies to which material |
| `.nojekyll` | Tells GitHub Pages to serve files as-is, without Jekyll |

## Release status

The final local audit rebuilt every page and ran the complete verification
suite: 43/43 Verilog examples, 18 circuits with 5,901 checks, 14 Playground
projects with 510 checks, and 582/582 site checks across the six audit stages.
Local file references and anchors resolve, generated output is reproducible,
and no secrets or personal paths are present.

The project is published as a public Git repository and is served as a static
site from the `main` branch. Every generated page is committed, so a clone
renders the full site without running the build first. See
[`docs/final-audit/REPORT.md`](docs/final-audit/REPORT.md) for the audit
results and the outstanding verification items: a Lighthouse run against the
deployed URL and testing on a physical Android handset.

## Progress

Progress lives under the `va.progress` key and uses the versioned
`verilog-academy.progress` schema documented in `js/progress.js`. Totals are
derived from `data/curriculum.json`: 23 theory topics, 6 practical
experiments and 29 overall.

Records change only when a learner activates an explicit completion control.
Marking is reversible, theory records are never overwritten by practical
records, and no progress is written on page load. The laboratory and the
dashboard read the same records. Playground drafts are stored separately under
`va.playground.drafts`, quiz attempts under `va.quizzes`, and neither ever
modifies `va.progress`.

## Stack

- HTML5
- Modern CSS with custom properties
- Vanilla JavaScript ES modules
- Inline SVG diagrams
- `localStorage`
- Local WOFF2 fonts
- Zero runtime dependencies
- Python standard library for build and preview only
- Icarus Verilog 13.0 for simulation evidence

## Licence

[`LICENSING.md`](LICENSING.md) explains which licence covers which part of the
repository.

- Original website source code and original Verilog examples: **MIT**, see
  [`LICENSE`](LICENSE).
- Original educational prose, diagrams and explanatory material:
  **CC BY-NC-SA 4.0**, see [`LICENSE-CONTENT`](LICENSE-CONTENT).
- Third-party fonts and tools: see
  [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md). Third-party material is
  not relicensed by this project.

The nine bundled WOFF2 files are Space Grotesk 2.000, Inter 4.001 and
JetBrains Mono 2.211 under the SIL Open Font License 1.1. Their copyright
notices and the full licence are in
[`assets/fonts/OFL-1.1.txt`](assets/fonts/OFL-1.1.txt); per-file metadata is in
[`assets/fonts/README.md`](assets/fonts/README.md).

## Scope

| Course | First release |
|---|---|
| EC-405 Theory | Units 1–3, 23 topics |
| EC-410 Laboratory | Experiments 1–6 |
| Circuit Lab | 18 interactive demonstrations |
| Playground | 14 verified projects with local Icarus workflow |
| Quizzes | 46 explained questions in four banks |
| Guides | Windows PC and Android |
| Progress | Local-only with JSON export/import |
| Quiz attempts | Local-only under `va.quizzes` |

EC-405 Units 4–5 and EC-410 Experiments 7–15 are reserved for a future
release.
