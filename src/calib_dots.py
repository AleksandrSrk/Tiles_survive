"""Калибровка миникарта -> игровые X:Y по СИНИМ ТОЧКАМ миникарты (домики нашего союза).
Вблизи нашего домика на глубоком зуме появляется полный HUD со строкой '#720 X:.. Y:..'.
Безопасность: клик по миникарте только когда миникарта видна (зелёный ромб в ней); иначе zoom_max.
Кадры: data/720/screens/calibdots/cd_<i>.png + журнал calibdots_journal.json (позиция точки в окне). Стоп: ScrollLock."""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np, cv2
import window_manager as wm
import driver as dv
OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\calibdots"
os.makedirs(OUT, exist_ok=True)
MM = (1585, 40, 1760, 165)  # область миникарты в кадре окна (x0,y0,x1,y1)


def minimap_visible(img):
    c = cv2.cvtColor(np.array(img)[85:120, 1640:1705], cv2.COLOR_RGB2HSV)
    g = ((c[..., 0] > 30) & (c[..., 0] < 65) & (c[..., 1] > 80)).mean()
    return g > 0.25


def find_dots(img):
    a = np.array(img)[MM[1]:MM[3], MM[0]:MM[2]]
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 0] > 92) & (hsv[..., 0] < 112) & (hsv[..., 1] > 120) & (hsv[..., 2] > 200)).astype(np.uint8) * 255
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, n):
        if 6 <= st[i, 4] <= 120:
            out.append((float(cen[i][0] + MM[0]), float(cen[i][1] + MM[1])))
    return out


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
        print("МИНИКАРТА НЕ ВИДНА после zoom_max - стоп"); sys.exit(3)
    dots = find_dots(img)
    print("синих точек:", len(dots), dots, flush=True)
    for i, (px, py) in enumerate(dots[:4]):
        w = dv.ensure_focus()
        img, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
        if not minimap_visible(img):
            dv.zoom_max()
            img, _ = wm.capture_window(OUT + r"\_chk.png", settle=0.3)
            if not minimap_visible(img):
                print("миникарта не видна - стоп"); break
        dv.safe_click(w.left + px, w.top + py)
        time.sleep(2.2)
        cx, cy = w.left + w.width // 2, w.top + w.height // 2
        # приближаем партиями, пока не включится полный HUD (миникарта пропала) или лимит 45 щелчков
        total = 0
        while total < 45:
            dv.safe_wheel(cx, cy, 5, delta=+120, pause=0.25)
            total += 5
            time.sleep(2.0)
            im2, _ = wm.capture_window(OUT + r"\_z.png", settle=0.2)
            if not minimap_visible(im2):
                break
        time.sleep(1.5)
        print("  щелчков:", total, flush=True)
        f = OUT + rf"\cd_{i:02d}.png"; wm.capture_window(f, settle=0.3)
        J.append({"i": i, "mm_x": px, "mm_y": py, "file": f})
        json.dump(J, open(OUT + r"\calibdots_journal.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("точка", i, round(px), round(py), flush=True)
        dv.zoom_max()
    print("готово", flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)

