/* ==========================================================================
   VERILOG ACADEMY — Dashboard
   Reads the local progress model, renders real completion data and wires the
   tracker, continue-learning, backup, import and reset interactions.
   ========================================================================== */

import {
  STORAGE_KEY,
  buildCatalog,
  createEmptyProgress,
  exportProgress,
  getNextItem,
  getRecentActivity,
  isComplete,
  markComplete,
  markIncomplete,
  parseBackup,
  readProgress,
  resetProgress,
  summarize,
  writeProgress,
} from "./progress.js";
import { toast } from "./ui.js";

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  day: "2-digit",
  month: "short",
  year: "numeric",
});
const timeFormatter = new Intl.DateTimeFormat(undefined, {
  hour: "2-digit",
  minute: "2-digit",
});

const state = {
  catalog: null,
  progress: createEmptyProgress(),
  status: "empty",
  warnings: [],
  error: null,
  storageOk: true,
  pendingImport: null,
  next: { theory: null, practical: null },
  allowed: { theory: new Set(), practical: new Set() },
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function pad(value) {
  return String(value).padStart(2, "0");
}

function findItem(kind, id) {
  if (!state.catalog) return null;
  const list = kind === "practical" ? state.catalog.practicalItems : state.catalog.theoryItems;
  return list.find((item) => item.id === id) || null;
}

function itemRowId(item) {
  return item.kind === "theory" ? `topic-${item.id}` : `lab-${item.id}`;
}

function itemMeta(item) {
  if (item.kind === "theory") {
    return `EC-405 · Unit ${item.unitNumber} · Topic ${pad(item.number)}`;
  }
  return `EC-410 · Experiment ${pad(item.number)}`;
}

function formatStamp(iso) {
  if (!iso) return "Date not recorded";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "Date not recorded";

  const dayStart = (value) =>
    new Date(value.getFullYear(), value.getMonth(), value.getDate()).getTime();
  const difference = Math.round((dayStart(new Date()) - dayStart(date)) / 86_400_000);

  if (difference === 0) return `Today · ${timeFormatter.format(date)}`;
  if (difference === 1) return `Yesterday · ${timeFormatter.format(date)}`;
  return dateFormatter.format(date);
}

function setBadge(node, label, variant) {
  if (!node) return;
  node.textContent = label;
  node.classList.remove("badge-cyan", "badge-violet", "badge-success", "badge-warning");
  if (variant) node.classList.add(`badge-${variant}`);
}

function setProgress(bar, fill, percent) {
  if (bar) bar.setAttribute("aria-valuenow", String(percent));
  if (fill) fill.style.setProperty("--progress", `${percent}%`);
}

function announce(message) {
  const live = $("[data-live]");
  if (!live) return;
  live.textContent = "";
  window.setTimeout(() => {
    live.textContent = message;
  }, 30);
}

function interactive() {
  return state.storageOk && state.status !== "invalid";
}

function renderOverall(summary) {
  const { overall, theory, practical } = summary;

  const ring = $("[data-overall-ring]");
  if (ring) {
    ring.style.setProperty("--ring-progress", String(overall.percent / 100));
    ring.style.setProperty(
      "--ring-stroke",
      overall.percent === 100 ? "var(--success)" : "var(--cyan)"
    );
    ring.setAttribute(
      "aria-label",
      `Overall progress: ${overall.percent} percent, ${overall.completed} of ${overall.total} available items complete`
    );
  }

  const percentNode = $("[data-overall-percent]");
  if (percentNode) percentNode.textContent = `${overall.percent}%`;

  const countNode = $("[data-overall-count]");
  if (countNode) countNode.textContent = String(overall.completed);

  const theoryCount = $("[data-theory-count]");
  if (theoryCount) theoryCount.textContent = String(theory.completed);
  const theoryPercent = $("[data-theory-percent]");
  if (theoryPercent) theoryPercent.textContent = `${theory.percent}%`;

  const practicalCount = $("[data-practical-count]");
  if (practicalCount) practicalCount.textContent = String(practical.completed);
  const practicalPercent = $("[data-practical-percent]");
  if (practicalPercent) practicalPercent.textContent = `${practical.percent}%`;

  setProgress($("[data-overall-bar]"), $("[data-overall-fill]"), overall.percent);

  const badge = $("[data-overall-badge]");
  if (overall.percent === 100) setBadge(badge, "Complete", "success");
  else if (overall.completed === 0) setBadge(badge, "Not started");
  else setBadge(badge, "In progress", "cyan");

  const lastActivity = $("[data-last-activity]");
  if (lastActivity) {
    const recent = getRecentActivity(state.progress, state.catalog, 1)[0];
    lastActivity.textContent = recent
      ? `Last completed ${formatStamp(recent.completedAt)}`
      : "No activity yet";
  }
}

function renderUnits(summary) {
  summary.units.forEach((unit) => {
    const count = $(`[data-unit-count="${unit.id}"]`);
    if (count) count.textContent = `${unit.completed} / ${unit.total}`;

    setProgress(
      $(`[data-unit-bar="${unit.id}"]`),
      $(`[data-unit-fill="${unit.id}"]`),
      unit.percent
    );

    const block = $(`[data-unit-block="${unit.id}"]`);
    if (block) block.classList.toggle("is-complete", unit.total > 0 && unit.completed === unit.total);
  });
}

function renderCheckboxes() {
  const enabled = interactive();
  $$(".check-input").forEach((input) => {
    input.checked = isComplete(state.progress, input.dataset.kind, input.dataset.id);
    input.disabled = !enabled;
  });
}

function renderContinue(summary) {
  ["theory", "practical"].forEach((kind) => {
    const item = getNextItem(state.progress, state.catalog, kind);
    state.next[kind] = item;

    const badge = $(`[data-continue-badge="${kind}"]`);
    const meta = $(`[data-continue-meta="${kind}"]`);
    const title = $(`[data-continue-title="${kind}"]`);
    const note = $(`[data-continue-note="${kind}"]`);
    const button = $(`[data-mark-next="${kind}"]`);
    const label = $(`[data-mark-next-label="${kind}"]`);
    const track = summary[kind];
    const noun = kind === "theory" ? "topic" : "experiment";

    if (item) {
      if (meta) {
        meta.textContent =
          kind === "theory"
            ? `Unit ${item.unitNumber} · Topic ${pad(item.number)}`
            : `Experiment ${pad(item.number)}`;
      }
      if (title) title.textContent = item.title;
      if (note) {
        note.textContent =
          track.completed > 0
            ? `Next unfinished ${noun} in curriculum order.`
            : `No ${noun}s completed yet. Begin with the first available ${noun}.`;
      }
      setBadge(badge, track.completed > 0 ? "Up next" : "Start here", kind === "theory" ? "cyan" : "violet");

      if (button) {
        button.disabled = !interactive();
        button.dataset.kind = kind;
        button.dataset.id = item.id;
        button.setAttribute("aria-label", `Mark complete: ${item.title}`);
      }
      if (label) label.textContent = "Mark complete";
    } else {
      if (meta) meta.textContent = "Track complete";
      if (title) title.textContent = "Every available item is complete.";
      if (note) note.textContent = "Nothing left to mark in this track. Review the tracker or export a backup.";
      setBadge(badge, "Complete", "success");

      if (button) {
        button.disabled = true;
        delete button.dataset.id;
        button.setAttribute("aria-label", "All complete");
      }
      if (label) label.textContent = "All complete";
    }
  });
}

function renderActivity(summary) {
  const list = $("[data-activity-list]");
  const count = $("[data-activity-count]");
  if (count) {
    count.textContent = String(summary.overall.completed);
    count.setAttribute(
      "aria-label",
      `${summary.overall.completed} completed ${summary.overall.completed === 1 ? "item" : "items"}`
    );
  }
  if (!list) return;

  const recent = getRecentActivity(state.progress, state.catalog, 5);
  list.replaceChildren();

  if (!recent.length) {
    const item = document.createElement("li");
    item.className = "activity-empty";
    item.innerHTML =
      '<span class="activity-empty__icon"><svg class="icon" aria-hidden="true"><use href="#icon-waveform"></use></svg></span>' +
      "<p>No activity yet.</p>" +
      "<span>Complete your first topic or experiment and it will appear here.</span>";
    list.appendChild(item);
    return;
  }

  recent.forEach((entry) => {
    const item = document.createElement("li");
    item.className = "activity-item";

    const dot = document.createElement("span");
    dot.className = `activity-dot activity-dot--${entry.kind}`;
    dot.setAttribute("aria-hidden", "true");

    const body = document.createElement("div");
    body.className = "activity-body";

    const link = document.createElement("a");
    link.className = "activity-title";
    link.href = `#${itemRowId(entry)}`;
    link.textContent = entry.title;

    const meta = document.createElement("span");
    meta.className = "activity-meta";
    meta.textContent = itemMeta(entry);

    const time = document.createElement("time");
    time.className = "activity-time";
    if (entry.completedAt) time.dateTime = entry.completedAt;
    time.textContent = formatStamp(entry.completedAt);

    body.append(link, meta, time);
    item.append(dot, body);
    list.appendChild(item);
  });
}

function renderDataState(summary) {
  const exportButton = $("[data-export]");
  const importButton = $("[data-import]");
  const resetButton = $("[data-reset-open]");
  const canWrite = state.storageOk;
  const canExport = state.storageOk && state.status !== "invalid";
  const hasRecords = summary.overall.completed > 0;
  const canReset = canWrite && (hasRecords || state.status === "invalid");

  if (exportButton) {
    exportButton.disabled = !canExport;
    exportButton.title = canExport
      ? "Download a JSON backup of your progress"
      : "Resolve the saved-data warning before exporting";
  }
  if (importButton) {
    importButton.disabled = !canWrite;
    importButton.title = canWrite
      ? "Import a validated JSON progress backup"
      : "Browser storage is unavailable";
  }
  if (resetButton) {
    resetButton.disabled = !canReset;
    resetButton.title = canReset ? "Remove every saved completion record" : "No progress to reset";
  }
}

function renderStorageNotice() {
  const alert = $("[data-storage-alert]");
  const message = $("[data-storage-message]");
  if (!alert || !message) return;

  let text = "";
  let variant = "info";

  if (state.status === "unavailable") {
    text = state.error || "Browser storage is unavailable. Progress cannot be saved in this context.";
    variant = "error";
  } else if (state.status === "invalid") {
    text = `${state.error} Import a valid backup or reset the stored record to recover.`;
    variant = "error";
  } else if (state.status === "migrated") {
    text =
      "Progress was saved in an older format. It was read without changes and will be upgraded the next time you mark an item.";
    variant = "info";
  } else if (state.warnings.length) {
    text = state.warnings.join(" ");
    variant = "warning";
  }

  if (!text) {
    alert.hidden = true;
    return;
  }

  alert.hidden = false;
  message.textContent = text;
  alert.setAttribute("role", variant === "error" ? "alert" : "status");
  alert.classList.toggle("dash-alert--error", variant === "error");
  alert.classList.toggle("dash-alert--info", variant === "info");
}

function renderGreeting(summary) {
  const lead = $("[data-welcome-lead]");
  const copy = $("[data-welcome-copy]");
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  if (lead) lead.textContent = `${greeting} — welcome to your`;

  if (!copy) return;
  if (summary.overall.completed === 0) {
    copy.textContent =
      "No account, no cloud sync. Nothing is marked complete yet — open the tracker below and mark the first item you finish.";
  } else if (summary.overall.completed === summary.overall.total) {
    copy.textContent =
      "Every available topic and experiment is marked complete. Review anything below, or export a backup to keep it safe.";
  } else {
    const itemWord = summary.overall.completed === 1 ? "item is" : "items are";
    copy.textContent = `${summary.overall.completed} of ${summary.overall.total} available ${itemWord} marked complete. This dashboard is built from the completion records saved in this browser.`;
  }
}

function render() {
  if (!state.catalog) return;
  const summary = summarize(state.progress, state.catalog);
  renderOverall(summary);
  renderUnits(summary);
  renderCheckboxes();
  renderContinue(summary);
  renderActivity(summary);
  renderDataState(summary);
  renderStorageNotice();
  renderGreeting(summary);
}

function applyReadResult(result) {
  state.progress = result.progress;
  state.status = result.status;
  state.warnings = Array.isArray(result.warnings) ? result.warnings : [];
  state.error = result.error || null;
  state.storageOk = result.status !== "unavailable";
}

function openDialog(dialog) {
  if (!dialog) return;
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

function closeDialog(dialog) {
  if (!dialog) return;
  if (dialog.open && typeof dialog.close === "function") dialog.close();
  else dialog.removeAttribute("open");
}

function showImportError(message) {
  const node = $("[data-import-error]");
  if (node) node.textContent = message;
  openDialog($("#import-error-dialog"));
}

function describeCounts(summary) {
  return `${summary.theory} theory · ${summary.practical} practical`;
}

function handleToggle(input) {
  if (!interactive()) return;

  const kind = input.dataset.kind;
  const id = input.dataset.id;
  const completed = input.checked;
  const result = completed
    ? markComplete(kind, id, { allowedIds: state.allowed[kind] })
    : markIncomplete(kind, id, { allowedIds: state.allowed[kind] });

  if (!result.ok) {
    input.checked = !completed;
    toast(result.error || "Progress could not be updated.", { type: "warning" });
    return;
  }

  state.progress = result.progress;
  state.status = "valid";
  state.warnings = [];
  state.error = null;
  render();

  const item = findItem(kind, id);
  const summary = summarize(state.progress, state.catalog);
  const track = summary[kind];
  announce(
    `${completed ? "Marked" : "Cleared"} ${item ? item.title : "item"}. ` +
      `${kind === "theory" ? "Theory" : "Practical"} progress: ${track.completed} of ${track.total}.`
  );
}

function handleNext(button) {
  const kind = button.dataset.kind;
  const item = state.next[kind];
  if (!item) return;

  const result = markComplete(kind, item.id, { allowedIds: state.allowed[kind] });
  if (!result.ok) {
    toast(result.error || "Progress could not be updated.", { type: "warning" });
    return;
  }

  state.progress = result.progress;
  state.status = "valid";
  state.warnings = [];
  state.error = null;
  render();

  const summary = summarize(state.progress, state.catalog);
  const track = summary[kind];
  toast(`Marked “${item.title}” complete.`, { type: "success" });
  announce(
    `${item.title} marked complete. ${kind === "theory" ? "Theory" : "Practical"} progress: ` +
      `${track.completed} of ${track.total}.`
  );
}

function handleExport() {
  if (!state.storageOk || state.status === "invalid") {
    toast("Resolve the saved-data warning before exporting.", { type: "warning" });
    return;
  }

  const text = exportProgress(state.progress);
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `verilog-academy-progress-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1500);

  toast("Progress backup exported.", { type: "success" });
  announce("Progress backup exported.");
}

function readFileText(file) {
  if (typeof file.text === "function") return file.text();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(new Error("The selected file could not be read."));
    reader.readAsText(file);
  });
}

async function handleImportFile(file) {
  if (!file) return;
  if (!state.storageOk) {
    showImportError("Browser storage is unavailable, so a backup cannot be imported.");
    return;
  }

  let text;
  try {
    text = await readFileText(file);
  } catch (error) {
    showImportError(error.message || "The selected file could not be read.");
    return;
  }

  const parsed = parseBackup(text, {
    allowedTheoryIds: state.allowed.theory,
    allowedPracticalIds: state.allowed.practical,
  });

  if (!parsed.ok) {
    showImportError(parsed.error);
    return;
  }

  const current = summarize(state.progress, state.catalog).overall;
  const incoming = parsed.summary;
  const replacing = current.completed > 0 || state.status === "invalid";

  const currentNode = $("[data-import-current]");
  if (currentNode) currentNode.textContent = `${current.completed} of ${current.total} items`;
  const incomingNode = $("[data-import-incoming]");
  if (incomingNode) incomingNode.textContent = `${describeCounts(incoming)} · ${incoming.total} total`;

  const title = $("[data-import-title]");
  if (title) title.textContent = replacing ? "Replace current progress?" : "Import this backup?";
  const copy = $("[data-import-copy]");
  if (copy) {
    copy.textContent = replacing
      ? "The backup passed validation. Importing it will replace the progress saved in this browser."
      : "The backup passed validation. Importing it will add these completion records to this browser.";
  }
  const note = $("[data-import-note]");
  if (note) {
    note.textContent = replacing
      ? "Your current records cannot be recovered after replacement unless you exported them first."
      : "No progress is currently saved in this browser, so nothing will be overwritten.";
  }
  const confirm = $("[data-import-confirm]");
  if (confirm) confirm.textContent = replacing ? "Replace progress" : "Import progress";

  state.pendingImport = parsed.progress;
  openDialog($("#import-dialog"));
}

function handleImportConfirm() {
  const pending = state.pendingImport;
  if (!pending) return;

  const written = writeProgress(pending);
  if (!written.ok) {
    closeDialog($("#import-dialog"));
    showImportError(written.error || "The backup could not be saved.");
    return;
  }

  state.progress = written.progress;
  state.status = "valid";
  state.warnings = [];
  state.error = null;
  state.pendingImport = null;

  closeDialog($("#import-dialog"));
  render();

  const summary = summarize(state.progress, state.catalog);
  toast("Progress imported and saved in this browser.", { type: "success" });
  announce(
    `Progress imported. ${summary.theory.completed} theory topics and ` +
      `${summary.practical.completed} practical experiments are complete.`
  );
}

function openResetDialog() {
  if (!state.catalog) return;
  const summary = summarize(state.progress, state.catalog);
  const summaryNode = $("[data-reset-summary]");
  if (summaryNode) {
    summaryNode.textContent =
      summary.overall.completed === 0
        ? "No completion records are stored in this browser. Resetting removes the saved progress key."
        : `This will remove ${summary.overall.completed} completion ${
            summary.overall.completed === 1 ? "record" : "records"
          } stored in this browser.`;
  }
  const theoryNode = $("[data-reset-theory]");
  if (theoryNode) {
    theoryNode.textContent = `${summary.theory.completed} ${
      summary.theory.completed === 1 ? "topic" : "topics"
    }`;
  }
  const practicalNode = $("[data-reset-practical]");
  if (practicalNode) {
    practicalNode.textContent = `${summary.practical.completed} ${
      summary.practical.completed === 1 ? "experiment" : "experiments"
    }`;
  }

  openDialog($("#reset-dialog"));
}

function handleResetConfirm() {
  const result = resetProgress();
  if (!result.ok) {
    toast(result.error || "Progress could not be reset.", { type: "warning" });
    return;
  }

  state.progress = createEmptyProgress();
  state.status = "empty";
  state.warnings = [];
  state.error = null;
  state.pendingImport = null;

  closeDialog($("#reset-dialog"));
  render();

  toast("Progress reset. Every completion record was removed.", { type: "success" });
  announce("Progress reset. No completion records remain.");
}

function bindEvents() {
  document.addEventListener("change", (event) => {
    const input = event.target.closest(".check-input");
    if (input) handleToggle(input);
  });

  document.addEventListener("click", (event) => {
    const nextButton = event.target.closest("[data-mark-next]");
    if (nextButton && !nextButton.disabled) {
      handleNext(nextButton);
      return;
    }

    if (event.target.closest("[data-export]")) {
      handleExport();
      return;
    }

    if (event.target.closest("[data-import]")) {
      const fileInput = $("[data-import-input]");
      if (fileInput) {
        fileInput.value = "";
        fileInput.click();
      }
      return;
    }

    if (event.target.closest("[data-reset-open]")) {
      openResetDialog();
      return;
    }

    if (event.target.closest("[data-import-confirm]")) {
      handleImportConfirm();
      return;
    }

    if (event.target.closest("[data-reset-confirm]")) {
      handleResetConfirm();
    }
  });

  const fileInput = $("[data-import-input]");
  fileInput?.addEventListener("change", () => {
    const file = fileInput.files && fileInput.files[0];
    if (file) handleImportFile(file);
  });

  window.addEventListener("storage", (event) => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    applyReadResult(readProgress());
    render();
    announce("Progress updated in another tab.");
    if (state.status === "invalid") {
      toast("Saved progress in another tab is unreadable.", { type: "warning" });
    }
  });
}

function showFatal(message) {
  const alert = $("[data-storage-alert]");
  const node = $("[data-storage-message]");
  if (alert && node) {
    alert.hidden = false;
    alert.classList.add("dash-alert--error");
    alert.setAttribute("role", "alert");
    node.textContent = message;
  }
  $$(".check-input").forEach((input) => {
    input.disabled = true;
  });
  $$("[data-export], [data-import], [data-reset-open], [data-mark-next]").forEach((button) => {
    button.disabled = true;
  });
}

function init() {
  const node = document.getElementById("curriculum-data");
  let curriculum = null;

  if (node) {
    try {
      curriculum = JSON.parse(node.textContent || "");
    } catch {
      curriculum = null;
    }
  }

  if (!curriculum) {
    showFatal("Curriculum metadata could not be read, so progress cannot be displayed.");
    return;
  }

  try {
    state.catalog = buildCatalog(curriculum);
  } catch (error) {
    showFatal(error.message || "Curriculum metadata is incomplete.");
    return;
  }

  state.allowed.theory = new Set(state.catalog.theoryItems.map((item) => item.id));
  state.allowed.practical = new Set(state.catalog.practicalItems.map((item) => item.id));

  applyReadResult(readProgress());
  bindEvents();
  render();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
  init();
}
