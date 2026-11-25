# Phase 7 — Verilog Playground

**Status:** complete, awaiting review. Phase 8 has not started.

**Date:** 25 November 2026

**Scope:** one Playground page, 14 verified starter projects, a lightweight
syntax-highlighting editor, local draft persistence, `.v` downloads, an honest
local Icarus workflow, browser/responsive/theme checks and the screenshots in
this folder. Phases 1–6 remain intact.

---

## 1. Delivered experience

The site now has a Playground at `playground/index.html`, linked from all six
navigation groups (home, theory, dashboard, site, laboratory and Circuit Lab)
and the footer. It contains:

- a hero that states the boundary plainly: **“No fake Run button.”** The page
  edits and downloads text; it does not compile, elaborate or simulate Verilog;
- a project selector for 14 verified starter projects and a library of 14 cards
  that open the same projects in the workbench;
- a two-file editor with **Design** (`design.v`) and **Testbench** (`tb.v`)
  tabs, line numbers, Verilog syntax highlighting, selection-aware copy,
  per-file reset, reset-both, and downloads named exactly `design.v` and `tb.v`;
- per-project metadata (category, level, check count), an aim, a line-by-line
  statement explanation, observations, common mistakes and a revision point;
- the exact local commands, a captured Icarus 13.0 transcript, and a visible
  “Verified original” badge that becomes **“Original example only”** as soon as
  either editor differs from the shipped source;
- an optional local draft, stored separately under `va.playground.drafts`, with
  save status, restore on reload and a two-step “Clear saved drafts” action;
- a four-step workflow section and a guidance section covering modules, design
  versus testbench, stimulus, compilation, reading output, common Icarus errors
  and common Verilog mistakes.

The workbench never calls `eval()`, never creates a `Function`, never assigns
editor content through `innerHTML`, and never loads the progress engine.

---

## 2. Example catalogue and verification

The canonical order and metadata live in `data/playground.json`. Every project
has `examples/playground/<id>/design.v`, `tb.v` and an Icarus-generated
`expected.txt`.

| # | Identifier | Project | Category | Level | Recorded checks |
|---:|---|---|---|---|---:|
| 1 | `and-gate` | AND Gate | Logic gates | Foundation | 4/4 |
| 2 | `or-gate` | OR Gate | Logic gates | Foundation | 4/4 |
| 3 | `xor-gate` | XOR Gate | Logic gates | Foundation | 4/4 |
| 4 | `half-adder` | Half Adder | Arithmetic | Foundation | 4/4 |
| 5 | `full-adder` | Full Adder | Arithmetic | Intermediate | 8/8 |
| 6 | `half-subtractor` | Half Subtractor | Arithmetic | Foundation | 4/4 |
| 7 | `full-subtractor` | Full Subtractor | Arithmetic | Intermediate | 8/8 |
| 8 | `four-bit-adder` | 4-Bit Ripple-Carry Adder | Arithmetic | Intermediate | 512/512 |
| 9 | `mux-4-to-1` | 4:1 Multiplexer | Routing | Intermediate | 64/64 |
| 10 | `demux-1-to-4` | 1:4 Demultiplexer | Routing | Intermediate | 8/8 |
| 11 | `decoder-2-to-4` | 2-to-4 Decoder with Enable | Routing | Intermediate | 8/8 |
| 12 | `priority-encoder` | 4-to-2 Priority Encoder | Behavioural | Advanced | 16/16 |
| 13 | `d-flip-flop` | D Flip-Flop with Enable and Reset | Sequential | Advanced | 8/8 |
| 14 | `alu-4-bit` | 4-Bit Behavioural ALU | Behavioural | Advanced | 8/8 |

Totals: **14 projects, 5 categories, 660 recorded self-check comparisons.**
The 4-bit adder alone covers all 512 combinations of `A`, `B` and `Cin`; the
other projects run the exhaustive or targeted vectors recorded in their
testbenches.

Every testbench is self-checking. It prints a small table, counts mismatches and
ends with `PASS: n/n`. For example, the AND gate transcript is:

```text
AND gate truth table
a b | y
----+--
0 0 | 0
0 1 | 0
1 0 | 0
1 1 | 1
PASS: 4/4 rows match
tb.v:28: $finish called at 4000 (1ps)
```

The 1-bit arithmetic projects use integer temporaries for their decimal column
so the transcript shows `0 + 1 = 1`, not a concatenation artefact. This was
fixed before the transcripts were recorded.

### Verification layers

1. **`tools/verify_examples.py --check`** compiles every example with
   `iverilog -g2001`, runs it with `vvp`, and compares stdout with the recorded
   transcript without rewriting it. All **43/43** examples pass (29 earlier
   examples plus 14 Playground projects).
