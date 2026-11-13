// Herdewvalley: one mod, drawn by role. The layout gives each copy props { role }:
//   brand    the top of the sidebar: name, search, fold
//   spaces   the spaces list, each space with its home
//   agents   the agents list, each agent as a villager
//   yard     the shown agent's yard: its space's home, its crops, and the villager at work
//   footer   Herdewvalley (the theme's own panel), Settings (Herdr's own), Add machine
//   tabs     the tab bar, with the villager's face on a tab that has an agent
//   status   the status bar with the clock; it also keeps the colors and the valley picture up to date
//   empty    what the middle of the window shows before any space exists
//   panel    the Herdewvalley panel (a popup)

import { View, div } from "gpui-kit";
import { props, theme } from "herdr";
import { Brand, Footer } from "./chrome.js";
import Spaces from "./spaces.js";
import Agents from "./agents.js";
import Yard from "./yard.js";
import Tabs from "./tabs.js";
import Status from "./status.js";
import Empty from "./empty.js";
import Panel from "./panel.js";

const ROLES = { brand: Brand, spaces: Spaces, agents: Agents, yard: Yard, footer: Footer, tabs: Tabs, status: Status, empty: Empty, panel: Panel };

export default class Herdewvalley extends View {
  init(p, cx) {
    const pr = props() ?? p ?? {};
    // The agents list opens its own sort menu as a popup of this mod.
    // Opened by name (mod.open, the palette, a key) it has no role: that is the panel.
    const R = pr.sortMenu ? Agents : ROLES[pr.role] ?? (pr.overlay ? Panel : null);
    this.role = R ? new R() : null;
    this.role?.init?.(pr, cx);
  }

  render(cx) {
    if (!this.role) return div().p(8).text_size(12).text_color(theme().dim).child(`herdewvalley: no role "${props()?.role}"`);
    return this.role.render(cx);
  }
}
