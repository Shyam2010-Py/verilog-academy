# Final source cleanup and licensing audit

**Project:** Verilog Academy
**Date:** 2026-11-25
**Scope:** Local maintenance only. No Git repository was initialised, no remote
was added, and nothing was uploaded, published or deployed.
**Verdict:** Source cleanup and regression testing are complete. Licensing is
verified for the bundled fonts, but this report is **not** a legal clearance.

---

## 1. Comment lines discovered

Comment-bearing lines were counted per language. For CSS and JavaScript the
count includes every line of a multi-line block comment; for Verilog it
includes inline `//` comments. Docstrings are code, not comments, and are not
included.

| Language | Files | Comment-bearing lines | Notes |
|---|---:|---:|---|
| Python | 10 | 62 | Shebangs, section dividers, short implementation notes |
| JavaScript | 11 | 132 | Module headers, section dividers, storage/flow notes |
| CSS | 15 | 203 | File headers and section dividers |
| HTML (generated) | 40 | 0 | No HTML comments anywhere |
| HTML (source/templates) | 41 | 0 | No HTML comments anywhere |
| SVG | 3 | 0 | No comments |
| Verilog | 74 | 75 | Educational design/testbench comments |
| JSON | 7 | 0 | JSON does not support comments |
| **Total** | **201** | **472** | |

No commented-out code blocks, `TODO`, `FIXME`, `HACK`, `XXX`, debug flags or
temporary development markers were found in the source tree. The only matches
for words such as "placeholder" and "temporary" were legitimate UI copy or
technical prose.

## 2. Nonessential comments removed

The cleanup was targeted, not a global strip. It touched 18 source files:
development-history lines were deleted, module headers and docstrings were
reworded to describe current behaviour, one redundant "fall through" comment
inside an empty `catch` block was removed, and one comment gained a legal
pointer to the bundled font licence.

| File | Change |
|---|---|
| `css/circuit-lab.css` | Removed "Reuses the Phase 1 tokens…" line |
| `css/dashboard.css` | Removed phase number and phase-history wording |
| `css/guides.css` | Removed phase title and reuse note |
| `css/labs.css` | Removed "Reuses Phase 1 tokens…" line |
| `css/home.css` | Removed phase number and reuse note |
| `css/pages.css` | Removed "Phase 01 visual review" wording |
| `css/playground.css` | Removed phase title and reuse note |
| `css/quizzes.css` | Removed phase title and reuse note |
| `css/theory.css` | Removed "Reuses the Phase 1 tokens…" line |
| `css/layout.css` | Condensed a three-line navigation-history note to one current line |
| `css/fonts.css` | Added the local `OFL-1.1.txt` pointer |
| `js/playground.js` | Removed the phase label; removed a redundant `catch` comment |
| `js/quizzes.js` | Removed the phase label from the module header |
| `js/progress.js` | Replaced "future lesson and lab pages" with current wording |
| `tools/quizzes.py` | Removed the phase number from the docstring and page eyebrow |
| `tools/build.py` | Replaced two phase-numbered section labels |
| `tools/verify_playground.py` | Removed the phase number from the docstring |

Separately, six **user-visible** phase labels were removed from page copy (not
comments): the Playground hero, the guide hub, both platform guides, the design
system badge and the quiz page eyebrow. Generated pages were rebuilt.

## 3. Legally required comments and notices preserved

| Item | Status |
|---|---|
| Python interpreter directives (`#!/usr/bin/env python3`) | Preserved in the 8 scripts that had them; the other two had none |
| Encoding, linting, formatting and build directives | None exist beyond the shebangs |
| Font copyright, version and licence metadata inside the WOFF2 files | Untouched; file hashes recorded in section 5 |
| `LICENSE` | Unchanged |
| `LICENSE-CONTENT` | Unchanged |
| `THIRD-PARTY-NOTICES.md` | Content unchanged; font details expanded in `assets/fonts/` instead |
| Educational Verilog comments | All 75 comment-bearing lines preserved |
| Section headers and useful docstrings | Preserved; only obsolete wording changed |
| Generated-file markers | None existed; the build uses token assertions rather than HTML comments |

No copyright notice was removed, and no new copyright owner, year or author was
invented.

## 4. Files modified

### Source and configuration

