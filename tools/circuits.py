"""Circuit Lab metadata, independent oracle and static renderer.

The JavaScript engine in js/circuit-engine.js is the interactive implementation.
Everything in this module is an independent model used to build the displayed
truth tables and the verification vectors. It must not mirror the JavaScript
gate structure: adders are checked with integer arithmetic, comparators with
integer comparison, and encoders with a priority loop.
"""

from __future__ import annotations

import html
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "circuits.json").read_text(encoding="utf-8"))

CATEGORIES = {item["id"]: item for item in DATA["categories"]}
CIRCUITS = DATA["circuits"]
BY_ID = {item["id"]: item for item in CIRCUITS}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def circuit(circuit_id: str) -> dict:
    try:
        return BY_ID[circuit_id]
    except KeyError as error:
        raise RuntimeError(f"Unknown circuit: {circuit_id}") from error


def input_signals(item: dict) -> list[dict]:
    return item["signals"]["inputs"]


def output_signals(item: dict) -> list[dict]:
    return item["signals"]["outputs"]


def defaults(item: dict) -> dict[str, int]:
    return {signal["name"]: int(signal.get("default", 0)) for signal in input_signals(item)}


def _bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width - 1, -1, -1)]


def _bus(values: dict, prefix: str, width: int) -> int:
    value = 0
    for index in range(width - 1, -1, -1):
        value = (value << 1) | int(values[f"{prefix}{index}"])
    return value


def oracle(circuit_id: str, values: dict[str, int]) -> dict[str, int]:
    """Independent expected outputs for one input vector."""
    v = {key: int(val) for key, val in values.items()}
    if circuit_id == "and-gate":
        return {"Y": int(bool(v["A"]) and bool(v["B"]))}
    if circuit_id == "or-gate":
        return {"Y": int(bool(v["A"]) or bool(v["B"]))}
    if circuit_id == "not-gate":
        return {"Y": int(not v["A"])}
    if circuit_id == "nand-gate":
        return {"Y": int(not (v["A"] and v["B"]))}
    if circuit_id == "nor-gate":
        return {"Y": int(not (v["A"] or v["B"]))}
    if circuit_id == "xor-gate":
        return {"Y": int(bool(v["A"]) != bool(v["B"]))}
    if circuit_id == "xnor-gate":
        return {"Y": int(bool(v["A"]) == bool(v["B"]))}
    if circuit_id == "half-adder":
        total = v["A"] + v["B"]
        return {"S": total & 1, "C": total >> 1}
    if circuit_id == "full-adder":
        total = v["A"] + v["B"] + v["Cin"]
        return {"S": total & 1, "Cout": total >> 1}
    if circuit_id == "half-subtractor":
        total = v["A"] - v["B"]
        return {"D": total % 2, "Bout": int(total < 0)}
    if circuit_id == "full-subtractor":
        total = v["A"] - v["B"] - v["Bin"]
        return {"D": total % 2, "Bout": int(total < 0)}
    if circuit_id == "four-bit-adder":
        a = _bus(v, "A", 4)
        b = _bus(v, "B", 4)
        total = a + b + v["Cin"]
        result = total & 0xF
        sign_a = (a >> 3) & 1
        sign_b = (b >> 3) & 1
        sign_s = (result >> 3) & 1
        overflow = int(sign_a == sign_b and sign_s != sign_a)
        outputs = {f"S{i}": (result >> i) & 1 for i in range(4)}
        outputs["Cout"] = (total >> 4) & 1
        outputs["OVF"] = overflow
        return outputs
    if circuit_id == "mux-4-to-1":
        select = (v["S1"] << 1) | v["S0"]
        return {"Y": v[f"D{select}"]}
    if circuit_id == "demux-1-to-4":
        select = (v["S1"] << 1) | v["S0"]
        return {f"Y{i}": (v["Din"] if select == i else 0) for i in range(4)}
    if circuit_id == "decoder-2-to-4":
        address = (v["A1"] << 1) | v["A0"]
        return {f"Y{i}": (v["EN"] if address == i else 0) for i in range(4)}
    if circuit_id == "encoder-4-to-2":
        code = 0
        valid = 0
        for index in range(3, -1, -1):
            if v[f"R{index}"]:
                code = index
                valid = 1
                break
        return {"Code1": (code >> 1) & 1, "Code0": code & 1, "Valid": valid}
    if circuit_id == "comparator-4-bit":
        a = _bus(v, "A", 4)
        b = _bus(v, "B", 4)
        return {"GT": int(a > b), "EQ": int(a == b), "LT": int(a < b)}
    raise RuntimeError(f"No combinational oracle for {circuit_id}")


