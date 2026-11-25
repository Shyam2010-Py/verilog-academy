/* ==========================================================================
   VERILOG ACADEMY — Circuit Lab diagrams
   Inline SVG builders. Every live wire and lamp carries a data attribute so
   the bench can repaint without rebuilding the diagram.
   ========================================================================== */

const esc = (value) =>
  String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

const svg = (title, description, body) => `
  <svg class="bench-svg" viewBox="0 0 520 240" role="img" aria-label="${esc(title)}" focusable="false">
    <title>${esc(title)}</title>
    <desc>${esc(description)}</desc>
    ${body}
  </svg>`;

const wire = (d, signal, extra = "") =>
  `<path class="cl-wire ${extra}" d="${d}" data-sig="${esc(signal)}" vector-effect="non-scaling-stroke"/>`;

const bus = (d, name, extra = "") =>
  `<path class="cl-wire cl-bus ${extra}" d="${d}" data-bus="${esc(name)}" vector-effect="non-scaling-stroke"/>`;

const clockWire = (d, extra = "") =>
  `<path class="cl-wire cl-clock-wire ${extra}" d="${d}" data-clock-wire="1" vector-effect="non-scaling-stroke"/>`;

const label = (x, y, text, cls = "cl-label") => `<text class="${cls}" x="${x}" y="${y}">${esc(text)}</text>`;

const value = (x, y, signal, anchor = "") =>
  `<text class="cl-value" x="${x}" y="${y}"${anchor ? ` text-anchor="${anchor}"` : ""} data-val="${esc(signal)}">0</text>`;

const busValue = (x, y, name) => `<text class="cl-bus-value" x="${x}" y="${y}" data-busval="${esc(name)}">0</text>`;

const busBits = (x, y, name) => `<text class="cl-bus-bits" x="${x}" y="${y}" data-busbits="${esc(name)}">0000</text>`;

const lamp = (x, y, signal, caption, side = "below") => {
  const text = side === "right"
    ? `<text class="cl-lamp-label" x="20" y="4" text-anchor="start">${esc(caption)}</text>`
    : `<text class="cl-lamp-label" x="0" y="38" text-anchor="middle">${esc(caption)}</text>`;
  return `
  <g class="cl-lamp-group" transform="translate(${x} ${y})">
    <circle class="cl-lamp-halo" r="22" aria-hidden="true"></circle>
    <circle class="cl-lamp" r="13" data-lamp="${esc(signal)}" aria-hidden="true"></circle>
    ${text}
  </g>`;
};

const block = (x, y, width, height, title, subtitle = "", extra = "") => `
  <g class="cl-block ${extra}">
    <rect x="${x}" y="${y}" width="${width}" height="${height}" rx="10"></rect>
    <text class="cl-block-title" x="${x + width / 2}" y="${y + height / 2 - (subtitle ? 4 : -5)}" text-anchor="middle">${esc(title)}</text>
    ${subtitle ? `<text class="cl-block-sub" x="${x + width / 2}" y="${y + height / 2 + 17}" text-anchor="middle">${esc(subtitle)}</text>` : ""}
  </g>`;

const pin = (x1, y1, x2, y2, signal, name) =>
  `${wire(`M${x1} ${y1} H${x2}`, signal)}${label(x1, y1 - 9, name)}${value(x2 - 8, y1 - 9, signal, "end")}`;

const gateBody = (kind) => {
  if (kind === "not") {
    return '<path class="cl-gate-body" d="M190 56 L190 164 L286 110 Z"></path>';
  }
  if (kind === "and" || kind === "nand") {
    return '<path class="cl-gate-body" d="M190 56 H244 A54 54 0 0 1 244 164 H190 Z"></path>';
  }
  const arc = '<path class="cl-gate-body" d="M190 56 Q214 110 190 164 Q258 164 296 110 Q258 56 190 56 Z"></path>';
  const xorArc = '<path class="cl-gate-extra" d="M178 56 Q202 110 178 164"></path>';
  return `${arc}${kind === "xor" || kind === "xnor" ? xorArc : ""}`;
};