| File | Change |
|---|---|
| `content/playground.html` | Removed the phase label from the hero eyebrow |
| `content/styleguide.html` | Replaced the phase badge with "Design system" |
| `content/guides/index.html` | Removed the phase label |
| `content/guides/windows.html` | Removed the phase label |
| `content/guides/android.html` | Removed the phase label |
| `css/circuit-lab.css`, `dashboard.css`, `guides.css`, `labs.css`, `home.css`, `pages.css`, `playground.css`, `quizzes.css`, `theory.css`, `layout.css`, `fonts.css` | Comment cleanup and licence pointer |
| `js/playground.js`, `js/quizzes.js`, `js/progress.js` | Comment cleanup |
| `tools/quizzes.py`, `tools/build.py`, `tools/verify_playground.py` | Comment cleanup |
| `tools/verify_phase8.py` | Corrected the run instruction in the module docstring |
| `README.md` | Release status, start-here table, audit summary, font licence details |
| `.gitignore` | Expanded for environments, logs, backups, secrets and editor files |
| `.gitattributes` | New: LF normalisation and binary declarations |
| `.editorconfig` | New: encoding, line endings and indentation |
| `CONTRIBUTING.md` | New |
| `SECURITY.md` | New |
| `CHANGELOG.md` | New |
| `GUIDE.md` | New: build, authoring, verification, storage and deployment guide |
| `docs/README.md` | New documentation index |
| `docs/phase8/REPORT.md` | Added a post-audit note closing the font-licence gap |
| `docs/final-audit/REPORT.md` | This report |
| `assets/fonts/OFL-1.1.txt` | New: three copyright notices and the full OFL 1.1 text |
| `assets/fonts/README.md` | New: per-file metadata and provenance |

### Generated output

All 40 HTML pages were rebuilt. The 18 Circuit Lab truth-table JSON files were
regenerated by the same build. The 16 Phase 8 screenshots were recaptured by the
browser audit.

### Deliberately unchanged

`LICENSE`, `LICENSE-CONTENT`, `THIRD-PARTY-NOTICES.md`, all nine WOFF2 files,
all Verilog sources and testbenches, all recorded transcripts, all curriculum
and quiz data, and every historical phase report.

## 5. The nine font files and their verified licences

Metadata was read directly from each file's embedded `name`, `head` and `OS/2`
tables by decompressing the WOFF2 Brotli stream, and cross-checked with
`fc-scan`. Licence texts were fetched from the upstream repositories on
2026-11-25.

Some static builds use internal family names that include the weight, such as
`Space Grotesk Light Medium` and `Inter Medium`. `css/fonts.css` maps all of
them to the public `Space Grotesk`, `Inter` and `JetBrains Mono` families with
the weights shown below; the files were not renamed or altered during this
audit.

| File | Family / style | CSS weight | Internal version | Copyright holder | Upstream | Licence | Status |
|---|---|---:|---|---|---|---|---|
| `space-grotesk-500.woff2` | Space Grotesk Medium | 500 | 2.000 | The Space Grotesk Project Authors | `floriankarsten/space-grotesk` | SIL OFL 1.1 | Licence verified; provenance partial |
| `space-grotesk-600.woff2` | Space Grotesk SemiBold | 600 | 2.000 | The Space Grotesk Project Authors | `floriankarsten/space-grotesk` | SIL OFL 1.1 | Licence verified; provenance partial |
| `space-grotesk-700.woff2` | Space Grotesk Bold | 700 | 2.000 | The Space Grotesk Project Authors | `floriankarsten/space-grotesk` | SIL OFL 1.1 | Licence verified; provenance partial |
| `inter-400.woff2` | Inter Regular | 400 | 4.001;git-66647c0bb | The Inter Project Authors | `rsms/inter` | SIL OFL 1.1 | Licence verified; provenance partial |
| `inter-500.woff2` | Inter Medium | 500 | 4.001;git-66647c0bb | The Inter Project Authors | `rsms/inter` | SIL OFL 1.1 | Licence verified; provenance partial |
| `inter-600.woff2` | Inter SemiBold | 600 | 4.001;git-66647c0bb | The Inter Project Authors | `rsms/inter` | SIL OFL 1.1 | Licence verified; provenance partial |
| `inter-700.woff2` | Inter Bold | 700 | 4.001;git-66647c0bb | The Inter Project Authors | `rsms/inter` | SIL OFL 1.1 | Licence verified; provenance partial |
| `jetbrains-mono-400.woff2` | JetBrains Mono Regular | 400 | 2.211 | The JetBrains Mono Project Authors | `JetBrains/JetBrainsMono` | SIL OFL 1.1 | Licence verified; provenance partial |
| `jetbrains-mono-500.woff2` | JetBrains Mono Medium | 500 | 2.211 | The JetBrains Mono Project Authors | `JetBrains/JetBrainsMono` | SIL OFL 1.1 | Licence verified; provenance partial |