2. **`tools/verify_playground.py`** checks metadata completeness, ids, levels,
   categories, design/testbench structure, the PASS summary, the Icarus finish
   line, the generated page, the embedded client JSON and the editor script’s
   safety rules. It reports **510 checks** and **660 recorded checks**.
3. **Browser harness** loads the real page in a same-origin iframe and exercises
   the editor, tabs, copy, downloads, drafts, reset, theme and keyboard paths.
4. **Layout harness** measures the real page at seven widths.
5. **Site-wide link and console checks** cover all 36 generated pages.

---

## 3. Workbench implementation

| File | Role |
|---|---|
| `content/playground.html` | Page source with `{{PG_*}}` tokens: hero, workbench shell, 14 briefs, 14 library cards, workflow, guidance and boundary sections. |
| `tools/playground.py` | Loads `data/playground.json` plus each project’s sources and transcript, escapes code for the page, renders briefs/cards/options and embeds the client JSON. |
| `js/playground.js` | Highlighting, gutter, tab switching, editing keys, status line, draft storage, copy, download, reset, project switching and the edited-state badge. |
| `css/playground.css` | Workbench, editor overlay, library, workflow, guidance, focus states and responsive rules for both themes. |
| `playground/index.html` | Generated page (133,338 bytes) with the 14 projects and embedded source/transcript data. |
| `tools/verify_playground.py` | Metadata, page and script-safety verifier. |
| `tools/build.py` | Calls `playground_pages()`, validates `counts.playground == 14` and writes the page. |
| `data/playground.json` | Canonical titles, categories, levels, summaries, aims, statements, observations, mistakes and revisions. |
| `data/site.json` | Navigation, footer and the `playground: 14` count. |

### Editor design

The editor is a transparent `<textarea>` layered over a highlighted `<pre>`.
The textarea owns the caret, selection, native undo/redo, scrolling and mobile
keyboard behaviour; the `<pre>` only paints tokens. A separate gutter is synced
to the textarea’s scroll position.

Highlighting is a single ordered token expression for comments, strings,
compiler directives, system tasks, literals, identifiers, keywords, types and
operators. Tokens are appended as DOM text nodes inside a `DocumentFragment`;
the script contains no `innerHTML`. The token stream is rebuilt on each input,
so editing never depends on the painted layer.

Keyboard behaviour:

- **Tab** inserts two spaces at the caret, or indents every selected line.
- **Shift+Tab** outdents the selected lines by two spaces (or one space/tab).
- **Escape** blurs the editor.
- Arrow keys, Home/End, Page Up/Down, Ctrl+Z/Y and text selection remain native.

The status line reports the active file, total lines and caret position
(`design.v · 16 lines · Ln 16, Col 1`). Line numbers are regenerated from the
actual text and the gutter width adapts to the digit count.

### Data flow

```text
data/playground.json
examples/playground/<id>/design.v
examples/playground/<id>/tb.v
examples/playground/<id>/expected.txt
        │
        └── tools/playground.py ──► content/playground.html tokens
                                  └─► playground/index.html
                                        ├─ 14 briefs + 14 cards + 14 options
                                        └─ #playground-data (escaped JSON)
                                              └─ js/playground.js
```

The browser never fetches the `.v` files at runtime; the sources and transcripts
are embedded at build time, so the page works from any static host and cannot
silently diverge from the verified examples.

---

## 4. Local simulation workflow

The page shows the same two commands for every project:

```powershell
iverilog -g2001 -o simulation.out design.v tb.v
vvp simulation.out
```

It explains that `simulation.out` is an Icarus simulation image, not a
bitstream, and that Windows users need `iverilog` and `vvp` on `PATH`. The
toolchain used for the recorded transcripts is:

```text
Icarus Verilog version 13.0 (stable) (v13_0)
Icarus Verilog runtime version 13.0 (stable) (v13_0)
```

The page never claims that the browser ran those commands. The transcript is
labelled as evidence for the original files. Editing either file changes the
badge to **“Original example only”** and replaces the note with an instruction
to compile the learner’s own files locally.

---

## 5. Browser functional results

The temporary same-origin harness loaded `playground/index.html` in an iframe,
seeded a `va.progress` sentinel, cleared `va.playground.drafts` and `va.theme`,
and ran **184 checks: 184 passed, 0 failed, 0 console errors.**

Covered paths:

