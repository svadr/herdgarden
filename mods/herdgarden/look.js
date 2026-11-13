// Keeps the layout wearing the right look: the palette's colors for the time of day, and the valley
// picture behind the panes for the season. Herdr can only show a picture as a node's background, scaled
// to cover it, so the picture is drawn at exactly the node's size (the valley in its bottom-right corner,
// faded and blurred as the person chose) by tools/bg.py, a small Python script, and kept in bg/.
// Drawing it in the mod itself is too slow for Herdr's script runtime. Without python3 the colors still
// follow the clock; only the picture is missing, and shared "hv.error" says why.

import * as fs from "fs/promises";
import { layout, run, appHome, settings, spaces, exec, shared, setShared, readTextFile, writeTextFile } from "herdr";
import { MOD, ART, look, colors } from "./core.js";

const STAGE = "stage"; // the stack that holds the panes (and the empty state)
const THEME = `themes/${MOD}.json`; // the layout's own theme file
let applied = null; // the key of the look the layout wears
let themed = null; // the theme text known to be in the theme file
let working = false;
let again = false;

// The layout's `colors` repaint the panels and the 16 terminal colors, but a terminal's plain text
// (the default foreground) and its cursor come from the theme file alone. So the file follows the look
// too: left as the day palette, night shows dark text on a dark window.
const PANEL = ["canvas", "chrome", "surface", "popover", "raised", "hover", "selected", "border", "input", "muted", "dim",
  "accent", "accent_foreground", "solid", "solid_foreground", "working", "blocked", "done", "idle", "unknown"];

export function themeText(c) {
  return JSON.stringify({
    background: c.background, foreground: c.foreground, selection: c.selection, cursor: c.foreground,
    ansi: Array.from({ length: 16 }, (_, i) => c[`ansi${i}`]),
    colors: Object.fromEntries(PANEL.map((name) => [name, c[name]])),
  }, null, 2) + "\n";
}

async function wearTheme(want) {
  const text = themeText(want);
  if (themed === text) return;
  const path = `${appHome()}/${THEME}`;
  const have = await readTextFile(path);
  if (have !== text) await writeTextFile(path, text, have);
  themed = text;
}

export function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// The size of the panes' area in layout px, from the window's size (read in a render).
export function stageSize(viewport) {
  const root = layout(), zoom = settings()?.zoom || 1;
  const sidebar = find(root, "sidebar"), panel = find(root, "panel");
  const w = viewport.width / zoom - (sidebar?.hidden ? 0 : (sidebar?.size?.px ?? 268) + 1) - 16 - (panel && !panel.hidden ? (panel.size?.px ?? 368) + 8 : 0);
  const h = viewport.height / zoom - 42 - 28 - 16;
  return { w: Math.max(240, Math.round(w)), h: Math.max(160, Math.round(h)) };
}

// Brings the layout up to date. Call it from a timer or a task, never from a render.
// `size`: the panes' area in layout px ({w, h}); without one the last size is kept.
let lastSize = null;
export async function syncLook(size) {
  if (size) lastSize = size;
  if (working) { again = true; return; }
  working = true;
  try {
    do {
      again = false;
      await once();
    } while (again);
  } catch (e) {
    // The last failure, readable in shared.json.
    setShared("hv.error", `${new Date().toISOString()} ${e?.message ?? e}`);
    working = false;
    return;
  }
  working = false;
  if (shared("hv.error")) setShared("hv.error", null);
}

async function once() {
  const L = look();
  const want = colors(L.palette, L.tod);
  const size = lastSize;
  const key = [L.palette, L.tod, L.season, L.strength, L.blur, size ? `${size.w}x${size.h}` : "none"].join("-");
  const hasSpaces = spaces().length > 0;
  const now = layout();
  const stage = find(now, STAGE);
  if (!stage) return; // another layout is showing
  const child = hasSpaces ? "main" : "empty";
  const file = size ? `mods/${MOD}/bg/${key}.png` : null;
  const same = key === applied && JSON.stringify(now.colors ?? {}) === JSON.stringify(want)
    && (!file || stage.background?.image === file);
  if (!same) {
    if (file && stage.background?.image !== file) {
      const dir = `${appHome()}/mods/${MOD}/bg`;
      if (!(await fs.exists(`${dir}/${key}.png`))) {
        const r = await exec("python3", [`${appHome()}/mods/${MOD}/tools/bg.py`, `${appHome()}/${ART}/scene/${L.palette}-${L.tod}-${L.season}.bin`,
          `${dir}/${key}.png`, String(size.w), String(size.h), want.canvas, String(L.strength), String(L.blur)], { timeout: 20000 });
        if (r.code !== 0) throw new Error(`bg.py: ${(r.stderr || r.stdout).trim().slice(-300)}`);
      }
      // Older pictures go, except the one the layout is still showing while this one loads.
      const keep = new Set([`${key}.png`, (stage.background?.image ?? "").split("/").pop()]);
      for (const name of await fs.readdir(dir)) if (name.endsWith(".png") && !keep.has(name)) { try { await fs.unlink(`${dir}/${name}`); } catch {} }
    }
    await wearTheme(want);
    // Read and write in the same tick, so a click made in between isn't lost.
    const next = JSON.parse(JSON.stringify(layout()));
    const st = find(next, STAGE);
    if (!st) return;
    next.colors = want;
    if (file) st.background = { image: file, fit: "cover" };
    run("layout.set", { layout: next });
    applied = key;
  } else {
    await wearTheme(want);
  }
  if (stage.active !== child) run("layout.select", { stack: STAGE, child });
}
