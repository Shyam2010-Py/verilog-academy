/* ==========================================================================
   VERILOG ACADEMY - Verilog Playground
   A local editor for verified starter projects. It highlights and edits text,
   stores optional drafts under va.playground.drafts, and downloads design.v
   and tb.v. It never compiles or simulates Verilog in the browser.
   ========================================================================== */

import { toast } from "./ui.js";

const DRAFT_KEY = "va.playground.drafts";
const DRAFT_VERSION = 1;
const TAB_TEXT = "  ";

const KEYWORDS = new Set([
  "always", "and", "assign", "automatic", "begin", "buf", "bufif0", "bufif1",
  "case", "casex", "casez", "cell", "cmos", "config", "deassign", "default",
  "defparam", "design", "disable", "edge", "else", "end", "endcase", "endconfig",
  "endfunction", "endgenerate", "endmodule", "endprimitive", "endspecify",
  "endtable", "endtask", "event", "for", "force", "forever", "fork", "function",
  "generate", "genvar", "if", "ifnone", "include", "initial", "inout", "input",
  "instance", "integer", "join", "large", "macromodule", "medium", "module",
  "nand", "negedge", "nmos", "nor", "not", "notif0", "notif1", "or", "output",
  "parameter", "pmos", "posedge", "primitive", "pull0", "pull1", "pulldown",
  "pullup", "rcmos", "real", "realtime", "reg", "release", "repeat", "rnmos",
  "rpmos", "rtran", "rtranif0", "rtranif1", "scalared", "signed", "small",
  "specify", "specparam", "strong0", "strong1", "supply0", "supply1", "table",
  "task", "time", "tran", "tranif0", "tranif1", "tri", "tri0", "tri1", "triand",
  "trior", "trireg", "unsigned", "vectored", "wait", "wand", "weak0", "weak1",
  "while", "wire", "wor", "xnor", "xor",
]);

const TYPES = new Set([
  "wire", "reg", "integer", "real", "time", "realtime", "input", "output",
  "inout", "parameter", "localparam", "signed", "unsigned", "tri", "tri0",
  "tri1", "triand", "trior", "trireg", "wand", "wor", "supply0", "supply1",
  "genvar", "automatic",
]);

const TOKEN_RE =
  /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*")|(`[A-Za-z_][A-Za-z0-9_]*)|(\$[A-Za-z_][A-Za-z0-9_$]*)|((?:\d[\d_]*)?'[sS]?[bBoOdDhH][0-9a-fA-FxXzZ?_]+|\b\d[\d_]*(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_$]*)|([&|^~!+\-*/%<>=?:]+)/g;

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const dataNode = $("#playground-data");
const workbench = $("[data-workbench]");
const exampleSelect = $("[data-example-select]");
const briefNodes = $$("[data-brief]");

let examples = [];
const byId = new Map();

try {
  const parsed = JSON.parse(dataNode.textContent);
  if (Array.isArray(parsed)) {
    examples = parsed.filter(
      (item) =>
        item &&
        typeof item.id === "string" &&
        typeof item.design === "string" &&
        typeof item.testbench === "string"
    );
  }
} catch (error) {
  console.error("Playground data could not be loaded:", error);
}

examples.forEach((item) => byId.set(item.id, item));

/* Editor wiring ---------------------------------------------------------- */

function createEditor(name) {
  const root = $(`[data-editor="${name}"]`);
  if (!root) return null;
  const textarea = $("[data-textarea]", root);
  const highlight = $("[data-highlight]", root);
  const gutter = $("[data-gutter]", root);
  const pre = highlight?.closest("pre");
  if (!textarea || !highlight || !gutter || !pre) return null;
  return { name, root, textarea, highlight, gutter, pre };
}

const editors = {
  design: createEditor("design"),
  testbench: createEditor("testbench"),
};

const state = {
  current: null,
  draftTimer: 0,
  clearArmed: false,
  clearTimer: 0,
  storageWarned: false,
};

/* Highlighting ----------------------------------------------------------- */

function highlightInto(source, target) {
  const fragment = document.createDocumentFragment();
  let position = 0;
  TOKEN_RE.lastIndex = 0;
  let match = TOKEN_RE.exec(source);

  while (match) {
    if (match.index > position) {
      fragment.appendChild(document.createTextNode(source.slice(position, match.index)));
    }

    const text = match[0];
    let kind = "tok-operator";
    if (match[1]) kind = "tok-comment";
    else if (match[2]) kind = "tok-string";
    else if (match[3]) kind = "tok-directive";
    else if (match[4]) kind = "tok-system";
    else if (match[5]) kind = "tok-number";
    else if (match[6]) {
      if (TYPES.has(text)) kind = "tok-type";
      else if (KEYWORDS.has(text)) kind = "tok-keyword";
      else kind = "";
    }

    if (kind) {
      const span = document.createElement("span");
      span.className = kind;
      span.textContent = text;
      fragment.appendChild(span);
    } else {
      fragment.appendChild(document.createTextNode(text));
    }

    position = match.index + text.length;
    match = TOKEN_RE.exec(source);
  }

  if (position < source.length) {
    fragment.appendChild(document.createTextNode(source.slice(position)));
  }

  /* Keeps the final empty line box so the highlight matches the textarea. */
  fragment.appendChild(document.createTextNode("\u200b"));
  target.replaceChildren(fragment);
}

