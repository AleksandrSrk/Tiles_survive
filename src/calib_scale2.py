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
    for name, (ox, oy) in (("S0", (0, 0)), ("S1", (3, 0)), ("S2", (0, 3))):
        w = dv.ensure_focus()
        im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
        if not minimap_visible(im0):
            dv.zoom_max()
            im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
            if not minimap_visible(im0):
                print("миникарта не видна - стоп"); break
        dv.safe_click(w.left + px + ox, w.top + py + oy); time.sleep(2.2)
        dv.safe_wheel(cx, cy, 5, delta=+120, pause=0.25); time.sleep(3.5)
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
