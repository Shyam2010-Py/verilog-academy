/* ==========================================================================
   VERILOG ACADEMY — Application entry
   ========================================================================== */

import { initApp } from "./ui.js";

window.__vaReady = true;

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp, { once: true });
} else {
  initApp();
}