def enumerate_inputs(item: dict):
    signals = input_signals(item)
    for combination in itertools.product((0, 1), repeat=len(signals)):
        yield {signal["name"]: int(bit) for signal, bit in zip(signals, combination)}


def input_key(item: dict, values: dict[str, int]) -> str:
    return "".join(str(int(values[signal["name"]])) for signal in input_signals(item))


def _decimal(bits: dict[str, int], prefix: str, width: int) -> int:
    value = 0
    for index in range(width - 1, -1, -1):
        value = (value << 1) | int(bits[f"{prefix}{index}"])
    return value


def truth_table(item: dict) -> dict:
    cid = item["id"]
    if item["kind"] == "sequential":
        rows = [
            {"key": "reset", "values": ["1", "X", "X", "X", "0 (async)"]},
            {"key": "load0", "values": ["0", "↑", "1", "0", "0"]},
            {"key": "load1", "values": ["0", "↑", "1", "1", "1"]},
            {"key": "hold-en", "values": ["0", "↑", "0", "X", "Q (hold)"]},
            {"key": "hold-noedge", "values": ["0", "0 or 1", "X", "X", "Q (hold)"]},
        ]
        return {
            "id": cid,
            "kind": "sequential",
            "caption": "D flip-flop state table",
            "note": "This is a next-state table, not a combinational truth table. Q changes only at a rising edge, except for asynchronous reset.",
            "columns": [
                {"key": "RST", "label": "RST", "scope": "input"},
                {"key": "CLK", "label": "CLK", "scope": "input"},
                {"key": "EN", "label": "EN", "scope": "input"},
                {"key": "D", "label": "D", "scope": "input"},
                {"key": "Qnext", "label": "Qnext", "scope": "output"},
            ],
            "rows": rows,
            "total": len(rows),
        }

    rows = []
    for values in enumerate_inputs(item):
        outputs = oracle(cid, values)
        cells: list[str] = []
        if cid in {"and-gate", "or-gate", "nand-gate", "nor-gate", "xor-gate", "xnor-gate", "half-adder", "half-subtractor"}:
            cells.extend(str(values[signal["name"]]) for signal in input_signals(item))
            cells.extend(str(outputs[signal["name"]]) for signal in output_signals(item))
            if cid in {"half-adder", "half-subtractor"}:
                total = values["A"] + values["B"] if cid == "half-adder" else values["A"] - values["B"]
                cells.append(str(total))
        elif cid == "not-gate":
            cells = [str(values["A"]), str(outputs["Y"])]
        elif cid in {"full-adder", "full-subtractor"}:
            cells.extend(str(values[signal["name"]]) for signal in input_signals(item))
            cells.extend(str(outputs[signal["name"]]) for signal in output_signals(item))
            total = (
                values["A"] + values["B"] + values["Cin"]
                if cid == "full-adder"
                else values["A"] - values["B"] - values["Bin"]
            )
            cells.append(str(total))
        elif cid == "four-bit-adder":
            a = _decimal(values, "A", 4)
            b = _decimal(values, "B", 4)
            s = _decimal(outputs, "S", 4)
            cells = [
                str(a),
                *[str(values[f"A{i}"]) for i in range(3, -1, -1)],
                str(b),
                *[str(values[f"B{i}"]) for i in range(3, -1, -1)],
                str(values["Cin"]),
                str(s),
                *[str(outputs[f"S{i}"]) for i in range(3, -1, -1)],
                str(outputs["Cout"]),
                str(outputs["OVF"]),
            ]
        elif cid == "mux-4-to-1":
            cells = [
                str(values["S1"]),
                str(values["S0"]),
                *[str(values[f"D{i}"]) for i in range(3, -1, -1)],
                str(outputs["Y"]),
            ]
        elif cid == "demux-1-to-4":
            cells = [str(values["Din"]), str(values["S1"]), str(values["S0"])]
            cells.extend(str(outputs[f"Y{i}"]) for i in range(3, -1, -1))
        elif cid == "decoder-2-to-4":
            cells = [str(values["EN"]), str(values["A1"]), str(values["A0"])]
            cells.extend(str(outputs[f"Y{i}"]) for i in range(3, -1, -1))
        elif cid == "encoder-4-to-2":
            code = (outputs["Code1"] << 1) | outputs["Code0"]
            cells = [str(values[f"R{i}"]) for i in range(3, -1, -1)]
            cells.extend([str(code), str(outputs["Code1"]), str(outputs["Code0"]), str(outputs["Valid"])])
        elif cid == "comparator-4-bit":
            a = _decimal(values, "A", 4)
            b = _decimal(values, "B", 4)
            cells = [
                str(a),
                *[str(values[f"A{i}"]) for i in range(3, -1, -1)],
                str(b),
                *[str(values[f"B{i}"]) for i in range(3, -1, -1)],
                str(outputs["GT"]),
                str(outputs["EQ"]),
                str(outputs["LT"]),
            ]
        else:
            raise RuntimeError(f"No table renderer for {cid}")
        rows.append({"key": input_key(item, values), "values": cells})

    columns = columns_for(item)
    return {
        "id": cid,
        "kind": item["kind"],
        "caption": item["table"]["caption"],
        "note": item["table"]["note"],
        "columns": columns,
        "rows": rows,
        "total": len(rows),
    }