SHA-256 prefixes for integrity records:

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `space-grotesk-500.woff2` | 13,312 | `1B1A8131D9EDF975` |
| `space-grotesk-600.woff2` | 13,284 | `685BBBF69FA616DF` |
| `space-grotesk-700.woff2` | 12,840 | `35F8AEC56CFD5CBF` |
| `inter-400.woff2` | 23,664 | `8909904AB6C872EB` |
| `inter-500.woff2` | 24,272 | `F3779F1EFCCC4BDC` |
| `inter-600.woff2` | 24,452 | `F9A06E79CD3A2A20` |
| `inter-700.woff2` | 24,356 | `6F56409FD3D64BB8` |
| `jetbrains-mono-400.woff2` | 21,168 | `14425BA9C695763C` |
| `jetbrains-mono-500.woff2` | 21,832 | `CB182FEEED4D798F` |

### Verification evidence

- All nine files embed the copyright line shown above and a licence URL:
  `https://openfontlicense.org` for Inter, `https://scripts.sil.org/OFL` for the
  other two families.
- Upstream licence files contain the same copyright line and the complete SIL
  Open Font License 1.1:
  - <https://raw.githubusercontent.com/floriankarsten/space-grotesk/master/OFL.txt>
  - <https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/OFL.txt>
- Space Grotesk's upstream README identifies Florian Karsten as the designer and
  the project as version 2.0; the bundled files report 2.000.
- Inter's upstream latest release at audit time was v4.1; the bundled files
  report 4.001. The release tag is consistent but was not independently matched
  file-for-file.
- JetBrains Mono's upstream latest release at audit time was v2.304; the bundled
  files report 2.211, so they are an older build.
- None of the three upstream licence files declares a Reserved Font Name. The
  OFL therefore permits bundling, subsetting and redistribution, provided the
  copyright notice and licence travel with the files.

### Licence-file status

`assets/fonts/OFL-1.1.txt` now contains:

1. the three copyright notices exactly as embedded in the fonts;
2. the internal version of each family;
3. the upstream repository URL for each family;
4. the complete, unmodified OFL 1.1 text.

`assets/fonts/README.md` records per-file family, style, weight, version,
copyright and source. `THIRD-PARTY-NOTICES.md` already named the three upstream
projects and the licence; it was left unchanged as instructed.

## 6. Font copyright notices and licence-file status

| Requirement | Status |
|---|---|
| Copyright notice for Space Grotesk | Present in each file's `name` table and in `OFL-1.1.txt` |
| Copyright notice for Inter | Present in each file's `name` table and in `OFL-1.1.txt` |
| Copyright notice for JetBrains Mono | Present in each file's `name` table and in `OFL-1.1.txt` |
| Full OFL 1.1 text distributed with the fonts | Yes, `assets/fonts/OFL-1.1.txt` |
| Licence URL in font metadata | Yes, all nine files |
| Reserved Font Name restriction | None declared upstream |
| Redistribution permitted | Yes, under OFL 1.1 conditions |
| Fonts relicensed under MIT or CC BY-NC-SA | No; explicitly excluded in the licence document |

The bundled files are a Latin/punctuation subset of the upstream families. That
makes them Modified Versions under the OFL. Because no Reserved Font Name is
declared, keeping the family names is permitted. The exact subsetting command
and download URL were not recorded, so build provenance is only partially
verified even though the licence is verified.

## 7. Third-party asset audit

