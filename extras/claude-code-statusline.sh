#!/bin/bash
# Herdewvalley "Gardener" status line for Claude Code.
#   line 1: gardener (model), home (folder), branch, coins (cost), sky + session time
#   line 2: context, 5-hour and 7-day usage as raked-line meters
#   line 3: what each meter is, and when the two limits reset
# Colours are the terminal's own ANSI colours, so the line follows whatever theme is active.
input=$(cat)
BRANCH=$(git branch --show-current 2>/dev/null)

printf '%s' "$input" | jq -r --arg branch "$BRANCH" '
  def rep(s; n): if n <= 0 then "" else s * n end;
  def pad(s; n): s + rep(" "; n - (s | length));
  def two: tostring | if length < 2 then "0" + . else . end;
  "\u001b[0m" as $rst | "\u001b[1m" as $bold | "\u001b[2m" as $dim
  | "\u001b[32m" as $green | "\u001b[33m" as $gold | "\u001b[31m" as $red
  | def col(p): if p >= 80 then $red elif p >= 50 then $gold else $green end;
    def meter(p): ((p / 10 | round) | if . > 10 then 10 elif . < 0 then 0 else . end) as $n
      | col(p) + rep("━"; $n) + $rst + $dim + rep("─"; 10 - $n) + $rst;
    def column(icon; p): (p | round) as $r
      | icon + " " + meter(p) + " " + pad("\($r)%"; 4) + "  ";

  (.model.display_name // "Claude") as $model
  | ((.workspace.current_dir // .cwd // "") | split("/") | last // "") as $dir
  | (((.cost.total_cost_usd // 0) * 100) | round) as $cents
  | ((.cost.total_duration_ms // 0) / 60000 | floor) as $mins
  | (if $mins >= 60 then "\($mins / 60 | floor)h \($mins % 60 | two)m" else "\($mins)m" end) as $time
  | (now | strflocaltime("%H") | tonumber) as $hour
  | (if $hour >= 5 and $hour < 8 then "🌅" elif $hour >= 8 and $hour < 18 then "☀️ " else "🌙" end) as $sky
  | (.context_window.used_percentage // 0) as $ctx
  | (if $ctx < 25 then "🌱" elif $ctx < 50 then "🌿" elif $ctx < 75 then "🪴" else "🌳" end) as $plant
  | .rate_limits.five_hour as $five | .rate_limits.seven_day as $week

  | "🧑‍🌾 " + $bold + $model + $rst
    + "  🏡 " + $dir
    + (if $branch != "" then "  🌿 " + $green + $branch + $rst else "" end)
    + "  🪙 " + $gold + "$\($cents / 100 | floor).\($cents % 100 | two)" + $rst
    + "  " + $sky + " " + $dim + $time + $rst,

    column($plant; $ctx)
    + (if $five then column("💧"; $five.used_percentage // 0) else "" end)
    + (if $week then column("🌾"; $week.used_percentage // 0) else "" end),

    $dim + pad("context used"; 20)
    + (if $five then pad("5h" + (if $five.resets_at then " · resets " + ($five.resets_at | strflocaltime("%-I:%M%p") | ascii_downcase) else " limit" end); 20) else "" end)
    + (if $week then "week" + (if $week.resets_at then " · resets " + ($week.resets_at | strflocaltime("%a")) else " limit" end) else "" end)
    + $rst
'
