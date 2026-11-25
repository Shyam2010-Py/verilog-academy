/* ==========================================================================
   VERILOG ACADEMY - Practice quiz system
   Four independent question banks, local attempt history under va.quizzes,
   one-question-at-a-time navigation and explanations after submission.
   No answer or explanation is rendered before the learner submits.
   ========================================================================== */

import { toast } from "./ui.js";

const STORAGE_KEY = "va.quizzes";
const STORAGE_VERSION = 1;
const MAX_ATTEMPTS = 20;
const LETTERS = ["A", "B", "C", "D"];

const dataNode = document.querySelector("#quiz-data");
let categories = [];
const byId = new Map();

try {
  const parsed = JSON.parse(dataNode?.textContent || "[]");
  const source = Array.isArray(parsed) ? parsed : parsed.categories;
  if (Array.isArray(source)) {
    categories = source.filter(
      (category) =>
        category &&
        typeof category.id === "string" &&
        Array.isArray(category.questions) &&
        category.questions.length > 0
    );
  }
} catch (error) {
  console.error("Quiz data could not be loaded:", error);
}

categories.forEach((category) => byId.set(category.id, category));

const state = {
  category: null,
  index: 0,
  answers: [],
  submitted: false,
  reviewOnly: false,
  currentResult: null,
  submitWarning: false,
  storageWarned: false,
};

const drafts = new Map();

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function clear(node) {
  if (node) node.replaceChildren();
}

function inline(target, text) {
  const value = String(text ?? "");
  const parts = value.split("`");
  parts.forEach((part, index) => {
    if (!part) return;
    if (index % 2 === 1) {
      target.appendChild(el("code", null, part));
    } else {
      target.appendChild(document.createTextNode(part));
    }
  });
}

function formatDate(value) {
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return value;
  }
}

function percent(score, total) {
  return total > 0 ? Math.round((score / total) * 100) : 0;
}

/* Storage ---------------------------------------------------------------- */

function emptyStore() {
  return { version: STORAGE_VERSION, attempts: {} };
}

function normaliseAttempt(raw, category) {
  if (!raw || typeof raw !== "object") return null;
  if (!Array.isArray(raw.answers) || raw.answers.length !== category.questions.length) return null;
  const answers = [];
  for (const value of raw.answers) {
    if (value === null) {
      answers.push(null);
    } else if (Number.isInteger(value) && value >= 0 && value < 4) {
      answers.push(value);
    } else {
      return null;
    }
  }
  const submittedAt = typeof raw.submittedAt === "string" ? raw.submittedAt : "";
  if (!submittedAt || Number.isNaN(Date.parse(submittedAt))) return null;
  const score = answers.reduce(
    (total, answer, index) => total + (answer === category.questions[index].answer ? 1 : 0),
    0
  );
  return {
    id: typeof raw.id === "string" && raw.id ? raw.id : submittedAt,
    submittedAt,
    answers,
    score,
    total: category.questions.length,
  };
}

function readStore() {
  const empty = emptyStore();
  let raw;
  try {
    raw = window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return empty;
  }
  if (!raw) return empty;

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* Ignore a storage context that is already unavailable. */
    }
    return empty;
  }

  if (
    !parsed ||
    typeof parsed !== "object" ||
    parsed.version !== STORAGE_VERSION ||
    !parsed.attempts ||
    typeof parsed.attempts !== "object" ||
    Array.isArray(parsed.attempts)
  ) {
    return empty;
  }

  const attempts = {};
  categories.forEach((category) => {
    const list = parsed.attempts[category.id];
    if (!Array.isArray(list)) return;
    const cleaned = list
      .map((entry) => normaliseAttempt(entry, category))
      .filter(Boolean)
      .slice(-MAX_ATTEMPTS);
    if (cleaned.length) attempts[category.id] = cleaned;
  });

  return { version: STORAGE_VERSION, attempts };
}

function writeStore(store) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    return true;
  } catch {
    if (!state.storageWarned) {
      state.storageWarned = true;
      toast("Quiz storage is unavailable. This attempt cannot be saved.", { type: "warning" });
    }
    return false;
  }
}

let store = readStore();

function getAttempts(categoryId) {
  const category = byId.get(categoryId);
  const list = Array.isArray(store.attempts[categoryId]) ? store.attempts[categoryId] : [];
  if (!category) return [];
  return list.map((entry) => normaliseAttempt(entry, category)).filter(Boolean);
}