def columns_for(item: dict) -> list[dict]:
    cid = item["id"]
    if cid in {"and-gate", "or-gate", "nand-gate", "nor-gate", "xor-gate", "xnor-gate"}:
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "B", "label": "B", "scope": "input"},
            {"key": "Y", "label": "Y", "scope": "output"},
        ]
    if cid == "not-gate":
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "Y", "label": "Y", "scope": "output"},
        ]
    if cid == "half-adder":
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "B", "label": "B", "scope": "input"},
            {"key": "S", "label": "S", "scope": "output"},
            {"key": "C", "label": "C", "scope": "output"},
            {"key": "sum", "label": "A + B", "scope": "value"},
        ]
    if cid == "full-adder":
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "B", "label": "B", "scope": "input"},
            {"key": "Cin", "label": "Cin", "scope": "input"},
            {"key": "S", "label": "S", "scope": "output"},
            {"key": "Cout", "label": "Cout", "scope": "output"},
            {"key": "sum", "label": "Total", "scope": "value"},
        ]
    if cid == "half-subtractor":
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "B", "label": "B", "scope": "input"},
            {"key": "D", "label": "D", "scope": "output"},
            {"key": "Bout", "label": "Bout", "scope": "output"},
            {"key": "result", "label": "A − B", "scope": "value"},
        ]
    if cid == "full-subtractor":
        return [
            {"key": "A", "label": "A", "scope": "input"},
            {"key": "B", "label": "B", "scope": "input"},
            {"key": "Bin", "label": "Bin", "scope": "input"},
            {"key": "D", "label": "D", "scope": "output"},
            {"key": "Bout", "label": "Bout", "scope": "output"},
            {"key": "result", "label": "Result", "scope": "value"},
        ]
    if cid == "four-bit-adder":
        columns = [{"key": "Adec", "label": "A", "scope": "value"}]
        columns += [{"key": f"A{i}", "label": f"A{i}", "scope": "input"} for i in range(3, -1, -1)]
        columns += [{"key": "Bdec", "label": "B", "scope": "value"}]
        columns += [{"key": f"B{i}", "label": f"B{i}", "scope": "input"} for i in range(3, -1, -1)]
        columns += [{"key": "Cin", "label": "Cin", "scope": "input"}, {"key": "Sdec", "label": "S", "scope": "value"}]
        columns += [{"key": f"S{i}", "label": f"S{i}", "scope": "output"} for i in range(3, -1, -1)]
        columns += [{"key": "Cout", "label": "Cout", "scope": "output"}, {"key": "OVF", "label": "OVF", "scope": "output"}]
        return columns
    if cid == "mux-4-to-1":
        return [
            {"key": "S1", "label": "S1", "scope": "input"},
            {"key": "S0", "label": "S0", "scope": "input"},
            *[{"key": f"D{i}", "label": f"D{i}", "scope": "input"} for i in range(3, -1, -1)],
            {"key": "Y", "label": "Y", "scope": "output"},
        ]
    if cid in {"demux-1-to-4", "decoder-2-to-4"}:
        if cid == "demux-1-to-4":
            base = [
                {"key": "Din", "label": "Din", "scope": "input"},
                {"key": "S1", "label": "S1", "scope": "input"},
                {"key": "S0", "label": "S0", "scope": "input"},
            ]
        else:
            base = [
                {"key": "EN", "label": "EN", "scope": "input"},
                {"key": "A1", "label": "A1", "scope": "input"},
                {"key": "A0", "label": "A0", "scope": "input"},
            ]
        base += [{"key": f"Y{i}", "label": f"Y{i}", "scope": "output"} for i in range(3, -1, -1)]
        return base
    if cid == "encoder-4-to-2":
        return [
            *[{"key": f"R{i}", "label": f"R{i}", "scope": "input"} for i in range(3, -1, -1)],
            {"key": "code", "label": "Code", "scope": "value"},
            {"key": "Code1", "label": "Code1", "scope": "output"},
            {"key": "Code0", "label": "Code0", "scope": "output"},
            {"key": "Valid", "label": "Valid", "scope": "output"},
        ]
    if cid == "comparator-4-bit":
        columns = [{"key": "Adec", "label": "A", "scope": "value"}]
        columns += [{"key": f"A{i}", "label": f"A{i}", "scope": "input"} for i in range(3, -1, -1)]
        columns += [{"key": "Bdec", "label": "B", "scope": "value"}]
        columns += [{"key": f"B{i}", "label": f"B{i}", "scope": "input"} for i in range(3, -1, -1)]
        columns += [
            {"key": "GT", "label": "GT", "scope": "output"},
            {"key": "EQ", "label": "EQ", "scope": "output"},
            {"key": "LT", "label": "LT", "scope": "output"},
        ]
        return columns
    raise RuntimeError(f"No column map for {cid}")


