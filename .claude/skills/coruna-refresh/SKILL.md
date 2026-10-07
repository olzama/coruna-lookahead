---
name: coruna-refresh
description: Refresh the Coruña Lookahead digest — open-ended, profile-driven discovery of events in and around A Coruña, verified on official pages, with exact info and ticket links. Use when asked to refresh, update or extend the digest, or to look for events.
---

# Coruña Lookahead refresh

The digest is `coruna-lookahead.html`, published at https://claude.ai/artifact/7GdwbbBHm11NWEP9tGReGn. Its listings live in the artifact's database: collections `events` and `exhibits` (readable by every viewer, writable by the owner), plus the owner-only `feedback` and `alerts`. The page renders whatever the database holds; the `EVENTS` / `EXHIBITS` arrays in the HTML are only a fallback snapshot for viewers without database access. `data/events/` and `data/exhibits/` hold a local copy of the documents. Three cloud routines also add and correct events and post alerts: a monthly 6-month deep scan, a weekly 30-day scan (Mondays) and a Thursday 10-day light scan. The owner reads the digest to decide how to spend evenings and weekends, so missing something they would have loved is the worst failure, and a wrong date or a link that makes them hunt is the second worst.

## Principles

- **Generalize from the owner's remarks.** A specific complaint or example illustrates a requirement for the whole digest. Fix the class of problem; never record the example itself as a fact without evidence.
- **Evidence-strength wording.** Statuses and claims (sold out, limited availability, popular, sells out fast) only when a source says so, worded exactly as strongly as the source.
- **Timing.** For high-interest events, the moment that matters is announcement or on-sale, because the best seats go first. Surface on-sale dates and flag such events in `DEMAND` from the start, not when they are nearly gone.

## 0. Know the person first

Read the owner's profile from the database (`ArtifactData` `get`, collection `settings`, doc `profile`: city, about, interests with levels, dislikes); it is the authority on taste and place, and interest keys are the event categories. Also read the project memory: the user profile, the precise-links rule, the project notes and loose ends. Then read the page's feedback with `ArtifactData` `list` on collection `feedback` and on `alerts`. Treat votes and notes as the strongest signal of taste: a "Not for me" with a reason describes a whole class of events to avoid, and a "More like this" describes a class to seek.

Write yourself a short brief before searching: what this person cares about now, what they used to love, what they dislike, their work, their languages, where they come from, their dog, and what kinds of events they would not think to look for but would value. Facts in the profile are evidence, not a checklist.

## 1. Discover broadly, not from a list

The aim is recall. Fixed source lists and keyword lists miss things, so generate the search space fresh each time from the brief:

- **Brainstorm angles** (aim for 30 or more): for each interest, ask what form it takes locally and who would organise it. Example: languages leads to the language schools (EOI), university philology faculties, cultural associations of Russian, Ukrainian, Greek and other communities, translation prizes and Galician-language institutions. A dog leads to adoption days, canicross, dog-friendly beaches and walks, shelter fundraisers and vet talks. Chess leads to clubs, simultaneous exhibitions, school and open tournaments and café chess nights. Include adjacent things the profile suggests but does not name: architecture, science talks, lectures by visiting writers, film clubs, choirs, early music, book fairs, markets of old books, nature walks, astronomy nights.
- **Search in Spanish and Galician, and in English** where useful. Search for organisers and venues, not only for event types.
- **Sweep the known structured sources**, every category and not a filtered subset:
  - the city agenda iCal (all categories; see project memory for the URL and IDs);
  - city news (coruna.gal novas), where some events appear only as announcements;
  - each venue's own agenda (Palacio de la Ópera, OSG, Amigos de la Ópera, Rosalía, Colón, Fórum, Filmoteca, Barrié, Afundación, Belas Artes, Fundación Luis Seoane, MUNCYT, Domus, Casa de las Ciencias, Aquarium, Kiosco Alfonso, Palacio Municipal, libraries, UDC, bookshops such as Moito Conto and Formatos);
  - Ataquilla venue pages and its site search (browser method below), which also reveals events nobody else lists.
