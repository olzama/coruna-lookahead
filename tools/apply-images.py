#!/usr/bin/env python3
"""Apply a pick-images.py result: add IMAGES entries to the page, set img
in the local data/ copies, and write an ArtifactData batch (update ops).

Usage: apply-images.py result.json batch.json [--page coruna-lookahead.html]
"""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("result"); ap.add_argument("batch")
ap.add_argument("--page", default="coruna-lookahead.html")
a = ap.parse_args()
res = json.load(open(a.result))["picks"]
page = open(a.page).read()
anchor = "const IMAGES = {\n"
lines = []
for r in {r["img"]: r for r in res}.values():
    if f"  {json.dumps(r['img'])}:" in page or f"\n  {r['img']}:" in page: continue
    ent = {"src": f"img/{r['img']}.jpg", "alt": r["alt"], "credit": r["credit"], "page": r["page"]}
    lines.append(f"  {json.dumps(r['img'])}: {json.dumps(ent, ensure_ascii=False)},\n")
page = page.replace(anchor, anchor + "".join(lines), 1)
open(a.page, "w").write(page)
batch = []
for r in res:
    p = f"data/{r['col']}/{r['id']}.json"
    d = json.load(open(p)); d["img"] = r["img"]
    json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
    batch.append({"op": "update", "collection": r["col"], "doc_id": r["id"], "data": {"img": r["img"]}})
json.dump(batch, open(a.batch, "w"), ensure_ascii=False)
print(len(lines), "new images,", len(batch), "listings")