function saveAttempt() {
  const category = state.category;
  const submittedAt = new Date().toISOString();
  const id =
    typeof window.crypto?.randomUUID === "function"
      ? window.crypto.randomUUID()
      : `${submittedAt}-${Math.random().toString(36).slice(2)}`;
  const entry = { id, submittedAt, answers: state.answers.slice() };
  const saved = normaliseAttempt(entry, category);
  store.attempts[category.id] = [...getAttempts(category.id), saved]
    .filter(Boolean)
    .slice(-MAX_ATTEMPTS);
  writeStore(store);
  return saved;
}

/* Rendering -------------------------------------------------------------- */

function bestAttempt(categoryId) {
  const attempts = getAttempts(categoryId);
  if (!attempts.length) return null;
  return attempts.reduce((best, attempt) =>
    percent(attempt.score, attempt.total) > percent(best.score, best.total) ? attempt : best
  );
}

function renderCategoryCards() {
  $$("[data-quiz-category]").forEach((card) => {
    const id = card.dataset.quizCategory;
    const category = byId.get(id);
    if (!category) return;
    const attempts = getAttempts(id);
    const best = bestAttempt(id);
    const target = $(`[data-quiz-best="${id}"]`);
    if (target) {
      target.textContent = attempts.length
        ? `Best ${percent(best.score, best.total)}% · ${attempts.length} attempt${attempts.length === 1 ? "" : "s"}`
        : "No attempts yet";
    }
    const active = state.category?.id === id;
    card.classList.toggle("is-active", active);
    card.setAttribute("aria-pressed", String(active));
  });
}

function renderStatus() {
  const status = $("[data-quiz-status]");
  if (!status) return;
  let label = "Ready to start";
  let tone = "";
  if (state.submitted) {
    label = state.reviewOnly ? "Reviewing saved attempt" : "Submitted";
    tone = "badge-success";
  } else if (state.answers.some((answer) => answer !== null)) {
    label = "In progress";
    tone = "badge-warning";
  }
  status.textContent = label;
  status.className = `badge ${tone}`.trim();
}

function renderMeter() {
  const total = state.category.questions.length;
  const answered = state.answers.filter((answer) => answer !== null).length;
  const value = Math.round((answered / total) * 100);
  const position = $("[data-quiz-position]");
  const answeredNode = $("[data-quiz-answered]");
  const progress = $("[data-quiz-progress]");
  const fill = $("[data-quiz-progress-fill]");
  if (position) position.textContent = `Question ${state.index + 1} of ${total}`;
  if (answeredNode) answeredNode.textContent = `${answered} of ${total} answered`;
  if (progress) progress.setAttribute("aria-valuenow", String(value));
  if (fill) fill.style.setProperty("--progress", `${value}%`);
}

function renderPalette() {
  const palette = $("[data-quiz-palette]");
  if (!palette) return;
  clear(palette);
  state.category.questions.forEach((question, index) => {
    const button = el("button", "quiz-palette__dot", String(index + 1));
    button.type = "button";
    button.dataset.quizJump = String(index);
    const answered = state.answers[index] !== null;
    const correct = answered && state.answers[index] === question.answer;
    button.classList.toggle("is-current", index === state.index);
    button.classList.toggle("is-answered", answered && !state.submitted);
    button.classList.toggle("is-correct", state.submitted && correct);
    button.classList.toggle("is-wrong", state.submitted && answered && !correct);
    if (index === state.index) button.setAttribute("aria-current", "step");
    let label = `Question ${index + 1}`;
    if (state.submitted) label += correct ? ", correct" : answered ? ", incorrect" : ", unanswered";
    else if (answered) label += ", answered";
    button.setAttribute("aria-label", label);
    palette.appendChild(button);
  });
}

function renderTable(table) {
  const wrap = el("div", "quiz-table-wrap");
  const node = el("table", "quiz-table");
  if (table.caption) {
    const caption = el("caption", null, table.caption);
    node.appendChild(caption);
  }
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  table.headers.forEach((header) => {
    const cell = el("th", null, String(header));
    cell.scope = "col";
    headRow.appendChild(cell);
  });
  head.appendChild(headRow);
  node.appendChild(head);
  const body = document.createElement("tbody");
  table.rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((value) => tr.appendChild(el("td", null, String(value))));
    body.appendChild(tr);
  });
  node.appendChild(body);
  wrap.appendChild(node);
  return wrap;
}

