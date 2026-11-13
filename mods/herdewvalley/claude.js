// Claude Code paints its own text colors from its theme, so on its default (dark) theme its file
// previews and code turn near-white and vanish when the valley goes light at dawn and day. Its
// "auto" theme asks the terminal for its background and follows each change, which Herdr answers.
// So once Herdewvalley is installed, a person who never picked a Claude Code theme gets "auto".
// A theme they chose (in Claude Code's settings or its older global config) is never touched.

import { home, readTextFile, writeTextFile, notify } from "herdr";

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
