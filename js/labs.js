/* ==========================================================================
   VERILOG ACADEMY — EC-410 practical laboratory
   Hydrates experiment progress and wires completion to js/progress.js.
   Reading a page never writes progress; only an explicit toggle does.
   ========================================================================== */

import {
  STORAGE_KEY,
  buildCatalog,
  getNextItem,
  isComplete,
  markComplete,
  markIncomplete,
  readProgress,
  summarize,
} from "./progress.js";
import { toast } from "./ui.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const dataNode = $("#curriculum-data");
let catalog = null;

try {
  catalog = buildCatalog(JSON.parse(dataNode.textContent));
} catch (error) {
  console.error("Curriculum data could not be loaded:", error);
}

const experimentId = $("[data-experiment-id]")?.dataset.experimentId || null;
const toggleButtons = $$("[data-experiment-toggle]");
const alertBox = $("[data-storage-alert]");
const alertMessage = $("[data-storage-message]");

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  day: "numeric",
  month: "short",
  year: "numeric",
});

function formatDate(value) {
  if (!value) return "previously";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "previously" : dateFormatter.format(date);
}

function setBar(bar, fill, percent) {
  if (bar) bar.setAttribute("aria-valuenow", String(percent));
  if (fill) fill.style.setProperty("--progress", `${percent}%`);
}

function setText(selector, value) {
  $$(selector).forEach((node) => {
    node.textContent = value;
  });
}

function showAlert(message, error = false) {
  if (!alertBox || !alertMessage) return;
  if (!message) {
    alertBox.hidden = true;
    alertMessage.textContent = "";
    return;
  }
  alertMessage.textContent = message;
  alertBox.hidden = false;
  alertBox.setAttribute("role", error ? "alert" : "status");
}

function pad(value) {
  return String(value).padStart(2, "0");
}

function renderLanding(progress, summary, readable) {
  if (!readable) {
    setText("[data-lab-count]", "—");
    setText("[data-lab-percent]", "—");
    setText("[data-lab-next-title]", "Progress unavailable");
    setText("[data-lab-next-meta]", "Open the dashboard to repair the saved record");
    setBar($("[data-lab-bar]"), $("[data-lab-fill]"), 0);
    const continueLink = $("[data-lab-continue]");
    if (continueLink) {
      continueLink.href = "../dashboard.html";
      $("[data-lab-continue-label]", continueLink).textContent = "Open dashboard";
    }
    $$("[data-lab-card]").forEach((card) => {
      card.classList.remove("is-complete");
      const state = card.querySelector("[data-lab-state]");
      if (state) state.textContent = "—";
    });
    return;
  }

  setText("[data-lab-count]", String(summary.practical.completed));
  setText("[data-lab-percent]", `${summary.practical.percent}%`);
  setBar($("[data-lab-bar]"), $("[data-lab-fill]"), summary.practical.percent);

  $$("[data-lab-card]").forEach((card) => {
    const id = card.dataset.labCard;
    const done = isComplete(progress, "practical", id);
    card.classList.toggle("is-complete", done);
    const state = card.querySelector("[data-lab-state]");
    if (state) {
      state.textContent = done ? "Complete" : "Not started";
      state.classList.toggle("badge-success", done);
      state.classList.toggle("badge-violet", !done);
    }
  });

  const next = getNextItem(progress, catalog, "practical");
  const continueLink = $("[data-lab-continue]");
  const nextCard = $("[data-lab-next]");

  if (next) {
    setText("[data-lab-next-title]", next.title);
    setText("[data-lab-next-meta]", `Experiment ${pad(next.number)} · ${summary.practical.completed} of ${summary.practical.total} recorded`);
    if (continueLink) {
      continueLink.href = `${next.id}.html`;
      $("[data-lab-continue-label]", continueLink).textContent =
        summary.practical.completed > 0
          ? `Continue with Experiment ${pad(next.number)}`
          : `Start with Experiment ${pad(next.number)}`;
    }
    if (nextCard) {
      nextCard.href = `${next.id}.html`;
      $("[data-lab-next-label]", nextCard).textContent = "Open experiment";
    }
  } else {
    setText("[data-lab-next-title]", "Every experiment is marked complete");
    setText("[data-lab-next-meta]", "Revisit any bench record, or review your progress");
    if (continueLink) {
      continueLink.href = "../dashboard.html";
      $("[data-lab-continue-label]", continueLink).textContent = "Review on dashboard";
    }
    if (nextCard) {
      nextCard.href = "../dashboard.html";
      $("[data-lab-next-label]", nextCard).textContent = "Open dashboard";
    }
  }
}

