"""The README's window screenshots and window GIFs, drawn from the design preview (index.html).
  python3 readme_shots.py <docs folder>
Needs Google Chrome and ImageMagick (`magick`). The yard GIFs come from gifs.py.
"""
import os, sys, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
DOCS = os.path.abspath(os.path.expanduser(sys.argv[1]))
W, H = 1182, 732  # the preview window, border included
TMP = tempfile.mkdtemp()

# Pin the preview's window to the top-left corner, drop its shadow, and hold the blocked "!" still
# (it blinks, and a screenshot can catch it half faded).
PIN = ('html,body{margin:0!important;padding:0!important;overflow:hidden!important;background:#fff!important}'
       '#win{position:fixed!important;left:0!important;top:0!important;z-index:2147483647!important;'
       'transform:none!important;box-shadow:none!important;margin:0!important}'
       '.plot .bang{animation:none!important;opacity:1!important}')
# Labels for the window GIF sit over the empty middle of the Claude Code pane, centered here.
LABEL_AT = (495, 300)
UI_FONT = '/System/Library/Fonts/SFNS.ttf' if os.path.exists('/System/Library/Fonts/SFNS.ttf') else 'Helvetica'


def shot(state, out, scale=2):
    """Screenshot the preview window in one state: the page's hash, such as 'paper-night-summer'."""
    css = PIN
    page = os.path.join(TMP, 'shot.html')
    with open(os.path.join(HERE, 'index.html')) as f:
        html = f.read()
    with open(page, 'w') as f:
        f.write(f'<base href="file://{HERE}/"><style>{css}</style>' + html)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                    f'--force-device-scale-factor={scale}', f'--window-size={W},{H}', '--virtual-time-budget=4300',
                    f'--screenshot={out}', f'file://{page}#{state}'], check=True, capture_output=True)
    return out


def label(png, text):
    """Draw a rounded dark badge with white text onto a frame, centered on LABEL_AT."""
    t = os.path.join(TMP, 'label-text.png')
    subprocess.run(['magick', '-background', 'none', '-fill', 'white', '-font', UI_FONT, '-pointsize', '28', f'label:{text}', t], check=True)
    w, h = map(int, subprocess.run(['magick', 'identify', '-format', '%w %h', t], capture_output=True, text=True, check=True).stdout.split())
    bw, bh = w + 48, h + 22
    x, y = LABEL_AT[0] - bw // 2, LABEL_AT[1]
    out = png.replace('.png', '-label.png')
    subprocess.run(['magick', png, '-fill', 'rgba(26,32,30,0.82)', '-draw', f'roundrectangle {x},{y},{x + bw},{y + bh},{bh // 2},{bh // 2}',
                    t, '-geometry', f'+{x + 24}+{y + 11}', '-composite', out], check=True)
    return out


def fade_gif(keys, texts, out, hold=300, steps=3, step_delay=12, width=880, colors=96):
    """A looping GIF that holds each key picture with its label, then fades to the next one without labels.
    Scaled to `width` (the README's column) with a shared palette of `colors`, to keep the file small."""
    seq = []
    for i, k in enumerate(keys):
        seq += ['-delay', str(hold), label(k, texts[i])]
        pat = os.path.join(TMP, f'fade{i}_%02d.png')
        subprocess.run(['magick', k, keys[(i + 1) % len(keys)], '-morph', str(steps), pat], check=True)
        seq += ['-delay', str(step_delay), *[pat % j for j in range(1, steps + 1)]]
    subprocess.run(['magick', '-loop', '0', *seq, '-resize', f'{width}x', '+dither', '-colors', str(colors),
                    '-fuzz', '2%', '-layers', 'Optimize', out], check=True)
    print(out, os.path.getsize(out) // 1024, 'KB')


if __name__ == '__main__':
    os.makedirs(DOCS, exist_ok=True)
    # The palettes, each by day and at night, in summer.
    for palette in ('paper', 'sand', 'blossom'):
        for tod in ('day', 'night'):
            print(shot(f'{palette}-{tod}-summer', os.path.join(DOCS, f'{palette}-{tod}-summer.png')))
    shutil.copy(os.path.join(DOCS, 'paper-day-summer.png'), os.path.join(DOCS, '..', 'preview.png'))
    # The first-run window, and a session full of text over the valley.
    print(shot('paper-day-first-summer', os.path.join(DOCS, 'paper-day-summer-first.png')))
    print(shot('paper-day-autumn-full', os.path.join(DOCS, 'paper-day-autumn-full.png')))
    # Dawn, day and night in one palette and season; the clock is the preview's sample time.
    tods = ('dawn', 'day', 'night')
    keys = [shot(f'paper-{tod}-summer', os.path.join(TMP, f'{tod}.png'), 1) for tod in tods]
    fade_gif(keys, ['Dawn · 6:10 am', 'Day · 5:20 pm', 'Night · 9:40 pm'], os.path.join(DOCS, 'window-times.gif'))
    shutil.rmtree(TMP)
