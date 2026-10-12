"""OCR всех кадров пробного обхода -> data/720/pilot/pilot_ocr.json (текст, центр bbox в px кадра, conf). Только обычный (не админ) процесс."""
import json, os, sys, time
import cv2, easyocr
D = r"D:\PROJECT\TilesSurviveMap\data\720\pilot"
J = json.load(open(D + r"\pilot_journal.json", encoding="utf-8"))
r = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)
Y0, Y1, X0, X1 = 150, 880, 20, 1560
out = []
for p in J:
    im = cv2.imread(p["file"])[Y0:Y1, X0:X1]
    t = time.time()
    res = r.readtext(im, detail=1, paragraph=False)
    items = []
    for box, txt, cf in res:
        xs = [q[0] for q in box]; ys = [q[1] for q in box]
        items.append({"t": txt, "c": round(float(cf), 2), "x": round(sum(xs) / 4 + X0, 1), "y": round(sum(ys) / 4 + Y0, 1),
                      "h": round(max(ys) - min(ys), 1), "w": round(max(xs) - min(xs), 1)})
    out.append({"k": p["k"], "xy": p["xy"], "mm": p["mm"], "clicks": p["clicks"], "items": items})
    print(p["k"], len(items), round(time.time() - t, 1), flush=True)
    json.dump(out, open(D + r"\pilot_ocr.json", "w", encoding="utf-8"), ensure_ascii=False)
print("готово")