- **Follow leads**: every page found points to organisers, cycles and partner venues. Follow the promising ones one or two hops.
- **Look slightly beyond the city** (Santiago, Ferrol, Betanzos) for things of unusual interest, and mark the travel.
- **Look further ahead** (up to 6 months) for things that will sell out, and note their on-sale dates.

Keep a candidate list with the source of each.

## 2. Verify every candidate on an official page

Aggregators (Quincemil, Planomato, Páxinas Galegas) are leads only: they have shown wrong prices, wrong dates and events that do not exist. Confirm date, time, venue, price and programme on the organiser's or venue's own page, or in the ticket system. When sources disagree, prefer the ticket system, then the organiser, then the venue, and mark the disagreement as "to confirm".

## 3. Get the most precise links

Each listing needs its own info page (`src`) and, if ticketed, the exact ticket page (`buy`). Follow the precise-links rule in memory. For Ataquilla, use Claude in Chrome: open the venue page (`/es/ventaentradas/recintos/<id>-<venue>`) or the search (`/es/ventaentradas/resultados-busqueda?query=<title>`), then run `tools/ataquilla-venue-extract.js` to read each card's `product_uri`, `sold_out` and session dates. Other sellers (Ticketmaster, Entradas.com, El Corte Inglés, Eventbrite, the organiser's own form or email) get the same treatment: link the event's page, never a homepage. Registration by email: put the address in `reg`.

## 4. Judge and write

- Rate each listing: `q` (1–10, quality and how much it would be missed; 9–10 only for exceptional), `rare` (0 regular, 1 uncommon, 2 rare: a once-in-years visit, premiere or retrospective), `fitw` (1–2, strength of a `fit`), and for similarity `people` (performers, creators, companies), `works` (composers, authors, directors, artists) and `series` (short key for the season or cycle). Keep `pick` (1–5) as a coarse fallback. The page scores from these (see its scoring comment): the top 5% (at least 3) of everything ahead are Don't miss, the next 10% Recommended; likes and visits carry over through shared people, works and series.
- Write a `PROFILE` `fit` note only when there is a real, specific connection to this person, and a `warn` note when there is a known reason for doubt (a touring company with recorded music, for example). No generic praise.
- Pictures appear in Highlights, on Don't miss and Recommended listings, and in the exhibitions column, not in the event list. Give every highly rated listing and every exhibition a picture. For each one without a picture, write 2–4 subjects into a plan for `tools/pick-images.py` (see its header), most specific first and of mixed kinds: the person, the work, the place, or a theme the event is about. Use exact names with a `hint` (e.g. "composer") so Wikidata finds the right entity; make theme queries descriptive ("violin and piano duo recital"). The tool takes Wikidata images, Commons categories and phrase searches, keeps only public domain / CC0 / CC BY / CC BY-SA files, and spreads kinds and limits reuse. Review every pick against its listing (look at the image): replace wrong ones, and give an image a focal point `pos` ("x% y%") when its subject is far from the top third, since cards crop to a wide frame; find a Commons file or category by web search (`site:commons.wikimedia.org`) and pass it as `file` or `cat`, or leave the listing without a picture. Then run `tools/apply-images.py result.json batch.json --data` (writes `images` docs with the credits and sets `img` on the listings), publish the page with the new `img/` files, and apply the batch. Event photos from venues and publishers are copyrighted; don't use them.
- Add to `DEMAND` whatever is likely to sell out, with the reason.
- Use or extend the categories in `CATS`; add a new type when a real cluster appears.
- Write each new or changed event with `ArtifactData` (`set` for new, `update` with `if_version` for changes) using the schema the routines use: id, cat, t, who, v, dates [{d, t}], pick, q, rare, fitw, people, works, series, far, price, src, buy, note, fit, warn, tbc, demand, soldOut, img, updatedAt, source. Keep the local copy in `data/` in sync. Past events may stay; the page hides them.
- Occasionally regenerate the HTML fallback snapshot from the database and republish, so signed-out visitors don't see stale listings.

## 5. Publish and report

Republish the page only when its code or the fallback snapshot changed (syntax-check first). Report briefly: what is new, what was corrected, which candidates were rejected and why, and the loose ends. Update the project memory: sources that proved useful, sources that proved unreliable, and resolved or new loose ends.
