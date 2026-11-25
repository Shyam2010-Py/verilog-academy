/* ==========================================================================
   VERILOG ACADEMY — Circuit Lab UI
   Hydrates the server-rendered benches, renders SVG diagrams, loads truth
   tables on demand and keeps search, filters and deep links in sync.
   ========================================================================== */

import { createCircuit } from "./circuit-engine.js";
import { paintDiagram, renderDiagram } from "./circuit-diagrams.js";

const DATA_NODE = document.getElementById("circuit-data");
const DATA = DATA_NODE ? JSON.parse(DATA_NODE.textContent) : [];
const BY_ID = new Map(DATA.map((item) => [item.id, item]));

const benches = new Map();
const truthCache = new Map();
const autoClocks = new Map();
const edgeLogs = new Map();
const tableState = new Map();

const inputOrder = (item) => item.signals.inputs.map((signal) => signal.name);
const outputOrder = (item) => item.signals.outputs.map((signal) => signal.name);
const cardId = (card) => card.dataset.circuit ?? card.dataset.bench;

function busValue(snapshot, prefix, width = 4) {
  let result = 0;
  for (let index = width - 1; index >= 0; index -= 1) {
    const name = `${prefix}${index}`;
    result = (result << 1) | (snapshot.outputs[name] ?? snapshot.inputs[name] ?? 0);
  }
  return result;
}

function bitsOf(value, width = 4) {
  return value.toString(2).padStart(width, "0");
}

function requestBits(snapshot) {
  return [3, 2, 1, 0].map((index) => snapshot.inputs[`R${index}`]).join("");
}

function describe(snapshot) {
  const { id, inputs, outputs } = snapshot;
  const item = BY_ID.get(id);
  if (!item) return "";
  switch (id) {
    case "half-adder":
      return `A = ${inputs.A}, B = ${inputs.B} → S = ${outputs.S}, C = ${outputs.C} (total ${inputs.A + inputs.B})`;
    case "full-adder":
      return `A = ${inputs.A}, B = ${inputs.B}, Cin = ${inputs.Cin} → S = ${outputs.S}, Cout = ${outputs.Cout} (total ${inputs.A + inputs.B + inputs.Cin})`;
    case "half-subtractor":
      return `A = ${inputs.A}, B = ${inputs.B} → D = ${outputs.D}, Bout = ${outputs.Bout} (${inputs.A} − ${inputs.B} = ${inputs.A - inputs.B})`;
    case "full-subtractor":
      return `A = ${inputs.A}, B = ${inputs.B}, Bin = ${inputs.Bin} → D = ${outputs.D}, Bout = ${outputs.Bout} (${inputs.A} − ${inputs.B} − ${inputs.Bin} = ${inputs.A - inputs.B - inputs.Bin})`;
    case "four-bit-adder": {
      const a = busValue(snapshot, "A");
      const b = busValue(snapshot, "B");
      const s = busValue(snapshot, "S");
      return `A = ${a} (${bitsOf(a)}), B = ${b} (${bitsOf(b)}), Cin = ${inputs.Cin} → S = ${s} (${bitsOf(s)}), Cout = ${outputs.Cout}, OVF = ${outputs.OVF}`;
    }
    case "mux-4-to-1": {
      const select = (inputs.S1 << 1) | inputs.S0;
      return `S = ${bitsOf(select, 2)} selects D${select}; Y = ${outputs.Y}`;
    }
    case "demux-1-to-4": {
      const select = (inputs.S1 << 1) | inputs.S0;
      return `Din = ${inputs.Din}, S = ${bitsOf(select, 2)} → Y${select} = ${outputs[`Y${select}`]}; other outputs 0`;
    }
    case "decoder-2-to-4": {
      const address = (inputs.A1 << 1) | inputs.A0;
      if (inputs.EN === 0) return "EN = 0 → all outputs forced low";
      return `EN = 1, A = ${bitsOf(address, 2)} → Y${address} = 1; other outputs 0`;
    }
    case "encoder-4-to-2": {
      const code = (outputs.Code1 << 1) | outputs.Code0;
      if (outputs.Valid === 0) return "No request active → Code = 00, Valid = 0";
      return `Requests ${requestBits(snapshot)} → Code = ${bitsOf(code, 2)} (${code}), Valid = 1`;
    }
    case "comparator-4-bit": {
      const a = busValue(snapshot, "A");
      const b = busValue(snapshot, "B");
      const relation = outputs.GT ? "A > B" : outputs.LT ? "A < B" : "A = B";
      return `A = ${a} (${bitsOf(a)}), B = ${b} (${bitsOf(b)}) → ${relation}; GT = ${outputs.GT}, EQ = ${outputs.EQ}, LT = ${outputs.LT}`;
    }
    case "d-flip-flop": {
      const clock = snapshot.state.clock ?? 0;
      const next = inputs.RST ? "Reset clears Q asynchronously" : inputs.EN ? `Next rising edge loads D = ${inputs.D}` : "Next edge holds Q";
      return `D = ${inputs.D}, EN = ${inputs.EN}, RST = ${inputs.RST}, CLK = ${clock} → Q = ${outputs.Q}, Q̄ = ${outputs.Qbar}. ${next}.`;
    }
    default: {
      const inputText = inputOrder(item)
        .map((name) => `${name} = ${inputs[name]}`)
        .join(", ");
      const outputText = outputOrder(item)
        .map((name) => `${name} = ${outputs[name]}`)
        .join(", ");
      return `${inputText} → ${outputText}`;
    }
  }
}

