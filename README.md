# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/bingx12/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/bingx12/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

THE WORLD TODAY — a pure-stdlib Python program that draws Thursday 19 November 2026's world news as a one-page newspaper front page and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB, byte-identical on every run).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

No network, no clock, no randomness: `main.py` renders everything itself from bitmap glyphs in `font_data.py` (generated at build time by `tools/generate_font_data.py` from local DejaVu fonts) and encodes the PNG with `zlib`.

## The day's stories

Every story on the page was reported on Thursday 19 November 2026 (Reuters, AP, Yonhap, NASA, The Hindu, Financial Times):

- **Lead — the Gulf war spreads.** Iran's drones hit Patriot batteries at the U.S. base at Ali Al Salem, Kuwait — its first strike on Kuwait since September — hours after U.S. jets destroyed an Iranian missile site on Qeshm Island. Three tankers caught fire after hitting mines in the Strait of Hormuz; no U.S. personnel were hurt.
- **Summit — Shenzhen.** Trump, Xi and Putin meet today in the first-ever three-way summit, on the APEC sidelines. Nuclear arms, Ukraine and Iran are on the table; no deal is expected.
- **Culture — Vice City.** After 13 years, Grand Theft Auto VI launches today on PS5 and Xbox — $79.99, 212 GB, rolling midnight release, early reviews at 99 on Metacritic.
- **America — Washington.** House Democrats nominate Hakeem Jeffries for Speaker, 251–11 — on course to be the first Black Speaker when the new Congress meets in January.
- **Space.** Voyager 1 reaches one light-day from Earth — 16.1 billion miles out, so far that a radio signal takes a full day to reach it. NASA confirms the milestone today.
- **Also today.** Cyclone Akvan bears down on India's east coast (landfall Friday near noon); the EU proposes a €45 billion loan for Ukraine; Australia sanctions Israeli settlers over West Bank expansion.

---

<sub>Entered on [make.fun](https://make.fun/?ref=k6eq9xtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
