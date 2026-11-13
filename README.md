<div align="center">

# 🌱 Herdgarden

**A quiet pixel garden for [Herdr](https://herdr.dev).**<br>
Your spaces are homes, your agents are villagers, and a small yard shows how each one's work is going.

![Herdgarden in the Paper palette on a summer day](preview.png)

</div>

## Watch your agents work

When you select an agent, the sidebar shows its yard. The villager in the yard acts out what the agent is doing:

- **Working:** walks a round of the crop bed and waters it.
- **Blocked:** waits on the path with a red **!** until you answer.
- **Done:** holds a basket of ripe crops.
- **Idle:** rests by the flower bed.

<p align="center">
  <img src="docs/yard-states.gif" width="100%" alt="Four yards side by side, labeled Working, Blocked, Done, and Idle">
</p>

A working villager doesn't stand still. They water both rows of the crop bed, look in on the flower bed, stop at the pond, and walk home again:

<p align="center">
  <img src="docs/yard-round.gif" width="60%" alt="A villager walks one full round of the garden, watering the crop bed">
</p>

## Dawn, day, and night

The whole window follows your clock. Dawn starts half an hour before your local sunrise, day starts an hour and a half after it, and night starts at sunset. Herdgarden works out sunrise and sunset from your time zone, so you don't set a location.

<p align="center">
  <img src="docs/window-times.gif" width="100%" alt="The Herdgarden window fading from dawn to day to night">
</p>

In the yard, the lamps and the house windows light up at dawn and after dark:

<p align="center">
  <img src="docs/yard-times.gif" width="60%" alt="The same yard at dawn, by day, and at night, labeled">
</p>

## Three palettes

Each palette has its own dawn, day, and night colors. **Paper** is the default: near-white with green-gray text. **Sand** is warmer, and **Blossom** has a pink tint. All three look like this in summer:

<table>
  <tr>
    <th></th>
    <th>Paper</th>
    <th>Sand</th>
    <th>Blossom</th>
  </tr>
  <tr>
    <th>Day</th>
    <td><img src="docs/paper-day-summer.png" alt="Paper palette by day"></td>
    <td><img src="docs/sand-day-summer.png" alt="Sand palette by day"></td>
    <td><img src="docs/blossom-day-summer.png" alt="Blossom palette by day"></td>
  </tr>
  <tr>
    <th>Night</th>
    <td><img src="docs/paper-night-summer.png" alt="Paper palette at night"></td>
    <td><img src="docs/sand-night-summer.png" alt="Sand palette at night"></td>
    <td><img src="docs/blossom-night-summer.png" alt="Blossom palette at night"></td>
  </tr>
</table>

Pick a palette in the **Herdgarden** panel. Click a picture to see it full size.

## Four seasons

The yard and the valley follow your calendar. Seasons start on 20 March, 21 June, 22 September, and 21 December, and they swap south of the equator.

- **Spring:** the cherry tree blooms, tulips fill the flower bed, and petals drift by.
- **Summer:** sunflowers.
- **Autumn:** the trees turn orange and gold, pumpkins ripen, and leaves fall.
- **Winter:** snow covers the roof, the pond freezes, the crops go under glass, and the villager shovels snow instead of watering.

<p align="center">
  <img src="docs/yard-seasons.gif" width="60%" alt="The same yard in spring, summer, autumn, and winter, labeled">
</p>

## Meet the villagers

<table>
  <tr>
    <td width="42%" align="center"><img src="docs/villagers.gif" alt="The four villagers walking, one row for each season"></td>
    <td>

Each agent program gets its own villager:

| Villager | Agent |
|---|---|
| 👒 The farmer | Claude Code |
| 🥽 The tinker | Codex |
| 🌸 The gardener | OpenCode |
| 🧔 The elder | Gemini |

Other agents get one of these four. A tab with an agent in it shows that villager's face before the tab name.

The villagers dress for the season: light colors in spring, scarves in autumn, and coats and mittens in winter.

</td>
  </tr>
</table>

## Keep the text readable

A pixel valley sits in the lower-right corner, behind your panes. Herdgarden fades and softly blurs it, so text on top stays easy to read. You can change both in the Herdgarden panel.

![A session full of text over the valley](docs/paper-day-autumn-full.png)

Before you open your first space, the window shows an empty plot with a **New space** button:

![The first-run window with an empty plot](docs/paper-day-summer-first.png)

## Install

```sh
git clone https://github.com/svadr/herdgarden.git
cd herdgarden
cp -R layouts themes mods ~/.config/herdr-app/
herdr-app do layout.switch --name herdgarden
```

You can also pick **Herdgarden** in Herdr's layout settings. To go back to your other layouts, press `ctrl-shift-l`.

Herdgarden needs macOS and `python3`. Python draws the valley picture at your window's size. Without Python, everything else still works.

If macOS **Reduce Motion** is on, Herdr doesn't play timed moves, so the yard uses a gentler animation: the villager faces you and steps along the beds. For the full walk, turn Reduce Motion off and restart Herdr.

## Change the look

Herdr's own **Settings** stays as it is. Herdgarden's choices live in their own **Herdgarden** row at the bottom of the sidebar:

- **Palette:** Paper (the default), Sand, or Blossom.
- **Seasons:** follow the calendar, or hold one season.
- **Time of day:** use sunrise and sunset for your time zone, use fixed hours, or hold one look.
- **Background picture:** set its strength and blur.
- **Animations:** turn them on or off.
- **Claude Code status line:** use the Gardener status line, or keep your own.

To hold a look from the terminal, run a Herdgarden command:

```sh
herdr-app do herdgarden.night   # or dawn, day, spring, summer, autumn, winter, paper, sand, blossom
herdr-app do herdgarden.auto    # follow the clock and the calendar again
```

To bind the same commands to keys, add them to `~/.config/herdr-app/keys.json`:

```json
{ "global": { "cmd-alt-n": "herdgarden.night", "cmd-alt-a": "herdgarden.auto" } }
```

## Use it with Claude Code

Claude Code picks its own text colors. On its default dark theme, its code and file previews are hard to read when the window turns light at dawn. If you never chose a Claude Code theme, Herdgarden sets it to **Auto** the first time it runs, so Claude Code follows the window from dawn to night. A theme you chose stays as it is, and `/theme` in Claude Code changes it at any time. Restart any Claude Code sessions that were already open.

Herdgarden also offers Claude Code its "Gardener" status line, the one in the screenshots. It shows 🧑‍🌾 the model, 🏡 the folder, 🌿 the branch, 🪙 the cost, and the session time under 🌅 ☀️ or 🌙, the sky the window shows. Under that are meters for context (a plant that grows from 🌱 to 🌳), 💧 5-hour usage and 🌾 7-day usage, and when the two limits reset. It needs `python3`.

The status line is off until you turn it on. To turn it on, open the **Herdgarden** panel and switch on **Claude Code status line**. Herdgarden then sets `statusLine` in `~/.claude/settings.json` and keeps your old status line in `~/.config/herdr-app/data/herdgarden/claude-statusline-before.json`. To get your old one back, switch it off again. The change shows on your next message in Claude Code.

## How it's made

All of the pixel art is original. Small Python scripts in [`mods/herdgarden/tools/art-src`](mods/herdgarden/tools/art-src) draw every picture, with no image editor. `gifs.py` draws the yard GIFs in this README, and `readme_shots.py` takes the window screenshots from the design preview. [`RECIPE.md`](RECIPE.md) describes the layout in enough detail for an agent to rebuild it from an empty folder. The spaces, agents, and tabs lists are copies of Herdr's own mods with small changes.

## License

The code and art are under the MIT license. The Pixelify Sans font is under the SIL Open Font License.