const gateDiagram = (kind, inputs, title, description) => {
  const output = "Y";
  const bubble = kind === "nand" || kind === "nor" || kind === "xnor" || kind === "not";
  const bodyEnd = bubble ? 298 : 296;
  const wireStart = bubble ? 309 : 296;
  const inputRows = inputs.length === 1 ? [110] : [78, 142];
  const inputSvg = inputs
    .map((signal, index) => {
      const y = inputRows[index];
      return `${wire(`M42 ${y} H190`, signal)}${label(18, y + 5, signal)}${value(154, y + 5, signal)}`;
    })
    .join("");
  const bubbleSvg = bubble
    ? `<circle class="cl-bubble" cx="${bodyEnd + 9}" cy="110" r="9"></circle>`
    : "";
  const gateLabelY = kind === "not" ? 116 : 116;
  return svg(
    title,
    description,
    `
    ${inputSvg}
    ${gateBody(kind)}
    ${bubbleSvg}
    <text class="cl-gate-name" x="228" y="${gateLabelY}" text-anchor="middle">${esc(kind.toUpperCase())}</text>
    ${wire(`M${wireStart} 110 H444`, output)}
    ${value(386, 100, output)}
    ${lamp(462, 110, output, output)}
    `
  );
};

const halfAdder = () => svg(
  "Half adder diagram",
  "Inputs A and B fan out to an XOR gate for the sum and an AND gate for the carry.",
  `
  ${wire("M42 50 H196", "A")}${label(18, 55, "A")}${value(168, 55, "A", "end")}
  ${wire("M42 72 H196", "B")}${label(18, 77, "B")}${value(120, 77, "B", "end")}
  ${wire("M160 50 V166 H196", "A", "cl-branch")}
  ${wire("M110 72 V188 H196", "B", "cl-branch")}
  <circle class="cl-junction" cx="160" cy="50" r="3"></circle>
  <circle class="cl-junction" cx="110" cy="72" r="3"></circle>
  ${block(196, 34, 112, 54, "XOR", "S = A ⊕ B")}
  ${block(196, 150, 112, 54, "AND", "C = A · B")}
  ${wire("M308 61 H430", "S")}${value(362, 51, "S")}${lamp(456, 61, "S", "S")}
  ${wire("M308 177 H430", "C")}${value(362, 167, "C")}${lamp(456, 177, "C", "C")}
  `
);

const fullAdder = () => svg(
  "Full adder diagram",
  "Inputs A, B and Cin enter a full adder block that produces sum S and carry Cout.",
  `
  ${pin(42, 60, 178, 60, "A", "A")}
  ${pin(42, 112, 178, 112, "B", "B")}
  ${pin(42, 164, 178, 164, "Cin", "Cin")}
  ${block(178, 34, 174, 158, "FULL ADDER", "p = A ⊕ B   g = A · B")}
  ${wire("M352 72 H430", "S")}${value(378, 62, "S")}${lamp(462, 72, "S", "S")}
  ${wire("M352 150 H430", "Cout")}${value(372, 140, "Cout")}${lamp(462, 150, "Cout", "Cout")}
  <text class="cl-note" x="260" y="216" text-anchor="middle">S = A ⊕ B ⊕ Cin   Cout = A·B + Cin·(A ⊕ B)</text>
  `
);

const halfSubtractor = () => svg(
  "Half subtractor diagram",
  "Inputs A and B fan out to an XOR gate for the difference and an AND gate with an inverted A for the borrow.",
  `
  ${wire("M42 50 H196", "A")}${label(18, 55, "A")}${value(168, 55, "A", "end")}
  ${wire("M42 72 H196", "B")}${label(18, 77, "B")}${value(120, 77, "B", "end")}
  ${wire("M160 50 V166 H196", "A", "cl-branch")}
  ${wire("M110 72 V188 H196", "B", "cl-branch")}
  <circle class="cl-junction" cx="160" cy="50" r="3"></circle>
  <circle class="cl-junction" cx="110" cy="72" r="3"></circle>
  ${block(196, 34, 112, 54, "XOR", "D = A ⊕ B")}
  ${block(196, 150, 112, 54, "AND", "Bout = ~A · B")}
  ${wire("M308 61 H430", "D")}${value(362, 51, "D")}${lamp(456, 61, "D", "D")}
  ${wire("M308 177 H430", "Bout")}${value(358, 167, "Bout")}${lamp(456, 177, "Bout", "Bout")}
  `
);

