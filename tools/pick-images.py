#!/usr/bin/env python3
"""Pick freely licensed pictures for digest listings from Wikimedia Commons.

Input (plan JSON): a list of items
  {"id": "...", "col": "events"|"exhibits", "date": "YYYY-MM-DD",
   "subjects": [{"q": "...", "kind": "person|work|place|theme", "hint": "...", "file": "..."}, ...]}
Subjects are written per item (by a person or a model), most specific first;
nothing about venues or artists is built into this script.
  q     name (person, work, place) or descriptive text (theme)
  hint  optional word expected in the Wikidata description, to pick the
        right entity among namesakes (e.g. "writer", "film", "ballet")
  file  optional Commons file title found by other means (e.g. web search)
  cat   optional Commons category to draw from (e.g. "Les Cousins (film)")

Lookup per subject, from most to least exact:
  1. file, if given;
  2. cat, if given: files in that Commons category;
  3. Wikidata: entity labelled q (matching hint) -> its image (P18), or else
     files in its Commons category (P373);
  4. Commons search: names quoted as a phrase; for people, the name must
     also appear in the file's title or description.
Every candidate's licence and author come from Commons' own metadata;
only public domain, CC0, CC BY and CC BY-SA raster images of usable size pass.

Assignment, in date order, scores candidates by exactness and subject order,
penalises reuse (capped by --max-reuse) and the same kind of picture as the
previous two listings. Winners are saved at 640 px in img/; the result JSON
holds key, kind, method, credit and source page per listing, and lists the
items with no picture under "none".

Usage: pick-images.py plan.json result.json [--img-dir img] [--max-reuse 2]
"""
import argparse, hashlib, json, os, re, subprocess, sys, time, unicodedata, urllib.parse

COMMONS = "https://commons.wikimedia.org/w/api.php"
WIKIDATA = "https://www.wikidata.org/w/api.php"
UA = "CorunaLookahead/1.0 (https://github.com/olzama/coruna-lookahead; olga.zamaraeva@gmail.com)"
OK_LICENSE = re.compile(r"^(public domain|pd\b.*|cc0( 1\.0)?|cc by(-sa)?( \d(\.\d)?)?( [a-z]{2,})?)$", re.I)
SKIP_TITLE = re.compile(r"logo|\bmap\b|mapa|stamp|sello|coat of arms|escudo|flag|bandera|diagram|chart|signature|firma|icon|\.pdf|\.svg|\.tif", re.I)
EXACT = {"file": 1.0, "wikidata": 0.9, "category": 0.8, "search": 0.5}


def get(api, params, tries=4):
    url = api + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-m", "30", "-A", UA, url], capture_output=True, text=True)
        try:
            out = json.loads(r.stdout)
            time.sleep(1)
            return out
        except ValueError:
            time.sleep(8 * (i + 1))
    return {}


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


