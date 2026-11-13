#!/usr/bin/env python3
# Herdgarden's Claude Code status line: "Gardener".
#
#   🧑‍🌾 Opus 5.5  🏡 herdr-app  🌿 main  🪙 $2.61  ☀️ 2h 02m
#   🪴 ━━━━━━──── 62%   💧 ━━──────── 21%   🌾 ━━━─────── 25%
#   context used        5h · resets 7:40pm  week · resets Mon
#
# Claude Code pipes the session as JSON on stdin. Colors are the terminal's 16 ANSI colors, which
# Herdgarden repaints for the palette and time of day, so the line follows the valley by itself.
# The sky (🌅 ☀️ 🌙) is the time of day the window shows: the status bar publishes it to shared
# "hv.now" in ~/.config/herdr-app/shared.json. Outside Herdr it falls back to fixed hours.
# Installed into ~/.claude/settings.json by claude.js (adoptClaudeStatusLine).

import datetime
import json
import os
import subprocess
import sys

BOLD, GREEN, YELLOW, RED, MUTED, DIM, RESET = "\033[1m", "\033[32m", "\033[33m", "\033[31m", "\033[37m", "\033[90m", "\033[0m"
SKY = {"dawn": "🌅", "day": "☀️", "night": "🌙"}
SHARED = os.path.expanduser("~/.config/herdr-app/shared.json")
WIDTH = 10  # meter cells


def get(d, *path):
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def time_of_day(now):
    try:
        with open(SHARED, encoding="utf-8") as f:
            tod = get(json.load(f), "hv.now", "tod")
        if tod in SKY:
            return tod
    except Exception:
        pass
    h = now.hour + now.minute / 60
    return "dawn" if 5.5 <= h < 8 else "day" if 8 <= h < 18 else "night"


def branch(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd or ".", "--no-optional-locks", "branch", "--show-current"],
                           capture_output=True, text=True, timeout=2)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def level(pct):
    return RED if pct >= 80 else YELLOW if pct >= 50 else GREEN


def meter(pct):
    filled = max(0, min(WIDTH, int(pct / 100 * WIDTH + 0.5)))  # half up: 25% is 3 cells, not 2
    return f"{level(pct)}{'━' * filled}{RESET}{DIM}{'─' * (WIDTH - filled)}{RESET}"


def plant(pct):
    return "🌱" if pct < 25 else "🌿" if pct < 50 else "🪴" if pct < 75 else "🌳"


def when(value):
    # resets_at: epoch seconds (or ms), or an ISO 8601 string
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).replace(".", "", 1).isdigit():
            n = float(value)
            return datetime.datetime.fromtimestamp(n / 1000 if n > 1e12 else n)
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
    except Exception:
        return None


def clock(t):
    return f"{t.hour % 12 or 12}:{t.minute:02d}{'pm' if t.hour >= 12 else 'am'}"


def duration(ms):
    s = int(ms // 1000)
    h, m = s // 3600, (s % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m {s % 60:02d}s"


def pad(text, n=20):
    return text + " " * max(1, n - len(text))


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        d = {}
    now = datetime.datetime.now()
    model = get(d, "model", "display_name") or "Claude"
    cwd = get(d, "workspace", "current_dir") or get(d, "cwd") or os.getcwd()
    cost = float(get(d, "cost", "total_cost_usd") or 0)
    ms = float(get(d, "cost", "total_duration_ms") or 0)
    ctx = get(d, "context_window", "used_percentage")
    five, week = get(d, "rate_limits", "five_hour"), get(d, "rate_limits", "seven_day")

    top = [f"🧑‍🌾 {BOLD}{model}{RESET}", f"🏡 {os.path.basename(cwd.rstrip('/')) or cwd}"]
    b = branch(cwd)
    if b:
        top.append(f"🌿 {GREEN}{b}{RESET}")
    top.append(f"🪙 {YELLOW}${cost:.2f}{RESET}")
    top.append(f"{SKY[time_of_day(now)]} {MUTED}{duration(ms)}{RESET}")
    lines = ["  ".join(top)]

    meters, names = [], []
    if ctx is not None:
        p = round(float(ctx))
        meters.append(f"{plant(p)} {meter(p)} {p}%")
        names.append(pad("context used"))
    for icon, lim, label, fmt in (("💧", five, "5h", clock), ("🌾", week, "week", lambda t: t.strftime("%a"))):
        pct = get(lim, "used_percentage")
        if pct is None:
            continue
        p = round(float(pct))
        meters.append(f"{icon} {meter(p)} {p}%")
        reset = when(get(lim, "resets_at"))
        names.append(pad(f"{label} · resets {fmt(reset)}" if reset else label))
    if meters:
        lines.append("   ".join(meters))
        lines.append(f"{MUTED}{''.join(names).rstrip()}{RESET}")
    print("\n".join(lines))


main()
