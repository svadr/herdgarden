// Herdgarden: what every part of the layout agrees on. The person's choices (shared "hv.config"),
// the season and time of day they lead to, the colors for each palette, and which villager or home
// stands for which agent or space. No drawing here.

import { shared, setShared, keys, window as appWindow } from "herdr";

export const MOD = "herdgarden";
export const ART = `mods/${MOD}/art`;
export const FONT = "Pixelify Sans";
export const PALETTES = ["paper", "sand", "blossom"];
export const SEASONS = ["spring", "summer", "autumn", "winter"];
export const TODS = ["dawn", "day", "night"];
export const KINDS = ["farmhouse", "cabin", "barn", "greenhouse"];

const DEFAULTS = { palette: "paper", seasonAuto: true, season: "summer", todAuto: true, sunMode: "sun", tod: "day", strength: 65, blur: 1.5, motion: true };

export function config() {
  return { ...DEFAULTS, ...(shared("hv.config") ?? {}) };
}

export function setConfig(patch) {
  setShared("hv.config", { ...config(), ...patch });
}

// ---- sunrise and sunset, from a rough place for the time zone (no location is asked for) ----
const ZONES = {
  "America/Mazatlan": [23.2, -106.4], "America/Phoenix": [33.4, -112.1], "America/Hermosillo": [29.1, -110.9], "America/Los_Angeles": [34.1, -118.2],
  "America/Tijuana": [32.5, -117.0], "America/Denver": [39.7, -105.0], "America/Chicago": [41.9, -87.6], "America/Mexico_City": [19.4, -99.1],
  "America/Monterrey": [25.7, -100.3], "America/New_York": [40.7, -74.0], "America/Toronto": [43.7, -79.4], "America/Bogota": [4.7, -74.1],
  "America/Lima": [-12.0, -77.0], "America/Sao_Paulo": [-23.5, -46.6], "America/Argentina/Buenos_Aires": [-34.6, -58.4], "America/Santiago": [-33.4, -70.7],
  "Europe/London": [51.5, -0.1], "Europe/Madrid": [40.4, -3.7], "Europe/Paris": [48.9, 2.3], "Europe/Berlin": [52.5, 13.4], "Europe/Rome": [41.9, 12.5],
  "Europe/Amsterdam": [52.4, 4.9], "Europe/Stockholm": [59.3, 18.1], "Europe/Istanbul": [41.0, 29.0], "Africa/Lagos": [6.5, 3.4], "Africa/Johannesburg": [-26.2, 28.0],
  "Asia/Dubai": [25.2, 55.3], "Asia/Kolkata": [28.6, 77.2], "Asia/Singapore": [1.35, 103.8], "Asia/Shanghai": [31.2, 121.5], "Asia/Tokyo": [35.7, 139.7],
  "Asia/Seoul": [37.6, 127.0], "Australia/Sydney": [-33.9, 151.2], "Australia/Melbourne": [-37.8, 145.0], "Pacific/Auckland": [-36.8, 174.8],
};

// The time zone's name, set once by the status bar (it asks the system); until then the clock's offset is used.
let zone = null;
export function setZone(name) { zone = name; }

function place(d) {
  const off = -d.getTimezoneOffset() / 60;
  return ZONES[zone ?? shared("hv.zone")] ?? [35, off * 15];
}

export function sunTimes(d) {
  const off = -d.getTimezoneOffset() / 60, pos = place(d), rad = Math.PI / 180;
  const n = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 864e5);
  const decl = -23.44 * Math.cos(2 * Math.PI / 365 * (n + 10));
  const b = 2 * Math.PI * (n - 81) / 364, eot = 9.87 * Math.sin(2 * b) - 7.53 * Math.cos(b) - 1.5 * Math.sin(b);
  const x = (Math.sin(-0.833 * rad) - Math.sin(pos[0] * rad) * Math.sin(decl * rad)) / (Math.cos(pos[0] * rad) * Math.cos(decl * rad));
  const half = Math.acos(Math.max(-1, Math.min(1, x))) / rad / 15;
  const noon = 12 + (off * 15 - pos[1]) / 15 - eot / 60;
  return { rise: noon - half, set: noon + half };
}