| Area | Checks performed |
|---|---|
| Data and selection | 14 options, 14 briefs, 14 library cards, first project selected, selector and card selection both switch projects |
| Editor rendering | Highlighted tokens present, gutter line count matches the source, status line updates after edits, tabs switch `aria-selected` and visible panel |
| Editing | Typing updates highlighting and line numbers; Tab inserts two spaces; Shift+Tab outdents; native selection preserved |
| Edited state | Any change flips the badge to “Original example only” and the panel to `is-edited`; reset restores “Verified original” |
| Copy | Whole-file copy and selected-text copy both reach the copy path and show the copied state |
| Downloads | `design.v` and `tb.v` blobs contain the exact current editor text, including edits |
| Drafts | Typing saves after the 500 ms debounce; reload restores both files; switching projects keeps independent drafts; clear-drafts requires two clicks, removes the key and leaves the current editor untouched |
| Reset | Reset file restores only the active file; reset both restores both files and removes the draft when both match the originals |
| Themes | Toggle switches Midnight/Daylight and updates the button state |
| Keyboard | Tab order reaches the selector, tabs, editor, copy and download controls |
| Progress | The seeded `va.progress` value is byte-for-byte unchanged after the full run |

The generated page loads only `js/playground.js`; it does not load
`js/progress.js`, and `js/playground.js` imports only `toast` from `js/ui.js`.

---

## 6. Responsive, theme and accessibility results

The layout harness measures the real page inside a fixed-width iframe and
checks document width, body width, key control visibility and element overflow.
It excludes only intentionally scrollable code surfaces (`.pg-output`,
`.code-block__body`, the editor’s textarea/highlight/gutter), the skip link and
the toast stack.

| Requested width | Effective viewport | Checks | Result |
|---:|---:|---:|---|
| 360 | 350 | 17 | PASS, no page overflow |
| 390 | 380 | 17 | PASS, no page overflow |
| 412 | 402 | 17 | PASS, no page overflow |
| 768 | 758 | 17 | PASS, no page overflow |
| 1024 | 1014 | 17 | PASS, no page overflow |
| 1440 | 1430 | 17 | PASS, no page overflow |
| 1920 | 1910 | 17 | PASS, no page overflow |

Daylight was measured separately at 390, 768, 1440 and 1920 px: **17/17 checks
at each width, 0 failures.** The effective viewport is about 10 px narrower than
the requested width because of the iframe scrollbar, so these runs are stricter
than testing 360/390/412 directly.

At phone widths the toolbar wraps into three rows (label, project, status), the
editor remains full-width with its own horizontal scrolling, the metadata rail
stacks below the editor, the library becomes one column and the guidance cards
become one column. At tablet widths the rail becomes a responsive grid and the
brief/workflow sections collapse to one column. The three-column guidance grid
is restored only when there is room for it.

Accessibility:

- a skip link targets `#main-content`;
- the selector has a visible label; tabs use `role="tablist"`, `role="tab"`,
  `aria-selected` and `aria-controls`;
- buttons have accessible names and visible focus rings;
- the status line is a live textual description, not colour-only feedback;
- the edited-state warning uses text plus colour;
- both themes keep body text and control contrast at the same tokens used by
  the rest of the site;
- keyboard-only navigation reaches every workbench control, and the editor
  remains fully keyboard-operable.

---

## 7. Site-wide build, link and console checks

| Check | Result |
|---|---|
| `tools/build.py` | 36 pages built: 23 theory, 7 laboratory, 1 Circuit Lab, 1 Playground, plus homepage, dashboard and styleguide |
| Local `href`/`src` references | 2,155 checked across the 36 built pages |
| Broken local links or anchors | 0 |
| Pages with console output or uncaught errors | 0 of 36 |
| Icarus example verification | 43/43 |
| Playground metadata/page verification | 510 checks, PASS |

The link check resolves relative paths and same-page anchors. During this pass
the Circuit Lab’s “Back to top” link was found to target `#top` without an
element id; `templates/shell.html` now gives `<body>` the `id="top"` so the
anchor has a real target on every page. No other broken reference was found.

Console checking used Chrome’s own `INFO:CONSOLE` logging with a fresh profile
per run. All 36 pages produced zero console messages, including the Playground.

---

## 8. Files

### Added

| Path | Purpose |
|---|---|
| `playground/index.html` | Generated Playground page. |
| `content/playground.html` | Page source with hero, workbench, 14 briefs, 14 cards, workflow and guidance. |
| `js/playground.js` | Editor, highlighting, tabs, drafts, copy, download, reset and edited-state logic. |
| `css/playground.css` | Workbench, editor, library, workflow, guidance, focus and responsive styling. |
| `data/playground.json` | Canonical metadata for 14 projects. |
| `tools/playground.py` | Metadata/source/transcript loader and page renderer. |
| `tools/verify_playground.py` | 510-check metadata/page/script-safety verifier. |
| `examples/playground/<id>/design.v` | 14 designs. |
| `examples/playground/<id>/tb.v` | 14 self-checking testbenches. |
| `examples/playground/<id>/expected.txt` | 14 Icarus-generated transcripts. |
| `docs/phase7/REPORT.md` | This report. |
| `docs/phase7/screenshots/` | 12 desktop/mobile/theme screenshots. |

