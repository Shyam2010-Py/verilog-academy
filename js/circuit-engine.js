/* ==========================================================================
   VERILOG ACADEMY — Circuit Lab engine
   A small, reusable functional model of combinational and clocked logic.
   No DOM, no dependencies, no Verilog parser. Every circuit is built from the
   same gate primitives so the implementation is independent of the Python
   truth-table oracle used by the build and verification tools.
   ========================================================================== */

export const ENGINE_VERSION = 1;

export const AND = (...values) => (values.every((value) => value === 1) ? 1 : 0);
export const OR = (...values) => (values.some((value) => value === 1) ? 1 : 0);
export const NOT = (value) => (value === 1 ? 0 : 1);
export const NAND = (...values) => NOT(AND(...values));
export const NOR = (...values) => NOT(OR(...values));
export const XOR = (...values) => values.reduce((result, value) => result ^ (value === 1 ? 1 : 0), 0);
export const XNOR = (...values) => NOT(XOR(...values));

const fullAdderGate = (a, b, cin) => {
  const propagate = XOR(a, b);
  return {
    s: XOR(propagate, cin),
    cout: OR(AND(a, b), AND(propagate, cin)),
  };
};

const bit = (inputs, prefix, index) => inputs[`${prefix}${index}`] ?? 0;

const bitBus = (inputs, prefix, width) => {
  const values = [];
  for (let index = width - 1; index >= 0; index -= 1) values.push(bit(inputs, prefix, index));
  return values;
};

const rippleCarry = (inputs) => {
  const a = bitBus(inputs, "A", 4);
  const b = bitBus(inputs, "B", 4);
  let carry = inputs.Cin ?? 0;
  const sum = [];
  for (let index = 3; index >= 0; index -= 1) {
    const stage = fullAdderGate(a[index], b[index], carry);
    sum[index] = stage.s;
    carry = stage.cout;
  }
  const a3 = a[0];
  const b3 = b[0];
  const s3 = sum[0];
  const ovf = AND(XNOR(a3, b3), XOR(s3, a3));
  return { sum, cout: carry, ovf };
};

const compare = (inputs) => {
  const a = bitBus(inputs, "A", 4);
  const b = bitBus(inputs, "B", 4);
  const eq = a.map((value, index) => XNOR(value, b[index]));
  const gt = OR(
    AND(a[0], NOT(b[0])),
    AND(eq[0], a[1], NOT(b[1])),
    AND(eq[0], eq[1], a[2], NOT(b[2])),
    AND(eq[0], eq[1], eq[2], a[3], NOT(b[3]))
  );
  const equal = AND(...eq);
  const lt = AND(NOT(gt), NOT(equal));
  return { GT: gt, EQ: equal, LT: lt };
};