function renderExplanation(question) {
  const box = el("div", "quiz-explanation");
  box.appendChild(el("span", "badge badge-success", "Explanation"));
  const answerLine = el("p", "quiz-explanation__answer");
  answerLine.appendChild(document.createTextNode("Correct answer: "));
  inline(answerLine, question.options[question.answer]);
  box.appendChild(answerLine);
  const body = el("p");
  inline(body, question.explanation);
  box.appendChild(body);
  if (state.answers[state.index] === null) {
    box.appendChild(el("p", "quiz-explanation__note", "You left this question unanswered, so it was marked incorrect."));
  }
  return box;
}

function renderQuestion({ focus = false } = {}) {
  const root = $("[data-quiz-question]");
  if (!root || !state.category) return;
  const question = state.category.questions[state.index];
  const total = state.category.questions.length;
  clear(root);

  const article = el("article", "quiz-question-card");
  const head = el("div", "quiz-question-card__head");
  head.appendChild(el("span", "badge badge-violet", question.type));
  head.appendChild(el("span", "quiz-question-card__num", `Question ${state.index + 1} of ${total}`));
  article.appendChild(head);

  const prompt = el("h3", "quiz-question-card__prompt");
  prompt.tabIndex = -1;
  inline(prompt, question.prompt);
  article.appendChild(prompt);

  if (question.code) {
    const pre = el("pre", "quiz-code");
    pre.appendChild(el("code", null, question.code));
    article.appendChild(pre);
  }

  if (question.table) article.appendChild(renderTable(question.table));

  const fieldset = el("fieldset", "quiz-options");
  fieldset.appendChild(el("legend", "sr-only", "Choose one answer"));
  question.options.forEach((option, index) => {
    const label = el("label", "quiz-option");
    const input = el("input", "quiz-option__input");
    input.type = "radio";
    input.name = `quiz-${state.category.id}-${question.id}`;
    input.value = String(index);
    input.dataset.quizOption = String(index);
    input.checked = state.answers[state.index] === index;
    input.disabled = state.submitted;
    label.appendChild(input);
    label.appendChild(el("span", "quiz-option__letter", LETTERS[index]));
    const text = el("span", "quiz-option__text");
    inline(text, option);
    label.appendChild(text);

    if (state.submitted) {
      const correct = index === question.answer;
      const selected = state.answers[state.index] === index;
      label.classList.toggle("is-correct", correct);
      label.classList.toggle("is-wrong", selected && !correct);
      if (correct) label.appendChild(el("span", "quiz-option__mark", "Correct answer"));
      else if (selected) label.appendChild(el("span", "quiz-option__mark", "Your answer"));
    }
    fieldset.appendChild(label);
  });
  article.appendChild(fieldset);

  if (state.submitted) article.appendChild(renderExplanation(question));

  root.appendChild(article);
  if (focus) prompt.focus({ preventScroll: true });
}

function renderResult() {
  const panel = $("[data-quiz-result]");
  if (!panel) return;
  clear(panel);
  panel.appendChild(el("span", "panel-kicker", "Your result"));
  const category = state.category;

  if (!state.currentResult) {
    const attempts = getAttempts(category.id);
    if (!attempts.length) {
      panel.appendChild(el("h3", null, "No attempt yet."));
      panel.appendChild(
        el(
          "p",
          null,
          "Choose a category, answer the questions and submit. Your score and explanations will appear here."
        )
      );
      return;
    }
    const best = bestAttempt(category.id);
    const latest = attempts[attempts.length - 1];
    panel.appendChild(el("h3", "quiz-result__score", `${percent(best.score, best.total)}%`));
    panel.appendChild(
      el(
        "p",
        "quiz-result__meta",
        `Best score · ${best.score}/${best.total} · ${attempts.length} saved attempt${attempts.length === 1 ? "" : "s"}`
      )
    );
    panel.appendChild(el("p", "quiz-result__note", `Latest attempt: ${formatDate(latest.submittedAt)}.`));
    const review = el("button", "btn btn-secondary btn-sm", "Review latest attempt");
    review.type = "button";
    review.dataset.quizReviewLatest = "true";
    panel.appendChild(review);
    return;
  }

  const result = state.currentResult;
  const value = percent(result.score, result.total);
  panel.appendChild(el("h3", "quiz-result__score", `${result.score} / ${result.total}`));
  panel.appendChild(el("p", "quiz-result__percent", `${value}%`));
  const meta = el("p", "quiz-result__meta");
  const unanswered = result.answers.filter((answer) => answer === null).length;
  meta.textContent = `${result.total - result.score} incorrect or unanswered · ${unanswered} left blank`;
  panel.appendChild(meta);
  panel.appendChild(
    el(
      "p",
      "quiz-result__note",
      state.reviewOnly
        ? `Reviewing a saved attempt from ${formatDate(result.submittedAt)}.`
        : `Saved locally · ${formatDate(result.submittedAt)}.`
    )
  );
  let message = "Start with the explanations and retry when the ideas are clearer.";
  if (value === 100) message = "Every answer is correct. The bank is secure.";
  else if (value >= 75) message = "Strong result. Read the missed explanations before moving on.";
  else if (value >= 50) message = "Halfway there. Review the incorrect questions, then retry.";
  panel.appendChild(el("p", "quiz-result__message", message));
}