### Modified

| Path | Change |
|---|---|
| `tools/build.py` | Imports `playground`, builds the Playground page, validates the 14-project count. |
| `tools/verify_examples.py` | Includes `examples/playground` in the compile/run/compare sweep. |
| `data/site.json` | Adds Playground to five navigation groups and the footer, plus `counts.playground`. |
| `templates/shell.html` | Adds `id="top"` to `<body>` for the Circuit Lab back-to-top anchor. |
| `README.md` | Phase 07 status, Playground usage and verification commands. |

No Phase 1–6 page, lesson, experiment, progress rule or licence file was
removed. EC-405 Units 4–5 and EC-410 Experiments 7–15 remain locked and
unbuilt.

---

## 9. Screenshots

All screenshots are in `docs/phase7/screenshots/`.

### Desktop, Midnight (1440 px)

- `desktop-hero.png` — hero, boundary card, facts and the compilation warning.
- `desktop-workbench.png` — project selector, Design tab, line numbers,
  highlighted source, status line and metadata rail.
- `desktop-library.png` — 14 verified project cards.
- `desktop-guidance.png` — module/testbench, compilation, output-reading, Icarus
  error and Verilog mistake guidance.

### Desktop, Daylight (1440 px)

- `desktop-hero-daylight.png` — the same hero and boundary card in Daylight.
- `desktop-workbench-daylight.png` — the workbench with readable syntax colours
  and the metadata rail.

### Mobile (390 px)

- `mobile-hero.png` — stacked hero and boundary card.
- `mobile-workbench.png` — wrapped toolbar, full-width editor and line numbers.
- `mobile-library.png` — single-column project cards.
- `mobile-guidance.png` — single-column guidance cards.
- `mobile-hero-daylight.png` — Daylight mobile hero.
- `mobile-workbench-daylight.png` — Daylight mobile workbench.

---

## 10. Limitations and honest boundaries

- **No browser compilation or simulation.** The page prepares and downloads
  files. It has no Verilog parser, elaborator, simulator or waveform viewer, and
  no server-side compiler. The “Run” affordance is deliberately absent.
- **Reference transcripts apply to the original files only.** Editing either
  file changes the badge and note. The page does not regenerate or compare the
  learner’s output.
- **Highlighting is lexical, not semantic.** It recognises Verilog-2001 tokens
  and common literal forms; it does not validate syntax, resolve modules or
  understand generate blocks. This is sufficient for colouring, not for
  correctness.
- **The editor is intentionally small.** It has native undo/redo and selection,
  but no multi-cursor, search-and-replace, folding, autocomplete, linting or
  project tree. Files are always named `design.v` and `tb.v` so the documented
  commands stay exact.
- **Drafts are per browser profile.** They use `va.playground.drafts` version 1
  and can be unavailable in private or restricted storage contexts; the page
  warns instead of failing. Malformed or version-mismatched draft data is
  discarded by the version guard. Drafts never touch `va.progress`.
- **Local toolchain required.** The commands assume Icarus Verilog is installed
  and on `PATH`. The transcripts were produced with Icarus 13.0; other versions
  may format `$finish` lines or warnings differently.
- **Automated accessibility testing is structural.** Keyboard paths, labels,
  roles, focus styles and contrast tokens were checked, but no screen-reader
  session or full WCAG audit was performed.
- **Mobile virtual keyboards were not exercised.** Responsive layout and touch
  target sizes were measured in headless Chrome; real soft-keyboard viewport
  changes remain a manual check.

---

## 11. Reproduction

```powershell
# Rebuild all generated pages
C:\msys64\ucrt64\bin\python.exe tools\build.py

# Compile and compare every example, without rewriting transcripts
C:\msys64\ucrt64\bin\python.exe tools\verify_examples.py --check

# Metadata, page, embedded data and script-safety checks
C:\msys64\ucrt64\bin\python.exe tools\verify_playground.py

# Preview
C:\msys64\ucrt64\bin\python.exe tools\serve.py
```

Expected results: 36 pages built, 43/43 examples pass, 510 Playground checks
pass, 14 projects and 660 recorded comparisons.

The temporary browser harness and section-view helper were removed after
testing; they are not part of the shipped site.

---

## 12. Review gate

Phase 7 is complete and paused for review. Phase 8 has not been started. No
quizzes, setup guides or new curriculum units were added.
