# Bundled fonts

The nine WOFF2 files in this directory are third-party Font Software, not
original Verilog Academy material. They are not covered by the project's MIT
or CC BY-NC-SA 4.0 licences.

Each family is licensed under the SIL Open Font License, Version 1.1. The full
licence text and the required copyright notices are in
[`OFL-1.1.txt`](OFL-1.1.txt).

## File inventory

Metadata below was read from each file's embedded `name`, `head` and `OS/2`
tables. Weights are the CSS weights declared in `css/fonts.css`.

| File | Family | Style | Weight | Internal version | Copyright notice |
|---|---|---|---:|---|---|
| `space-grotesk-500.woff2` | Space Grotesk | Medium | 500 | 2.000 | Copyright 2020 The Space Grotesk Project Authors |
| `space-grotesk-600.woff2` | Space Grotesk | SemiBold | 600 | 2.000 | Copyright 2020 The Space Grotesk Project Authors |
| `space-grotesk-700.woff2` | Space Grotesk | Bold | 700 | 2.000 | Copyright 2020 The Space Grotesk Project Authors |
| `inter-400.woff2` | Inter | Regular | 400 | 4.001;git-66647c0bb | Copyright 2016 The Inter Project Authors |
| `inter-500.woff2` | Inter | Medium | 500 | 4.001;git-66647c0bb | Copyright 2016 The Inter Project Authors |
| `inter-600.woff2` | Inter | SemiBold | 600 | 4.001;git-66647c0bb | Copyright 2016 The Inter Project Authors |
| `inter-700.woff2` | Inter | Bold | 700 | 4.001;git-66647c0bb | Copyright 2016 The Inter Project Authors |
| `jetbrains-mono-400.woff2` | JetBrains Mono | Regular | 400 | 2.211 | Copyright 2020 The JetBrains Mono Project Authors |
| `jetbrains-mono-500.woff2` | JetBrains Mono | Medium | 500 | 2.211 | Copyright 2020 The JetBrains Mono Project Authors |

Every file also embeds the licence URL `https://openfontlicense.org` (Inter) or
`https://scripts.sil.org/OFL` (Space Grotesk and JetBrains Mono). No Reserved
Font Names are declared in the upstream licence files or in the embedded
metadata.

Some static builds use internal family names that include the weight, for
example `Space Grotesk Light Medium` and `Inter Medium`. `css/fonts.css` maps
them to the public family names and the weights above; the files were not
renamed.

## Upstream projects

| Family | Upstream source | Designer / project |
|---|---|---|
| Space Grotesk | <https://github.com/floriankarsten/space-grotesk> | Florian Karsten / The Space Grotesk Project Authors |
| Inter | <https://github.com/rsms/inter> | Rasmus Andersson (rsms) / The Inter Project Authors |
| JetBrains Mono | <https://github.com/JetBrains/JetBrainsMono> | JetBrains / The JetBrains Mono Project Authors |

## Redistribution status

The SIL OFL 1.1 permits bundling and redistributing the Font Software with
software, provided the copyright notice and licence accompany each copy. This
directory satisfies that condition with `OFL-1.1.txt`, and
`THIRD-PARTY-NOTICES.md` points to it.

The bundled files contain a Latin/punctuation subset of the upstream character
sets. The exact download URL and subsetting step were not recorded when the
files were added, so the build provenance is reported as partially unresolved
in `docs/final-audit/REPORT.md`. The licence itself is verified from the
embedded metadata and the upstream repositories.