// Dawn runs from half an hour before sunrise to an hour and a half after it; night starts at sunset.
export function phases(d, sunMode) {
  if (sunMode === "hours") return [5.5, 8, 18];
  const s = sunTimes(d);
  return [s.rise - 0.5, s.rise + 1.5, s.set];
}

export function todOf(d, sunMode) {
  const now = d.getHours() + d.getMinutes() / 60, p = phases(d, sunMode);
  return now >= p[0] && now < p[1] ? "dawn" : now >= p[1] && now < p[2] ? "day" : "night";
}

// Seasons start on 20 March, 21 June, 22 September and 21 December, swapped south of the equator.
export function seasonOf(d) {
  const md = (d.getMonth() + 1) * 100 + d.getDate();
  const k = md >= 320 && md < 621 ? 0 : md >= 621 && md < 922 ? 1 : md >= 922 && md < 1221 ? 2 : 3;
  return SEASONS[(k + (place(d)[0] < 0 ? 2 : 0)) % 4];
}

export function clockText(h) {
  const m = Math.round(h * 60), hh = Math.floor(m / 60) % 24, mm = m % 60;
  return `${hh % 12 || 12}:${mm < 10 ? "0" : ""}${mm} ${hh >= 12 ? "pm" : "am"}`;
}

// What the window wears right now.
export function look(d = new Date()) {
  const c = config();
  return {
    palette: PALETTES.includes(c.palette) ? c.palette : "paper",
    tod: c.todAuto ? todOf(d, c.sunMode) : (TODS.includes(c.tod) ? c.tod : "day"),
    season: c.seasonAuto ? seasonOf(d) : (SEASONS.includes(c.season) ? c.season : "summer"),
    strength: c.strength, blur: c.blur, motion: c.motion !== false,
  };
}

// ---- colors ----
// canvas, chrome, line, text, muted, dim, accent, working, blocked, done, blue, magenta, cyan
const INK = {
  "paper-dawn": ["#fbf8f4", "#f5f1ec", "#e3ddd6", "#2f3432", "#676b68", "#a3a39d", "#bc4e34", "#467552", "#bc4e34", "#8a6714", "#3a6f8f", "#7d5a96", "#2f7f78"],
  "paper-day": ["#fbfbf7", "#f4f5ef", "#dfe2d9", "#2b3531", "#66726b", "#9aa39c", "#bc4e34", "#467552", "#bc4e34", "#8a6714", "#3a6f8f", "#7d5a96", "#2f7f78"],
  "paper-night": ["#121816", "#0e1312", "#25302b", "#dde5df", "#8e9b94", "#5f6c66", "#e8866a", "#8cc29a", "#e8866a", "#e3be6a", "#8cc0dc", "#c3a6dc", "#8fd0c8"],
  "sand-dawn": ["#fcf2e8", "#f7e7d9", "#ecd6c3", "#3c2c26", "#7d6253", "#bfa391", "#b34a30", "#4f7538", "#b4432f", "#8f6a16", "#3f6f8a", "#8a4f7a", "#2f7f78"],
  "sand-day": ["#fbf6ee", "#f4ecdf", "#e6dac8", "#3a2e25", "#7a6853", "#b3a28e", "#ad5028", "#4f7538", "#b4432f", "#8f6a16", "#3f6f8a", "#8a4f7a", "#2f7f78"],
  "sand-night": ["#1a1612", "#15110e", "#332b23", "#efe5d6", "#a39480", "#6f6252", "#ea9a6e", "#a9c785", "#ee8468", "#e8c273", "#9cc4d8", "#d3a6c9", "#8fd0c8"],
  "blossom-dawn": ["#fef3f1", "#fbe6e4", "#f0d5d3", "#43302f", "#876260", "#c9a5a3", "#b8445d", "#3f775a", "#b93a3a", "#8c6620", "#4a6f96", "#8f4a8c", "#2f7f78"],
  "blossom-day": ["#fdf7f4", "#f8ece7", "#ecdcd5", "#40302e", "#836660", "#bda49d", "#b8445d", "#3f775a", "#b93a3a", "#8c6620", "#4a6f96", "#8f4a8c", "#2f7f78"],
  "blossom-night": ["#18131a", "#130f15", "#2f2633", "#f1e6ea", "#a8939f", "#6e5d69", "#f08fa4", "#9fd3b0", "#f27a8a", "#efc57c", "#a5bfe6", "#d9a9e0", "#8fd0c8"],
};

