// The yard of the agent you are looking at: its space's home, its crops, and the villager.
//   working  walks a round of the beds and waters them; in winter clears snow with a shovel instead
//   blocked  stands by the path with a "!"
//   done     stands by ripe crops with a harvest basket
//   idle     rests by the flower bed, "z z"
// The picture is 212 x 132 art pixels, scaled to the sidebar's width. The yard pictures already carry the
// dawn and night light.
//
// Two ways to move, chosen by the system's Reduce Motion setting (looked up, and looked up again each minute):
//   off  the round from the design: one timed move per leg, a side-on walk cycle, a stop at each bed, the
//        tool in use only there; petals, leaves and snow are a looping picture.
//   on   Herdr skips timed moves and animated pictures then, but keeps loops and spins running. A loop only
//        swings there and back, so the villager faces you and works along the beds, stepping in place; what
//        falls rides big slow wheels (a spin turns one way).

import { h_flex, v_flex } from "gpui-base";
import { div, image, svg } from "gpui-kit";
import { agents, spaces, theme, run, settings, exec } from "herdr";
import { ART, FONT, look, villager, villagerArt, homeOf, keyHint } from "./core.js";
import { narrow } from "./chrome.js";

const W = 212, H = 132;
const BX = 12, BY = 80; // the crop bed's corner
// The round, from the design: where each leg ends (relative to the crop bed), as a percent of the round,
// whether the villager walks or stands, which way they face, and whether the tool is in use.
const ROUND_MS = 52100;
const START = [-2, -2];
const LEGS = [
  { until: 6.76, x: 30, y: -2, walk: true, dir: 1, work: true },
  { until: 12.52, x: 30, y: -2, walk: false, dir: 1, work: true },
  { until: 19.27, x: 62, y: -2, walk: true, dir: 1, work: true },
  { until: 26.53, x: 96, y: -7, walk: true, dir: 1, work: false },
  { until: 34.97, x: 136, y: -7, walk: true, dir: 1, work: true },
  { until: 40.73, x: 136, y: -7, walk: false, dir: 1, work: true },
  { until: 48.75, x: 174, y: -7, walk: true, dir: 1, work: true },
  { until: 63.53, x: 104, y: -7, walk: true, dir: -1, work: true },
  { until: 67.54, x: 104, y: 12, walk: true, dir: -1, work: false },
  { until: 75.22, x: 104, y: 12, walk: false, dir: 1, work: false },
  { until: 84.57, x: 62, y: -2, walk: true, dir: -1, work: false },
  { until: 98.08, x: -2, y: -2, walk: true, dir: -1, work: true },
  { until: 100, x: -2, y: -2, walk: false, dir: 1, work: true },
];
// With reduced motion: the line the villager works along (from, to, top), there and back, and two steps.
const ROW = [BX + 2, BX + 170, BY - 4];
const SWING_MS = 40000;
const STEP_MS = 560;
const CROPS = {
  working: "2 3 3 2 3 1 2 3 2 1", blocked: "3 2 3 wilt 2 2 3 wilt 2 3", done: "4 4 4 4 4 4 4 4 4 4", idle: "1 1 2 1 1 1 2 1 1 1",
};
const SPOT = { blocked: [97, 62], done: [BX + 32, BY - 2], idle: [118, 90] };
const RANK = { blocked: 4, done: 3, working: 2, idle: 1 };
// The wheels of weather/<season>-<name>.svg: name, color, ms for one turn. See tools/art-src/weather_wheel.py.
const WHEEL_D = 250, WHEEL_R = 468;
const WHEELS = {
  spring: [["a", "#fbd0dd", 230000], ["b", "#ffffff", 290000]],
  autumn: [["a", "#e8862e", 210000], ["b", "#f1c040", 260000], ["c", "#c9472b", 310000]],
  winter: [["a", "#ffffff", 200000], ["b", "#ffffff", 150000]],
};
const FLIES = [[40, 60, 2600], [150, 66, 3400], [176, 108, 2900], [60, 112, 3800]];

