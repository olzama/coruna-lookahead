# Coruña Lookahead

A personal cultural digest for A Coruña: a weekly, monthly and long-range view of concerts, opera, theatre, dance, cinema, exhibitions, literature, chess and other events, ranked by the owner's interests and kept current by scheduled Claude scans.

Live page: https://claude.ai/artifact/7GdwbbBHm11NWEP9tGReGn

## How it works

- **The page** (`coruna-lookahead.html`) is a Claude artifact. It shows events by week, the next 30 days or everything ahead; ranks them by the owner's interest levels and an editorial rating; highlights what not to miss and what to book early; and links each listing to its own info page and, where possible, its exact ticket page.
- **The data** lives in the artifact's database:
  - `events` and `exhibits`: the listings, readable by every viewer.
  - `settings/profile`: the owner's interests (each with a description and a level), dislikes, background and location. Edited on the page; private to the owner.
  - `feedback` (likes, dislikes and notes on listings) and `alerts` (early warnings): private to the owner.
  The HTML also carries a snapshot of the listings for viewers without database access.
- **Scheduled scans** (Claude Code routines, prompts in `routines/`) search the web, verify events on official pages and write to the database:
  - monthly: 30 days to 6 months ahead (seasons, on-sale dates);
  - weekly: the next 30 days;
  - light: the next 10 days (short-notice events).
  The scans take the owner's taste from the profile and work out where to look each time; there is no fixed source list.
- **Manual refresh**: the Claude Code skill in `.claude/skills/coruna-refresh/` does a full, deeper pass, including reading ticket sites through a browser.
- `tools/ataquilla-venue-extract.js` lists the exact event pages on an Ataquilla venue page (run in a browser).

## Making your own

You need a paid Claude plan that includes Claude Code cloud sessions (Pro or above). The scans run on your plan's usage limits.

1. Publish your own copy of `coruna-lookahead.html` as a Claude artifact (or copy the live page from claude.ai).
2. Open it and fill in **Your interests**: your city, what you care about and how much, and what you don't want.
3. Create the three routines at claude.ai/code/routines using the prompts in `routines/`, with your artifact's link in place of `ARTIFACT_URL`, in a cloud environment with full network access.
4. Optionally clear the starting listings; the first scans will fill them for your city.

## Licence

© 2026 Olga Zamaraeva. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): free to copy and adapt, including commercially, with credit to Olga Zamaraeva. Event information belongs to the venues and organisers; images are from Wikimedia Commons under their own licences. See `LICENSE.md`.
