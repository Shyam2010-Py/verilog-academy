/* ==========================================================================
   VERILOG ACADEMY — UI primitives
   Theme, navigation, copy, toast, dialogs, reveal and motion controls.
   ========================================================================== */

const THEME_KEY = "va.theme";
const THEMES = new Set(["midnight", "daylight"]);

function getStoredTheme() {
  try {
    const stored = window.localStorage.getItem(THEME_KEY);
    return THEMES.has(stored) ? stored : "midnight";
  } catch {
    return "midnight";
  }
}

function setTheme(theme) {
  const next = THEMES.has(theme) ? theme : "midnight";
  document.documentElement.dataset.theme = next;

  const toggle = document.querySelector("#theme-toggle");
  if (toggle) {
    const isDaylight = next === "daylight";
    toggle.setAttribute("aria-label", isDaylight ? "Switch to Midnight theme" : "Switch to Daylight theme");
    toggle.setAttribute("title", isDaylight ? "Switch to Midnight theme" : "Switch to Daylight theme");
    toggle.setAttribute("aria-pressed", String(isDaylight));
  }

  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) {
    meta.setAttribute("content", next === "daylight" ? "#F4F6FB" : "#05070D");
  }

  try {
    window.localStorage.setItem(THEME_KEY, next);
  } catch {
    /* Storage can be unavailable in private or restricted contexts. */
  }
}

export function initTheme() {
  setTheme(getStoredTheme());

  const toggle = document.querySelector("#theme-toggle");
  if (!toggle) return;

  toggle.addEventListener("click", () => {
    const current = document.documentElement.dataset.theme === "daylight" ? "daylight" : "midnight";
    setTheme(current === "daylight" ? "midnight" : "daylight");
  });
}

export function initHeader() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  const update = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
}

export function initMobileNav() {
  const dialog = document.querySelector("#mobile-nav");
  const openButton = document.querySelector("#menu-toggle");
  const closeButton = document.querySelector("#mobile-nav-close");

  if (!dialog || !openButton) return;

  const open = () => {
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    document.documentElement.classList.add("nav-open");
    openButton.setAttribute("aria-expanded", "true");
  };

  const close = () => {
    if (dialog.open && typeof dialog.close === "function") {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
    document.documentElement.classList.remove("nav-open");
    openButton.setAttribute("aria-expanded", "false");
    openButton.focus({ preventScroll: true });
  };

  openButton.addEventListener("click", open);
  closeButton?.addEventListener("click", close);

  dialog.addEventListener("close", () => {
    document.documentElement.classList.remove("nav-open");
    openButton.setAttribute("aria-expanded", "false");
    openButton.focus({ preventScroll: true });
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) close();
  });

  dialog.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (typeof dialog.close === "function") dialog.close();
    });
  });
}

export function initReveal() {
  const items = Array.from(document.querySelectorAll("[data-reveal]"));
  if (!items.length) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduced || !("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  items.forEach((item) => observer.observe(item));
}

function getToastStack() {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    stack.setAttribute("aria-live", "polite");
    stack.setAttribute("aria-atomic", "true");
    document.body.appendChild(stack);
  }
  return stack;
}

export function toast(message, options = {}) {
  const { type = "info", duration = 2800 } = options;
  const stack = getToastStack();
  const node = document.createElement("div");
  const icon = type === "success" ? "icon-check" : type === "warning" ? "icon-alert" : "icon-info";

  node.className = `toast${type === "success" ? " toast--success" : ""}${type === "warning" ? " toast--warning" : ""}`;
  node.setAttribute("role", "status");
  node.innerHTML = `<svg class="icon" aria-hidden="true"><use href="#${icon}"></use></svg><span></span>`;
  node.querySelector("span").textContent = message;
  stack.appendChild(node);

  const remove = () => {
    node.classList.add("is-leaving");
    window.setTimeout(() => node.remove(), 180);
  };

  window.setTimeout(remove, duration);
  return node;
}

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      /* Permission can be denied; fall through to the selection fallback. */
    }
  }

  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  const copied = document.execCommand("copy");
  area.remove();

  if (!copied) throw new Error("Copy command was rejected.");
}

