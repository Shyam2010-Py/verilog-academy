/* ==========================================================================
   VERILOG ACADEMY — Progress model
   Versioned, local-only completion records for EC-405 and EC-410.

   Storage key : va.progress
   Schema      : verilog-academy.progress
   Version     : 1

   Stored shape
   ------------
   {
     "schema": "verilog-academy.progress",
     "version": 1,
     "createdAt": "2026-11-24T10:00:00.000Z",
     "updatedAt": "2026-11-24T10:20:00.000Z",
     "theory": {
       "vlsi-design-flow": { "completedAt": "2026-11-24T10:20:00.000Z" }
     },
     "practical": {
       "experiment-01": { "completedAt": "2026-11-24T10:22:00.000Z" }
     }
   }

   Rules
   -----
   - Reading never writes. A missing, malformed or outdated record is not
     silently replaced during dashboard initialisation.
   - Theory topics and practical experiments are stored separately.
   - Timestamps are ISO-8601 strings, or null for migrated records whose
     original completion date is unknown.
   - Totals and percentages are derived from curriculum metadata, never from
     hard-coded dashboard values.
   ========================================================================== */

export const STORAGE_KEY = "va.progress";
export const SCHEMA_ID = "verilog-academy.progress";
export const SCHEMA_VERSION = 1;

const KINDS = new Set(["theory", "practical"]);
const MAX_RECORDS = 500;
const MAX_IMPORT_BYTES = 1_000_000;

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function normalizeIso(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  const time = Date.parse(value);
  if (Number.isNaN(time)) return null;
  return new Date(time).toISOString();
}

function nowIso(now = new Date()) {
  const date = now instanceof Date ? now : new Date(now);
  return Number.isNaN(date.getTime()) ? new Date().toISOString() : date.toISOString();
}

function failure(error) {
  return { ok: false, error };
}

function emptyBucket() {
  return {};
}

export function createEmptyProgress(now = new Date()) {
  const timestamp = nowIso(now);
  return {
    schema: SCHEMA_ID,
    version: SCHEMA_VERSION,
    createdAt: timestamp,
    updatedAt: timestamp,
    theory: emptyBucket(),
    practical: emptyBucket(),
  };
}

function migrateLegacy(raw) {
  const theorySource = raw.theory ?? raw.completedTopics;
  const practicalSource = raw.practical ?? raw.completedExperiments;
  if (theorySource === undefined && practicalSource === undefined) return null;

  const fallbackStamp =
    normalizeIso(raw.updatedAt) || normalizeIso(raw.createdAt) || null;

  const toBucket = (value) => {
    if (Array.isArray(value)) {
      const bucket = {};
      value.forEach((id) => {
        if (typeof id === "string" && id) bucket[id] = { completedAt: fallbackStamp };
      });
      return bucket;
    }
    return isPlainObject(value) ? value : {};
  };

  return {
    schema: SCHEMA_ID,
    version: SCHEMA_VERSION,
    createdAt: normalizeIso(raw.createdAt) || fallbackStamp,
    updatedAt: normalizeIso(raw.updatedAt) || fallbackStamp,
    theory: toBucket(theorySource),
    practical: toBucket(practicalSource),
  };
}

function readBucket(source, kind, { strict, allowedIds, warnings }) {
  if (!isPlainObject(source)) {
    return failure(`The ${kind} section must be a JSON object.`);
  }

  const entries = Object.entries(source);
  if (entries.length > MAX_RECORDS) {
    return failure(`The ${kind} section contains too many records.`);
  }

  const bucket = {};
  const label = kind === "theory" ? "theory topic" : "practical experiment";

  for (const [id, value] of entries) {
    if (!id) {
      if (strict) return failure(`A ${label} record has an empty identifier.`);
      continue;
    }

    if (allowedIds && !allowedIds.has(id)) {
      if (strict) return failure(`Unknown ${label} identifier: "${id}".`);
      // Keep unknown identifiers when reading local data. A future release may
      // understand them, and dropping them would destroy valid user records.
      bucket[id] = isPlainObject(value) ? { ...value } : value;
      continue;
    }

    let entry = null;
    if (isPlainObject(value) && (value.completedAt === null || value.completedAt === undefined)) {
      entry = { completedAt: null };
    } else if (isPlainObject(value)) {
      const stamp = normalizeIso(value.completedAt);
      if (stamp) entry = { completedAt: stamp };
    } else if (!strict && typeof value === "string") {
      const stamp = normalizeIso(value);
      if (stamp) entry = { completedAt: stamp };
    }

    if (!entry) {
      if (strict) return failure(`Invalid completion record for ${label} "${id}".`);
      warnings.push(`Ignored an unreadable ${label} record ("${id}").`);
      continue;
    }

    bucket[id] = entry;
  }

  return { ok: true, bucket };
}

