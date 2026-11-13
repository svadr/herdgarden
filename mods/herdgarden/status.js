// The status bar: Herdr's own (machine, branch, agents, the palette key), plus the clock with a sun or
// a moon. This copy is always there, so it also keeps the window's look up to date: it notices when the
// time of day, the season, the person's choices or the window's size change, and has look.js apply them.

import { div, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { spaces, agents, theme, run, exec, setShared, shared, layout, nextCommand } from "herdr";
import { ART, look, clockText, setZone, keyHint, config, setConfig, PALETTES, SEASONS, TODS } from "./core.js";
import { syncLook, stageSize, find } from "./look.js";
import { adoptClaudeTheme, adoptClaudeStatusLine, claudeStatusLineOn } from "./claude.js";

const TOD_ICON = { dawn: "dawn", day: "sun", night: "moon" };

export default class Status {
  init(_p, cx) {
    this.key = null;
    this.size = null;
    this.gen = 0;
    this.wake = null;
    // The clock, and with it the time of day and the season.
    cx.timer.every(30000, (cx) => cx.notify());
    // The time zone's name gives sunrise and sunset a place; the system knows it.
    cx.spawn(async (cx) => {
      try {
        const r = await exec("readlink", ["/etc/localtime"]);
        const name = r.code === 0 ? (r.stdout.trim().split("zoneinfo/")[1] ?? null) : null;
        if (name) { setZone(name); if (shared("hv.zone") !== name) setShared("hv.zone", name); cx.notify(); }
      } catch {}
    });
    // Claude Code's own colors follow the valley only on its "auto" theme (see claude.js).
    cx.spawn(async () => {
      try { setShared("hv.claude", await adoptClaudeTheme()); } catch (e) { setShared("hv.claude", `error: ${e?.message ?? e}`); }
      // Then its status line, only if the person turned it on in the panel (both write
      // ~/.claude/settings.json, so one after the other). With no choice made yet, the switch
      // shows what is there now, so nothing changes until the person flips it.
      try {
        const want = config().claudeLine, on = await claudeStatusLineOn();
        if (want === undefined) { setConfig({ claudeLine: on }); setShared("hv.claude.statusline", on ? "on" : "off"); }
        else setShared("hv.claude.statusline", want && !on ? await adoptClaudeStatusLine() : (on ? "on" : "off"));
      } catch (e) { setShared("hv.claude.statusline", `error: ${e?.message ?? e}`); }
    });
    // Commands for keys.json or `herdr-app do`: herdgarden.night, .day, .dawn, .spring, .summer, .autumn,
    // .winter, .paper, .sand, .blossom hold that choice; herdgarden.auto follows the clock and calendar again.
    cx.spawn(async (cx) => {
      for (;;) {
        const c = await nextCommand();
        if (TODS.includes(c)) setConfig({ todAuto: false, tod: c });
        else if (SEASONS.includes(c)) setConfig({ seasonAuto: false, season: c });
        else if (PALETTES.includes(c)) setConfig({ palette: c });
        else if (c === "auto") setConfig({ todAuto: true, seasonAuto: true });
        cx.notify();
      }
    });
    // One task applies looks, one at a time; renders only wake it.
    cx.spawn(async () => {
      for (;;) {
        await new Promise((resolve) => { this.wake = resolve; });
        await syncLook(this.size);
      }
    });
  }

  // Called from render: note what the window should wear, and if that changed, apply it shortly
  // (a resize sends many sizes; only the last one is drawn).
  note(cx) {
    const L = look();
    let size = this.size;
    try { size = stageSize(window.viewport_size()); } catch {}
    const stage = find(layout(), "stage");
    const key = JSON.stringify([L.palette, L.tod, L.season, L.strength, L.blur, size, spaces().length > 0, stage?.background?.image ?? null, stage?.active ?? null]);
    if (key === this.key) return L;
    this.key = key;
    // What the window wears now, for programs outside Herdr: the Claude Code status line's sky reads it.
    const now = { palette: L.palette, tod: L.tod, season: L.season };
    const was = shared("hv.now");
    if (was?.palette !== now.palette || was?.tod !== now.tod || was?.season !== now.season) setShared("hv.now", now);
    this.size = size;
    const n = ++this.gen;
    cx.timer.after(350, () => { if (n === this.gen) this.wake?.(); });
    return L;
  }

  render(cx) {
    const t = theme();
    const L = this.note(cx);
    const space = spaces().find(s => s.active);
    const list = agents();
    const needs = list.filter(a => a.status === "blocked").length;
    const hint = keyHint("app.palette");
    const now = new Date();
    const label = (icon, text) => h_flex().gap(6).items_center().child(svg(`mods/workspace-chrome/${icon}.svg`).size(13)).child(text);
    return h_flex().id("hv-status").size_full().px(14).gap(16).items_center().bg(t.chrome).border_t(1).border_color(t.border).text_size(11.8).text_color(t.muted)
      // A wider or narrower window: look again, so the valley picture is redrawn for it.
      .on_size_change((_size, cx) => cx.notify())
      .child(label(space?.machine ? "server" : "monitor", space?.machine ?? "This computer"))
      .when(Boolean(space?.branch), el => el.child(label("branch", space.branch)))
      .when(spaces().length > 0, el => el.child(h_flex().gap(6).items_center().child(div().size(6).rounded(3).bg(t.dim)).child(`${list.length} agents`)
        .when(needs > 0, el => el.child(div().text_color(t.blocked).child(`· ${needs} needs you`)))))
      .child(div().flex_1())
      .child(div().id("palette").text_color(t.dim).on_click(() => run("app.palette")).child(hint ? `${hint}  commands` : "commands"))
      .child(h_flex().gap(6).items_center().child(svg(`${ART}/${TOD_ICON[L.tod]}.svg`).size(13).text_color(t.done)).child(clockText(now.getHours() + now.getMinutes() / 60)));
  }
}
