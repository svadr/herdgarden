// Claude Code paints its own text colors from its theme, so on its default (dark) theme its file
// previews and code turn near-white and vanish when the valley goes light at dawn and day. Its
// "auto" theme asks the terminal for its background and follows each change, which Herdr answers.
// So once Herdgarden is installed, a person who never picked a Claude Code theme gets "auto".
// A theme they chose (in Claude Code's settings or its older global config) is never touched.

import { home, appHome, readTextFile, writeTextFile, notify } from "herdr";
import { MOD } from "./core.js";

const DEFAULT = "dark"; // what Claude Code shows when no theme is set

export async function adoptClaudeTheme() {
  const path = `${home()}/.claude/settings.json`;
  const text = await readTextFile(path);
  if (text === null) return "no-settings";
  let settings;
  try { settings = JSON.parse(text); } catch { return "unreadable-settings"; }
  if (!settings || typeof settings !== "object" || Array.isArray(settings)) return "unreadable-settings";
  if (settings.theme !== undefined) return "already-set";
  let legacy = null;
  try { legacy = JSON.parse((await readTextFile(`${home()}/.claude.json`)) ?? "{}")?.theme ?? null; } catch {}
  if (legacy && legacy !== DEFAULT) return "already-set";
  await writeTextFile(path, JSON.stringify({ ...settings, theme: "auto" }, null, 2) + "\n", text);
  notify({
    title: "Claude Code follows the valley",
    body: "Its theme is now Auto, so its text stays readable from dawn to night. /theme in Claude Code changes it.",
    level: "info", timeout: 8000,
  });
  return "set";
}

// Herdgarden also offers Claude Code a status line: "Gardener" (tools/statusline.py), the model as the
// gardener, the folder as a home, meters as plants, and the sky for the time of day. It is opt-in: the
// "Claude Code status line" switch in the Herdgarden panel (hv.config.claudeLine) turns it on or off.
// Turning it on keeps the status line it replaces in data/herdgarden/; turning it off puts that one back.

const SETTINGS = () => `${home()}/.claude/settings.json`;
const KEEP = () => `${appHome()}/data/${MOD}/claude-statusline-before.json`;
const GARDENER = () => ({ type: "command", command: `python3 '${appHome()}/mods/${MOD}/tools/statusline.py'`, padding: 0 });

async function readSettings() {
  const text = await readTextFile(SETTINGS());
  if (text === null) return { text, settings: {} };
  let settings;
  try { settings = JSON.parse(text); } catch { return { text, settings: null }; }
  if (!settings || typeof settings !== "object" || Array.isArray(settings)) return { text, settings: null };
  return { text, settings };
}

const isGardener = (line) => line?.type === "command" && line.command === GARDENER().command;

// Whether Claude Code's status line is the Gardener right now.
export async function claudeStatusLineOn() {
  const { settings } = await readSettings();
  return !!settings && isGardener(settings.statusLine);
}

export async function adoptClaudeStatusLine() {
  const { text, settings } = await readSettings();
  if (!settings) return "unreadable-settings";
  const had = settings.statusLine;
  if (isGardener(had)) return "already-set";
  // Keep the status line it replaces. An older copy is overwritten: it belongs to an earlier turn-on.
  await writeTextFile(KEEP(), JSON.stringify({ statusLine: had ?? null, replaced: new Date().toISOString() }, null, 2) + "\n", await readTextFile(KEEP()));
  await writeTextFile(SETTINGS(), JSON.stringify({ ...settings, statusLine: GARDENER() }, null, 2) + "\n", text);
  notify({
    title: "Claude Code shows the Gardener status line",
    body: "It appears on your next Claude Code message. Turn it off in the Herdgarden panel to get your old one back.",
    level: "info", timeout: 8000,
  });
  return "set";
}

export async function dropClaudeStatusLine() {
  const { text, settings } = await readSettings();
  if (!settings) return "unreadable-settings";
  if (!isGardener(settings.statusLine)) return "not-set"; // the person changed it since: leave theirs alone
  let before = null;
  try { before = JSON.parse((await readTextFile(KEEP())) ?? "null")?.statusLine ?? null; } catch {}
  const next = { ...settings };
  if (before) next.statusLine = before; else delete next.statusLine;
  await writeTextFile(SETTINGS(), JSON.stringify(next, null, 2) + "\n", text);
  notify({
    title: before ? "Claude Code has its old status line back" : "Claude Code's status line is off",
    body: "It changes on your next Claude Code message.",
    level: "info", timeout: 8000,
  });
  return before ? "restored" : "removed";
}