function renderGutter(editor) {
  const lines = editor.textarea.value.split("\n").length;
  const numbers = [];
  for (let index = 1; index <= lines; index += 1) numbers.push(String(index));
  editor.gutter.textContent = numbers.join("\n");
  editor.gutter.dataset.digits = String(String(lines).length);
}

function syncScroll(editor) {
  const { textarea, pre, gutter } = editor;
  pre.scrollTop = textarea.scrollTop;
  pre.scrollLeft = textarea.scrollLeft;
  gutter.style.transform = `translateY(${-textarea.scrollTop}px)`;
}

function renderEditor(editor) {
  if (!editor) return;
  highlightInto(editor.textarea.value, editor.highlight);
  renderGutter(editor);
  syncScroll(editor);
}

/* Project state ---------------------------------------------------------- */

function activeFile() {
  const selected = $('[data-tab][aria-selected="true"]', workbench);
  return selected?.dataset.tab === "testbench" ? "testbench" : "design";
}

function fileName(file) {
  return file === "testbench" ? "tb.v" : "design.v";
}

function isModified() {
  if (!state.current) return false;
  return (
    editors.design.textarea.value !== state.current.design ||
    editors.testbench.textarea.value !== state.current.testbench
  );
}

function updateStatus() {
  if (!state.current) return;
  const file = activeFile();
  const textarea = editors[file].textarea;
  const lines = textarea.value.split("\n").length;
  const before = textarea.value.slice(0, textarea.selectionStart);
  const line = before.split("\n").length;
  const column = textarea.selectionStart - before.lastIndexOf("\n");
  const status = $("[data-editor-status]");
  if (status) {
    status.textContent = `${fileName(file)} · ${lines} lines · Ln ${line}, Col ${column}`;
  }
}

function updateReference() {
  if (!state.current) return;
  const modified = isModified();
  const brief = briefNodes.find((node) => node.dataset.brief === state.current.id);
  const badge = brief ? $("[data-reference-badge]", brief) : null;
  const note = brief ? $("[data-reference-note]", brief) : null;
  const panel = brief ? $("[data-reference]", brief) : null;
  const projectState = $("[data-project-state]");

  if (badge) {
    badge.textContent = modified ? "Original example only" : "Verified original";
    badge.className = modified ? "badge badge-warning" : "badge badge-success";
  }
  if (panel) panel.classList.toggle("is-edited", modified);
  if (note) {
    note.textContent = modified
      ? "These files have been edited. The transcript below belongs to the original example and was not regenerated. Compile your own design.v and tb.v locally to produce your output."
      : "Produced by compiling and running the original design.v and tb.v with Icarus Verilog 13.0. The output is not regenerated in the browser.";
  }
  if (projectState) {
    projectState.textContent = modified ? "Edited locally" : "Verified original";
    projectState.className = modified ? "badge badge-warning" : "badge badge-success";
  }
}

/* Draft storage ---------------------------------------------------------- */

function readDraftStore() {
  const empty = { version: DRAFT_VERSION, drafts: {} };
  let raw;
  try {
    raw = window.localStorage.getItem(DRAFT_KEY);
  } catch {
    return empty;
  }
  if (!raw) return empty;

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    try {
      window.localStorage.removeItem(DRAFT_KEY);
    } catch {
      /* Ignore a storage context that is already unavailable. */
    }
    return empty;
  }

  if (
    !parsed ||
    typeof parsed !== "object" ||
    parsed.version !== DRAFT_VERSION ||
    !parsed.drafts ||
    typeof parsed.drafts !== "object"
  ) {
    return empty;
  }

  const drafts = {};
  Object.entries(parsed.drafts).forEach(([id, entry]) => {
    if (!byId.has(id) || !entry || typeof entry !== "object") return;
    const design = typeof entry.design === "string" ? entry.design : null;
    const testbench = typeof entry.testbench === "string" ? entry.testbench : null;
    if (design === null && testbench === null) return;
    drafts[id] = {
      design,
      testbench,
      savedAt: typeof entry.savedAt === "string" ? entry.savedAt : "",
    };
  });

  return { version: DRAFT_VERSION, drafts };
}

