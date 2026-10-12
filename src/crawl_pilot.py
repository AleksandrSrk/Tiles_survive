"""Пробный обход слоя B: сетка точек миникарты вокруг центра штата, на каждой точке дозум до полного HUD (+EXTRA щелчков),
кадр -> data/720/pilot/p_<i>.png, журнал pilot_journal.json (mm-точка, игровой X:Y центра по формуле, число щелчков).
Дальше кадры разбираются офлайн (OCR ников, сшивка по общим домам -> масштаб). Стоп: ScrollLock."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2
import window_manager as wm
import driver as dv

BASE = r"D:\PROJECT\TilesSurviveMap"
OUT = BASE + r"\data\720\pilot"
os.makedirs(OUT, exist_ok=True)
M = np.array(json.load(open(BASE + r"\assets\reference\minimap_to_game.json", encoding="utf-8"))["M"])
MM = (1585, 40, 1760, 165)
X0, Y0, STEP, NX, NY = 1662.0, 69.0, 2.0, 3, 3
EXTRA = 10


def minimap_visible(img):
    c = cv2.cvtColor(np.array(img)[85:120, 1640:1705], cv2.COLOR_RGB2HSV)
    return ((c[..., 0] > 30) & (c[..., 0] < 65) & (c[..., 1] > 80)).mean() > 0.25


def find_dots(img):
    a = np.array(img)[MM[1]:MM[3], MM[0]:MM[2]]
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 0] > 92) & (hsv[..., 0] < 112) & (hsv[..., 1] > 120) & (hsv[..., 2] > 200)).astype(np.uint8) * 255
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    return [(float(cen[i][0] + MM[0]), float(cen[i][1] + MM[1])) for i in range(1, n) if 6 <= st[i, 4] <= 120]


J = []
try:
    if dv.abort_requested():
        print("ScrollLock включён"); sys.exit(2)
    w = dv.ensure_focus()
    img, _ = wm.capture_window(OUT + r"\_probe.png", settle=0.5)
    if not dv.is_own_state(np.array(img)):
        print("[не свой штат -> goto_own_state]", dv.goto_own_state(), flush=True)
    dv.zoom_max()
    img, _ = wm.capture_window(OUT + r"\_map.png", settle=0.5)
    if not minimap_visible(img):
        print("МИНИКАРТА НЕ ВИДНА - стоп"); sys.exit(3)
    dots = find_dots(img)
    pts = []
    for j in range(NY):
        for i in range(NX):
            px, py = X0 + STEP * i, Y0 + STEP * j
            if any(((px - dx) ** 2 + (py - dy) ** 2) ** 0.5 < 7.0 for dx, dy in dots):
                print("пропуск (рядом синяя точка):", px, py, flush=True); continue
            pts.append((px, py))
    print("точек:", len(pts), flush=True)
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    for k, (px, py) in enumerate(pts):
        w = dv.ensure_focus()
        im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
        if not minimap_visible(im0):
            dv.zoom_max()
            im0, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
            if not minimap_visible(im0):
                print("миникарта не видна - стоп"); break
        dv.safe_click(w.left + px, w.top + py); time.sleep(3.0)
        total = 0; hud = False
        while total < 45:
            dv.safe_wheel(cx, cy, 5, delta=+120, pause=0.25); total += 5; time.sleep(1.8)
            im2, _ = wm.capture_window(OUT + r"\_z.png", settle=0.2)
            if not minimap_visible(im2):
                hud = True; break
        if hud:
            dv.safe_wheel(cx, cy, EXTRA, delta=+120, pause=0.25); total += EXTRA
        time.sleep(2.0)
        f = OUT + rf"\p_{k:02d}.png"; wm.capture_window(f, settle=0.3)
        g = (np.array([px, py, 1.0]) @ M).tolist()
        J.append({"k": k, "mm": [px, py], "xy": g, "clicks": total, "hud": hud, "file": f})
        json.dump(J, open(OUT + r"\pilot_journal.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[{k+1}/{len(pts)}] mm=({px:.0f},{py:.0f}) XY=({g[0]:.0f},{g[1]:.0f}) щелчков={total} hud={hud}", flush=True)
        dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)