export default class Yard {
  init(p, cx) {
    this.width = 268;
    this.reduced = false; // the system's Reduce Motion setting
    this.leg = -1; // -1: standing at the start, before the first leg
    this.runs = 0; // bumped to stop the round's timer
    this.ids = 0; // a new id per round, so nothing slides to the start
    this.id = 0;
    this.walking = null; // the agent the round belongs to
    this.dur = 1;
    const ask = (cx) => cx.spawn(async (cx) => {
      let on = false;
      try { on = (await exec("defaults", ["read", "com.apple.universalaccess", "reduceMotion"])).stdout.trim() === "1"; } catch {}
      if (on !== this.reduced) { this.reduced = on; cx.notify(); }
    });
    ask(cx);
    cx.timer.every(60000, ask);
  }

  step(cx, i) {
    this.leg = i;
    // Whole milliseconds: Herdr drops a timed move whose duration is a fraction.
    this.dur = Math.round((LEGS[i].until - (i ? LEGS[i - 1].until : 0)) / 100 * ROUND_MS);
    const n = ++this.runs;
    cx.timer.after(this.dur, (cx) => {
      if (n !== this.runs) return;
      this.step(cx, (i + 1) % LEGS.length);
      cx.notify();
    });
  }

  stop() {
    if (!this.walking) return;
    this.walking = null;
    this.runs++;
    this.leg = -1;
  }

  // The villager on their round (full motion).
  rounds(cx, s, L, a) {
    const who = villager(a.program, a.app);
    const winter = L.season === "winter";
    const at = (x, y, w, h) => div().absolute().left(x * s).top(y * s).w(w * s).h(h * s);
    const pic = (path, x, y, w, h) => at(x, y, w, h).child(image(path).size_full());
    if (this.walking !== a.address) {
      // A new round: stand at the start under a new id, then set off.
      this.walking = a.address;
      this.id = ++this.ids;
      this.leg = -1;
      const n = ++this.runs;
      cx.timer.after(60, (cx) => { if (n !== this.runs) return; this.step(cx, 0); cx.notify(); });
    }
    const leg = this.leg >= 0 ? LEGS[this.leg] : null;
    const [x, y] = leg ? [BX + leg.x, BY + leg.y] : [BX + START[0], BY + START[1]];
    const right = !leg || leg.dir > 0;
    const side = right ? "r" : "l";
    // Things in the hands are drawn for a villager facing right; facing left they mirror around the body.
    const mx = (px, w) => (right ? px : 16 - px - w);
    const halted = leg && !leg.walk;
    const using = !leg || leg.work;
    const kids = [];
    if (L.tod !== "day") kids.push(at(-20, -8, 56, 56).opacity(L.tod === "dawn" ? 0.45 : 1).child(image(`${ART}/tool/halo.png`).size_full()));
    kids.push(pic(leg?.walk ? `${villagerArt(who, L.season, `walk-${side}`)}.webp` : `${villagerArt(who, L.season, `stand-${side}`)}.png`, 0, 0, 16, 32));
    if (!winter) {
      kids.push(pic(`${ART}/tool/can${right ? "" : "-l"}.png`, mx(11, 9), 19, 9, 7));
      if (using) [[21, 22, 520], [20, 25, 700], [22, 27, 610]].forEach(([dx, dy, period], i) => kids.push(
        at(mx(dx, 1), dy, 1, 2).id(`hv-drop-${i}`).bg("#bfe6f5").loop("opacity", { from: 1, to: 0.1, period })));
    } else {
      const shovel = at(mx(8, 14), 18, 14, 12).id("hv-shovel").child(image(`${ART}/tool/shovel${right ? "" : "-l"}.png`).size_full());
      kids.push(halted ? shovel.loop("top", { from: 18 * s, to: 13 * s, period: 900 }) : shovel);
      if (halted) [[21, 14], [23, 11], [19, 12]].forEach(([dx, dy], i) => kids.push(
        at(mx(dx, 2), dy, 2, 2).id(`hv-snow-${i}`).bg("#ffffff").loop("opacity", { from: 0, to: 1, period: 900 })));
    }
    // One box slides sideways and the one inside it up and down, each with its own timed move.
    const move = { duration: leg ? this.dur : 1, easing: "linear" };
    return div().id(`hv-round-x-${this.id}`).absolute().left(x * s).top(0).w(16 * s).h(H * s).transition("left", move)
      .child(div().id(`hv-round-y-${this.id}`).absolute().left(0).top(y * s).w(16 * s).h(32 * s).transition("top", move).children(kids));
  }

