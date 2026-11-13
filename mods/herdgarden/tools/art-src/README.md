# Herdgarden art sources

The Python scripts that draw every picture in `../../art/`. Standard library only, plus `img2webp` (from `webp`) for the walk and weather loops.

To redraw everything after a change:

```sh
python3 export_herdr.py ~/.config/herdr-app/mods/herdgarden/art
```

- `scene.py` draws the valley behind the panes (3 palettes, 3 times of day, 4 seasons).
- `garden2.py`, `garden_empty.py`, and `garden_seasons.py` draw the yard.
- `villagers3.py`, `villagers_side.py`, and `villagers_seasons.py` draw the villagers and their seasonal clothes.
- `art/` holds the small sprites that have no script (homes, crops, tools).
- `index.html` is the design preview the layout was built from.
