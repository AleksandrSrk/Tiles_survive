import json, re, cv2, easyocr
D = r"D:\PROJECT\TilesSurviveMap\data\720\screens\calib"
J = json.load(open(D + r"\calib_journal.json", encoding="utf-8"))
r = easyocr.Reader(["en"], gpu=False, verbose=False)
out = []
for p in J:
    res = {}
    for k in ("a", "b"):
        im = cv2.imread(p[k]); c = im[36:60, 868:1040]
        c = cv2.resize(c, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        t = " ".join(r.readtext(c, detail=0, allowlist="0123456789XY:#. "))
        res[k] = t
    out.append({**{kk: p[kk] for kk in ("i", "dx", "dy")}, **res})
    print(out[-1], flush=True)
json.dump(out, open(D + r"\calib_ocr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