IIPROP = {"prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 800}


def info(pages):
    """Commons pages with imageinfo -> licensed candidates, in search order."""
    out = []
    for p in sorted(pages, key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata") or {}
        g = lambda k: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", (m.get(k) or {}).get("value", ""))).strip()
        title, lic = p.get("title", "")[5:], g("LicenseShortName")
        if ii.get("mime") not in ("image/jpeg", "image/png"): continue
        if (ii.get("width") or 0) < 600 or SKIP_TITLE.search(title): continue
        if not OK_LICENSE.match(lic): continue
        out.append({"title": title, "lic": lic, "artist": g("Artist")[:80] or "unknown author",
                    "url": ii.get("thumburl") or ii.get("url", ""), "page": ii.get("descriptionurl", ""),
                    "desc": g("ImageDescription")[:160]})
    return out


def by_file(title):
    d = get(COMMONS, {"action": "query", "titles": "File:" + title, **IIPROP})
    return info((d.get("query") or {}).get("pages", {}).values())


def by_category(cat):
    d = get(COMMONS, {"action": "query", "generator": "categorymembers", "gcmtitle": "Category:" + cat,
                      "gcmtype": "file", "gcmlimit": 12, **IIPROP})
    return info((d.get("query") or {}).get("pages", {}).values())


def by_wikidata(q, hint):
    d = get(WIKIDATA, {"action": "wbsearchentities", "search": q, "language": "en", "uselang": "en", "limit": 7})
    for e in d.get("search", []):
        labels = [e.get("label", "")] + list(e.get("aliases") or [])
        if fold(q) not in [fold(l) for l in labels]: continue
        if hint and fold(hint) not in fold(e.get("description", "")): continue
        claims = get(WIKIDATA, {"action": "wbgetclaims", "entity": e["id"]}).get("claims") or {}
        val = lambda p: next((c["mainsnak"].get("datavalue", {}).get("value") for c in claims.get(p, [])), None)
        if val("P18"): return by_file(val("P18"))
        if val("P373"): return by_category(val("P373"))
        return []
    return []


def by_search(q, kind):
    phrase = kind in ("person", "work")
    d = get(COMMONS, {"action": "query", "generator": "search", "gsrsearch": f'"{q}"' if phrase else q,
                      "gsrnamespace": 6, "gsrlimit": 8, **IIPROP})
    out = info((d.get("query") or {}).get("pages", {}).values())
    if kind == "person":
        toks = [t for t in fold(q).split() if len(t) > 2]
        out = [c for c in out if all(t in fold(c["title"] + " " + c["desc"]) for t in toks)]
    return out


def lookup(s):
    if s.get("file"):
        return [(c, "file") for c in by_file(s["file"])]
    found = [(c, "category") for c in by_category(s["cat"])] if s.get("cat") else []
    if s["kind"] in ("person", "work", "place"):
        found += [(c, "wikidata") for c in by_wikidata(s["q"], s.get("hint"))]
    found += [(c, "search") for c in by_search(s["q"], s["kind"])]
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("result")
    ap.add_argument("--img-dir", default="img"); ap.add_argument("--max-reuse", type=int, default=2)
    a = ap.parse_args()
    plan = sorted(json.load(open(a.plan)), key=lambda x: x.get("date", ""))
    used, kinds, picks, none = {}, [], [], []
    for item in plan:
        best = None
        for si, s in enumerate(item["subjects"]):
            for rank, (c, how) in enumerate(lookup(s)):
                n = used.get(c["title"], 0)
                if n >= a.max_reuse: continue
                score = EXACT[how] + 0.3 / (1 + rank) - 0.2 * si - 0.6 * n
                score -= 0.25 * sum(k == s["kind"] for k in kinds[-2:])
                if not best or score > best[0]: best = (score, c, s, how)
        if not best:
            none.append(item["id"]); print(f"none    {item['id']}", file=sys.stderr); continue
        _, c, s, how = best
        key = "c-" + hashlib.sha1(c["title"].encode()).hexdigest()[:10]
        dest = f"{a.img_dir}/{key}.jpg"
        if not os.path.exists(dest):
            raw = f"/tmp/{key}.src"
            subprocess.run(["curl", "-s", "-m", "40", "-A", UA, c["url"], "-o", raw], check=False)
            r = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", "640", raw, "--out", dest], capture_output=True)
            if r.returncode:
                none.append(item["id"]); print(f"fail    {item['id']} {c['title']}", file=sys.stderr); continue
        used[c["title"]] = used.get(c["title"], 0) + 1
        kinds.append(s["kind"])
        picks.append({"id": item["id"], "col": item["col"], "img": key, "kind": s["kind"], "how": how,
                      "subject": s["q"], "file": c["title"], "page": c["page"], "alt": c["desc"] or s["q"],
                      "credit": f"{c['title'].rsplit('.', 1)[0]}, by {c['artist']}, {c['lic']} (Wikimedia Commons)."})
        print(f"{s['kind']:7} {how:8} {item['id']:22} <- {c['title'][:60]} ({c['lic']})", file=sys.stderr)
        json.dump({"picks": picks, "none": none}, open(a.result, "w"), ensure_ascii=False, indent=1)
    json.dump({"picks": picks, "none": none}, open(a.result, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