export function initCopyButtons() {
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy], .copy-btn");
    if (!button) return;

    const targetSelector = button.getAttribute("data-copy-target");
    const target = targetSelector
      ? document.querySelector(targetSelector)
      : button.closest(".code-block")?.querySelector("code") || button.closest("[data-copy-root]")?.querySelector("code");

    if (!target) return;

    try {
      await copyText(target.textContent || "");
      const label = button.querySelector(".copy-label");
      const original = label ? label.textContent : button.textContent;
      if (label) label.textContent = "Copied";
      button.classList.add("is-copied");
      toast("Copied to clipboard.", { type: "success", duration: 1800 });
      window.setTimeout(() => {
        if (label) label.textContent = original;
        button.classList.remove("is-copied");
      }, 1600);
    } catch {
      toast("Could not copy. Select the code manually.", { type: "warning" });
    }
  });
}

export function initDemoActions() {
  document.addEventListener("click", (event) => {
    const toastButton = event.target.closest("[data-demo-toast]");
    if (toastButton) {
      toast(toastButton.getAttribute("data-demo-toast") || "Action complete.", { type: "success" });
    }
  });
}

export function initDialogs() {
  document.addEventListener("click", (event) => {
    const opener = event.target.closest("[data-dialog-open]");
    if (opener) {
      const dialog = document.querySelector(`#${opener.getAttribute("data-dialog-open")}`);
      if (dialog && typeof dialog.showModal === "function") {
        dialog.showModal();
      }
      return;
    }

    const closer = event.target.closest("[data-dialog-close]");
    if (closer) {
      const dialog = closer.closest("dialog");
      if (dialog && typeof dialog.close === "function") dialog.close();
    }
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });
}

export function initWorkbench() {
  const root = document.querySelector("[data-workbench]");
  if (!root) return;

  const tabs = Array.from(root.querySelectorAll('[role="tab"]'));
  const panels = tabs.map((tab) => document.getElementById(tab.getAttribute("aria-controls")));
  if (tabs.length < 2 || panels.some((panel) => !panel)) return;

  function select(index, moveFocus = false) {
    tabs.forEach((tab, i) => {
      const selected = i === index;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[i].hidden = !selected;
    });
    if (moveFocus) tabs[index].focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(index));
    tab.addEventListener("keydown", (event) => {
      let next = null;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      if (next === null) return;
      event.preventDefault();
      select(next, true);
    });
  });
}

export function initMarquee() {
  const strip = document.querySelector(".signal-strip");
  const button = document.querySelector("[data-marquee-toggle]");
  if (!strip || !button) return;

  const icon = button.querySelector("use");

  button.addEventListener("click", () => {
    const paused = strip.classList.toggle("is-paused");
    button.setAttribute("aria-pressed", String(paused));
    button.setAttribute("aria-label", paused ? "Play topic ticker" : "Pause topic ticker");
    if (icon) icon.setAttribute("href", paused ? "#icon-play" : "#icon-pause");
  });
}

export function initMotionDemo() {
  const button = document.querySelector("[data-toggle-motion]");
  const demo = document.querySelector("[data-motion-demo]");
  if (!button || !demo) return;

  button.addEventListener("click", () => {
    const paused = demo.classList.toggle("is-paused");
    button.textContent = paused ? "Resume signal" : "Pause signal";
    button.setAttribute("aria-pressed", String(paused));
  });
}

export function initApp() {
  initTheme();
  initHeader();
  initMobileNav();
  initReveal();
  initCopyButtons();
  initDialogs();
  initDemoActions();
  initMarquee();
  initWorkbench();
  initMotionDemo();
}