function normalizeStored(raw, { strict = false, allowed = null, now = new Date() } = {}) {
  if (!isPlainObject(raw)) {
    return failure("Progress data must be a JSON object.");
  }

  let source = raw;
  let migrated = false;
  const version = raw.version;

  if (version === 0 || version === undefined || version === null) {
    const legacy = migrateLegacy(raw);
    if (!legacy) return failure("Progress data is not in a recognised format.");
    source = legacy;
    migrated = true;
  } else if (version !== SCHEMA_VERSION) {
    if (typeof version === "number" && version > SCHEMA_VERSION) {
      return failure(
        `Progress version ${version} is newer than this dashboard supports (version ${SCHEMA_VERSION}).`
      );
    }
    return failure(`Unsupported progress version: ${String(version)}.`);
  }

  if (source.schema !== undefined && source.schema !== SCHEMA_ID) {
    return failure("This file is not a Verilog Academy progress file.");
  }
  if (strict && source.schema !== SCHEMA_ID) {
    return failure("This file is not a Verilog Academy progress backup.");
  }

  if (strict && (!(allowed?.theory instanceof Set) || !(allowed?.practical instanceof Set))) {
    return failure("Curriculum identifiers are unavailable, so the backup cannot be validated.");
  }

  if (!isPlainObject(source.theory) || !isPlainObject(source.practical)) {
    return failure("Progress data is missing its theory or practical section.");
  }

  if (source.createdAt !== undefined && source.createdAt !== null && !normalizeIso(source.createdAt)) {
    return failure("The progress createdAt value is not a valid date.");
  }
  if (source.updatedAt !== undefined && source.updatedAt !== null && !normalizeIso(source.updatedAt)) {
    return failure("The progress updatedAt value is not a valid date.");
  }
  if (strict && (!normalizeIso(source.createdAt) || !normalizeIso(source.updatedAt))) {
    return failure("The backup is missing a valid createdAt or updatedAt timestamp.");
  }

  const warnings = [];
  const theory = readBucket(source.theory, "theory", {
    strict,
    allowedIds: allowed?.theory,
    warnings,
  });
  if (!theory.ok) return theory;

  const practical = readBucket(source.practical, "practical", {
    strict,
    allowedIds: allowed?.practical,
    warnings,
  });
  if (!practical.ok) return practical;

  const timestamp = nowIso(now);

  return {
    ok: true,
    migrated,
    warnings,
    progress: {
      schema: SCHEMA_ID,
      version: SCHEMA_VERSION,
      createdAt: normalizeIso(source.createdAt) || timestamp,
      updatedAt: normalizeIso(source.updatedAt) || timestamp,
      theory: theory.bucket,
      practical: practical.bucket,
    },
  };
}

/**
 * Read local progress without writing anything.
 * status: empty | valid | migrated | repaired | invalid | unavailable
 */
export function readProgress() {
  let rawText;
  try {
    rawText = window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return {
      progress: createEmptyProgress(),
      status: "unavailable",
      warnings: [],
      error: "Browser storage is unavailable. Progress cannot be saved in this context.",
    };
  }

  if (rawText === null) {
    return { progress: createEmptyProgress(), status: "empty", warnings: [], error: null };
  }

  let raw;
  try {
    raw = JSON.parse(rawText);
  } catch {
    return {
      progress: createEmptyProgress(),
      status: "invalid",
      warnings: [],
      error: "Saved progress is not valid JSON. The existing record was left untouched.",
    };
  }

  const normalized = normalizeStored(raw, { strict: false, now: new Date() });
  if (!normalized.ok) {
    return {
      progress: createEmptyProgress(),
      status: "invalid",
      warnings: [],
      error: `${normalized.error} The existing record was left untouched.`,
    };
  }

  const status = normalized.migrated
    ? "migrated"
    : normalized.warnings.length
      ? "repaired"
      : "valid";

  return {
    progress: normalized.progress,
    status,
    warnings: normalized.warnings,
    error: null,
  };
}

function cleanBucket(bucket) {
  const clean = {};
  if (!isPlainObject(bucket)) return clean;

  let count = 0;
  for (const [id, value] of Object.entries(bucket)) {
    if (count >= MAX_RECORDS) break;
    if (!id || !isPlainObject(value)) continue;
    if (value.completedAt === null) {
      clean[id] = { completedAt: null };
      count += 1;
      continue;
    }
    const stamp = normalizeIso(value.completedAt);
    if (stamp) {
      clean[id] = { completedAt: stamp };
      count += 1;
    }
  }

  return clean;
}

