// The middle of the window before any space exists (and again whenever every space is closed).
// Herdr's own welcome window floats over this on a first launch; its last button makes the first space.

import { div, image } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { theme, run } from "herdr";
import { ART, FONT, look, villagerArt, keyHint } from "./core.js";

export default class Empty {
  render() {
    const t = theme(), L = look();
    const key = (action) => keyHint(action);
    const chip = (text, strong) => div().flex_none().px(5).py(1).rounded(4).text_size(10.5)
      .when(strong, (el) => el.bg("#ffffff2e").text_color(t.accent_foreground))
      .when(!strong, (el) => el.border(1).border_color(t.border).text_color(t.muted))
      .child(text);
    const step = (pic, title, text) => h_flex().gap(12).items_center()
      .child(h_flex().w(30).h(30).flex_none().items_end().justify_center().child(pic))
      .child(v_flex().gap(1).child(div().font_medium().text_color(t.foreground).child(title)).child(div().text_size(11.5).text_color(t.muted).child(text)));
    const hints = [["app.palette", "Palette"], ["app.settings", "Settings"], ["app.help", "Help"]].filter(([a]) => key(a));
    return v_flex().size_full().pt(58).pl(58).items_start().text_size(13)
      .child(v_flex().w(400).items_start()
        .child(image(`${ART}/sprout.svg`).size(36))
        .child(div().mt(18).font_family(FONT).text_size(25).text_color(t.foreground).child("Nothing planted yet"))
        .child(div().mt(8).text_size(13.5).text_color(t.muted).child("A space is a place to work: a folder, its tabs, and the agents you start there. Open one and it gets a home in the valley."))
        .child(h_flex().id("empty-new").mt(18).h(30).pl(13).pr(8).gap(10).items_center().rounded(7).bg(t.accent).text_color(t.accent_foreground).font_semibold().cursor_pointer()
          .hover((s) => s.opacity(0.9)).on_click(() => run("space.new"))
          .child("New space").when(Boolean(key("space.new")), (el) => el.child(chip(key("space.new"), true))))
        .child(div().mt(30).w_full().h(1).bg(t.border))
        .child(v_flex().mt(14).gap(12)
          .child(step(image(`${ART}/home/farmhouse.png`).size(24), "Open a space", "It gets a home in the sidebar."))
          .child(step(image(`${villagerArt("farmer", L.season, "bust")}.png`).w(24).h(30), "Start an agent", "A villager moves in. The + in the tab bar starts any agent you have installed."))
          .child(step(image(`${ART}/crop/3-day.png`).w(20).h(24), "Watch the yard", "It shows how the work is going: at work while working, a “!” when blocked, a harvest when done.")))
        .child(h_flex().mt(26).gap(16).text_size(11.5).text_color(t.dim)
          .children(hints.map(([a, name]) => h_flex().gap(6).items_center().child(chip(key(a), false)).child(name)))));
  }
}