def write_truth_tables(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for item in CIRCUITS:
        target = directory / f"{item['id']}.json"
        payload = truth_table(item)
        target.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )
        written.append(target)
    return written


# ---------------------------------------------------------------------------
# Static HTML
# ---------------------------------------------------------------------------

def _render_switch(signal: dict) -> str:
    name = signal["name"]
    return (
        f'<button class="bench-switch" type="button" role="switch" aria-checked="false" '
        f'data-input="{esc(name)}" aria-label="{esc(signal["label"])} input, currently 0">'
        f'<span class="bench-switch__label">{esc(signal["label"])}</span>'
        f'<span class="bench-switch__track" aria-hidden="true"><span></span></span>'
        f'<span class="bench-switch__value" data-input-value="{esc(name)}">0</span>'
        f"</button>"
    )


def _render_inputs(item: dict) -> str:
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for signal in input_signals(item):
        group = signal.get("group") or ""
        if group not in groups:
            groups[group] = []
            order.append(group)
        groups[group].append(signal)

    chunks = []
    for group in order:
        signals = groups[group]
        label = group
        content = "".join(_render_switch(signal) for signal in signals)
        if label:
            chunks.append(
                '<div class="bench-group">'
                f'<span class="bench-group__label">{esc(label)}</span>'
                f'<div class="bench-group__row">{content}</div>'
                "</div>"
            )
        else:
            chunks.append(f'<div class="bench-group bench-group--single">{content}</div>')
    return "".join(chunks)


def _render_outputs(item: dict) -> str:
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for signal in output_signals(item):
        group = signal.get("group") or ""
        if group not in groups:
            groups[group] = []
            order.append(group)
        groups[group].append(signal)

    chunks = []
    for group in order:
        signals = groups[group]
        label = group
        items = "".join(
            f'<div class="bench-output" data-output="{esc(signal["name"])}">'
            f'<span class="bench-led" data-led="{esc(signal["name"])}" aria-hidden="true"></span>'
            f'<span class="bench-output__label">{esc(signal["label"])}</span>'
            f'<strong class="bench-output__value" data-output-value="{esc(signal["name"])}">0</strong>'
            "</div>"
            for signal in signals
        )
        if label:
            chunks.append(
                '<div class="bench-group bench-group--out">'
                f'<span class="bench-group__label">{esc(label)}</span>'
                f'<div class="bench-group__row">{items}</div>'
                "</div>"
            )
        else:
            chunks.append(f'<div class="bench-group bench-group--single">{items}</div>')
    return "".join(chunks)


def _render_list(values: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(value)}</li>" for value in values) + "</ul>"