const fullSubtractor = () => svg(
  "Full subtractor diagram",
  "Inputs A, B and Bin enter a full subtractor block that produces difference D and borrow Bout.",
  `
  ${pin(42, 60, 178, 60, "A", "A")}
  ${pin(42, 112, 178, 112, "B", "B")}
  ${pin(42, 164, 178, 164, "Bin", "Bin")}
  ${block(178, 34, 174, 158, "FULL SUBTRACTOR", "D = A ⊕ B ⊕ Bin")}
  ${wire("M352 72 H430", "D")}${value(386, 62, "D")}${lamp(462, 72, "D", "D")}
  ${wire("M352 150 H430", "Bout")}${value(372, 140, "Bout")}${lamp(462, 150, "Bout", "Bout")}
  <text class="cl-note" x="260" y="216" text-anchor="middle">Bout = ~A·B + Bin·~(A ⊕ B)</text>
  `
);

const rippleAdder = () => {
  const stages = [0, 1, 2, 3]
    .map((index) => {
      const x = 116 + index * 76;
      return `
      <g class="cl-stage">
        <rect x="${x}" y="92" width="62" height="62" rx="8"></rect>
        <text class="cl-stage-title" x="${x + 31}" y="118" text-anchor="middle">FA${index}</text>
        <text class="cl-stage-sub" x="${x + 31}" y="136" text-anchor="middle">bit ${index}</text>
      </g>`;
    })
    .join("");
  return svg(
    "Four-bit ripple-carry adder diagram",
    "Two four-bit operands and a carry input enter four full adder stages. The sum bus, carry out and overflow flag are shown on the right.",
    `
    ${bus("M38 82 H108", "A")}${label(14, 65, "A[3:0]")}${busValue(14, 78, "A")}${busBits(76, 65, "A")}
    ${bus("M38 166 H108", "B")}${label(14, 149, "B[3:0]")}${busValue(14, 162, "B")}${busBits(76, 149, "B")}
    ${wire("M42 120 H116", "Cin")}${label(14, 113, "Cin")}${value(88, 113, "Cin")}
    ${stages}
    <path class="cl-carry" d="M178 154 H194 M254 154 H270 M330 154 H346" marker-end="url(#cl-arrow)"></path>
    <text class="cl-note" x="262" y="184" text-anchor="middle">carry ripples left to right</text>
    ${bus("M406 123 H470", "S")}
    ${busValue(432, 112, "S")}${busBits(432, 142, "S")}
    ${lamp(492, 72, "Cout", "Cout")}
    ${lamp(492, 176, "OVF", "OVF")}
    <text class="cl-note" x="262" y="220" text-anchor="middle">S = (A + B + Cin) mod 16</text>
    <defs>
      <marker id="cl-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="currentColor"></path>
      </marker>
    </defs>
    `
  );
};

const mux = () => svg(
  "Four-to-one multiplexer diagram",
  "Four data inputs enter a trapezoid. The two-bit select code chooses one input for output Y.",
  `
  ${[0, 1, 2, 3]
    .map((index) => {
      const y = 54 + index * 42;
      return `${wire(`M48 ${y} H190`, `D${index}`, "cl-select-wire")}${label(16, y + 5, `D${index}`)}${value(152, y + 5, `D${index}`)}`;
    })
    .join("")}
  <path class="cl-mux-body" d="M190 34 L336 78 L336 158 L190 202 Z"></path>
  <text class="cl-block-title" x="258" y="112" text-anchor="middle">4:1 MUX</text>
  <text class="cl-block-sub" x="258" y="132" text-anchor="middle">Y = D[S]</text>
  ${wire("M248 202 V222", "S1")}${label(226, 236, "S1")}${value(268, 236, "S1")}
  ${wire("M290 202 V222", "S0")}${label(302, 236, "S0")}${value(334, 236, "S0")}
  ${wire("M336 118 H438", "Y")}${value(376, 108, "Y")}${lamp(464, 118, "Y", "Y")}
  `
);

const demux = () => svg(
  "One-to-four demultiplexer diagram",
  "Input Din is routed to one of four outputs selected by S1 and S0. The unselected outputs stay low.",
  `
  ${pin(42, 112, 176, 112, "Din", "Din")}
  ${block(176, 44, 158, 136, "1:4 DEMUX", "Y[i] = Din · (S = i)")}
  ${wire("M244 180 V218", "S1")}${label(220, 234, "S1")}${value(266, 234, "S1")}
  ${wire("M292 180 V218", "S0")}${label(308, 234, "S0")}${value(342, 234, "S0")}
  ${wire("M334 70 H424", "Y0")}${value(366, 60, "Y0")}${lamp(452, 70, "Y0", "Y0", "right")}
  ${wire("M334 110 H424", "Y1")}${value(366, 100, "Y1")}${lamp(452, 110, "Y1", "Y1", "right")}
  ${wire("M334 150 H424", "Y2")}${value(366, 140, "Y2")}${lamp(452, 150, "Y2", "Y2", "right")}
  ${wire("M334 190 H424", "Y3")}${value(366, 180, "Y3")}${lamp(452, 190, "Y3", "Y3", "right")}
  `
);

