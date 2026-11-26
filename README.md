# news-image-20261125 — The World in One Day

Entry for the make.fun bounty [Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125).

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/prosky1/news-image-20261125-entry/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/prosky1/news-image-20261125-entry/reward.svg)](https://make.fun/bounty/news-image-20261125)

Bounty: https://make.fun/bounty/news-image-20261125

## What it is

One 1024×1024 image summing up the world news of **Wednesday, 25 November 2026**:
36 stories across 9 regions as a broadsheet front page — lead stories,
thirteen pictured stories located on a world map, and twenty-three dated
briefs, every one first reported that Wednesday, with a date check naming
the nearby Tuesday stories left out.

## How it runs

- `main.py` (Python 3.13) draws the page with Pillow and writes
  `entry.png` to `MAKEFUN_OUTPUT_DIR` (default `/output`). Where Pillow
  is unavailable (the stdlib-only harness container) it publishes the
  bundled `entry.png` instead — the same bytes this code renders.
  No network; every run writes the same bytes.

## License

MIT — see `LICENSE`.