def _render_card(item: dict, index: int) -> str:
    cid = item["id"]
    category = CATEGORIES[item["category"]]
    initial = oracle(cid, defaults(item)) if item["kind"] == "combinational" else {"Q": 0, "Qbar": 1}
    for signal in output_signals(item):
        # Server-rendered initial outputs are only a fallback; the engine repaints them.
        pass
    kind_label = "Sequential" if item["kind"] == "sequential" else "Combinational"
    kind_badge = "badge-cyan" if item["kind"] == "sequential" else "badge"
    clock_controls = ""
    if item["kind"] == "sequential":
        clock_controls = (
            '<div class="bench-clock" data-clock-controls>'
            '<button class="btn btn-primary btn-sm" type="button" data-clock-pulse>'
            '<svg class="icon icon-sm" aria-hidden="true"><use href="#icon-play"></use></svg>'
            "Clock ↑</button>"
            '<button class="btn btn-secondary btn-sm" type="button" data-clock-auto aria-pressed="false">'
            "Auto clock</button>"
            '<span class="bench-clock__led" data-clock-led aria-hidden="true"></span>'
            '<span class="bench-clock__state" data-clock-state>CLK = 0</span>'
            "</div>"
            '<div class="bench-edge-log">'
            '<span class="bench-edge-log__label">Edge log</span>'
            '<ol class="bench-edge-log__list" data-edge-list aria-live="polite"></ol>'
            "</div>"
        )
    random_button = (
        '<button class="btn btn-secondary btn-sm" type="button" data-bench-random>Randomise inputs</button>'
        if item["kind"] == "combinational"
        else ""
    )
    verilog = esc(item["verilog"]).replace("\n", "<br>")
    search_blob = " ".join(
        [
            item["title"],
            item["summary"],
            category["title"],
            kind_label,
            item["equation"],
            " ".join(item["objectives"]),
            " ".join(item["applications"]),
        ]
    ).lower()
    table_note = esc(item["table"]["note"])
    clock_note = (
        "Only a rising edge can update Q. RST acts immediately, even with no clock edge."
        if item["kind"] == "sequential"
        else "The truth table describes the settled output after every input combination."
    )
    timing = (
        "Sequential logic stores state. Q changes on a rising clock edge, or immediately when asynchronous RST is high. "
        "Changing D while EN is low, or while the clock is not rising, must leave Q unchanged. The clock button creates one rising edge; "
        "auto-clock repeats it. This is a zero-delay functional model and does not model metastability."
        if item["kind"] == "sequential"
        else "Combinational logic has no stored state. The output is a function of the present inputs. In this ideal model it updates immediately; "
        "real gates add a small propagation delay, and unequal path delays can produce a brief glitch while the output settles. "
        "The truth table describes the settled result, not every transient."
    )
    outputs_html = _render_outputs(item)
    # Replace the placeholder zeros with the independent initial oracle values.
    for signal in output_signals(item):
        name = signal["name"]
        outputs_html = outputs_html.replace(
            f'data-output-value="{esc(name)}">0</strong>',
            f'data-output-value="{esc(name)}">{int(initial[name])}</strong>',
            1,
        )
    # LED initial state is painted by JavaScript; the fallback stays low.

    return f"""
      <article class="circuit-card panel" id="circuit-{esc(cid)}" data-circuit="{esc(cid)}" data-category="{esc(item["category"])}" data-kind="{esc(item["kind"])}" data-search="{esc(search_blob)}" data-reveal>
        <header class="circuit-card__head">
          <span class="circuit-card__num">{index:02d}</span>
          <div class="circuit-card__title-wrap">
            <div class="circuit-card__tags">
              <span class="badge badge-violet">{esc(category["title"])}</span>
              <span class="badge {kind_badge}">{kind_label}</span>
            </div>
            <h3 class="circuit-card__title">{esc(item["title"])}</h3>
            <p class="circuit-card__summary">{esc(item["summary"])}</p>
          </div>
          <span class="circuit-card__scope">{esc(item["scope"])}</span>
        </header>

        <div class="bench" data-bench="{esc(cid)}">
          <div class="bench__visual">
            <div class="bench__diagram" data-diagram="{esc(cid)}" role="img" aria-label="Interactive logic diagram for {esc(item["title"])}"></div>
            <div class="bench__legend" aria-hidden="true">
              <span><i class="legend-dot legend-dot--high"></i>logic 1</span>
              <span><i class="legend-dot"></i>logic 0</span>
              <span class="bench__legend-note">active-high</span>
            </div>
          </div>
          <div class="bench__panel">
            <div class="bench__inputs">
              <span class="bench__panel-label">Inputs</span>
              {_render_inputs(item)}
            </div>
            <div class="bench__outputs">
              <span class="bench__panel-label">Outputs</span>
              {outputs_html}
            </div>
            <p class="bench__summary" data-bench-summary aria-live="polite">Set the inputs to evaluate this circuit.</p>
            {clock_controls}
            <div class="bench__actions">
              <button class="btn btn-secondary btn-sm" type="button" data-bench-reset>
                <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-reset"></use></svg>
                Reset
              </button>
              {random_button}
            </div>
          </div>
        </div>

        <div class="circuit-equation">
          <span class="circuit-equation__label">Boolean</span>
          <code>{esc(item["equation"])}</code>
        </div>

        <details class="circuit-notes" data-notes="{esc(cid)}" data-truth-src="data/{esc(cid)}.json">
          <summary>
            <span>Study this circuit</span>
            <span class="circuit-notes__meta">{esc(item["scope"])} &middot; truth table and worked notes</span>
            <svg class="icon icon-sm circuit-notes__chevron" aria-hidden="true"><use href="#icon-chevron-down"></use></svg>
          </summary>
          <div class="circuit-notes__body">
            <div class="notes-grid">
              <section class="note-block">
                <h4>Learning objectives</h4>
                {_render_list(item["objectives"])}
              </section>
              <section class="note-block">
                <h4>Circuit operation</h4>
                {"".join(f"<p>{esc(paragraph)}</p>" for paragraph in item["operation"])}
              </section>
              <section class="note-block">
                <h4>Inputs and outputs</h4>
                <p>{esc(item["io"])}</p>
              </section>
              <section class="note-block">
                <h4>Practical example</h4>
                {_render_list(item["applications"])}
              </section>
              <section class="note-block">
                <h4>Observations</h4>
                {_render_list(item["observations"])}
              </section>
              <section class="note-block">
                <h4>Common mistakes</h4>
                {_render_list(item["mistakes"])}
              </section>
            </div>

            <section class="truth-panel">
              <div class="truth-panel__head">
                <div>
                  <h4>{esc(item["table"]["caption"])}</h4>
                  <p>{table_note}</p>
                </div>
                <span class="badge badge-cyan" data-truth-count>Loading table</span>
              </div>
              <p class="truth-hint">{clock_note} The active input row is highlighted while the bench is live.</p>
              <div class="truth-table-wrap" data-truth-table>
                <p class="truth-loading">Open this section to load the complete truth table.</p>
              </div>
            </section>

            <div class="notes-grid notes-grid--lower">
              <section class="note-block">
                <h4>Timing and state</h4>
                <p>{esc(timing)}</p>
              </section>
              <section class="note-block">
                <h4>In Verilog</h4>
                <pre class="circuit-code"><code>{verilog}</code></pre>
              </section>
              <section class="note-block">
                <h4>Revision</h4>
                {_render_list(item["revision"])}
              </section>
            </div>
            <p class="circuit-disclaimer">This bench is a JavaScript logic model. It evaluates the same Boolean behaviour as the circuit but it does not compile or simulate Verilog.</p>
          </div>
        </details>
      </article>
    """