export function cleanProgress(progress, now = new Date()) {
  const timestamp = nowIso(now);
  return {
    schema: SCHEMA_ID,
    version: SCHEMA_VERSION,
    createdAt: normalizeIso(progress?.createdAt) || timestamp,
    updatedAt: normalizeIso(progress?.updatedAt) || timestamp,
    theory: cleanBucket(progress?.theory),
    practical: cleanBucket(progress?.practical),
  };
}

/** Persist a full progress object. Returns { ok, progress?, error? }. */
export function writeProgress(progress, now = new Date()) {
  const clean = cleanProgress(progress, now);
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(clean));
    return { ok: true, progress: clean };
  } catch {
    return failure("Browser storage is unavailable. Progress was not saved.");
  }
}

export function isComplete(progress, kind, id) {
  if (!KINDS.has(kind) || !id) return false;
  return Boolean(progress?.[kind]?.[id]);
}

/**
 * Mark or reverse one item.
 * Returns { ok, changed, progress?, error? }.
 */
export function setItemCompletion(kind, id, completed, { allowedIds = null, now = new Date() } = {}) {
  if (!KINDS.has(kind)) return failure("Unknown progress category.");
  if (typeof id !== "string" || !id) return failure("A progress identifier is required.");
  if (allowedIds && !allowedIds.has(id)) {
    return failure(`Unknown ${kind === "theory" ? "theory topic" : "practical experiment"} identifier.`);
  }

  const current = readProgress();
  if (current.status === "invalid") {
    return failure("Saved progress is unreadable. Import a valid backup or reset the stored data first.");
  }
  if (current.status === "unavailable") {
    return failure(current.error || "Browser storage is unavailable.");
  }

  const next = {
    ...current.progress,
    theory: { ...current.progress.theory },
    practical: { ...current.progress.practical },
  };

  if (completed) {
    if (next[kind][id]) {
      return { ok: true, changed: false, progress: current.progress };
    }
    next[kind][id] = { completedAt: nowIso(now) };
  } else {
    if (!next[kind][id]) {
      return { ok: true, changed: false, progress: current.progress };
    }
    delete next[kind][id];
  }

  next.updatedAt = nowIso(now);
  const written = writeProgress(next, now);
  if (!written.ok) return written;

  return { ok: true, changed: true, progress: written.progress };
}

export function markComplete(kind, id, options = {}) {
  return setItemCompletion(kind, id, true, options);
}

export function markIncomplete(kind, id, options = {}) {
  return setItemCompletion(kind, id, false, options);
}

export function resetProgress() {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
    return { ok: true };
  } catch {
    return failure("Browser storage is unavailable. Progress was not reset.");
  }
}

export function exportProgress(progress, now = new Date()) {
  return `${JSON.stringify(cleanProgress(progress, now), null, 2)}\n`;
}

/**
 * Validate a backup strictly against the current schema and curriculum.
 * Returns { ok, progress?, summary?, error? }.
 */
export function parseBackup(text, { allowedTheoryIds, allowedPracticalIds } = {}) {
  if (typeof text !== "string" || !text.trim()) {
    return failure("The selected file is empty.");
  }
  if (text.length > MAX_IMPORT_BYTES) {
    return failure("The selected file is too large to be a progress backup.");
  }

  let raw;
  try {
    raw = JSON.parse(text);
  } catch {
    return failure("The selected file is not valid JSON.");
  }

  if (!isPlainObject(raw) || raw.schema !== SCHEMA_ID) {
    return failure("This file is not a Verilog Academy progress backup.");
  }

  if (raw.version !== SCHEMA_VERSION) {
    if (typeof raw.version === "number" && raw.version > SCHEMA_VERSION) {
      return failure(
        `This backup uses version ${raw.version}, but this dashboard supports version ${SCHEMA_VERSION}.`
      );
    }
    return failure(
      `This backup uses an unsupported version (${String(raw.version)}). Export a fresh backup from this dashboard.`
    );
  }

  if (!isPlainObject(raw.theory) || !isPlainObject(raw.practical)) {
    return failure("The backup is missing its theory or practical section.");
  }

  const normalized = normalizeStored(raw, {
    strict: true,
    allowed: { theory: allowedTheoryIds, practical: allowedPracticalIds },
    now: new Date(),
  });
  if (!normalized.ok) return normalized;

  const theory = Object.keys(normalized.progress.theory).length;
  const practical = Object.keys(normalized.progress.practical).length;

  return {
    ok: true,
    progress: normalized.progress,
    summary: {
      theory,
      practical,
      total: theory + practical,
    },
    error: null,
  };
}

/**
 * Turn the authoritative curriculum JSON into a flat catalogue used by the
 * dashboard and by lesson and lab pages.
 */