function updateSwitch(card, name, value) {
  const button = card.querySelector(`[data-input="${CSS.escape(name)}"]`);
  if (!button) return;
  const item = BY_ID.get(cardId(card));
  const signal = item.signals.inputs.find((entry) => entry.name === name);
  const label = signal ? signal.label : name;
  button.setAttribute("aria-checked", String(value === 1));
  button.classList.toggle("is-on", value === 1);
  button.setAttribute("aria-label", `${label} input, currently ${value}. Activate to set ${1 - value}.`);
  const valueNode = button.querySelector("[data-input-value]");
  if (valueNode) valueNode.textContent = String(value);
}

function paint(card, bench) {
  const snapshot = bench.snapshot();
  const id = snapshot.id;

  paintDiagram(card.querySelector("[data-diagram]"), snapshot);

  for (const [name, value] of Object.entries(snapshot.inputs)) updateSwitch(card, name, value);

  card.querySelectorAll("[data-output]").forEach((row) => {
    const name = row.dataset.output;
    const value = snapshot.outputs[name] ?? 0;
    const valueNode = row.querySelector("[data-output-value]");
    const led = row.querySelector("[data-led]");
    if (valueNode) valueNode.textContent = String(value);
    if (led) led.classList.toggle("is-high", value === 1);
  });

  const summary = card.querySelector("[data-bench-summary]");
  if (summary) summary.textContent = describe(snapshot);

  const clockLed = card.querySelector("[data-clock-led]");
  const clockState = card.querySelector("[data-clock-state]");
  if (clockLed) clockLed.classList.toggle("is-high", (snapshot.state.clock ?? 0) === 1);
  if (clockState) clockState.textContent = `CLK = ${snapshot.state.clock ?? 0}`;

  updateActiveRow(card, snapshot);
  renderEdgeLog(card);
  return snapshot;
}

function tableKey(item, snapshot) {
  return inputOrder(item)
    .map((name) => String(snapshot.inputs[name] ?? 0))
    .join("");
}

function updateActiveRow(card, snapshot) {
  const item = BY_ID.get(snapshot.id);
  if (!item || item.kind === "sequential") return;
  const wrapper = card.querySelector("[data-truth-table]");
  if (!wrapper) return;
  const key = tableKey(item, snapshot);
  const rows = wrapper.querySelectorAll("tr[data-key]");
  if (!rows.length) return;
  rows.forEach((row) => {
    row.classList.toggle("is-active", row.dataset.key === key);
  });
  tableState.set(snapshot.id, { key, loaded: true });
}