function renderHistory() {
  const target = $("[data-quiz-history]");
  const count = $("[data-quiz-attempt-count]");
  if (!target) return;
  clear(target);
  const attempts = getAttempts(state.category.id).slice().reverse();
  if (count) count.textContent = String(attempts.length);
  if (!attempts.length) {
    target.appendChild(el("p", "quiz-empty", "No saved attempts for this category yet."));
    return;
  }
  const list = el("div", "quiz-history-list");
  attempts.forEach((attempt) => {
    const row = el("button", "quiz-history-row");
    row.type = "button";
    row.dataset.quizAttempt = attempt.id;
    const value = percent(attempt.score, attempt.total);
    row.setAttribute(
      "aria-label",
      `Review attempt from ${formatDate(attempt.submittedAt)}. Score ${attempt.score} of ${attempt.total}, ${value} percent.`
    );
    const top = el("span", "quiz-history-row__top");
    top.appendChild(el("span", "quiz-history-row__date", formatDate(attempt.submittedAt)));
    top.appendChild(el("span", "quiz-history-row__score", `${attempt.score}/${attempt.total}`));
    row.appendChild(top);
    const bottom = el("span", "quiz-history-row__bottom");
    bottom.appendChild(el("span", null, `${value}%`));
    bottom.appendChild(el("span", "quiz-history-row__review", "Review"));
    row.appendChild(bottom);
    list.appendChild(row);
  });
  target.appendChild(list);
}

function renderAll() {
  if (!state.category) return;
  const category = state.category;
  const heading = $("[data-quiz-heading]");
  const intro = $("[data-quiz-intro]");
  const kicker = $("[data-quiz-kicker]");
  const title = $("[data-quiz-title]");
  if (heading) heading.textContent = category.title;
  if (title) title.textContent = category.title;
  if (kicker) kicker.textContent = category.kicker;
  if (intro) {
    intro.textContent = `${category.questions.length} questions. Answer at your own pace, submit once, then review every explanation.`;
  }
  renderCategoryCards();
  renderStatus();
  renderMeter();
  renderQuestion();
  renderPalette();
  renderResult();
  renderHistory();

  const submit = $("[data-quiz-submit]");
  const retry = $("[data-quiz-retry]");
  const review = $("[data-quiz-review]");
  if (submit) submit.hidden = state.submitted;
  if (retry) retry.hidden = !state.submitted;
  if (review) review.hidden = !state.submitted;
  const warning = $("[data-quiz-warning]");
  if (warning) {
    warning.textContent = state.submitWarning
      ? "Some questions are unanswered. They will be marked incorrect. Press Submit answers again to confirm."
      : "";
  }
}

/* Actions ---------------------------------------------------------------- */

function scrollToRunner() {
  const runner = $("#quiz-runner");
  if (!runner) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  runner.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
}

function selectCategory(id, { scroll = false } = {}) {
  const next = byId.get(id);
  if (!next) return;
  if (state.category && !state.submitted && state.answers.some((answer) => answer !== null)) {
    drafts.set(state.category.id, state.answers.slice());
  }
  state.category = next;
  state.answers = drafts.get(id) || new Array(next.questions.length).fill(null);
  state.index = 0;
  state.submitted = false;
  state.reviewOnly = false;
  state.currentResult = null;
  state.submitWarning = false;
  renderAll();
  if (scroll) scrollToRunner();
}

function goTo(index, { focus = true } = {}) {
  const total = state.category.questions.length;
  state.index = Math.max(0, Math.min(total - 1, index));
  state.submitWarning = false;
  renderQuestion({ focus });
  renderMeter();
  renderPalette();
  const warning = $("[data-quiz-warning]");
  if (warning) warning.textContent = "";
}