function renderExperiment(progress, summary, readable) {
  const item = catalog.practicalItems.find((experiment) => experiment.id === experimentId);
  if (!item) return;

  if (!readable) {
    toggleButtons.forEach((button) => {
      button.disabled = true;
      button.setAttribute("aria-pressed", "false");
      $("[data-experiment-toggle-label]", button).textContent = "Progress unavailable";
    });
    const status = $("[data-experiment-status]");
    if (status) {
      status.textContent =
        "Saved progress cannot be read. Open the dashboard to import a valid backup or reset the record.";
    }
    return;
  }

  setText(
    "[data-lab-unit-count]",
    `${summary.practical.completed} / ${summary.practical.total}`
  );
  setBar($("[data-lab-bar]"), $("[data-lab-fill]"), summary.practical.percent);

  const done = isComplete(progress, "practical", experimentId);
  toggleButtons.forEach((button) => {
    button.disabled = false;
    button.setAttribute("aria-pressed", String(done));
    $("[data-experiment-toggle-label]", button).textContent = done
      ? "Completed — undo"
      : "Mark experiment complete";
  });

  const status = $("[data-experiment-status]");
  if (status) {
    const entry = progress.practical[experimentId];
    status.textContent = done
      ? `Completed ${formatDate(entry?.completedAt)}. This record is reversible.`
      : `Not marked complete. ${summary.practical.completed} of ${summary.practical.total} experiments recorded.`;
  }
}

function refresh() {
  if (!catalog) {
    showAlert("The curriculum data could not be loaded, so progress cannot be calculated.", true);
    toggleButtons.forEach((button) => {
      button.disabled = true;
    });
    return;
  }

  const result = readProgress();
  const readable = result.status !== "invalid" && result.status !== "unavailable";

  if (!readable) {
    showAlert(result.error || "Saved progress is unavailable.", true);
  } else if (result.status === "migrated") {
    showAlert(
      "Progress was saved in an older format. It was read without changes and will be upgraded the next time you mark an experiment."
    );
  } else if (result.status === "repaired") {
    showAlert("Some unreadable completion records were ignored. The stored record was not rewritten.");
  } else {
    showAlert("");
  }

  const summary = summarize(result.progress, catalog);
  if (experimentId) {
    renderExperiment(result.progress, summary, readable);
  } else {
    renderLanding(result.progress, summary, readable);
  }
}

function handleToggle() {
  if (!catalog || !experimentId) return;
  const current = readProgress();
  if (current.status === "invalid" || current.status === "unavailable") {
    toast(current.error || "Saved progress cannot be read.", { type: "warning" });
    refresh();
    return;
  }

  const done = isComplete(current.progress, "practical", experimentId);
  const allowedIds = new Set(catalog.practicalItems.map((experiment) => experiment.id));
  const result = done
    ? markIncomplete("practical", experimentId, { allowedIds })
    : markComplete("practical", experimentId, { allowedIds });

  if (!result.ok) {
    toast(result.error || "Progress could not be updated.", { type: "warning" });
    refresh();
    return;
  }

  if (result.changed) {
    const title =
      catalog.practicalItems.find((experiment) => experiment.id === experimentId)?.title ||
      "Experiment";
    toast(done ? "Completion removed." : `Marked “${title}” complete.`, {
      type: done ? "info" : "success",
    });
  }
  refresh();
}

toggleButtons.forEach((button) => button.addEventListener("click", handleToggle));

window.addEventListener("storage", (event) => {
  if (event.key === STORAGE_KEY || event.key === null) refresh();
});

refresh();
