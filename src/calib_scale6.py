"""Масштаб игровых X:Y на рабочем зуме: точка 0 по синей точке миникарты, приближаем до полного HUD,
потом два драга известной длины; кадры A,B,C -> cs_*.png, сдвиг по phaseCorrelate печатается. Стоп: ScrollLock."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2
import window_manager as wm
import driver as dv
MM = (1585, 40, 1760, 165)


def minimap_visible(img):
    c = cv2.cvtColor(np.array(img)[85:120, 1640:1705], cv2.COLOR_RGB2HSV)
    return ((c[..., 0] > 30) & (c[..., 0] < 65) & (c[..., 1] > 80)).mean() > 0.25


def find_dots(img):
    a = np.array(img)[MM[1]:MM[3], MM[0]:MM[2]]
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 0] > 92) & (hsv[..., 0] < 112) & (hsv[..., 1] > 120) & (hsv[..., 2] > 200)).astype(np.uint8) * 255
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    return [(float(cen[i][0] + MM[0]), float(cen[i][1] + MM[1])) for i in range(1, n) if 6 <= st[i, 4] <= 120]


OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\calibscale"
os.makedirs(OUT, exist_ok=True)


def shift(a, b):
    roi = np.zeros((1028, 1774), np.uint8); roi[170:880, 250:1560] = 255
    sf = cv2.SIFT_create(6000); bf = cv2.BFMatcher()
    ka, da = sf.detectAndCompute(cv2.cvtColor(np.array(a), cv2.COLOR_RGB2GRAY), roi)
    kb, db = sf.detectAndCompute(cv2.cvtColor(np.array(b), cv2.COLOR_RGB2GRAY), roi)
    ms = [m for m, n in (p for p in bf.knnMatch(da, db, k=2) if len(p) == 2) if m.distance < 0.75 * n.distance]
    d = np.float32([np.array(kb[m.trainIdx].pt) - np.array(ka[m.queryIdx].pt) for m in ms]) if ms else np.zeros((0, 2), np.float32)
    best, bi = None, 0
    for x in d:
        inl = np.linalg.norm(d - x, axis=1) < 3
        if inl.sum() > bi: bi = int(inl.sum()); best = d[inl].mean(0)
    return best, bi, len(ms)

def shift_old(a, b):
    g = [cv2.cvtColor(np.array(x), cv2.COLOR_RGB2GRAY).astype(np.float32)[150:878, 300:1474] for x in (a, b)]
    win = cv2.createHanningWindow((g[0].shape[1], g[0].shape[0]), cv2.CV_32F)
    return cv2.phaseCorrelate(g[0], g[1], win)


try:
    w = dv.ensure_focus()
    dv.zoom_max()
    img, _ = wm.capture_window(OUT + r"\_map.png", settle=0.5)
    if not minimap_visible(img):
        print("миникарта не видна - стоп"); sys.exit(3)
    px, py = find_dots(img)[0]
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    fr = []
    for name, (ox, oy) in (("S0", (0, 0)), ("S1", (4, 0)), ("S2", (3, 3))):
        w = dv.ensure_focus()
        im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
        if not minimap_visible(im0):
            dv.zoom_max()
            im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
            if not minimap_visible(im0):
                print("миникарта не видна - стоп"); break
        dv.safe_click(w.left + px + ox, w.top + py + oy); time.sleep(2.2)
        total = 0
        while total < 45 and False:
            dv.safe_wheel(cx, cy, 5, delta=+120, pause=0.25); total += 5; time.sleep(2.0)
            im2, _ = wm.capture_window(OUT + r"\_z.png", settle=0.2)
            if not minimap_visible(im2): break
        dv.safe_wheel(cx, cy, 45, delta=+120, pause=0.2); time.sleep(3.0)
        print("  щелчков: 45 фикс.", flush=True)
        f, _ = wm.capture_window(OUT + rf"\cs_{name}.png", settle=0.3)
        fr.append(f)
        print("кадр", name, flush=True)
        dv.zoom_max()
    if len(fr) == 3:
        print("сдвиг S0->S1 (клик +3,0 мм):", shift(fr[0], fr[1]), flush=True)
        print("сдвиг S0->S2 (клик 0,+3 мм):", shift(fr[0], fr[2]), flush=True)
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)




