#!/usr/bin/env python3
"""Compile and run every Verilog example and record its real output.

Every lesson embeds the .v sources and the expected.txt captured here, so the
prose and the simulator can never drift apart silently.

    python tools/verify_examples.py           # run and refresh expected.txt
    python tools/verify_examples.py --check   # run and compare, do not write

Icarus Verilog is used in Verilog-2001 mode (-g2001). A non-zero exit code,
a compile error, empty output or (with --check) a mismatch fails the run.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_GROUPS = [
    ROOT / "examples" / "verilog",
    ROOT / "examples" / "labs",
    ROOT / "examples" / "playground",
]
FALLBACK_BIN = Path(r"C:\msys64\ucrt64\bin")


def find_tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for candidate in (FALLBACK_BIN / f"{name}.exe", FALLBACK_BIN / name):
        if candidate.is_file():
            return str(candidate)
    raise SystemExit(
        f"{name} was not found. Install Icarus Verilog or add its bin directory to PATH."
    )


def sources_for(directory: Path) -> list[Path]:
    design = directory / "design.v"
    single = directory / "example.v"
    tb = directory / "tb.v"
    sources = [path for path in (design, single) if path.is_file()]
    if tb.is_file():
        sources.append(tb)
    if not sources:
        raise SystemExit(f"No runnable source found in {directory}")
    return sources


def normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip() + "\n"


def run_example(directory: Path, iverilog: str, vvp: str) -> tuple[bool, str, str]:
    sources = sources_for(directory)
    with tempfile.TemporaryDirectory(prefix="va-verify-") as temp:
        image = Path(temp) / f"{directory.name}.out"
        compile_cmd = [iverilog, "-g2001", "-o", str(image)] + [p.name for p in sources]
        compiled = subprocess.run(
            compile_cmd,
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if compiled.returncode != 0:
            return False, compiled.stdout, compiled.stderr or "iverilog failed"

        simulated = subprocess.run(
            [vvp, str(image)],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if simulated.returncode != 0:
            return False, simulated.stdout, simulated.stderr or "vvp failed"
        return True, normalise(simulated.stdout), compiled.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare instead of writing")
    args = parser.parse_args()

    iverilog = find_tool("iverilog")
    vvp = find_tool("vvp")

    directories = sorted(
        directory for group in EXAMPLE_GROUPS for directory in group.iterdir() if directory.is_dir()
    )
    if not directories:
        raise SystemExit(f"No examples found under {', '.join(str(g) for g in EXAMPLE_GROUPS)}")

    failures = 0
    for directory in directories:
        ok, output, warnings = run_example(directory, iverilog, vvp)
        label = directory.name
        if not ok:
            failures += 1
            print(f"FAIL  {label}")
            print(output)
            print(warnings)
            continue

        if not output.strip():
            failures += 1
            print(f"FAIL  {label}: simulator produced no output")
            continue

        target = directory / "expected.txt"
        if args.check:
            previous = (
                normalise(target.read_text(encoding="utf-8")) if target.is_file() else None
            )
            if previous != output:
                failures += 1
                print(f"FAIL  {label}: output does not match expected.txt")
                if previous is None:
                    print("      expected.txt is missing; run without --check to create it")
                continue
        else:
            target.write_text(output, encoding="utf-8", newline="\n")

        note = ""
        if warnings.strip():
            note = f"  ({len(warnings.strip().splitlines())} compiler warning line(s))"
        print(f"ok    {label}{note}")
        if warnings.strip() and not args.check:
            print(warnings.rstrip())

    total = len(directories)
    print(f"\n{total - failures}/{total} examples passed")
    if failures:
        print("Review the failures above before rebuilding the site.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