function writeDraftStore(store) {
  try {
    window.localStorage.setItem(DRAFT_KEY, JSON.stringify(store));
    return true;
  } catch {
    if (!state.storageWarned) {
      state.storageWarned = true;
      toast("Draft storage is unavailable. Your edits are not saved.", { type: "warning" });
    }
    return false;
  }
}

function persistDraft() {
  if (!state.current) return;
  const id = state.current.id;
  const design = editors.design.textarea.value;
  const testbench = editors.testbench.textarea.value;
  const store = readDraftStore();

  if (design === state.current.design && testbench === state.current.testbench) {
    delete store.drafts[id];
  } else {
    store.drafts[id] = { design, testbench, savedAt: new Date().toISOString() };
  }

  writeDraftStore(store);
  updateDraftStatus();
}

function scheduleDraft() {
  window.clearTimeout(state.draftTimer);
  state.draftTimer = window.setTimeout(persistDraft, 500);
}

function flushDraft() {
  window.clearTimeout(state.draftTimer);
  state.draftTimer = 0;
  persistDraft();
}

function updateDraftStatus() {
  if (!state.current) return;
  const label = $("[data-draft-status]");
  if (!label) return;
  const entry = readDraftStore().drafts[state.current.id];
  if (!entry) {
    label.textContent = "No draft saved for this project.";
    label.classList.remove("is-saved");
    return;
  }

  let when = "";
  if (entry.savedAt) {
    const date = new Date(entry.savedAt);
    if (!Number.isNaN(date.getTime())) {
      when = new Intl.DateTimeFormat(undefined, {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    }
  }

  label.textContent = when
    ? `Draft saved in this browser · ${when}`
    : "Draft saved in this browser.";
  label.classList.add("is-saved");
}

/* Project switching ------------------------------------------------------ */

function setProjectText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = value;
}

function selectExample(id, options = {}) {
  const next = byId.get(id);
  if (!next) return;

  if (state.current && state.current.id !== id) flushDraft();

  const store = readDraftStore();
  const draft = store.drafts[id] || null;
  const design = draft && typeof draft.design === "string" ? draft.design : next.design;
  const testbench =
    draft && typeof draft.testbench === "string" ? draft.testbench : next.testbench;

  state.current = next;

  editors.design.textarea.value = design;
  editors.testbench.textarea.value = testbench;

  renderEditor(editors.design);
  renderEditor(editors.testbench);

  if (exampleSelect) exampleSelect.value = id;

  setProjectText("[data-project-title]", next.title);
  setProjectText("[data-project-summary]", next.summary);
  setProjectText("[data-project-category]", next.category);
  setProjectText("[data-meta-category]", next.category);
  setProjectText("[data-meta-level]", next.level);
  setProjectText("[data-meta-checks]", String(next.checks));

  briefNodes.forEach((node) => {
    node.hidden = node.dataset.brief !== id;
  });

  updateReference();
  updateStatus();
  updateDraftStatus();

  if (options.focus) {
    const file = activeFile();
    editors[file].textarea.focus({ preventScroll: true });
  }
}

/* Editing behaviour ------------------------------------------------------ */

function replaceValue(editor, start, end, text) {
  const textarea = editor.textarea;
  textarea.setRangeText(text, start, end, "preserve");
}

function indentSelection(editor, outdent) {
  const textarea = editor.textarea;
  const value = textarea.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;

  if (!outdent && start === end) {
    textarea.setRangeText(TAB_TEXT, start, end, "end");
    return;
  }

  const lineStart = value.lastIndexOf("\n", start - 1) + 1;
  const probe = end > start && value[end - 1] === "\n" ? end - 1 : end;
  let lineEnd = value.indexOf("\n", probe);
  if (lineEnd === -1) lineEnd = value.length;

  const lines = value.slice(lineStart, lineEnd).split("\n");
  let deltaStart = 0;
  let deltaEnd = 0;

  const changed = lines.map((line, index) => {
    if (outdent) {
      const removed = line.startsWith(TAB_TEXT)
        ? TAB_TEXT.length
        : line.startsWith(" ") || line.startsWith("\t")
          ? 1
          : 0;
      if (index === 0) deltaStart = -removed;
      deltaEnd -= removed;
      return line.slice(removed);
    }
    if (index === 0) deltaStart = TAB_TEXT.length;
    deltaEnd += TAB_TEXT.length;
    return TAB_TEXT + line;
  });

  replaceValue(editor, lineStart, lineEnd, changed.join("\n"));
  textarea.selectionStart = Math.max(lineStart, start + deltaStart);
  textarea.selectionEnd = Math.max(textarea.selectionStart, end + deltaEnd);
}

function handleEdit(editor) {
  renderEditor(editor);
  updateStatus();
  updateReference();
  scheduleDraft();
}

Object.values(editors).forEach((editor) => {
  if (!editor) return;
  const { textarea } = editor;

  textarea.addEventListener("input", () => handleEdit(editor));

  textarea.addEventListener("scroll", () => syncScroll(editor), { passive: true });

  textarea.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      indentSelection(editor, event.shiftKey);
      handleEdit(editor);
      return;
    }
    if (event.key === "Escape") {
      textarea.blur();
    }
  });

  ["keyup", "click", "select"].forEach((type) => {
    textarea.addEventListener(type, updateStatus);
  });
});