const decoder = () => svg(
  "Two-to-four decoder diagram",
  "Enable EN and address bits A1 and A0 select one of four one-hot outputs.",
  `
  ${pin(42, 72, 176, 72, "EN", "EN")}
  ${pin(42, 122, 176, 122, "A1", "A1")}
  ${pin(42, 172, 176, 172, "A0", "A0")}
  ${block(176, 44, 158, 156, "2:4 DECODER", "Y[i] = EN · (A = i)")}
  ${wire("M334 70 H424", "Y0")}${value(366, 60, "Y0")}${lamp(452, 70, "Y0", "Y0", "right")}
  ${wire("M334 110 H424", "Y1")}${value(366, 100, "Y1")}${lamp(452, 110, "Y1", "Y1", "right")}
  ${wire("M334 150 H424", "Y2")}${value(366, 140, "Y2")}${lamp(452, 150, "Y2", "Y2", "right")}
  ${wire("M334 190 H424", "Y3")}${value(366, 180, "Y3")}${lamp(452, 190, "Y3", "Y3", "right")}
  `
);

const encoder = () => svg(
  "Four-to-two priority encoder diagram",
  "Four request lines enter a priority encoder. The code reports the highest active request and Valid flags any request.",
  `
  ${[0, 1, 2, 3]
    .map((index) => {
      const y = 52 + index * 38;
      return `${wire(`M42 ${y} H176`, `R${index}`)}${label(16, y + 5, `R${index}`)}${value(140, y + 5, `R${index}`)}`;
    })
    .join("")}
  ${block(176, 28, 158, 184, "4:2 PRIORITY", "R3 has highest priority")}
  ${wire("M334 76 H424", "Code1")}${value(360, 66, "Code1")}${lamp(452, 76, "Code1", "Code1", "right")}
  ${wire("M334 122 H424", "Code0")}${value(360, 112, "Code0")}${lamp(452, 122, "Code0", "Code0", "right")}
  ${wire("M334 178 H424", "Valid")}${value(364, 168, "Valid")}${lamp(452, 178, "Valid", "Valid", "right")}
  `
);

const comparator = () => svg(
  "Four-bit magnitude comparator diagram",
  "Two four-bit unsigned operands enter a comparator that asserts exactly one of GT, EQ or LT.",
  `
  ${bus("M38 82 H160", "A")}${label(14, 65, "A[3:0]")}${busValue(14, 78, "A")}${busBits(76, 65, "A")}
  ${bus("M38 166 H160", "B")}${label(14, 149, "B[3:0]")}${busValue(14, 162, "B")}${busBits(76, 149, "B")}
  ${block(160, 38, 158, 174, "4-BIT COMPARATOR", "unsigned magnitude")}
  ${wire("M318 66 H428", "GT")}${value(368, 56, "GT")}${lamp(456, 66, "GT", "GT", "right")}
  ${wire("M318 122 H428", "EQ")}${value(368, 112, "EQ")}${lamp(456, 122, "EQ", "EQ", "right")}
  ${wire("M318 178 H428", "LT")}${value(368, 168, "LT")}${lamp(456, 178, "LT", "LT", "right")}
  `
);

const dFlipFlop = () => svg(
  "D flip-flop diagram",
  "Data D and enable EN enter a positive-edge-triggered D flip-flop with asynchronous reset RST and complementary outputs Q and Qbar.",
  `
  ${pin(42, 72, 190, 72, "D", "D")}
  ${pin(42, 126, 190, 126, "EN", "EN")}
  ${pin(42, 180, 190, 180, "RST", "RST")}
  ${block(190, 34, 154, 178, "D FLIP-FLOP", "positive edge")}
  ${clockWire("M212 212 V232 H260")}${label(160, 246, "CLK")}
  <path class="cl-clock-triangle" d="M248 226 L264 214 L264 238 Z"></path>
  ${wire("M344 82 H428", "Q")}${value(376, 72, "Q")}${lamp(456, 82, "Q", "Q")}
  ${wire("M344 158 H428", "Qbar")}${value(368, 148, "Qbar")}${lamp(456, 158, "Qbar", "Q̄")}
  `
);

