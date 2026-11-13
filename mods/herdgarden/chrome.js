// The top and the foot of the sidebar. The foot has the theme's own row, Herdgarden, above Herdr's
// Settings and Add machine: Settings opens Herdr's own settings, untouched.

import { div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { theme, run, window as appWindow, shared, setShared, updates, layout, openOverlay, settings } from "herdr";
import { MOD, ART, FONT } from "./core.js";
import { find } from "./look.js";

const ICON = "mods/workspace-chrome";
// The sidebar's rail goes by its width, not a flag: dragging its edge narrows it too.
export const narrow = () => (find(layout(), "sidebar")?.size?.px ?? Infinity) < 160;

// To the rail (on macOS wide enough for the traffic lights), or back to the width it had.
// The yard has no room on the rail, so it goes and comes back with it.
export function toggleSidebar() {
  const width = find(layout(), "sidebar")?.size?.px;
  const toRail = !narrow();
  if (toRail) setShared("sidebar.width", width);
  setShared("sidebar.collapsed", toRail);
  run(toRail ? "layout.hide" : "layout.show", { id: "yard" });
  run("layout.resize", { id: "sidebar", px: toRail ? (appWindow()?.platform === "macos" ? 76 : 44) : (shared("sidebar.width") ?? 268) });
}

// How tall the Herdgarden panel may be, in layout px. Read in a render (the only place the window can be).
export function panelRoom() {
  try { return Math.max(240, Math.min(640, Math.floor(window.viewport_size().height / (settings()?.zoom || 1)) - 32)); } catch { return 600; }
}

export class Brand {
  button(id, label, action) {
    const t = theme();
    return div().id(id).size(26).flex_none().flex().items_center().justify_center().rounded(6).text_color(t.muted).hover(s => s.bg(t.hover).text_color(t.foreground))
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation()).on_click(action).child(label);
  }

  render() {
    const t = theme(), w = appWindow();
    const collapsed = narrow();
    return h_flex().size_full().bg(t.chrome).pl(collapsed ? 6 : 14).pr(10).gap(4).items_center().text_size(13.5)
      .when(w?.platform === "macos" && !w?.fullscreen && !collapsed, el => el.pl(76))
      .when(!collapsed, el => el.child(h_flex().flex_1().min_w(0).gap(7).items_center()
        .child(image(`${ART}/sprout.svg`).size(15).flex_none())
        .child(div().font_family(FONT).text_size(14.5).text_color(t.foreground).truncate().child("herdgarden"))))
      .when(!collapsed, el => el.child(this.button("search", svg(`${ICON}/search.svg`).size(15), () => run("mod.open", { name: "picker" }))))
      // On the macOS rail the traffic lights fill the row; the agents list's » unfolds it.
      .when(!(collapsed && w?.platform === "macos"), el => el.child(this.button("sidebar-toggle", svg(`${ICON}/sidebar.svg`).size(15), toggleSidebar)));
  }
}

export class Footer {
  render() {
    const t = theme();
    // The panel is as tall as its rows; this is only the most it may take (the window's height, less a margin).
    this.room = panelRoom();
    const collapsed = narrow();
    const row = (id, icon, label, dim, action) => h_flex().id(id).h(28).px(8).gap(9).items_center().rounded(8)
      .when(collapsed, el => el.relative().w(32).px(0).justify_center().tooltip(label))
      .text_color(dim ? t.dim : t.muted).hover(s => s.bg(t.hover).text_color(t.foreground)).cursor_pointer()
      .on_click(action).child(icon)
      .when(!collapsed, el => el.child(label));
    const ready = div().size(6).rounded_full().bg(t.accent);
    return v_flex().size_full().bg(t.chrome).border_t(1).border_color(t.border).px(8).pt(4).pb(8).text_size(13)
      .when(collapsed, el => el.px(0).items_center())
      .child(row("herdgarden", image(`${ART}/sprout.svg`).size(14).flex_none(), "Herdgarden", false,
        () => openOverlay({ mod: MOD, kind: "popup", width: 268, height: this.room, props: { role: "panel" } })))
      .child(row("settings", svg(`${ICON}/settings.svg`).size(14), "Settings", false, () => run("app.settings"))
        .when(Boolean(updates().app.ready), el => el.child(collapsed ? ready.absolute().top(5).right(6) : ready)))
      .child(row("machine", svg(`${ICON}/plus.svg`).size(14), "Add machine", true, () => run("mod.open", { name: "machine-add" })));
  }
}
