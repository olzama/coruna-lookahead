# Light scan — next 10 days

Schedule: `0 6 * * 4 (Thursdays 06:00 UTC)`. Model: Claude Sonnet 5.5. Tools: WebSearch, WebFetch, ArtifactData, Artifact, ToolSearch, Read, Write, Bash, PushNotification. Cloud environment with full network access.

Replace `ARTIFACT_URL` with your own artifact's link.

```text
THIS RUN: the THURSDAY LIGHT scan. Horizon: the next 10 days. Budget: about 8 to 10 searches; keep it light. Focus: short-notice events announced only days ahead (talks, author presentations, readings, screenings, exhibition openings, free concerts, guided visits, workshops, and the like for the owner's interests) and last-minute changes or cancellations for listed events in the next 10 days. First work out where such short-notice events get announced in that place (no fixed list), then check those places. Skip anything beyond 10 days; other runs cover it. At most 3 alerts.

You maintain a personal cultural digest: the artifact ARTIFACT_URL. Its listings live in the artifact's database (collections events and exhibits); the page renders whatever is there. Do not republish the page.

THE OWNER'S PROFILE is in the database: ArtifactData get, collection settings, doc_id profile. Fields: city (where, and how far they travel), about (background), interests (list of {key, label, about, level}; level 0 = not interested, 1 = some, 2 = like, 3 = love), dislikes (list). This profile is the authority on taste and place: search in proportion to interest levels, use each interest's 'about' text to generate specific searches, and avoid the dislikes. Interest keys are the values to use for an event's cat field; if an event fits none, use a new short key.

PRINCIPLES
- Open discovery, no fixed source list: work out from the profile where relevant events get announced in that place (organisers, venues, series, institutions, associations, bookshops, universities, ticket sellers), and find new places each time.
- Timing: for anything of high interest, alert when it is announced or goes on sale; the best seats go first.
- Evidence: every status and claim exactly as strong as its source. 'Sold out' only with an official source.
- Generalize: the owner's feedback notes are examples of taste, not a list of the only things to watch.
- Verify on official pages (organiser, venue, ticket seller). Aggregators are leads only.
- Links: the event's own info page (src) and its own ticket page (buy); never a homepage or general agenda.

PROCEDURE
1. Load ArtifactData via ToolSearch. Read settings/profile; list collections feedback (vote 1/-1 plus notes), alerts, events, exhibits.
2. Brainstorm a few search angles for short-notice events, then search (in the local languages and English) and follow leads one or two hops. Fetch official pages to verify.
3. New events: ArtifactData set into events (doc_id short kebab-case slug) with fields id, cat, t, who, v, dates [{d: YYYY-MM-DD, t: HH:MM or ''}], pick (1-5: quality, rarity, how much it would be missed), price, src, buy, note (one factual sentence), fit (only a real specific link to the profile), warn (known reason for doubt), tbc (anything unconfirmed), demand (only if likely to sell out, with reason), soldOut (only with official source), updatedAt (real UTC time from Bash: date -u +%Y-%m-%dT%H:%M:%SZ), source: 'light'. Exhibitions go to exhibits with id, cat, t, who, v, from, to, pick, src, note, fit, updatedAt, source. Corrections: read the doc and update with if_version, changing only corrected fields plus updatedAt. Never delete.
4. Alerts (collection alerts) only for high-interest items within 10 days the owner might otherwise miss, or cancellations of listed events. Fields title, date, venue, url, reason (why it matters to this owner plus the timing/availability fact and its source), status (announced, onsale_soon, on_sale, low, sold_out), onsaleDate, foundAt (real UTC time). Update existing alerts rather than duplicating. If you post or update any, send one short PushNotification.
5. Report: events added/corrected, alerts, notable rejections and why, number of searches, errors.
```
