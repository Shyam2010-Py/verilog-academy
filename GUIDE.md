# Verilog Academy — project guide

This guide is for anyone building, maintaining or reviewing the site. It covers
the local toolchain, the build pipeline, the content formats, the verification
suite, storage behaviour, licensing and the boundary of the first release.

The short version:

```powershell
python tools/build.py
python tools/serve.py
```

Open <http://127.0.0.1:8000/>.

On the reference Windows machine the interpreter is
`C:\msys64\ucrt64\bin\python.exe`. The scripts use only the Python standard
library, so any Python 3.10+ installation should work. Icarus Verilog 13.0 is
required only for the Verilog checks.

## 1. What the project is

A static engineering-education platform:

- EC-405 Theory, Units 1-3 (23 topics).
- EC-410 Laboratory, Experiments 1-6.
- An 18-demo Interactive Circuit Lab.
- A 14-project Verilog Playground.
- Four quiz banks with 46 explained questions.
- Windows and Android setup guides.
- Local-only progress, quiz attempts and Playground drafts.

EC-405 Units 4-5 and EC-410 Experiments 7-15 are locked roadmap entries. They
have no pages and cannot be completed.

There is no backend, build step at runtime, framework, package manager, CDN or
tracking script. The generated site is plain HTML, CSS, JavaScript, JSON, SVG
and WOFF2.

## 2. Requirements

| Tool | Purpose | Needed for |
|---|---|---|
| Python 3.10+ | Build, preview, verification | Everything |
| Icarus Verilog 13.0 (`iverilog`, `vvp`) | Compile and run examples | Example verification |
| GTKWave 3.3.128 (optional) | Inspect VCD waveforms | Manual study only |
| Google Chrome | Headless browser audit | `verify_phase8.py` browser stages |

The site itself needs only a modern browser. It does not need Python, Icarus or
GTKWave to be viewed.

## 3. Quick start

```powershell
# Generate every HTML page from content, templates and data
python tools/build.py

# Start a local static server on 127.0.0.1:8000
python tools/serve.py
```

Open the printed URL. Use a server rather than opening files directly: the site
uses native ES modules and `localStorage`, and `file://` breaks both.

## 4. Repository map

| Path | Contents |
|---|---|
| `content/` | Page fragments and the 23 theory lessons |
| `content/experiments/` | Six laboratory experiment fragments |
| `content/guides/` | Guide hub, Windows guide, Android guide |
| `templates/` | `shell.html`, `lesson.html`, `experiment.html`, `icons.svg` |
| `data/` | Curriculum, navigation, labs, circuits, playground, quizzes, theory |
| `examples/verilog/` | Theory designs, testbenches and transcripts |
| `examples/labs/` | Laboratory designs, testbenches and transcripts |
| `examples/playground/` | 14 Playground projects |
| `css/` | Fonts, tokens, themes, base, layout, components and page styles |
| `js/` | App shell, progress, dashboard, theory, labs, Circuit Lab, Playground, quizzes |
| `tools/` | Build, preview, oracle and verification scripts |
| `assets/fonts/` | Nine WOFF2 files, font inventory and `OFL-1.1.txt` |
| `assets/svg/` | Logo mark and favicon |
| `theory/`, `labs/`, `circuit-lab/`, `playground/`, `quizzes/`, `guides/` | Generated pages |
| `docs/` | Phase reports, audit report and verification screenshots |

Generated HTML is committed for static hosting. Do not edit it by hand.

## 5. Build pipeline

`tools/build.py`:

1. Loads `data/site.json`, `data/curriculum.json` and the content modules.
2. Renders `content/*.html` into `templates/shell.html`.
3. Renders theory lessons through `templates/lesson.html`.
4. Renders laboratory experiments through `templates/experiment.html`.
5. Calls `tools/circuits.py`, `tools/playground.py` and `tools/quizzes.py` for
   their pages and JSON payloads.
6. Replaces `{{TOKEN}}` placeholders and asserts build-time counts.
7. Writes the homepage, dashboard, style guide, track pages, lesson pages,
   experiment pages, Circuit Lab, Playground, quiz page and guides.

The build is deterministic: rebuilding without source changes produces
byte-identical HTML and JSON. The final audit hashed 58 generated HTML/JSON files
and confirmed zero changes on a second build.

Common build failure causes:

- a `{{TOKEN}}` with no value in the data;
- a lesson or experiment referenced by curriculum but missing from `content/`;
- a quiz or circuit with a duplicate id;
- a changed count that no longer matches the assertions in `build.py`.

## 6. Authoring content

### Theory lesson

1. Add the lesson fragment under `content/lessons/`.
2. Register it in `data/theory.json` and the relevant unit in
   `data/curriculum.json`.
3. Add a design, testbench and expected transcript under
   `examples/verilog/<slug>/`.
4. Run `python tools/verify_examples.py` to record the transcript, then
   `--check`.
5. Rebuild and open the lesson.

### Laboratory experiment

1. Add the fragment under `content/experiments/`.
2. Add the design, testbench and transcript under `examples/labs/experiment-NN/`.
3. Add vectors or metadata used by `tools/verify_circuits.py` if the experiment
   has a truth table.
4. Rebuild and verify.

### Quiz question

Edit `data/quizzes.json`. Every question needs a unique `id`, one of the seven
supported types, a prompt, options where applicable, the correct answer, an
explanation, and a bank (`theory`, `laboratory`, `circuit-lab`, `playground`).
`tools/quizzes.py` validates uniqueness and counts; `tools/verify_phase8.py`
checks that no answer or explanation is present in the DOM before submission.

### Circuit Lab demo

