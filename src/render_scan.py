"""Рисует карту по скану из БД, без OCR: python src\\render_scan.py [--state 720] [--scan ID]  (по умолчанию последний)"""
import argparse, os, sqlite3, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_template
ap = argparse.ArgumentParser(); ap.add_argument("--state", default="720"); ap.add_argument("--scan", type=int); ap.add_argument("--out")
a = ap.parse_args()
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db = sqlite3.connect(os.path.join(base, "data", a.state, "layer_a.sqlite"))
sid = a.scan or db.execute("SELECT max(id) FROM scans WHERE state=? AND layer='A'", (a.state,)).fetchone()[0]
when = db.execute("SELECT scanned_at FROM scans WHERE id=?", (sid,)).fetchone()[0]
own = {c: {"tag": t, "rgb": [r, g, b] if r is not None else None} for c, t, r, g, b in db.execute("SELECT cell_id,tag,r,g,b FROM cell_owners WHERE scan_id=?", (sid,))}
out = a.out or os.path.join(base, "data", a.state, f"map_{a.state}_scan{sid}.png")
render_template.render(own, out, title=f"Штат {a.state} · слой А", subtitle=when.replace("T", "  "))
print(out)