/* Actions ---------------------------------------------------------------- */

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {}
  }

  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  area.remove();
  return copied;
}

function flashButton(button, label) {
  const span = button.querySelector("span");
  if (!span) return;
  const original = span.textContent;
  span.textContent = label;
  button.classList.add("is-copied");
  window.setTimeout(() => {
    span.textContent = original;
    button.classList.remove("is-copied");
  }, 1600);
}

function download(name, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.rel = "noopener";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1500);
  toast(`${name} downloaded.`, { type: "success" });
}

function resetFile(file) {
  if (!state.current) return;
  const textarea = editors[file].textarea;
  textarea.value = file === "testbench" ? state.current.testbench : state.current.design;
  renderEditor(editors[file]);
  updateStatus();
  updateReference();
  flushDraft();
  toast(`${fileName(file)} restored to the original example.`);
}

function resetBoth() {
  if (!state.current) return;
  editors.design.textarea.value = state.current.design;
  editors.testbench.textarea.value = state.current.testbench;
  renderEditor(editors.design);
  renderEditor(editors.testbench);
  updateStatus();
  updateReference();
  flushDraft();
  toast("Both files restored to the original example.");
}

function clearDrafts(button) {
  if (!state.clearArmed) {
    state.clearArmed = true;
    const span = button.querySelector("span") || button;
    button.dataset.originalLabel = span.textContent;
    span.textContent = "Click again to confirm";
    button.classList.add("is-armed");
    window.clearTimeout(state.clearTimer);
    state.clearTimer = window.setTimeout(() => {
      state.clearArmed = false;
      span.textContent = button.dataset.originalLabel || "Clear saved drafts";
      button.classList.remove("is-armed");
    }, 4000);
    return;
  }

  state.clearArmed = false;
  window.clearTimeout(state.clearTimer);
  const span = button.querySelector("span") || button;
  span.textContent = button.dataset.originalLabel || "Clear saved drafts";
  button.classList.remove("is-armed");

  try {
    window.localStorage.removeItem(DRAFT_KEY);
  } catch {
    /* Storage can be unavailable; the editors stay untouched. */
  }
  updateDraftStatus();
  toast("Stored drafts cleared. The current editor contents are unchanged.");
}

if (workbench) {
  document.addEventListener("click", async (event) => {
    const tab = event.target.closest("[data-tab]");
    if (tab) {
      window.setTimeout(updateStatus, 0);
      return;
    }

    const action = event.target.closest("[data-action]")?.dataset.action;
    if (!action) return;

    if (action === "copy") {
      const button = event.target.closest("[data-action]");
      const file = activeFile();
      const textarea = editors[file].textarea;
      const hasSelection = textarea.selectionStart !== textarea.selectionEnd;
      const text = hasSelection
        ? textarea.value.slice(textarea.selectionStart, textarea.selectionEnd)
        : textarea.value;

      if (await copyText(text)) {
        flashButton(button, "Copied");
        toast(hasSelection ? "Selected code copied." : `${fileName(file)} copied.`, {
          type: "success",
          duration: 1800,
        });
      } else {
        toast("Could not copy. Select the code manually.", { type: "warning" });
      }
      return;
    }

    if (action === "download-design") {
      download("design.v", editors.design.textarea.value);
      return;
    }

    if (action === "download-testbench") {
      download("tb.v", editors.testbench.textarea.value);
      return;
    }

    if (action === "reset-file") {
      resetFile(activeFile());
      return;
    }

    if (action === "reset-all") {
      resetBoth();
      return;
    }

    if (action === "clear-drafts") {
      clearDrafts(event.target.closest("[data-action]"));
    }
  });
}

if (exampleSelect) {
  exampleSelect.addEventListener("change", () => selectExample(exampleSelect.value));
}

$$("[data-select-example]").forEach((card) => {
  card.addEventListener("click", () => {
    const id = card.dataset.selectExample;
    if (id && byId.has(id)) selectExample(id);
  });
});

window.addEventListener("pagehide", () => {
  window.clearTimeout(state.draftTimer);
  persistDraft();
});

/* Initial project -------------------------------------------------------- */

if (examples.length) {
  selectExample(examples[0].id);
}
