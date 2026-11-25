# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 1.x | Yes |

## Reporting a vulnerability

Verilog Academy is a static site with no server, accounts or remote API. The
main risks are script injection through content, unsafe handling of
`localStorage`, and leaked local paths or credentials in the repository.

Please report suspected issues privately to the project owner. Once the
project has a repository host, use that host's private vulnerability reporting
or security-advisory feature rather than a public issue.

Include the affected page or file, the browser and version, reproduction
steps, and any suggested fix. Do not include personal progress exports,
cookies, tokens or other sensitive data in a report.

## Scope

- **In scope:** stored/reflected script injection, unsafe DOM construction,
  malformed-backup handling, localStorage key confusion, exposed secrets or
  personal paths, dependency or font-licence problems.
- **Out of scope:** the static site's inability to compile Verilog, visual
  differences between browsers, and missing features on the locked roadmap.

## Data handling

The site stores progress, quiz attempts and Playground drafts only in the
browser's `localStorage`. There is no telemetry and no upload. Export files are
created locally by the learner and are not sent anywhere.
