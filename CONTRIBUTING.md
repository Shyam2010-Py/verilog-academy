# Contributing

Verilog Academy is a static educational site with no runtime dependencies.
Contributions should keep it that way: HTML, CSS, vanilla JavaScript, inline
SVG, JSON and Verilog only.

## Before you start

- Read [`GUIDE.md`](GUIDE.md) for the build, content and verification workflow.
- Check the scope in [`README.md`](README.md). EC-405 Units 4-5 and EC-410
  Experiments 7-15 are intentionally locked.
- Do not add analytics, trackers, CDN links, web fonts from a third party,
  frameworks or a backend service.

## Local workflow

```powershell
python tools/build.py
python tools/verify_examples.py --check
python tools/verify_circuits.py
python tools/verify_playground.py
python tools/serve.py
```

Then run the browser audit against the preview server:

```powershell
python tools/verify_phase8.py
```

Use the interpreter that has your project dependencies available. On the
reference Windows machine this is `C:\msys64\ucrt64\bin\python.exe`; the
scripts themselves use only the Python standard library.

## Editing rules

- Edit sources in `content/`, `templates/`, `data/`, `css/`, `js/` or
  `examples/`. Never hand-edit generated HTML in the project root, `theory/`,
  `labs/`, `circuit-lab/`, `playground/`, `quizzes/` or `guides/`.
- Keep the design system in `css/tokens.css` and `css/themes.css` as the single
  source for colour, type, spacing and motion values.
- Preserve keyboard access, visible focus, reduced-motion behaviour and both
  Midnight and Daylight themes.
- Test at 360, 390, 412, 768, 1024, 1080, 1280 and 1440 px. The header collapses
  below 1080 px.
- Add or update the matching verifier when you add a new content type.
- Keep learner data out of the repository. `va.progress`, `va.quizzes` and
  `va.playground.drafts` live in the browser, never in source files.

## Verilog examples

Every design must have a self-checking testbench, compile with
`iverilog -g2001`, run under `vvp`, and produce a recorded transcript. Run
`python tools/verify_examples.py` after changing a design or testbench so the
recorded transcript is refreshed, then re-run with `--check`.

Comments in published Verilog are educational and should explain the hardware,
not the editing history.

## Commit messages

Use a short imperative subject, for example:

```text
Add 4-bit comparator bench
Fix quiz retry focus
Document GTKWave version check
```

Group unrelated changes into separate commits.

## Licensing of contributions

By contributing you agree that:

- code and Verilog examples are licensed under the project's MIT licence;
- original educational prose and diagrams are licensed under CC BY-NC-SA 4.0;
- you have the right to submit the material and it contains no copied
  third-party content without compatible permission and attribution.

Third-party fonts and tools remain under their own licences. See
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