| Asset | Source | Creator | Licence | Attribution | Modifications | Status |
|---|---|---|---|---|---|---|
| 3 × Space Grotesk WOFF2 | <https://github.com/floriankarsten/space-grotesk> | The Space Grotesk Project Authors; design by Florian Karsten | SIL OFL 1.1 | Copyright + licence in `assets/fonts/OFL-1.1.txt` | Latin subset; WOFF2 packaging | Licence verified; build provenance partial |
| 4 × Inter WOFF2 | <https://github.com/rsms/inter> | The Inter Project Authors (Rasmus Andersson / rsms) | SIL OFL 1.1 | Same | Latin subset; WOFF2 packaging | Licence verified; build provenance partial |
| 2 × JetBrains Mono WOFF2 | <https://github.com/JetBrains/JetBrainsMono> | The JetBrains Mono Project Authors (JetBrains) | SIL OFL 1.1 | Same | Latin subset; WOFF2 packaging | Licence verified; build provenance partial |
| Logo, favicon, icon sprite | Project repository | Project authors | MIT | None required | Original SVG | No third-party markers found |
| CSS and JavaScript | Project repository | Project authors | MIT | None required | Original, no libraries or frameworks | No third-party markers found; no external runtime requests |
| Verilog designs and testbenches | Project repository | Project authors | MIT | None required | Original | Verified by compilation and transcript comparison |
| Simulator transcripts | Generated by Icarus Verilog | Project authors / tool output | MIT for the compilation | None required | Generated output | Verified against `vvp` runs |
| Screenshots in `docs/` | Captured from this site | Project authors | CC BY-NC-SA 4.0 (site content) | None required | Screen captures | Original captures; no personal data observed |
| Icarus Verilog 13.0 | <https://github.com/steveicarus/iverilog> | Stephen Williams and contributors | GPL-2.0-or-later | Not distributed | None | Not bundled |
| GTKWave 3.3.128 | <https://gtkwave.sourceforge.net/> | GTKWave contributors | GPL-2.0-or-later | Not distributed | None | Not bundled |
| Python 3 standard library | <https://www.python.org/> | Python Software Foundation | PSF License | Not distributed | None | Not bundled |
| Google Chrome | Google | Google | Proprietary | Not distributed | None | Used only for local headless verification |
| EC-405 / EC-410 codes and experiment titles | Course terminology | Not reproduced from a document | N/A | Used only to describe scope | No syllabus text, tables or figures copied | Reference use only |

No third-party images, diagrams, lesson text, code samples, icon sets, CSS
frameworks, JavaScript libraries, analytics or CDN resources were found. A
search of runtime HTML, CSS and JavaScript found no external `http(s)` resource
references apart from SVG namespace declarations.

## 8. MIT and CC BY-NC-SA scope audit

| Material | Intended licence | Audit result |
|---|---|---|
| Build, preview and verification scripts | MIT | Covered by `LICENSE` |
| Site JavaScript and CSS | MIT | Covered by `LICENSE` |
| Original SVG logo, favicon and icons | MIT | Covered by `LICENSE` |
| Original Verilog designs and testbenches | MIT | Covered by `LICENSE` |
| Original lesson, laboratory and guide prose | CC BY-NC-SA 4.0 | Covered by `LICENSE-CONTENT` |
| Original diagrams, truth tables and explanatory tables | CC BY-NC-SA 4.0 | Covered by `LICENSE-CONTENT` |
| Quiz questions and explanations | CC BY-NC-SA 4.0 | Original educational content |
| Bundled fonts | SIL OFL 1.1 | Excluded from both project licences |
| Icarus, GTKWave, Python, Chrome | Their own licences | Not distributed |
| Course codes and experiment titles | N/A | Reference only; no syllabus reproduced |

`LICENSE` and `LICENSE-CONTENT` use "Verilog Academy authors" rather than a
named individual. No ownership of third-party fonts, tools or curriculum
documents is claimed. The scope and terms of both licences were not changed.

## 9. Security and `.gitignore` findings

| Check | Result |
|---|---|
| API keys, access tokens, cloud credentials | None found |
| Passwords, client secrets, private keys | None found |
| `AKIA…`, `ghp_…`, `-----BEGIN … PRIVATE KEY-----` patterns | No matches |
| Email addresses in source or docs | None found |
| Personal Windows paths (`C:\Users\…`, `AppData`) | None found |
| Usernames or machine names in docs/screenshots | None found |
| `.env`, `*.pem`, `*.key`, `node_modules`, virtual environments | None present |
| `__pycache__` | Removed; now ignored |
| Debug or temporary fixtures | None found |
| Local simulation output (`.out`, `.vcd`, `.fst`, `.ghw`) | None present; ignored |
| Generated HTML committed for static hosting | Intentional, not debug output |
| `docs/` screenshots (11.5 MB) | Intentional evidence, not temporary files |
| `C:\msys64\…` paths in the Windows guide | Documented toolchain paths, not personal data |
| `robots.txt` | `User-agent: *` / `Allow: /` |
| `.nojekyll` | Present for GitHub Pages |
| `.gitattributes` | LF normalisation; fonts and images marked binary |

`.gitignore` now covers Python caches, virtual environments, `node_modules`,
simulation output, logs, backups, editor folders, `.env` files, keys and local
scratch directories. It does not ignore source, tests, documentation or
generated pages.

No file was deleted as "uncertain". The only removal was the reproducible
`tools/__pycache__` directory.

## 10. Rebuild and regression test results

All commands were run on 2026-11-25 with
`C:\msys64\ucrt64\bin\python.exe`, Icarus Verilog 13.0 and Chrome 148.