function renderEdgeLog(card) {
  const log = edgeLogs.get(cardId(card));
  const target = card.querySelector("[data-edge-list]");
  if (!log || !target) return;
  target.innerHTML = log
    .map((entry) => `<li><span>${entry.edge}</span>${entry.text}</li>`)
    .join("");
}

function pushEdge(card, snapshot, text) {
  const id = cardId(card);
  const log = edgeLogs.get(id) ?? [];
  const clock = snapshot.state.clock === 1 ? "↑" : "•";
  log.unshift({ edge: clock, text });
  edgeLogs.set(id, log.slice(0, 5));
  renderEdgeLog(card);
}

function initBench(card) {
  const id = cardId(card);
  const item = BY_ID.get(id);
  if (!item) return;
  const defaults = Object.fromEntries(item.signals.inputs.map((signal) => [signal.name, signal.default ?? 0]));
  const bench = createCircuit(id, defaults);
  benches.set(id, bench);
  edgeLogs.set(id, []);

  const diagram = card.querySelector("[data-diagram]");
  if (diagram) diagram.innerHTML = renderDiagram(id);

  card.querySelectorAll("[data-input]").forEach((button) => {
    button.addEventListener("click", () => {
      const name = button.dataset.input;
      const current = bench.snapshot().inputs[name];
      const next = current === 1 ? 0 : 1;
      bench.setInput(name, next);
      const snapshot = bench.snapshot();
      if (id === "d-flip-flop") {
        if (name === "RST" && next === 1) pushEdge(card, snapshot, "RST asserted → Q cleared immediately (asynchronous)");
        else if (name === "EN" && next === 0) pushEdge(card, snapshot, "EN = 0 → stored Q held");
        else if (name === "D") pushEdge(card, snapshot, next === 1 ? "D changed to 1; Q changes only at a rising edge" : "D changed to 0; Q changes only at a rising edge");
      }
      paint(card, bench);
    });
  });

  const resetButton = card.querySelector("[data-bench-reset]");
  resetButton?.addEventListener("click", () => {
    stopAutoClock(id);
    bench.reset();
    edgeLogs.set(id, []);
    if (id === "d-flip-flop") {
      const snapshot = bench.snapshot();
      pushEdge(card, snapshot, "Bench reset → Q = 0, CLK = 0");
    }
    paint(card, bench);
  });

  const randomButton = card.querySelector("[data-bench-random]");
  randomButton?.addEventListener("click", () => {
    for (const signal of item.signals.inputs) {
      bench.setInput(signal.name, Math.random() < 0.5 ? 0 : 1);
    }
    paint(card, bench);
  });

  const clockPulse = card.querySelector("[data-clock-pulse]");
  clockPulse?.addEventListener("click", () => {
    bench.pulseClock();
    const snapshot = bench.snapshot();
    const loaded = snapshot.inputs.RST === 0 && snapshot.inputs.EN === 1;
    pushEdge(
      card,
      snapshot,
      loaded
        ? `Rising edge: EN = 1, D = ${snapshot.inputs.D} → Q = ${snapshot.outputs.Q}`
        : snapshot.inputs.RST === 1
          ? "Rising edge ignored: RST is still asserted"
          : "Rising edge: EN = 0 → Q held"
    );
    paint(card, bench);
  });

  const autoButton = card.querySelector("[data-clock-auto]");
  autoButton?.addEventListener("click", () => {
    const id = cardId(card);
    if (autoClocks.has(id)) {
      stopAutoClock(id);
      autoButton.setAttribute("aria-pressed", "false");
      autoButton.textContent = "Auto clock";
      return;
    }
    autoButton.setAttribute("aria-pressed", "true");
    autoButton.textContent = "Stop clock";
    const timer = window.setInterval(() => {
      const rising = bench.toggleClock();
      const snapshot = bench.snapshot();
      if (rising) {
        const loaded = snapshot.inputs.RST === 0 && snapshot.inputs.EN === 1;
        pushEdge(
          card,
          snapshot,
          loaded
            ? `Auto rising edge: EN = 1, D = ${snapshot.inputs.D} → Q = ${snapshot.outputs.Q}`
            : snapshot.inputs.RST === 1
              ? "Auto rising edge ignored: RST asserted"
              : "Auto rising edge: EN = 0 → Q held"
        );
      }
      paint(card, bench);
    }, 760);
    autoClocks.set(id, { timer, button: autoButton });
  });

  paint(card, bench);
}