export function buildCatalog(curriculum) {
  const courses = Array.isArray(curriculum?.courses) ? curriculum.courses : [];
  const ec405 = courses.find((course) => course.id === "ec405");
  const ec410 = courses.find((course) => course.id === "ec410");

  if (!ec405 || !ec410) {
    throw new Error("Curriculum metadata is missing EC-405 or EC-410.");
  }

  const units = (ec405.units || [])
    .filter((unit) => unit.status === "available")
    .map((unit) => {
      const topics = (unit.topics || []).map((topic) => ({
        kind: "theory",
        id: topic.id,
        number: topic.number,
        title: topic.title,
        slug: topic.slug,
        unitId: unit.id,
        unitNumber: unit.number,
        unitTitle: unit.title,
      }));
      return {
        id: unit.id,
        number: unit.number,
        title: unit.title,
        periods: unit.periods,
        total: topics.length,
        topics,
      };
    });

  const theoryItems = units.flatMap((unit) => unit.topics);

  const practicalItems = (ec410.experiments || [])
    .filter((experiment) => experiment.status === "available")
    .map((experiment) => ({
      kind: "practical",
      id: experiment.id,
      number: experiment.number,
      title: experiment.title,
      slug: experiment.slug,
    }));

  const lockedUnits = (ec405.units || [])
    .filter((unit) => unit.status === "locked")
    .map((unit) => ({
      id: unit.id,
      number: unit.number,
      title: unit.title,
      periods: unit.periods,
    }));

  const lockedExperiments = (ec410.experiments || []).filter(
    (experiment) => experiment.status === "locked"
  );

  return {
    courses: {
      theory: {
        code: ec405.code,
        title: ec405.title,
        periods: ec405.totalPeriods,
      },
      practical: {
        code: ec410.code,
        title: ec410.title,
        periods: ec410.totalPeriods,
      },
    },
    units,
    theoryItems,
    practicalItems,
    lockedUnits,
    lockedExperiments,
    totals: {
      theory: theoryItems.length,
      practical: practicalItems.length,
      overall: theoryItems.length + practicalItems.length,
    },
  };
}

function percentOf(completed, total) {
  if (!total) return 0;
  return Math.round((completed / total) * 100);
}

/** Derive every dashboard number from stored records and curriculum metadata. */
export function summarize(progress, catalog) {
  const theoryCompleted = catalog.theoryItems.filter((item) =>
    isComplete(progress, "theory", item.id)
  ).length;
  const practicalCompleted = catalog.practicalItems.filter((item) =>
    isComplete(progress, "practical", item.id)
  ).length;

  const units = catalog.units.map((unit) => {
    const completed = unit.topics.filter((topic) =>
      isComplete(progress, "theory", topic.id)
    ).length;
    return {
      id: unit.id,
      number: unit.number,
      title: unit.title,
      completed,
      total: unit.total,
      percent: percentOf(completed, unit.total),
    };
  });

  const theoryTotal = catalog.totals.theory;
  const practicalTotal = catalog.totals.practical;
  const overallTotal = catalog.totals.overall;
  const overallCompleted = theoryCompleted + practicalCompleted;

  return {
    theory: {
      completed: theoryCompleted,
      total: theoryTotal,
      percent: percentOf(theoryCompleted, theoryTotal),
    },
    practical: {
      completed: practicalCompleted,
      total: practicalTotal,
      percent: percentOf(practicalCompleted, practicalTotal),
    },
    overall: {
      completed: overallCompleted,
      total: overallTotal,
      percent: percentOf(overallCompleted, overallTotal),
    },
    units,
  };
}

/** Most recently completed items, newest first. Null timestamps sort last. */
export function getRecentActivity(progress, catalog, limit = 5) {
  const items = [...catalog.theoryItems, ...catalog.practicalItems];
  const completed = items
    .map((item) => {
      const entry = progress?.[item.kind]?.[item.id];
      if (!entry) return null;
      return {
        ...item,
        completedAt: entry.completedAt || null,
        time: entry.completedAt ? Date.parse(entry.completedAt) : Number.NEGATIVE_INFINITY,
      };
    })
    .filter(Boolean);

  completed.sort((a, b) => b.time - a.time);
  return completed.slice(0, limit);
}

/** First unfinished item in a track, in curriculum order. */
export function getNextItem(progress, catalog, kind) {
  const items = kind === "practical" ? catalog.practicalItems : catalog.theoryItems;
  return items.find((item) => !isComplete(progress, kind, item.id)) || null;
}

/** Load the authoritative curriculum used by lessons and laboratory pages. */
let curriculumPromise = null;

export function loadCurriculum() {
  if (!curriculumPromise) {
    const url = new URL("../data/curriculum.json", import.meta.url);
    curriculumPromise = fetch(url, { cache: "no-cache" }).then((response) => {
      if (!response.ok) throw new Error(`Curriculum request failed (HTTP ${response.status}).`);
      return response.json();
    });
  }
  return curriculumPromise;
}
