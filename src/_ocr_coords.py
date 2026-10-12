import glob, cv2, easyocr, re, sys
r = easyocr.Reader(["en"], gpu=False, verbose=False)
for f in sorted(glob.glob(r"D:\PROJECT\TilesSurviveMap\data\720\screens\reconb2\rc_*.png")):
    im = cv2.imread(f); c = im[33:62, 830:1050]
    c = cv2.resize(c, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    print(f.split("\\")[-1], r.readtext(c, detail=0), flush=True)