function stopAutoClock(id) {
  const current = autoClocks.get(id);
  if (!current) return;
  window.clearInterval(current.timer);
  current.button.setAttribute("aria-pressed", "false");
  current.button.textContent = "Auto clock";
  autoClocks.delete(id);
}

function renderTruth(card, payload) {
  const wrapper = card.querySelector("[data-truth-table]");
  const count = card.querySelector("[data-truth-count]");
  if (!wrapper) return;
  const table = document.createElement("table");
  table.className = "truth-table";
  const caption = document.createElement("caption");
  caption.textContent = payload.caption;
  table.appendChild(caption);

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  for (const column of payload.columns) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = column.label;
    th.className = `truth-col truth-col--${column.scope}`;
    headRow.appendChild(th);
  }
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (const row of payload.rows) {
    const tr = document.createElement("tr");
    if (row.key) tr.dataset.key = row.key;
    for (let index = 0; index < payload.columns.length; index += 1) {
      const td = document.createElement("td");
      td.textContent = row.values[index];
      const scope = payload.columns[index].scope;
      if (scope === "output") td.className = "truth-cell--output";
      if (scope === "value") td.className = "truth-cell--value";
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);

  wrapper.replaceChildren(table);
  if (count) count.textContent = `${payload.total.toLocaleString()} rows`;
  const bench = benches.get(cardId(card));
  if (bench) updateActiveRow(card, bench.snapshot());
  tableState.set(cardId(card), { loaded: true, total: payload.total });
}

async function loadTruth(card) {
  const id = cardId(card);
  if (truthCache.has(id)) {
    renderTruth(card, truthCache.get(id));
    return truthCache.get(id);
  }
  const details = card.querySelector("[data-notes]");
  if (!details) return null;
  const wrapper = card.querySelector("[data-truth-table]");
  if (wrapper) wrapper.innerHTML = '<p class="truth-loading">Loading truth table…</p>';
  try {
    const response = await fetch(details.dataset.truthSrc, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    truthCache.set(id, payload);
    renderTruth(card, payload);
    return payload;
  } catch (error) {
    if (wrapper) {
      wrapper.innerHTML = '<p class="truth-error">The truth table could not be loaded. Reload the page or serve the site from a local web server.</p>';
    }
    return null;
  }
}

function initNotes(card) {
  const details = card.querySelector("[data-notes]");
  if (!details) return;
  details.addEventListener("toggle", () => {
    if (details.open) loadTruth(card);
  });
}

function initSearch() {
  const input = document.getElementById("circuit-search");
  const cards = Array.from(document.querySelectorAll("[data-circuit]"));
  const chips = Array.from(document.querySelectorAll("[data-filter]"));
  const count = document.querySelector("[data-circuit-count]");
  const empty = document.querySelector("[data-circuit-empty]");
  const clear = document.querySelector("[data-search-clear]");
  const reset = document.querySelector("[data-search-reset]");
  const total = cards.length;
  let category = "#";

  function apply() {
    const query = (input?.value ?? "").trim().toLowerCase();
    let visible = 0;
    for (const card of cards) {
      const matchesCategory = category === "#" || card.dataset.category === category;
      const matchesQuery = !query || card.dataset.search.includes(query);
      const show = matchesCategory && matchesQuery;
      card.hidden = !show;
      if (show) visible += 1;
    }
    if (count) {
      if (query || category !== "#") count.textContent = `Showing ${visible} of ${total} circuits`;
      else count.textContent = `Showing all ${total} circuits`;
    }
    if (empty) empty.hidden = visible !== 0;
    if (clear) clear.hidden = !query;
    for (const chip of chips) {
      const active = chip.dataset.filter === category;
      chip.classList.toggle("is-active", active);
      chip.setAttribute("aria-pressed", String(active));
    }
    return visible;
  }

  input?.addEventListener("input", apply);
  input?.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      input.value = "";
      apply();
      input.focus();
    }
  });

  for (const chip of chips) {
    chip.addEventListener("click", () => {
      category = chip.dataset.filter;
      apply();
    });
  }

  clear?.addEventListener("click", () => {
    if (input) input.value = "";
    apply();
    input?.focus();
  });

  reset?.addEventListener("click", () => {
    if (input) input.value = "";
    category = "#";
    apply();
    input?.focus();
  });

  document.querySelectorAll("[data-filter-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      category = link.dataset.filterLink;
      if (input) input.value = "";
      apply();
      document.getElementById("circuits")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  apply();
}

