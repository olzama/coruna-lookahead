#!/usr/bin/env python3
"""Pick freely licensed pictures for digest listings from Wikimedia Commons.

Input (plan JSON): a list of items
  {"id": "...", "col": "events"|"exhibits", "date": "YYYY-MM-DD",
   "subjects": [{"q": "search text", "kind": "person|work|place|theme"}, ...]}
Subjects are written per item (by a person or a model) from most to least
specific; nothing about venues or artists is built into this script.

For each item, in date order, the script searches Commons for every subject,
keeps only properly licensed raster images of usable size, and scores them:
  + relevance (search rank, earlier subjects preferred)
  - reuse (an image already used, more strongly the more often; capped)
  - sameness (the same kind of picture as the previous two listings)
It downloads the winner at 640 px into img/ and writes a result JSON with
the image key, kind, credit and source page for every assignment.

Usage: pick-images.py plan.json result.json [--img-dir img] [--max-reuse 2]
"""
import argparse, hashlib, json, re, subprocess, sys, time, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "CorunaLookahead/1.0 (https://github.com/olzama/coruna-lookahead; olga.zamaraeva@gmail.com)"
OK_LICENSE = re.compile(r"^(public domain|pd|cc0|cc by(-sa)?( \d(\.\d)?)?( [a-z]{2,})?)$", re.I)
SKIP_TITLE = re.compile(r"logo|map|mapa|stamp|sello|coat of arms|escudo|flag|bandera|diagram|chart|signature|firma|icon|\.pdf|\.svg|\.tif", re.I)


def api(params, tries=4):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(8 * (i + 1))
    return {}


def candidates(q, limit=8):
    d = api({"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": limit,
             "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 800})
    pages = sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for rank, p in enumerate(pages):
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata") or {}
        g = lambda k: re.sub(r"<[^>]+>", "", (m.get(k) or {}).get("value", "")).strip()
        lic, title = g("LicenseShortName"), p.get("title", "")[5:]
        if ii.get("mime") not in ("image/jpeg", "image/png"): continue
        if (ii.get("width") or 0) < 600 or SKIP_TITLE.search(title): continue
        if not OK_LICENSE.match(lic.replace("Public Domain", "public domain")): continue
        artist = re.sub(r"\s+", " ", g("Artist"))[:80] or "unknown author"
        out.append({"title": title, "rank": rank, "lic": lic, "artist": artist,
                    "url": (ii.get("thumburl") or ii.get("url", "")).split("?")[0],
                    "page": ii.get("descriptionurl", ""), "desc": g("ImageDescription")[:120]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("result")
    ap.add_argument("--img-dir", default="img"); ap.add_argument("--max-reuse", type=int, default=2)
    a = ap.parse_args()
    plan = sorted(json.load(open(a.plan)), key=lambda x: x.get("date", ""))
    used, recent_kinds, result = {}, [], []
    for item in plan:
        best = None
        for si, s in enumerate(item["subjects"]):
            for c in candidates(s["q"]):
                n = used.get(c["title"], 0)
                if n >= a.max_reuse: continue
                score = 1.0 / (1 + c["rank"]) + (1 - 0.15 * si) - 0.6 * n
                score -= 0.35 * sum(k == s["kind"] for k in recent_kinds[-2:])
                if not best or score > best[0]: best = (score, c, s)
            time.sleep(1.5)
        if not best:
            print(f"none  {item['id']}", file=sys.stderr); continue
        _, c, s = best
        key = "c-" + hashlib.sha1(c["title"].encode()).hexdigest()[:10]
        if c["title"] not in used:
            raw = f"/tmp/{key}.src"
            subprocess.run(["curl", "-s", "-m", "40", "-A", UA, c["url"], "-o", raw], check=False)
            r = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", "640", raw, "--out", f"{a.img_dir}/{key}.jpg"], capture_output=True)
            if r.returncode: print(f"fail  {item['id']} {c['title']}", file=sys.stderr); continue
            time.sleep(1.5)
        used[c["title"]] = used.get(c["title"], 0) + 1
        recent_kinds.append(s["kind"])
        credit = f"{c['title'].rsplit('.', 1)[0]}, by {c['artist']}, {c['lic']} (Wikimedia Commons)."
        result.append({"id": item["id"], "col": item["col"], "img": key, "kind": s["kind"], "subject": s["q"],
                       "file": c["title"], "credit": credit, "page": c["page"], "alt": c["desc"] or s["q"]})
        print(f"{s['kind']:7} {item['id']:22} <- {c['title'][:60]} ({c['lic']})", file=sys.stderr)
        json.dump(result, open(a.result, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
