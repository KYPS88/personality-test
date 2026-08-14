# -*- coding: utf-8 -*-
"""แปลงเนื้อหาจาก chunk tuples เป็น JSON แยกรายบท สำหรับเสิร์ฟทีละบท"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
PT = os.path.join(os.path.dirname(HERE), "pt")
sys.path.insert(0, PT)

import mkbooks as M
import mkcomplete as C

def to_chapters(chunks):
    """แปลง chunk list เป็น list ของบท"""
    chapters = []
    cur = None
    cur_part = None
    KNOWN = {"part","h1","subtitle","h2","h3","p","bullets","callout","table","enn","worksheet"}
    for it in chunks:
        k = it[0]
        if k not in KNOWN:      # เช่น pagebreak — ไม่ใช่เนื้อหา ข้ามไป
            continue
        if k == "part":
            cur_part = re.sub(r"<br/>", " · ", it[2])
            continue
        if k == "h1":
            if cur: chapters.append(cur)
            cur = {"title": it[1], "part": cur_part, "blocks": []}
            continue
        if cur is None:
            cur = {"title": "บทนำ", "part": cur_part, "blocks": []}
        if k == "subtitle":
            cur["subtitle"] = it[1]
        elif k == "h2":
            cur["blocks"].append({"t":"h2","v":it[1]})
        elif k == "h3":
            cur["blocks"].append({"t":"h3","v":it[1]})
        elif k == "p":
            cur["blocks"].append({"t":"p","v":it[1]})
        elif k == "bullets":
            cur["blocks"].append({"t":"ul","v":list(it[1])})
        elif k == "callout":
            cur["blocks"].append({"t":"callout","title":it[1],"v":it[2]})
        elif k == "table":
            cur["blocks"].append({"t":"table","head":list(it[1]),"rows":[list(r) for r in it[2]]})
        elif k == "enn":
            cur["blocks"].append({"t":"kv","rows":[list(r) for r in it[2]]})
        elif k == "worksheet":
            cur["blocks"].append({"t":"worksheet","title":it[1],"lines":list(it[2])})
    if cur: chapters.append(cur)
    # ตัดบทที่ไม่มีเนื้อหาออก กันบทว่างโผล่ให้ผู้อ่านเห็น
    return [c for c in chapters if c.get("blocks")]

BOOKS = {}
for b in M.BOOKS:
    key = {"1-BigFive.pdf":"bigfive","2-HEXACO.pdf":"hexaco","3-Enneagram.pdf":"enneagram"}.get(b["file"])
    if not key: continue
    BOOKS[key] = {
        "id": key,
        "title": b["BOOK"]["title"],
        "subtitle": " ".join(b["BOOK"]["subtitle"]),
        "accent": b["ACC"]["main"].hexval()[2:] if hasattr(b["ACC"]["main"],'hexval') else str(b["ACC"]["main"]),
        "chapters": to_chapters(b["chunks"]),
    }

BOOKS["complete"] = {
    "id": "complete",
    "title": "ถอดรหัสบุคลิกภาพ ฉบับรวม",
    "subtitle": "Big Five · HEXACO · Enneagram",
    "accent": "D9A441",
    "chapters": to_chapters(C.CHUNKS),
}

ACCENTS = {"bigfive":"3E8E7E","hexaco":"D9A441","enneagram":"B98CCE","complete":"D9A441"}
for k,v in BOOKS.items():
    v["accent"] = ACCENTS[k]
    v["n_chapters"] = len(v["chapters"])

out = os.path.join(HERE, "content.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(BOOKS, f, ensure_ascii=False)

for k,v in BOOKS.items():
    print(k, v["n_chapters"], "บท")
print("wrote", out, os.path.getsize(out), "bytes")