function initHash() {
  if (!window.location.hash) return;
  const target = document.querySelector(window.location.hash);
  if (!target || !target.matches("[data-circuit]")) return;
  const card = target;
  let parent = card.parentElement;
  while (parent) {
    if (parent.hidden) parent.hidden = false;
    parent = parent.parentElement;
  }
  window.setTimeout(() => card.scrollIntoView({ block: "start" }), 120);
}

function exposeTestApi() {
  window.__circuitLab = {
    ids: DATA.map((item) => item.id),
    setInputs(id, values) {
      const bench = benches.get(id);
      const card = document.querySelector(`[data-circuit="${CSS.escape(id)}"]`);
      if (!bench || !card) throw new Error(`Unknown bench ${id}`);
      bench.setInputs(values);
      return paint(card, bench);
    },
    setInput(id, name, value) {
      return window.__circuitLab.setInputs(id, { [name]: value });
    },
    pulseClock(id) {
      const bench = benches.get(id);
      const card = document.querySelector(`[data-circuit="${CSS.escape(id)}"]`);
      if (!bench || !card) throw new Error(`Unknown bench ${id}`);
      bench.pulseClock();
      return paint(card, bench);
    },
    reset(id) {
      const bench = benches.get(id);
      const card = document.querySelector(`[data-circuit="${CSS.escape(id)}"]`);
      if (!bench || !card) throw new Error(`Unknown bench ${id}`);
      stopAutoClock(id);
      bench.reset();
      edgeLogs.set(id, []);
      return paint(card, bench);
    },
    snapshot(id) {
      return benches.get(id)?.snapshot() ?? null;
    },
    dom(id) {
      const card = document.querySelector(`[data-circuit="${CSS.escape(id)}"]`);
      if (!card) return null;
      const outputs = {};
      card.querySelectorAll("[data-output]").forEach((row) => {
        outputs[row.dataset.output] = Number(row.querySelector("[data-output-value]")?.textContent ?? 0);
      });
      return {
        outputs,
        summary: card.querySelector("[data-bench-summary]")?.textContent ?? "",
        activeRow: card.querySelector("tr.is-active")?.dataset.key ?? null,
        loaded: Boolean(card.querySelector("table.truth-table")),
        hidden: card.hidden,
      };
    },
    loadTruth(id) {
      const card = document.querySelector(`[data-circuit="${CSS.escape(id)}"]`);
      return card ? loadTruth(card) : null;
    },
    tableState(id) {
      return tableState.get(id) ?? { loaded: false };
    },
    stopAutoClock,
  };
}

function init() {
  document.querySelectorAll("[data-bench]").forEach((card) => initBench(card));
  document.querySelectorAll("[data-circuit]").forEach((card) => initNotes(card));
  initSearch();
  initHash();
  exposeTestApi();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}
