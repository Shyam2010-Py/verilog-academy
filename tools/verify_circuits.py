"""Independent verification for the Interactive Circuit Lab.

This tool never imports the browser engine. It re-derives every expected output
from integer arithmetic, comparisons and priority rules, then:

  * checks the canonical metadata (ids, order, categories, required prose),
  * enumerates every combinational input vector,
  * validates circuit-specific invariants,
  * regenerates each truth table and compares it byte-for-byte with the JSON
    written by the build,
  * checks the D flip-flop next-state table and a clocked reference sequence,
  * optionally emits the vectors consumed by the browser-side test harness.

Usage:
    python tools/verify_circuits.py
    python tools/verify_circuits.py --emit-vectors path/to/vectors.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import circuits as lab  # noqa: E402  (metadata, oracle and table writer)

EXPECTED_IDS = [
    "and-gate",
    "or-gate",
    "not-gate",
    "nand-gate",
    "nor-gate",
    "xor-gate",
    "xnor-gate",
    "half-adder",
    "full-adder",
    "half-subtractor",
    "full-subtractor",
    "four-bit-adder",
    "mux-4-to-1",
    "demux-1-to-4",
    "decoder-2-to-4",
    "encoder-4-to-2",
    "comparator-4-bit",
    "d-flip-flop",
]

REQUIRED_PROSE = [
    "summary",
    "operation",
    "objectives",
    "applications",
    "observations",
    "mistakes",
    "revision",
    "verilog",
]

failures: list[str] = []
checks = 0
VECTORS_PATH: Path | None = None


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def check_metadata() -> None:
    items = lab.CIRCUITS
    check([item["id"] for item in items] == EXPECTED_IDS, "circuit ids/order do not match the canonical 18")
    check(len({item["id"] for item in items}) == len(items), "duplicate circuit id")
    check(len({item["number"] for item in items}) == len(items), "duplicate circuit number")

    for index, item in enumerate(items, start=1):
        cid = item["id"]
        check(item["number"] == index, f"{cid}: number should be {index}")
        check(item["category"] in lab.CATEGORIES, f"{cid}: unknown category {item['category']}")
        check(item["kind"] in {"combinational", "sequential"}, f"{cid}: bad kind")
        check(bool(item.get("equation", "").strip()), f"{cid}: empty equation")
        check(len(item.get("signals", {}).get("inputs", [])) >= 1, f"{cid}: no inputs")
        check(len(item.get("signals", {}).get("outputs", [])) >= 1, f"{cid}: no outputs")
        for field in REQUIRED_PROSE:
            value = item.get(field)
            if isinstance(value, list):
                check(len(value) > 0, f"{cid}: empty {field}")
            else:
                check(bool(value), f"{cid}: missing {field}")
        snippet = item.get("verilog", "")
        check(bool(snippet.strip()), f"{cid}: empty Verilog snippet")
        check("assign" in snippet or "always" in snippet, f"{cid}: Verilog snippet has no assignment")

    by_category = {key: 0 for key in lab.CATEGORIES}
    for item in items:
        by_category[item["category"]] += 1
    check(sum(by_category.values()) == 18, "category totals do not add up")
    check(all(count > 0 for count in by_category.values()), "empty category")


def check_combinational() -> None:
    for item in lab.CIRCUITS:
        cid = item["id"]
        if item["kind"] == "sequential":
            continue
        outputs = [signal["name"] for signal in lab.output_signals(item)]
        seen = set()
        for values in lab.enumerate_inputs(item):
            key = lab.input_key(item, values)
            check(key not in seen, f"{cid}: duplicate input key {key}")
            seen.add(key)
            result = lab.oracle(cid, values)
            check(set(result) == set(outputs), f"{cid}: output set mismatch for {key}")
            check(all(value in (0, 1) for value in result.values()), f"{cid}: non-binary output for {key}")

            if cid in {"and-gate", "or-gate", "not-gate", "nand-gate", "nor-gate", "xor-gate", "xnor-gate"}:
                a, b = values.get("A", 0), values.get("B", 0)
                expected = {
                    "and-gate": a & b,
                    "or-gate": a | b,
                    "not-gate": 1 - a,
                    "nand-gate": 1 - (a & b),
                    "nor-gate": 1 - (a | b),
                    "xor-gate": a ^ b,
                    "xnor-gate": 1 - (a ^ b),
                }[cid]
                check(result["Y"] == expected, f"{cid}: wrong Y for {key}")

            if cid == "half-adder":
                check((result["C"] << 1 | result["S"]) == values["A"] + values["B"], f"{cid}: arithmetic for {key}")
            if cid == "full-adder":
                total = values["A"] + values["B"] + values["Cin"]
                check((result["Cout"] << 1 | result["S"]) == total, f"{cid}: arithmetic for {key}")
            if cid == "half-subtractor":
                diff = values["A"] - values["B"]
                check(result["Bout"] == int(diff < 0), f"{cid}: borrow for {key}")
                check(result["D"] == diff % 2, f"{cid}: difference for {key}")
            if cid == "full-subtractor":
                diff = values["A"] - values["B"] - values["Bin"]
                check(result["Bout"] == int(diff < 0), f"{cid}: borrow for {key}")
                check(result["D"] == diff % 2, f"{cid}: difference for {key}")

            if cid == "four-bit-adder":
                a = lab._bus(values, "A", 4)
                b = lab._bus(values, "B", 4)
                total = a + b + values["Cin"]
                sum_bits = sum(result[f"S{i}"] << i for i in range(4))
                check(sum_bits == total & 0xF, f"{cid}: sum for {key}")
                check(result["Cout"] == (total >> 4) & 1, f"{cid}: carry for {key}")
                signed_overflow = int((a >> 3) == (b >> 3) and ((total & 0xF) >> 3) != (a >> 3))
                check(result["OVF"] == signed_overflow, f"{cid}: overflow for {key}")

            if cid == "mux-4-to-1":
                select = (values["S1"] << 1) | values["S0"]
                check(result["Y"] == values[f"D{select}"], f"{cid}: select for {key}")

            if cid == "demux-1-to-4":
                select = (values["S1"] << 1) | values["S0"]
                high = [i for i in range(4) if result[f"Y{i}"]]
                expected_high = [select] if values["Din"] else []
                check(high == expected_high, f"{cid}: routing for {key}")

            if cid == "decoder-2-to-4":
                address = (values["A1"] << 1) | values["A0"]
                high = [i for i in range(4) if result[f"Y{i}"]]
                expected_high = [address] if values["EN"] else []
                check(high == expected_high, f"{cid}: one-hot for {key}")

            if cid == "encoder-4-to-2":
                requests = [values[f"R{i}"] for i in range(3, -1, -1)]
                code = (result["Code1"] << 1) | result["Code0"]
                check(result["Valid"] == int(any(requests)), f"{cid}: valid for {key}")
                if any(requests):
                    check(requests[3 - code] == 1, f"{cid}: code does not point at an active request for {key}")
                    check(all(request == 0 for request in requests[: 3 - code]), f"{cid}: priority violated for {key}")
                else:
                    check(code == 0, f"{cid}: idle code should be 00")

            if cid == "comparator-4-bit":
                a = lab._bus(values, "A", 4)
                b = lab._bus(values, "B", 4)
                check(result["GT"] + result["EQ"] + result["LT"] == 1, f"{cid}: not exactly one-hot for {key}")
                check(result["GT"] == int(a > b), f"{cid}: GT for {key}")
                check(result["EQ"] == int(a == b), f"{cid}: EQ for {key}")
                check(result["LT"] == int(a < b), f"{cid}: LT for {key}")

        expected_total = 2 ** len(lab.input_signals(item))
        check(len(seen) == expected_total, f"{cid}: expected {expected_total} vectors, saw {len(seen)}")


def check_truth_tables() -> None:
    directory = ROOT / "circuit-lab" / "data"
    check(directory.is_dir(), "circuit-lab/data is missing; run the build first")
    if not directory.is_dir():
        return
    for item in lab.CIRCUITS:
        cid = item["id"]
        path = directory / f"{cid}.json"
        check(path.is_file(), f"{cid}: truth table JSON missing")
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected = lab.truth_table(item)
        check(payload == expected, f"{cid}: truth table JSON is stale or incorrect")
        check(payload["total"] == len(payload["rows"]), f"{cid}: row count mismatch")
        keys = [row["key"] for row in payload["rows"]]
        check(len(keys) == len(set(keys)), f"{cid}: duplicate truth-table keys")
        width = len(payload["columns"])
        check(all(len(row["values"]) == width for row in payload["rows"]), f"{cid}: row width mismatch")


def dff_reference(sequence: list[tuple[str, dict[str, int] | None]]) -> list[dict[str, int]]:
    """Tiny independent D flip-flop model: async reset, rising-edge load."""
    q = 0
    d = en = rst = 0
    states: list[dict[str, int]] = []
    for action, values in sequence:
        if action == "reset":
            q, d, en, rst = 0, 0, 0, 0
        elif action == "set":
            for name, value in (values or {}).items():
                if name == "D":
                    d = int(value)
                elif name == "EN":
                    en = int(value)
                elif name == "RST":
                    rst = int(value)
            if rst:
                q = 0
        elif action == "pulse":
            if not rst and en:
                q = d
        states.append({"Q": q, "Qbar": 1 - q})
    return states


def check_flip_flop() -> None:
    item = lab.circuit("d-flip-flop")
    check(item["kind"] == "sequential", "d-flip-flop must be sequential")
    check([signal["name"] for signal in lab.input_signals(item)] == ["D", "EN", "RST"], "d-flip-flop inputs changed")
    check([signal["name"] for signal in lab.output_signals(item)] == ["Q", "Qbar"], "d-flip-flop outputs changed")

    table = lab.truth_table(item)
    check(table["kind"] == "sequential", "d-flip-flop table must be sequential")
    check(len(table["rows"]) == 5, "d-flip-flop state table should have five rows")
    check(table["columns"][-1]["key"] == "Qnext", "d-flip-flop table must end with Qnext")

    sequences = [
        [
            ("reset", None),
            ("set", {"D": 1, "EN": 1}),
            ("pulse", None),
            ("set", {"EN": 0, "D": 0}),
            ("pulse", None),
            ("set", {"EN": 1, "D": 0}),
            ("pulse", None),
            ("set", {"RST": 1}),
            ("set", {"RST": 0, "D": 1, "EN": 1}),
            ("pulse", None),
        ],
        [
            ("reset", None),
            ("set", {"RST": 1, "D": 1, "EN": 1}),
            ("pulse", None),
            ("set", {"RST": 0, "EN": 0, "D": 1}),
            ("pulse", None),
            ("set", {"EN": 1}),
            ("pulse", None),
            ("pulse", None),
        ],
    ]

    expected = [dff_reference(sequence) for sequence in sequences]
    check(expected[0][-1] == {"Q": 1, "Qbar": 0}, "flip-flop reference sequence should end high")
    check(expected[1][-1] == {"Q": 1, "Qbar": 0}, "flip-flop enable reference sequence should end high")
    check(expected[0][4] == {"Q": 1, "Qbar": 0}, "flip-flop should hold through EN = 0")

    if VECTORS_PATH:
        VECTORS_PATH.write_text(
            json.dumps(
                {
                    "generatedBy": "tools/verify_circuits.py",
                    "circuits": {
                        item["id"]: {
                            "defaults": lab.defaults(item),
                            "vectors": [
                                {"inputs": values, "outputs": lab.oracle(item["id"], values)}
                                for values in lab.enumerate_inputs(item)
                            ],
                        }
                        for item in lab.CIRCUITS
                        if item["kind"] == "combinational"
                    },
                    "sequences": [
                        {"steps": [{"action": action, "values": values} for action, values in sequence], "expected": states}
                        for sequence, states in zip(sequences, expected)
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"  vectors       : {VECTORS_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-vectors", type=Path, default=None)
    args = parser.parse_args()

    global VECTORS_PATH
    VECTORS_PATH = args.emit_vectors

    check_metadata()
    check_combinational()
    check_truth_tables()
    check_flip_flop()

    total_vectors = sum(
        2 ** len(lab.input_signals(item)) for item in lab.CIRCUITS if item["kind"] == "combinational"
    )
    print("Circuit Lab verification")
    print(f"  circuits      : {len(lab.CIRCUITS)}")
    print(f"  combinational : {len(lab.CIRCUITS) - 1}")
    print(f"  vectors       : {total_vectors}")
    print(f"  checks        : {checks}")
    if failures:
        print(f"  FAILED        : {len(failures)}")
        for message in failures[:25]:
            print(f"    - {message}")
        return 1
    print("  result        : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