Edit `data/circuits.json` and, if the evaluation model changes, the independent
oracle in `tools/circuits.py`. The JavaScript engine must never be its own test
oracle. Run `python tools/verify_circuits.py`.

### Playground project

Add `design.v`, `tb.v` and the recorded transcript under
`examples/playground/<slug>/`, then register the project in
`data/playground.json`. Run `python tools/verify_playground.py`.

## 7. Design system and accessibility

- `css/tokens.css` owns colour, type, spacing, radius, motion and z-index.
- `css/themes.css` defines Midnight and Daylight overrides.
- `css/base.css` provides resets, focus rings, skip link and reduced motion.
- `css/components.css` provides buttons, badges, panels, tables, callouts,
  dialogs and toasts.
- Page styles consume tokens; they should not introduce raw colours.

Requirements for new UI:

- semantic landmarks and heading order;
- visible focus and keyboard operation;
- `aria-*` state kept in sync with visual state;
- text and controls legible in both themes;
- no horizontal overflow at 360 px;
- reduced-motion fallback;
- no `innerHTML` with learner-controlled or data-file content.

## 8. Local storage and backups

| Key | Schema | Owner |
|---|---|---|
| `va.theme` | plain string | `js/ui.js` |
| `va.progress` | `verilog-academy.progress` | `js/progress.js` |
| `va.playground.drafts` | `verilog-academy.playground` | `js/playground.js` |
| `va.quizzes` | `verilog-academy.quizzes` | `js/quizzes.js` |

Rules:

- Never write one key from another module.
- Quiz attempts and drafts must never modify `va.progress`.
- Reading must tolerate missing, malformed, unsupported or unavailable storage.
- A malformed value is reported to the learner and replaced only on the next
  explicit write; it is not silently trusted.
- Import validates the schema, curriculum ids and record types before writing.

The dashboard exports a JSON backup and imports it after confirmation. To reset
local data during testing, use the dashboard controls or clear the site's
storage in the browser developer tools. Do not commit exported progress files.

## 9. Verification

| Command | Covers |
|---|---|
| `python tools/verify_examples.py --check` | 43 designs compile, run and match transcripts |
| `python tools/verify_circuits.py` | 18 circuits, 914 vectors, 5,901 independent checks |
| `python tools/verify_playground.py` | 14 projects, 510 checks, 660 comparisons |
| `python tools/verify_phase8.py` | Data, guides, links, browser behaviour, storage, responsive, screenshots |

`verify_phase8.py` starts its own preview server and supports stages so a long
run can be resumed:

```powershell
python tools/verify_phase8.py --stage static
python tools/verify_phase8.py --stage pages
python tools/verify_phase8.py --stage responsive
python tools/verify_phase8.py --stage quiz
python tools/verify_phase8.py --stage ui
python tools/verify_phase8.py --stage screenshots
```

The browser stages need Google Chrome. The verifier looks for Chrome in the
usual Windows location and writes screenshots to `docs/phase8/screenshots/`.

The audit checks:

- curriculum counts, ids and locked items;
- all local file references and anchors;
- duplicate element ids and missing icons;
- console and network errors on twelve key pages;
- horizontal overflow at 360, 390, 412, 768, 901, 960, 1024, 1080, 1280, 1440
  and 1920 px;
- quiz submit/review/retry, answer secrecy and malformed-storage recovery;
- theme toggle, mobile dialog and keyboard skip link;
- storage isolation between progress, drafts and quizzes.

## 10. Fonts and licensing

The nine WOFF2 files are third-party Font Software under the SIL Open Font
License 1.1. Copyright notices, internal versions and per-file metadata are in
`assets/fonts/README.md`; the full licence is
`assets/fonts/OFL-1.1.txt`. They are not covered by MIT or CC BY-NC-SA.

Original code and Verilog are MIT (`LICENSE`). Original prose, diagrams and
tables are CC BY-NC-SA 4.0 (`LICENSE-CONTENT`). See
`THIRD-PARTY-NOTICES.md` for the complete split.

Do not copy official syllabus documents, textbook text or third-party diagrams
into the site. Course codes and experiment titles are used only to describe
scope.

## 11. Deployment notes

The output is a static tree. Relative paths make it work on a project-site
subpath as well as a domain root. `.nojekyll` prevents Jekyll processing on
GitHub Pages. `robots.txt` allows indexing.

Deployment is an owner decision and is intentionally not automated. Before any
publication:

- review the audit report and unresolved provenance items;
- confirm the repository owner, name and visibility;
- decide whether generated HTML is committed or built in CI;
- run Lighthouse against the deployed URL;
- test on a physical Android handset if mobile claims are to be strengthened.

## 12. Troubleshooting

**Blank page or module errors.** Serve over HTTP, not `file://`.

**Port 8000 already in use.** Stop the other server or run
`python tools/serve.py --port 8080`, then use that URL.

**`iverilog` not found.** Add the Icarus `bin` directory to `PATH` and confirm
with `iverilog -V`.

**GTKWave `--version` prints nothing.** On the UCRT64 build, verify with
`where.exe gtkwave` and `pacman -Q mingw-w64-ucrt-x86_64-gtkwave` instead.

**Chrome not found by the audit.** Install Google Chrome or update the path in
`tools/browser_audit.py`.

**Fonts look different.** Check that `assets/fonts/*.woff2` exist and that the
page is served from the project root so `../assets/...` resolves.

**Progress disappeared.** It is per origin. `127.0.0.1:8000` and `localhost:8000`
are different origins; use one consistently. Restore from a dashboard export if
available.

## 13. Contribution workflow

Read `CONTRIBUTING.md`. In short: edit sources, rebuild, run the relevant
verifier, check both themes and the responsive widths, and keep generated
artefacts in sync. Do not add runtime dependencies or hand-edit generated
pages.