  // The agent whose yard shows: the focused one, else the most urgent in the shown tab, then the shown space.
  shown() {
    const list = agents(), active = spaces().find((s) => s.active);
    const urgent = (l) => [...l].sort((x, y) => (RANK[y.status] ?? 0) - (RANK[x.status] ?? 0))[0] ?? null;
    const tab = active?.tabs.find((c) => c.active);
    return { agent: list.find((a) => a.focused) ?? urgent(list.filter((a) => a.tab === tab?.id)) ?? urgent(list.filter((a) => a.space === active?.id)), space: active };
  }

  walker(cx, s, L, a, status) {
    if (status === "working" && L.motion && !this.reduced) return this.rounds(cx, s, L, a);
    this.stop();
    const who = villager(a.program, a.app);
    const winter = L.season === "winter";
    const at = (x, y, w, h) => div().absolute().left(x * s).top(y * s).w(w * s).h(h * s);
    const pic = (path, x, y, w, h) => at(x, y, w, h).child(image(path).size_full());
    const working = status === "working";
    const moving = working && L.motion;
    const kids = [];
    if (L.tod !== "day") kids.push(at(-20, -8, 56, 56).opacity(L.tod === "dawn" ? 0.45 : 1).child(image(`${ART}/tool/halo.png`).size_full()));
    const stand = `${villagerArt(who, L.season)}.png`;
    if (moving) {
      // Two pictures take turns: an opacity that swings far past 0 and 1 is either fully there or not.
      kids.push(pic(stand, 0, 0, 16, 32).id("hv-step-a").loop("opacity", { from: 21, to: -20, period: STEP_MS, easing: "linear" }));
      kids.push(pic(`${villagerArt(who, L.season, "step")}.png`, 0, 0, 16, 32).id("hv-step-b").loop("opacity", { from: -20, to: 21, period: STEP_MS, easing: "linear" }));
    } else kids.push(pic(stand, 0, 0, 16, 32));
    if (working && !winter) {
      kids.push(pic(`${ART}/tool/can.png`, 11, 19, 9, 7));
      [[21, 22, 520], [20, 25, 700], [22, 27, 610]].forEach(([dx, dy, period], i) => kids.push(
        at(dx, dy, 1, 2).id(`hv-drop-${i}`).bg("#bfe6f5").when(L.motion, (el) => el.loop("opacity", { from: 1, to: 0.1, period }))));
    }
    if (working && winter) {
      const shovel = at(8, 18, 14, 12).id("hv-shovel").child(image(`${ART}/tool/shovel.png`).size_full());
      kids.push(L.motion ? shovel.loop("top", { from: 18 * s, to: 13 * s, period: 900 }) : shovel);
      [[21, 14], [23, 11], [19, 12]].forEach(([dx, dy], i) => kids.push(
        at(dx, dy, 2, 2).id(`hv-snow-${i}`).bg("#ffffff").when(L.motion, (el) => el.loop("opacity", { from: 0, to: 1, period: 900 }))));
    }
    if (status === "done") kids.push(pic(`${ART}/tool/basket.png`, 10, 21, 9, 6));
    if (status === "blocked") kids.push(pic(`${ART}/tool/bang.png`, 5, -10, 7, 9).id("hv-bang").when(L.motion, (el) => el.loop("opacity", { from: 1, to: 0.25, period: 1000 })));
    if (status === "idle") kids.push(div().absolute().left(14 * s).top(-6 * s).id("hv-zz").font_family(FONT).text_size(9 * s).text_color("#fffaf0").whitespace_nowrap()
      .when(L.motion, (el) => el.loop("opacity", { from: 0.95, to: 0.15, period: 2400 })).child("z z"));
    const [x, y] = working ? [ROW[0] + 30, ROW[2]] : SPOT[status] ?? SPOT.idle;
    const body = div().id(`hv-walker-${status}`).absolute().left(x * s).top(y * s).w(16 * s).h(32 * s).children(kids);
    return moving ? body.loop("left", { from: ROW[0] * s, to: ROW[1] * s, period: SWING_MS, easing: "ease-in-out" }) : body;
  }

