#!/usr/bin/env python3
"""Apply a pick-images.py result.

Writes an ArtifactData batch: an `images` doc per new picture ({src, alt,
credit, page}) and an update setting `img` on each listing. With --page,
also adds the pictures to the page's inline IMAGES map; with --data, sets
`img` in the local data/ copies.

Usage: apply-images.py result.json batch.json [--page coruna-lookahead.html] [--data]
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("result"); ap.add_argument("batch")
ap.add_argument("--page"); ap.add_argument("--data", action="store_true")
a = ap.parse_args()
res = json.load(open(a.result))["picks"]
uniq = {r["img"]: r for r in res}.values()
entry = lambda r: {"src": r.get("src") or f"img/{r['img']}.jpg", "alt": r["alt"], "credit": r["credit"], "page": r["page"]}
batch = [{"op": "set", "collection": "images", "doc_id": r["img"], "data": entry(r)} for r in uniq]
if a.page:
    page = open(a.page).read()
    anchor = "const IMAGES = {\n"
    lines = [f"  {json.dumps(r['img'])}: {json.dumps(entry(r), ensure_ascii=False)},\n" for r in uniq if f"  {json.dumps(r['img'])}:" not in page]
    open(a.page, "w").write(page.replace(anchor, anchor + "".join(lines), 1))
for r in res:
    if a.data:
        p = f"data/{r['col']}/{r['id']}.json"
        if os.path.exists(p):
            d = json.load(open(p)); d["img"] = r["img"]
            json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
    batch.append({"op": "update", "collection": r["col"], "doc_id": r["id"], "data": {"img": r["img"]}})
json.dump(batch, open(a.batch, "w"), ensure_ascii=False)
print(len(uniq), "images,", len(res), "listings; batch entries for existing docs need if_version")