const BUILDERS = {
  "and-gate": () => gateDiagram("and", ["A", "B"], "AND gate", "A and B feed an AND gate. Output Y is high only when both inputs are high."),
  "or-gate": () => gateDiagram("or", ["A", "B"], "OR gate", "A and B feed an OR gate. Output Y is high when either input is high."),
  "not-gate": () => gateDiagram("not", ["A"], "NOT gate", "Input A passes through an inverter. Output Y is the complement of A."),
  "nand-gate": () => gateDiagram("nand", ["A", "B"], "NAND gate", "A and B feed an AND gate with an output bubble. Output Y is the complement of A AND B."),
  "nor-gate": () => gateDiagram("nor", ["A", "B"], "NOR gate", "A and B feed an OR gate with an output bubble. Output Y is the complement of A OR B."),
  "xor-gate": () => gateDiagram("xor", ["A", "B"], "XOR gate", "A and B feed an exclusive-OR gate. Output Y is high when the inputs differ."),
  "xnor-gate": () => gateDiagram("xnor", ["A", "B"], "XNOR gate", "A and B feed an exclusive-NOR gate. Output Y is high when the inputs match."),
  "half-adder": halfAdder,
  "full-adder": fullAdder,
  "half-subtractor": halfSubtractor,
  "full-subtractor": fullSubtractor,
  "four-bit-adder": rippleAdder,
  "mux-4-to-1": mux,
  "demux-1-to-4": demux,
  "decoder-2-to-4": decoder,
  "encoder-4-to-2": encoder,
  "comparator-4-bit": comparator,
  "d-flip-flop": dFlipFlop,
};

export function renderDiagram(circuitId) {
  const builder = BUILDERS[circuitId];
  if (!builder) throw new Error(`No diagram for ${circuitId}`);
  return builder();
}

const numberFrom = (snapshot, prefix, width) => {
  let result = 0;
  for (let index = width - 1; index >= 0; index -= 1) {
    result = (result << 1) | (snapshot.outputs[`${prefix}${index}`] ?? snapshot.inputs[`${prefix}${index}`] ?? 0);
  }
  return result;
};

const readSignal = (snapshot, name) => {
  if (name in snapshot.inputs) return snapshot.inputs[name];
  if (name in snapshot.outputs) return snapshot.outputs[name];
  if (name === "clock") return snapshot.state.clock ?? 0;
  return 0;
};

export function paintDiagram(root, snapshot) {
  if (!root) return;

  root.querySelectorAll("[data-sig]").forEach((node) => {
    const name = node.dataset.sig;
    node.classList.toggle("is-high", readSignal(snapshot, name) === 1);
  });

  root.querySelectorAll("[data-lamp]").forEach((node) => {
    const name = node.dataset.lamp;
    node.classList.toggle("is-high", readSignal(snapshot, name) === 1);
  });

  root.querySelectorAll("[data-val]").forEach((node) => {
    node.textContent = String(readSignal(snapshot, node.dataset.val));
  });

  root.querySelectorAll("[data-bus]").forEach((node) => {
    const name = node.dataset.bus;
    const value = numberFrom(snapshot, name, 4);
    node.classList.toggle("is-high", value > 0);
  });

  root.querySelectorAll("[data-busval]").forEach((node) => {
    node.textContent = String(numberFrom(snapshot, node.dataset.busval, 4));
  });

  root.querySelectorAll("[data-busbits]").forEach((node) => {
    const name = node.dataset.busbits;
    const value = numberFrom(snapshot, name, 4);
    node.textContent = value.toString(2).padStart(4, "0");
  });

  if (snapshot.id === "mux-4-to-1") {
    const select = (snapshot.inputs.S1 << 1) | snapshot.inputs.S0;
    root.querySelectorAll("[data-sig^='D']").forEach((node) => {
      node.classList.toggle("is-selected", Number(node.dataset.sig.slice(1)) === select);
    });
  }

  root.querySelectorAll("[data-clock-wire]").forEach((node) => {
    node.classList.toggle("is-high", (snapshot.state.clock ?? 0) === 1);
  });
}