export function rgb(hex) {
  const h = hex.replace("#", "");
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

export function mix(a, b, t) {
  const x = rgb(a), y = rgb(b);
  return "#" + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, "0")).join("");
}

// Every theme color for one palette and time of day, by Herdr's names.
export function colors(palette, tod) {
  const [canvas, chrome, line, fg, muted, dim, accent, working, blocked, done, blue, magenta, cyan] = INK[`${palette}-${tod}`] ?? INK["paper-day"];
  const dark = tod === "night";
  const lift = (c) => (dark ? mix(c, "#ffffff", 0.22) : mix(c, fg, 0.22));
  return {
    background: canvas, canvas, chrome, surface: canvas, popover: dark ? mix(canvas, fg, 0.05) : canvas,
    raised: mix(canvas, fg, 0.045), hover: mix(chrome, fg, 0.06), selected: mix(chrome, fg, 0.085),
    border: line, input: mix(line, fg, 0.16), foreground: fg, muted, dim, accent, accent_foreground: canvas,
    solid: fg, solid_foreground: canvas, selection: mix(canvas, accent, 0.24),
    working, blocked, done, idle: dim, unknown: dim,
    ansi0: dark ? mix(canvas, fg, 0.2) : fg, ansi1: blocked, ansi2: working, ansi3: done, ansi4: blue, ansi5: magenta, ansi6: cyan,
    ansi7: dark ? mix(fg, canvas, 0.14) : muted,
    ansi8: dark ? mix(dim, fg, 0.25) : mix(muted, canvas, 0.25), ansi9: lift(blocked), ansi10: lift(working), ansi11: lift(done),
    ansi12: lift(blue), ansi13: lift(magenta), ansi14: lift(cyan), ansi15: dark ? "#ffffff" : mix(fg, "#000000", 0.25),
  };
}

// ---- villagers and homes ----
const VILLAGERS = ["farmer", "tinker", "gardener", "elder"];

function hash(text) {
  let h = 0;
  for (const ch of String(text ?? "")) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return h;
}

// Which villager an agent program is. The four known ones are fixed; any other gets one by its name.
export function villager(program, app) {
  const id = `${program?.key ?? ""} ${app ?? ""} ${program?.name ?? ""}`.toLowerCase();
  if (id.includes("claude")) return "farmer";
  if (id.includes("codex")) return "tinker";
  if (id.includes("opencode")) return "gardener";
  if (id.includes("gemini")) return "elder";
  return VILLAGERS[hash(program?.key ?? app ?? id) % 4];
}

export const villagerArt = (who, season, part) => `${ART}/villager/${who}-${season}${part ? "-" + part : ""}`;

// Each space keeps the home it got when it was first seen (shared "hv.homes"); new ones take the kind used least.
export function homes(spaceList) {
  const stored = shared("hv.homes") ?? {};
  const ids = new Set(spaceList.map((s) => s.id));
  const kept = Object.fromEntries(Object.entries(stored).filter(([id]) => ids.has(id)));
  let changed = Object.keys(kept).length !== Object.keys(stored).length;
  for (const s of spaceList) {
    if (kept[s.id]) continue;
    const uses = (k) => Object.values(kept).filter((v) => v === k).length;
    kept[s.id] = KINDS.reduce((best, k) => (uses(k) < uses(best) ? k : best));
    changed = true;
  }
  return { map: kept, changed };
}

export const homeOf = (id) => (shared("hv.homes") ?? {})[id] ?? KINDS[hash(id) % 4];

// A key binding as people read it ("⌘N"), or "" when the command has no key.
export function keyHint(action) {
  const mac = appWindow()?.platform === "macos";
  const mod = { cmd: mac ? "⌘" : "Ctrl+", ctrl: mac ? "⌃" : "Ctrl+", shift: mac ? "⇧" : "Shift+", alt: mac ? "⌥" : "Alt+", option: mac ? "⌥" : "Alt+" };
  const b = keys().find((k) => k.section === "global" && k.action === action);
  if (!b) return "";
  const parts = b.keys.endsWith("--") ? [...b.keys.slice(0, -2).split("-"), "-"] : b.keys.split("-");
  return parts.map((p) => mod[p.toLowerCase()] ?? p.toUpperCase()).join("");
}