def render_lab() -> str:
    total = len(CIRCUITS)
    combinational = sum(1 for item in CIRCUITS if item["kind"] == "combinational")
    sequential = total - combinational
    category_chips = [
        '<button class="filter-chip is-active" type="button" data-filter="#" aria-pressed="true">All circuits</button>'
    ]
    for category in DATA["categories"]:
        count = sum(1 for item in CIRCUITS if item["category"] == category["id"])
        category_chips.append(
            f'<button class="filter-chip" type="button" data-filter="{esc(category["id"])}" aria-pressed="false">'
            f'{esc(category["title"])}<span>{count}</span></button>'
        )
    cards = "\n".join(_render_card(item, index) for index, item in enumerate(CIRCUITS, start=1))
    category_links = "".join(
        f'<a class="workbench-jump" href="#circuits" data-filter-link="{esc(category["id"])}">'
        f'<span>{esc(category["title"])}</span><strong>{sum(1 for item in CIRCUITS if item["category"] == category["id"])}</strong>'
        "</a>"
        for category in DATA["categories"]
    )

    return f"""
<section class="theory-hero circuit-hero">
  <div class="theory-hero__atmosphere" aria-hidden="true"></div>
  <div class="container circuit-hero__grid">
    <div class="circuit-hero__copy" data-reveal>
      <span class="eyebrow">Interactive Circuit Lab</span>
      <h1 class="display">{total} working circuits.<br><span class="gradient-text">Not screenshots.</span></h1>
      <p class="lede">Flip a switch and the diagram, Boolean expression, output state and truth table move together. Seven gates, five arithmetic blocks, three routing circuits, two code blocks and a clocked flip-flop, all built as one reusable vanilla JavaScript engine.</p>
      <p class="circuit-hero__claim">This is a digital electronics workbench, not a Verilog compiler. It models logic levels and state so you can test your understanding before you write HDL.</p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="#circuit-and-gate">
          Start with the AND gate
          <svg class="icon" aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
        </a>
        <a class="btn btn-secondary btn-lg" href="#how-it-works">How the bench works</a>
      </div>
      <div class="hero-facts theory-facts" aria-label="Circuit Lab scope">
        <div><strong>{total}</strong><span>Working demos</span></div>
        <div><strong>{combinational}</strong><span>Combinational</span></div>
        <div><strong>{sequential}</strong><span>Sequential</span></div>
        <div><strong>18</strong><span>Verified engines</span></div>
      </div>
      <div class="circuit-hero__links">
        <a class="text-link" href="{{{{ROOT}}}}theory/index.html">EC-405 theory <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg></a>
        <a class="text-link" href="{{{{ROOT}}}}labs/index.html">EC-410 laboratory <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg></a>
        <a class="text-link" href="{{{{ROOT}}}}dashboard.html">Dashboard <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg></a>
      </div>
    </div>

    <aside class="circuit-hero__panel panel" data-reveal style="--reveal-delay: 100ms">
      <div class="circuit-hero__panel-head">
        <span class="panel-kicker">Bench rules</span>
        <span class="badge badge-success"><span class="badge-dot"></span>Live</span>
      </div>
      <ol class="bench-rules">
        <li><strong>1 = high.</strong><span>Every input and output on this page is active-high unless a bubble or a Q̄ label says otherwise.</span></li>
        <li><strong>Change one input.</strong><span>Watch the wire, the lamp, the equation and the highlighted row move together.</span></li>
        <li><strong>Check the table.</strong><span>Open “Study this circuit” for the complete truth table, worked notes and the Verilog equivalent.</span></li>
      </ol>
      <div class="circuit-hero__categories">{category_links}</div>
    </aside>
  </div>
</section>

<div class="container">
  <noscript>
    <div class="theory-noscript">
      <svg class="icon" aria-hidden="true"><use href="#icon-alert"></use></svg>
      <p><strong>The bench needs JavaScript.</strong> The notes and equations are readable without it, but switches, diagrams, live outputs and truth-table highlighting cannot work. This page never loads a Verilog simulator.</p>
    </div>
  </noscript>
</div>

<section class="section-tight circuit-how" id="how-it-works">
  <div class="container">
    <div class="section-header" data-reveal>
      <div>
        <span class="eyebrow">01 / The workbench</span>
        <h2>Set. Read. Prove.</h2>
      </div>
      <p>Every demo runs the same loop. Set the active-high inputs, read the live outputs and diagram, then open the notes and compare the highlighted row with the Boolean equation.</p>
    </div>
    <div class="circuit-how__grid">
      <article class="circuit-how__step panel" data-reveal>
        <span class="circuit-how__num">01</span>
        <h3>Set the inputs</h3>
        <p>Each switch is a logic source. A switch labelled 1 drives the node high; 0 drives it low. Buses such as A3…A0 are grouped, with the highest bit first.</p>
      </article>
      <article class="circuit-how__step panel" data-reveal style="--reveal-delay: 60ms">
        <span class="circuit-how__num">02</span>
        <h3>Read the outputs</h3>
        <p>LEDs and numeric values show the present output. The SVG diagram colours live wires and highlights the selected channel or active path. The Boolean expression never changes; the values do.</p>
      </article>
      <article class="circuit-how__step panel" data-reveal style="--reveal-delay: 120ms">
        <span class="circuit-how__num">03</span>
        <h3>Check the table</h3>
        <p>Open the notes to load the complete truth table. The row matching the live inputs is highlighted. For the flip-flop, the state table and edge log replace combinational highlighting.</p>
      </article>
    </div>
    <div class="circuit-conventions panel" data-reveal>
      <div>
        <span class="panel-kicker">Conventions used here</span>
        <h3>Active-high, ideal timing, honest boundaries.</h3>
      </div>
      <dl class="convention-list">
        <div><dt>Active-high</dt><dd>A plain signal name means 1 = high = true. A bubble, overbar or “active-low” label marks the opposite polarity. Q̄ is the complement of Q.</dd></div>
        <div><dt>Combinational</dt><dd>No stored state. Outputs settle from the present inputs. Real gates add propagation delay; this model updates immediately.</dd></div>
        <div><dt>Sequential</dt><dd>State changes only on a clock edge, except asynchronous reset. The D flip-flop exposes clock, enable and reset separately so you can test each one.</dd></div>
        <div><dt>Not Verilog</dt><dd>The engine evaluates JavaScript logic functions. It does not parse, compile or simulate Verilog, and it is not a timing-accurate simulator.</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section-tight circuit-directory" id="circuits">
  <div class="container">
    <div class="section-header" data-reveal>
      <div>
        <span class="eyebrow">02 / The bench</span>
        <h2>All {total} demonstrations.</h2>
      </div>
      <p>Filter by category or search by name, equation or application. Each card is a working bench; nothing is a static picture. Reset any circuit at any time.</p>
    </div>

    <div class="circuit-toolbar panel" data-circuit-toolbar>
      <div class="circuit-search">
        <label for="circuit-search">Search circuits</label>
        <div class="circuit-search__field">
          <svg class="icon" aria-hidden="true"><use href="#icon-search"></use></svg>
          <input id="circuit-search" type="search" placeholder="AND, adder, select, compare, flip-flop…" autocomplete="off" spellcheck="false">
          <button class="circuit-search__clear" type="button" data-search-clear hidden aria-label="Clear search">Clear</button>
        </div>
      </div>
      <div class="circuit-filters" role="group" aria-label="Filter circuits by category">
        {"".join(category_chips)}
      </div>
      <p class="circuit-count" data-circuit-count aria-live="polite">Showing all {total} circuits</p>
    </div>

    <div class="circuit-empty panel" data-circuit-empty hidden>
      <svg class="icon icon-lg" aria-hidden="true"><use href="#icon-search"></use></svg>
      <h3>No circuits match that search.</h3>
      <p>Try a gate name, a function such as “subtract”, or a category such as “routing”.</p>
      <button class="btn btn-secondary btn-sm" type="button" data-search-reset>Clear filters</button>
    </div>

    <div class="circuit-grid">
      {cards}
    </div>
  </div>
</section>

<section class="section-tight">
  <div class="container">
    <div class="panel panel-glow cta-panel" data-reveal>
      <div>
        <span class="eyebrow">Next step</span>
        <h2>Predict first. Then switch.</h2>
        <p>The bench is most useful when you write down the expected output before you touch a switch. When the circuit disagrees with your prediction, the highlighted truth-table row tells you exactly which rule you missed.</p>
      </div>
      <div class="cta-actions">
        <a class="btn btn-primary" href="{{{{ROOT}}}}theory/index.html">
          Review the theory
          <svg class="icon" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg>
        </a>
        <a class="btn btn-secondary" href="{{{{ROOT}}}}labs/index.html">
          Run a real lab
          <svg class="icon" aria-hidden="true"><use href="#icon-arrow-up-right"></use></svg>
        </a>
      </div>
    </div>
    <p class="circuit-footnote"><a href="#top">Back to top</a> <span aria-hidden="true">·</span> {total} independent logic definitions, {combinational} combinational and {sequential} sequential. All outputs checked against an independent truth-table generator.</p>
  </div>
</section>
"""


def minimal_client_data() -> list[dict]:
    payload = []
    for item in CIRCUITS:
        payload.append(
            {
                "id": item["id"],
                "title": item["title"],
                "kind": item["kind"],
                "category": item["category"],
                "equation": item["equation"],
                "signals": item["signals"],
            }
        )
    return payload


def client_data_json() -> str:
    return json.dumps(minimal_client_data(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
