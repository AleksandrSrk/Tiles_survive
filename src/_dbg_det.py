import sys, cv2, numpy as np
sys.path.insert(0, r"D:\PROJECT\TilesSurviveMap\src")
import layer_a_process as L
im = cv2.imread(r"D:\PROJECT\TilesSurviveMap\data\720\scans\scan_20261011_172308\frames_zoom\g_x071_y+001.png")
print(L.detect(im, L.valid_mask()))
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
for (x, y) in ((1356, 411), (1450, 412)):
    print((x, y), hsv[y, x], im[y, x])
import easyocr
r = easyocr.Reader(["ru", "en"], gpu=False, verbose=False)
x, y, w, h = 1342, 397, 193, 35
for fx in (2, 3):
    crop = cv2.resize(im[max(0, y - 3):y + h + 3, max(0, x - 4):x + w + 8], None, fx=fx, fy=fx, interpolation=cv2.INTER_CUBIC)
    t = " ".join(r.readtext(crop, detail=0, paragraph=False)); print(fx, repr(t), L.parse(t))