| Test | Command | Result |
|---|---|---|
| Static build | `python tools/build.py` | 40 pages; 23 theory topics, 6 labs + 9 locked, 18 circuits, 14 Playground projects, 46 quiz questions, 2 guides + hub |
| Verilog examples | `python tools/verify_examples.py --check` | **43/43 passed** |
| Circuit Lab | `python tools/verify_circuits.py` | **PASS** — 18 circuits, 914 vectors, 5,901 checks |
| Playground | `python tools/verify_playground.py` | **PASS** — 510 checks, 660 comparisons |
| Site audit, static | `python tools/verify_phase8.py --stage static` | **333/333** |
| Site audit, pages | `--stage pages` | **96/96** |
| Site audit, responsive | `--stage responsive` | **55/55** |
| Site audit, quiz | `--stage quiz` | **67/67** |
| Site audit, UI | `--stage ui` | **16/16** |
| Site audit, screenshots | `--stage screenshots` | **15/15**, 16 PNGs captured |
| **Site audit total** | | **582/582 checks passed** |
| Browser audit | `python tools/browser_audit.py --url …` on home and quizzes | 0 console or network errors on both pages |
| Local links | Part of static stage | 2,243 local file references resolve; all same-page anchors resolve |
| Duplicate element ids | Part of static stage | 0 |
| Missing SVG icon references | Part of static stage | 0 |
| Unreplaced `{{TOKEN}}` placeholders | Build assertions and scan | 0 |
| Midnight / Daylight | UI stage and screenshots | Both themes render and toggle |
| Responsive widths | Responsive stage | 11 widths × 5 pages, 0 horizontal overflow |
| Rebuild determinism | Hash, rebuild, hash | 58 generated HTML/JSON files; **0 changed** |

The browser audit uses a temporary Chrome profile (`va-chrome-*`). It never
opens or modifies a real learner profile. Quiz storage tests use sentinel values
and confirm that `va.progress` and `va.playground.drafts` are unchanged.

No test failed. No failure was suppressed.

## 11. Unresolved copyright or licensing questions

1. **Exact font build provenance.** The bundled WOFF2 files are Latin subsets.
   Their download URL and subsetting step were not recorded. The OFL licence is
   verified and permits this, but a stricter provenance record would need the
   original download source.
2. **Release-tag mapping.** Inter reports `4.001` and JetBrains Mono `2.211`.
   These are the authoritative internal versions, but they were not matched
   file-for-file to a named upstream release archive.
3. **Original-asset provenance.** The SVG, CSS, JavaScript, prose and Verilog are
   treated as original because the repository contains no third-party markers or
   external sources. That is a provenance assessment from the available files,
   not an independent copyright search.
4. **Lighthouse.** Not run. No Node/npm/Lighthouse CLI is installed and no public
   URL exists. Performance, SEO and best-practice scores remain unmeasured.
5. **Physical Android.** The Android guide was checked in Chrome device emulation
   at 360–412 px, not on a physical handset.
6. **Screen readers.** Automated name, landmark, focus and skip-link checks pass,
   but no NVDA, JAWS or VoiceOver session was performed.
7. **GTKWave version output.** `gtkwave --version` prints nothing on this UCRT64
   build. The guide therefore documents `where.exe gtkwave` and
   `pacman -Q mingw-w64-ucrt-x86_64-gtkwave` as the evidence path.
8. **CI.** No workflow exists because the project is not yet a Git repository.

## 12. Remaining actions before GitHub publication

1. **Owner review of this report**, especially the font provenance note and the
   decision to keep the bundled subset files rather than replace them.
2. **Decide generated-output policy:** commit the 40 generated HTML pages (the
   current static-hosting model) or build them in CI.
3. **Initialise Git only after approval:** choose the repository name, owner and
   visibility, add the remote, then create the first commit. This audit did not
   run `git init`.
4. **Optional CI:** add a workflow that runs the build, example verification,
   Circuit Lab and Playground checks on Ubuntu with Icarus installed. The Chrome
   stages need a browser and a preview server, so they may stay local.
5. **Run Lighthouse against the deployed URL** and record the result.
6. **Test on a physical Android handset** and with a screen reader if the guide's
   claims are to be strengthened.
7. **Consider a SHA-256 manifest** for the font files and, if desired, a copy of
   `OFL-1.1.txt` beside each family. The current single file already satisfies
   the notice requirement.
8. **Re-run the full suite** after any further content or licence change.

Publication, deployment, repository creation and visibility changes remain
explicitly out of scope until the owner authorises them.