  render(cx) {
    const t = theme(), L = look();
    if (narrow()) return div().size_full().bg(t.chrome);
    const { agent, space } = this.shown();
    const none = spaces().length === 0;
    const status = agent?.status ?? null;
    const s = Math.max(0.5, (this.width - 16) / W);
    const kind = none ? "empty" : homeOf(agent?.space ?? space?.id);
    const winter = L.season === "winter";
    const at = (x, y, w, h) => div().absolute().left(x * s).top(y * s).w(w * s).h(h * s);
    const crops = agent ? (CROPS[status] ?? CROPS.idle).split(" ") : [];
    const crop = (name, i) => at(BX + 5 + (i % 5) * 15, BY + (i < 5 ? 6 : 30), 10, 12)
      .child(image(`${ART}/crop/${name}${winter ? "-winter" : ""}-${L.tod}.png`).size_full());
    // What falls. Full motion: a looping picture. Reduced motion: each color is a big wheel of flakes, centred
    // to the left of the yard and turning slowly. No motion: a still.
    const still = L.season === "summer" || (L.motion && this.reduced) ? null
      : at(0, 0, W, H).child(image(`${ART}/weather/${L.season}.${L.motion ? "webp" : "png"}`).size_full());
    const wheels = !(L.motion && this.reduced) ? [] : (WHEELS[L.season] ?? []).map(([name, color, period], i) => {
      const el = svg(`${ART}/weather/${L.season}-${name}.svg`).id(`hv-wheel-${L.season}-${i}`).absolute()
        .left(-(WHEEL_D + WHEEL_R) * s).top((H / 2 - WHEEL_R) * s).w(2 * WHEEL_R * s).h(2 * WHEEL_R * s).text_color(color);
      return el.spin(period);
    });
    if (!agent) this.stop();
    const flies = L.tod === "night" && L.motion && (L.season === "spring" || L.season === "summer")
      ? FLIES.map(([x, y, period], i) => at(x, y, 1.5, 1.5).id(`hv-fly-${i}`).bg("#fff3a8").loop("opacity", { from: 0, to: 1, period })) : [];
    const name = none ? "Empty plot" : agent ? agent.program?.name ?? "Agent" : space?.name ?? "";
    const place = agent ? agent.space_name : "";
    const hint = keyHint("space.new");
    const right = none ? (hint ? `${hint} to build` : "") : agent ? status : "no agent";
    return v_flex().id("hv-yard").size_full().bg(t.chrome).px(8).pb(8).justify_end()
      // Sizes come in window px; the mod draws in layout px, which the person's zoom scales.
      .on_size_change((size, cx) => { const w = size.width / (settings()?.zoom || 1); if (Math.abs(w - this.width) > 0.5) { this.width = w; cx.notify(); } })
      .child(v_flex().id("hv-yard-card").flex_none().rounded(8).border(1).border_color(t.border).bg(t.raised).overflow_hidden()
        .when(Boolean(agent), (el) => el.cursor_pointer().on_click(() => run("pane.focus", { pane: agent.pane })))
        .child(h_flex().h(22).px(9).gap(8).items_center().justify_between().text_size(10.8).text_color(t.muted)
          .child(h_flex().min_w(0).gap(4).items_center()
            .child(div().flex_none().font_medium().text_color(t.foreground).child(name))
            .when(Boolean(place), (el) => el.child(div().min_w(0).truncate().child(`· ${place}`))))
          .child(div().flex_none().text_color(agent ? (t[status] ?? t.dim) : t.dim).child(right ?? "")))
        .child(div().relative().w(W * s).h(H * s).overflow_hidden()
          .child(at(0, 0, W, H).child(image(`${ART}/yard/${kind}-${L.season}-${L.tod}.png`).size_full()))
          .children(crops.slice(0, 5).map(crop))
          .when(Boolean(agent), (el) => el.child(this.walker(cx, s, L, agent, status)))
          .children(crops.slice(5).map((n, i) => crop(n, i + 5)))
          .when(Boolean(still), (el) => el.child(still))
          .children(wheels)
          .children(flies)));
  }
}
