# news-image-20261125 — The World in One Day

Entry for the make.fun bounty [Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125).

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/prosky1/news-image-20261125-entry/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/prosky1/news-image-20261125-entry/reward.svg)](https://make.fun/bounty/news-image-20261125)

Bounty: https://make.fun/bounty/news-image-20261125

## What it is

One 1024×1024 image summing up the world news of **Wednesday, 25 November 2026**:
37 stories across 7 regions on a cream newspaper front page — three large
features with full-width illustrations, ten illustrated medium cards,
twenty-four sourced briefs, a world map with numbered pins 1–13, a
stories-by-region bar, and a verification legend
(CONFIRMED / OFFICIAL / REPORTED / CLAIM). Tuesday events are labelled
Tuesday on their cards; US market closes are Tuesday 24 Nov closes
reported Wednesday, Asia closes are Wednesday 25 Nov closes.

## How it runs

- `main.ts` (Node 22, standard library only) copies the bundled
  `entry.png` to `MAKEFUN_OUTPUT_DIR` (default `/output`). No network;
  every run writes the same bytes.
- `draw.py` renders `entry.png` with Pillow from the story data in
  `stories.py`.

## License

MIT — see `LICENSE`.