function submitQuiz() {
  if (state.submitted) return;
  const category = state.category;
  const unanswered = state.answers.filter((answer) => answer === null).length;
  if (unanswered > 0 && !state.submitWarning) {
    state.submitWarning = true;
    const warning = $("[data-quiz-warning]");
    if (warning) {
      warning.textContent = "Some questions are unanswered. They will be marked incorrect. Press Submit answers again to confirm.";
    }
    toast(`${unanswered} unanswered question${unanswered === 1 ? "" : "s"} will be marked incorrect.`, {
      type: "warning",
    });
    return;
  }
  const result = saveAttempt();
  if (!result) {
    toast("This attempt could not be saved. Your score is still shown below.", { type: "warning" });
  }
  state.currentResult = result || {
    id: "unsaved",
    submittedAt: new Date().toISOString(),
    answers: state.answers.slice(),
    score: state.answers.reduce(
      (total, answer, index) => total + (answer === category.questions[index].answer ? 1 : 0),
      0
    ),
    total: category.questions.length,
  };
  state.submitted = true;
  state.reviewOnly = false;
  state.submitWarning = false;
  drafts.delete(category.id);
  renderAll();
  toast(`Attempt saved: ${state.currentResult.score}/${state.currentResult.total}.`, { type: "success" });
}

function retryQuiz() {
  if (!state.category) return;
  state.answers = new Array(state.category.questions.length).fill(null);
  state.index = 0;
  state.submitted = false;
  state.reviewOnly = false;
  state.currentResult = null;
  state.submitWarning = false;
  drafts.delete(state.category.id);
  renderAll();
  toast("Fresh attempt started. Previous results remain in the history.", { type: "success" });
}

function reviewAnswers() {
  if (!state.submitted || !state.category) return;
  const firstWrong = state.answers.findIndex(
    (answer, index) => answer !== state.category.questions[index].answer
  );
  state.index = firstWrong >= 0 ? firstWrong : 0;
  renderQuestion({ focus: true });
  renderMeter();
  renderPalette();
  scrollToRunner();
}

function reviewAttempt(id) {
  const attempt = getAttempts(state.category.id).find((item) => item.id === id);
  if (!attempt) return;
  state.answers = attempt.answers.slice();
  state.submitted = true;
  state.reviewOnly = true;
  state.currentResult = attempt;
  state.index = 0;
  state.submitWarning = false;
  drafts.delete(state.category.id);
  renderAll();
  scrollToRunner();
}

/* Events ----------------------------------------------------------------- */

document.addEventListener("click", (event) => {
  const start = event.target.closest("[data-quiz-start]");
  if (start) {
    event.preventDefault();
    selectCategory(start.dataset.quizStart, { scroll: true });
    return;
  }

  const card = event.target.closest("[data-quiz-category]");
  if (card) {
    selectCategory(card.dataset.quizCategory, { scroll: true });
    return;
  }

  const jump = event.target.closest("[data-quiz-jump]");
  if (jump) {
    goTo(Number(jump.dataset.quizJump));
    return;
  }

  const attempt = event.target.closest("[data-quiz-attempt]");
  if (attempt) {
    reviewAttempt(attempt.dataset.quizAttempt);
    return;
  }

  if (event.target.closest("[data-quiz-review-latest]")) {
    const attempts = getAttempts(state.category.id);
    if (attempts.length) reviewAttempt(attempts[attempts.length - 1].id);
    return;
  }

  if (event.target.closest("[data-quiz-prev]")) {
    goTo(state.index - 1);
    return;
  }

  if (event.target.closest("[data-quiz-next]")) {
    goTo(state.index + 1);
    return;
  }

  if (event.target.closest("[data-quiz-submit]")) {
    submitQuiz();
    return;
  }

  if (event.target.closest("[data-quiz-retry]")) {
    retryQuiz();
    return;
  }

  if (event.target.closest("[data-quiz-review]")) {
    reviewAnswers();
  }
});

document.addEventListener("change", (event) => {
  const input = event.target.closest("[data-quiz-option]");
  if (!input || state.submitted) return;
  state.answers[state.index] = Number(input.dataset.quizOption);
  state.submitWarning = false;
  renderMeter();
  renderPalette();
  renderStatus();
  const warning = $("[data-quiz-warning]");
  if (warning) warning.textContent = "";
});

if (categories.length) {
  selectCategory(categories[0].id);
} else {
  const root = $("[data-quiz-question]");
  if (root) {
    root.appendChild(
      el(
        "p",
        "quiz-empty",
        "The quiz data could not be loaded. Rebuild the page and reload."
      )
    );
  }
}

window.__quizzes = {
  get state() {
    return {
      category: state.category?.id || null,
      index: state.index,
      answers: state.answers.slice(),
      submitted: state.submitted,
      reviewOnly: state.reviewOnly,
    };
  },
  storageKey: STORAGE_KEY,
  categories: categories.map((category) => category.id),
};
