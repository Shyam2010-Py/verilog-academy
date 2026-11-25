/* ==========================================================================
   VERILOG ACADEMY — EC-405 theory classroom
   Hydrates computed progress and wires topic completion to js/progress.js.
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

const lessonId = $("[data-lesson-id]")?.dataset.lessonId || null;
const toggleButtons = $$("[data-topic-toggle]");
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

function unitSummary(summary, unitId) {
  return summary.units.find((unit) => unit.id === unitId) || null;
}

function renderLanding(progress, summary, readable) {
  if (!readable) {
    setText("[data-theory-count]", "—");
    setText("[data-theory-percent]", "—");
    setText("[data-theory-next-title]", "Progress unavailable");
    setText("[data-theory-next-meta]", "Open the dashboard to repair the saved record");
    setBar($("[data-theory-bar]"), $("[data-theory-fill]"), 0);
    const continueLink = $("[data-theory-continue]");
    if (continueLink) {
      continueLink.href = "../dashboard.html";
      $("[data-theory-continue-label]", continueLink).textContent = "Open dashboard";
    }
    $$("[data-topic-row]").forEach((row) => {
      row.classList.remove("is-complete");
      row.querySelector("[data-topic-state]").textContent = "—";
    });
    $$("[data-unit-card]").forEach((card) => {
      const unitId = card.dataset.unitCard;
      setText(`[data-unit-count="${unitId}"]`, "—");
      setText(`[data-unit-percent="${unitId}"]`, "—");
      setBar($(`[data-unit-bar="${unitId}"]`), $(`[data-unit-fill="${unitId}"]`), 0);
    });
    return;
  }

  setText("[data-theory-count]", String(summary.theory.completed));
  setText("[data-theory-percent]", `${summary.theory.percent}%`);
  setBar($("[data-theory-bar]"), $("[data-theory-fill]"), summary.theory.percent);

  $$("[data-topic-row]").forEach((row) => {
    const done = isComplete(progress, "theory", row.dataset.topicRow);
    row.classList.toggle("is-complete", done);
    const state = row.querySelector("[data-topic-state]");
    if (state) state.textContent = done ? "Complete" : "Not started";
  });

  catalog.units.forEach((unit) => {
    const stats = unitSummary(summary, unit.id);
    if (!stats) return;
    const card = $(`[data-unit-card="${unit.id}"]`);
    setText(`[data-unit-count="${unit.id}"]`, `${stats.completed} / ${stats.total}`);
    setText(`[data-unit-percent="${unit.id}"]`, `${stats.percent}%`);
    setBar($(`[data-unit-bar="${unit.id}"]`), $(`[data-unit-fill="${unit.id}"]`), stats.percent);

    const start = $(`[data-unit-start="${unit.id}"]`);
    if (start) {
      const next =
        unit.topics.find((topic) => !isComplete(progress, "theory", topic.id)) || unit.topics[0];
      if (next) start.href = `${next.id}.html`;
      const label = $("[data-unit-start-label]", start);
      if (label) {
        label.textContent =
          stats.completed === stats.total
            ? "Review unit"
            : stats.completed > 0
              ? "Continue unit"
              : "Start unit";
      }
    }

    if (card) card.classList.toggle("is-complete", stats.completed === stats.total);
  });

  const next = getNextItem(progress, catalog, "theory");
  const continueLink = $("[data-theory-continue]");
  const nextCard = $("[data-theory-next]");

  if (next) {
    const label = `Unit ${next.unitNumber} · Topic ${String(next.number).padStart(2, "0")}`;
    setText("[data-theory-next-title]", next.title);
    setText("[data-theory-next-meta]", label);
    if (continueLink) {
      continueLink.href = `${next.id}.html`;
      $("[data-theory-continue-label]", continueLink).textContent =
        `Continue with Topic ${String(next.number).padStart(2, "0")}`;
    }
    if (nextCard) {
      nextCard.href = `${next.id}.html`;
      $("[data-theory-next-label]", nextCard).textContent = "Open topic";
    }
  } else {
    setText("[data-theory-next-title]", "Every topic is marked complete");
    setText("[data-theory-next-meta]", "Revisit any lesson, or review your records");
    if (continueLink) {
      continueLink.href = "../dashboard.html";
      $("[data-theory-continue-label]", continueLink).textContent = "Review on dashboard";
    }
    if (nextCard) {
      nextCard.href = "../dashboard.html";
      $("[data-theory-next-label]", nextCard).textContent = "Open dashboard";
    }
  }
}

function renderLesson(progress, summary, readable) {
  const item = catalog.theoryItems.find((topic) => topic.id === lessonId);
  if (!item) return;

  const buttons = toggleButtons;
  if (!readable) {
    buttons.forEach((button) => {
      button.disabled = true;
      button.setAttribute("aria-pressed", "false");
      $("[data-topic-toggle-label]", button).textContent = "Progress unavailable";
    });
    const status = $("[data-topic-status]");
    if (status) {
      status.textContent =
        "Saved progress cannot be read. Open the dashboard to import a valid backup or reset the record.";
    }
    return;
  }

  const unitStats = unitSummary(summary, item.unitId);
  if (unitStats) {
    setText("[data-lesson-unit-count]", `${unitStats.completed} / ${unitStats.total}`);
    setBar(
      $("[data-lesson-unit-bar]"),
      $("[data-lesson-unit-fill]"),
      unitStats.percent
    );
  }

  const done = isComplete(progress, "theory", lessonId);
  buttons.forEach((button) => {
    button.disabled = false;
    button.setAttribute("aria-pressed", String(done));
    $("[data-topic-toggle-label]", button).textContent = done
      ? "Completed — undo"
      : "Mark topic complete";
  });

  const status = $("[data-topic-status]");
  if (status) {
    const entry = progress.theory[lessonId];
    status.textContent = done
      ? `Completed ${formatDate(entry?.completedAt)}. This record is reversible.`
      : `Not marked complete. Unit ${item.unitNumber}: ${
          unitStats ? `${unitStats.completed} of ${unitStats.total}` : "0 of 0"
        } topics recorded.`;
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
      "Progress was saved in an older format. It was read without changes and will be upgraded the next time you mark a topic."
    );
  } else if (result.status === "repaired") {
    showAlert("Some unreadable completion records were ignored. The stored record was not rewritten.");
  } else {
    showAlert("");
  }

  const summary = summarize(result.progress, catalog);
  if (lessonId) {
    renderLesson(result.progress, summary, readable);
  } else {
    renderLanding(result.progress, summary, readable);
  }
}

function handleToggle() {
  if (!catalog || !lessonId) return;
  const current = readProgress();
  if (current.status === "invalid" || current.status === "unavailable") {
    toast(current.error || "Saved progress cannot be read.", { type: "warning" });
    refresh();
    return;
  }

  const done = isComplete(current.progress, "theory", lessonId);
  const allowedIds = new Set(catalog.theoryItems.map((topic) => topic.id));
  const result = done
    ? markIncomplete("theory", lessonId, { allowedIds })
    : markComplete("theory", lessonId, { allowedIds });

  if (!result.ok) {
    toast(result.error || "Progress could not be updated.", { type: "warning" });
    refresh();
    return;
  }

  if (result.changed) {
    const title = catalog.theoryItems.find((topic) => topic.id === lessonId)?.title || "Topic";
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
