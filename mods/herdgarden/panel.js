// The Herdgarden panel: the theme's own choices, kept in shared "hv.config". Herdr's settings are not
// touched; this opens from its own row in the sidebar.

import { div } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { theme } from "herdr";
import { FONT, PALETTES, SEASONS, TODS, config, setConfig, look, colors, sunTimes, clockText } from "./core.js";
import { panelRoom } from "./chrome.js";

const cap = (s) => s[0].toUpperCase() + s.slice(1);
const STRENGTHS = [40, 55, 65, 80, 100];
const BLURS = [0, 1, 1.5, 2, 3];

export default class Panel {
  render() {
    const t = theme(), c = config(), L = look(), sun = sunTimes(new Date());
    const stop = (_e, cx) => cx.stop_propagation();
    const line = () => div().h(1).flex_none().bg(t.border);
    const label = (text) => div().text_size(11).text_color(t.muted).child(text);
    const toggle = (id, text, on, action) => h_flex().id(id).h(22).items_center().justify_between().cursor_pointer().on_mouse_down("left", stop).on_click(action)
      .child(div().font_medium().text_color(t.foreground).child(text))
      .child(div().relative().w(28).h(16).flex_none().rounded_full().bg(on ? t.working : t.dim)
        .child(div().absolute().top(2).left(on ? 14 : 2).size(12).rounded_full().bg(t.canvas)));
    const seg = (id, items, value, action, show = cap) => h_flex().p(2).gap(2).rounded(7).bg(t.selected)
      .children(items.map((v) => div().id(`${id}-${v}`).flex_1().h(22).flex().items_center().justify_center().rounded(5).text_size(11.5).cursor_pointer()
        .when(v === value, (el) => el.bg(t.foreground).text_color(t.canvas))
        .when(v !== value, (el) => el.text_color(t.muted).hover((s) => s.text_color(t.foreground)))
        .on_mouse_down("left", stop).on_click(() => action(v)).child(show(v))));
    const radio = (id, on, title, text, action) => h_flex().id(id).gap(8).items_start().cursor_pointer().on_mouse_down("left", stop).on_click(action)
      .child(div().mt(3).size(11).flex_none().rounded_full().border(on ? 3.5 : 1.5).border_color(on ? t.accent : t.dim))
      .child(v_flex().gap(1).child(div().font_medium().text_color(t.foreground).child(title)).child(div().text_size(11).text_color(t.muted).child(text)));
    const swatch = (p) => {
      const k = colors(p, L.tod), on = c.palette === p;
      return v_flex().id(`pal-${p}`).flex_1().min_w(0).p(4).gap(4).items_center().rounded(8).cursor_pointer().border(1.5).border_color(on ? t.accent : t.popover)
        .on_mouse_down("left", stop).on_click(() => setConfig({ palette: p }))
        .child(h_flex().w_full().h(28).px(6).pb(6).gap(3).items_end().rounded(5).bg(k.canvas).border(1).border_color(k.border)
          .child(div().size(7).rounded_full().bg(k.accent)).child(div().size(7).rounded_full().bg(k.working)))
        .child(div().text_size(11.5).text_color(on ? t.foreground : t.muted).when(on, (el) => el.font_medium()).child(cap(p)));
    };
    // Never taller than the window: past that, the rows scroll.
    return v_flex().id("hv-panel").w_full().max_h(panelRoom()).overflow_y_scrollbar().p(12).gap(8).bg(t.popover).text_size(12.5).text_color(t.foreground)
      .child(div().font_family(FONT).text_size(14).text_color(t.muted).child("herdgarden"))
      .child(label("Palette"))
      .child(h_flex().gap(6).children(PALETTES.map(swatch)))
      .child(line())
      .child(toggle("follow-season", "Follow the seasons", c.seasonAuto, () => setConfig(c.seasonAuto ? { seasonAuto: false, season: L.season } : { seasonAuto: true })))
      .when(c.seasonAuto, (el) => el.child(label(`Now: ${L.season}`)))
      .when(!c.seasonAuto, (el) => el.child(seg("season", SEASONS, L.season, (v) => setConfig({ season: v }))))
      .child(line())
      .child(toggle("follow-tod", "Follow the time of day", c.todAuto, () => setConfig(c.todAuto ? { todAuto: false, tod: L.tod } : { todAuto: true })))
      .when(c.todAuto, (el) => el
        .child(radio("sun", c.sunMode !== "hours", "Sunrise and sunset", `Today: sunrise ${clockText(sun.rise)}, sunset ${clockText(sun.set)}`, () => setConfig({ sunMode: "sun" })))
        .child(radio("hours", c.sunMode === "hours", "Fixed hours", "Dawn 5:30 am, day 8:00 am, night 6:00 pm", () => setConfig({ sunMode: "hours" }))))
      .when(!c.todAuto, (el) => el.child(seg("tod", TODS, L.tod, (v) => setConfig({ tod: v }))))
      .child(line())
      .child(label("Background picture: strength"))
      .child(seg("strength", STRENGTHS, c.strength, (v) => setConfig({ strength: v }), (v) => `${v}%`))
      .child(label("Background picture: blur"))
      .child(seg("blur", BLURS, c.blur, (v) => setConfig({ blur: v }), (v) => (v ? String(v) : "Off")))
      .child(line())
      .child(toggle("motion", "Animations", c.motion !== false, () => setConfig({ motion: c.motion === false })));
  }
}