const DEFINITIONS = {
  "and-gate": {
    evaluate: (inputs) => ({ Y: AND(inputs.A, inputs.B) }),
  },
  "or-gate": {
    evaluate: (inputs) => ({ Y: OR(inputs.A, inputs.B) }),
  },
  "not-gate": {
    evaluate: (inputs) => ({ Y: NOT(inputs.A) }),
  },
  "nand-gate": {
    evaluate: (inputs) => ({ Y: NAND(inputs.A, inputs.B) }),
  },
  "nor-gate": {
    evaluate: (inputs) => ({ Y: NOR(inputs.A, inputs.B) }),
  },
  "xor-gate": {
    evaluate: (inputs) => ({ Y: XOR(inputs.A, inputs.B) }),
  },
  "xnor-gate": {
    evaluate: (inputs) => ({ Y: XNOR(inputs.A, inputs.B) }),
  },
  "half-adder": {
    evaluate: (inputs) => ({
      S: XOR(inputs.A, inputs.B),
      C: AND(inputs.A, inputs.B),
    }),
  },
  "full-adder": {
    evaluate: (inputs) => {
      const stage = fullAdderGate(inputs.A, inputs.B, inputs.Cin);
      return { S: stage.s, Cout: stage.cout };
    },
  },
  "half-subtractor": {
    evaluate: (inputs) => ({
      D: XOR(inputs.A, inputs.B),
      Bout: AND(NOT(inputs.A), inputs.B),
    }),
  },
  "full-subtractor": {
    evaluate: (inputs) => {
      const difference = XOR(inputs.A, inputs.B, inputs.Bin);
      const borrow = OR(
        AND(NOT(inputs.A), inputs.B),
        AND(inputs.Bin, XNOR(inputs.A, inputs.B))
      );
      return { D: difference, Bout: borrow };
    },
  },
  "four-bit-adder": {
    evaluate: (inputs) => {
      const result = rippleCarry(inputs);
      return {
        S3: result.sum[0],
        S2: result.sum[1],
        S1: result.sum[2],
        S0: result.sum[3],
        Cout: result.cout,
        OVF: result.ovf,
      };
    },
  },
  "mux-4-to-1": {
    evaluate: (inputs) => {
      const y = OR(
        AND(inputs.D0, NOT(inputs.S1), NOT(inputs.S0)),
        AND(inputs.D1, NOT(inputs.S1), inputs.S0),
        AND(inputs.D2, inputs.S1, NOT(inputs.S0)),
        AND(inputs.D3, inputs.S1, inputs.S0)
      );
      return { Y: y };
    },
  },
  "demux-1-to-4": {
    evaluate: (inputs) => ({
      Y3: AND(inputs.Din, inputs.S1, inputs.S0),
      Y2: AND(inputs.Din, inputs.S1, NOT(inputs.S0)),
      Y1: AND(inputs.Din, NOT(inputs.S1), inputs.S0),
      Y0: AND(inputs.Din, NOT(inputs.S1), NOT(inputs.S0)),
    }),
  },
  "decoder-2-to-4": {
    evaluate: (inputs) => ({
      Y3: AND(inputs.EN, inputs.A1, inputs.A0),
      Y2: AND(inputs.EN, inputs.A1, NOT(inputs.A0)),
      Y1: AND(inputs.EN, NOT(inputs.A1), inputs.A0),
      Y0: AND(inputs.EN, NOT(inputs.A1), NOT(inputs.A0)),
    }),
  },
  "encoder-4-to-2": {
    evaluate: (inputs) => ({
      Code1: OR(inputs.R3, inputs.R2),
      Code0: OR(inputs.R3, AND(NOT(inputs.R2), inputs.R1)),
      Valid: OR(inputs.R3, inputs.R2, inputs.R1, inputs.R0),
    }),
  },
  "comparator-4-bit": {
    evaluate: (inputs) => compare(inputs),
  },
  "d-flip-flop": {
    sequential: true,
    initialState: () => ({ q: 0, clock: 0 }),
    afterInput: (inputs, state) => {
      /* RST is asynchronous: it clears the state without a clock edge. */
      if (inputs.RST === 1) state.q = 0;
    },
    evaluate: (inputs, state) => ({
      Q: state.q,
      Qbar: NOT(state.q),
    }),
    edge: (inputs, state) => {
      /* Called only for a 0 -> 1 clock transition. */
      if (inputs.RST === 0 && inputs.EN === 1) state.q = inputs.D === 1 ? 1 : 0;
    },
  },
};

export const CIRCUIT_IDS = Object.freeze(Object.keys(DEFINITIONS));

export function getDefinition(circuitId) {
  const definition = DEFINITIONS[circuitId];
  if (!definition) throw new Error(`Unknown circuit: ${circuitId}`);
  return definition;
}

export function isSequential(circuitId) {
  return getDefinition(circuitId).sequential === true;
}

/** Evaluate a combinational circuit. `inputs` must contain every input. */
export function evaluate(circuitId, inputs) {
  const definition = getDefinition(circuitId);
  if (definition.sequential) {
    throw new Error(`${circuitId} is sequential; use createCircuit().`);
  }
  return definition.evaluate(inputs, {});
}

/**
 * Create a stateful bench for any circuit.
 * Combinational circuits still expose the same API so the UI stays uniform.
 */
export function createCircuit(circuitId, signalDefaults = {}) {
  const definition = getDefinition(circuitId);
  const defaults = { ...signalDefaults };
  const inputs = {};

  for (const [name, value] of Object.entries(defaults)) {
    inputs[name] = value === 1 ? 1 : 0;
  }

  let state = definition.initialState ? definition.initialState() : {};

  const applyInputs = () => {
    if (definition.afterInput) definition.afterInput(inputs, state);
  };

  applyInputs();

  const setInput = (name, value) => {
    if (!(name in inputs)) throw new Error(`Unknown input "${name}" for ${circuitId}`);
    inputs[name] = value === 1 ? 1 : 0;
    applyInputs();
  };

  const setInputs = (values) => {
    for (const [name, value] of Object.entries(values)) setInput(name, value);
  };

  const snapshot = () => ({
    id: circuitId,
    kind: definition.sequential ? "sequential" : "combinational",
    inputs: { ...inputs },
    state: { ...state },
    outputs: definition.evaluate(inputs, state),
  });

  const reset = () => {
    for (const [name, value] of Object.entries(defaults)) inputs[name] = value === 1 ? 1 : 0;
    state = definition.initialState ? definition.initialState() : {};
    applyInputs();
  };

  const pulseClock = () => {
    if (!definition.sequential) return false;
    state.clock = 0;
    state.clock = 1;
    if (definition.edge) definition.edge(inputs, state);
    return true;
  };

  const toggleClock = () => {
    if (!definition.sequential) return false;
    const next = state.clock === 1 ? 0 : 1;
    state.clock = next;
    if (next === 1 && definition.edge) definition.edge(inputs, state);
    return next === 1;
  };

  return {
    id: circuitId,
    setInput,
    setInputs,
    reset,
    pulseClock,
    toggleClock,
    snapshot,
    isSequential: () => definition.sequential === true,
  };
}
