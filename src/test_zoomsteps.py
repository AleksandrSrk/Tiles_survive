"""Замер зума: от макс. отдаления приближаем по 5 щелчков (пауза 0.3 с между щелчками),
после каждой пятёрки кадр. Стоп: кадр перестал меняться (упор) или 80 щелчков.
Кадры: data/720/screens/zoomsteps/z_NNN.png (NNN = число щелчков). Журнал: zoom_log.json"""
import sys, os, time, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import cv2
import window_manager as wm
import driver as dv

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\zoomsteps"
os.makedirs(OUT, exist_ok=True)
log = []


def small(img):
    return cv2.resize(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY), (320, 180),
                      interpolation=cv2.INTER_AREA).astype(np.float32)


try:
    if dv.abort_requested():
        print("ScrollLock включён — выключи и запусти снова"); sys.exit(2)
    w = wm.ensure_window()
    dv.clear_popups()
    print("[1] отдаляем до упора:", dv.zoom_max(), flush=True)
    cx, cy = w.left + w.width // 2, w.top + w.height // 2
    img, _ = wm.capture_window(OUT + r"\z_000.png", settle=0.8)
    prev = small(img)
    total, still = 0, 0
    for batch in range(16):
        dv.safe_wheel(cx, cy, 5, delta=+120, pause=0.3)
        total += 5
        time.sleep(1.0)
        img, _ = wm.capture_window(OUT + rf"\z_{total:03d}.png", settle=0.5)
        cur = small(img)
        d = float(np.abs(cur - prev).mean())
        log.append({"clicks": total, "diff_prev": round(d, 2)})
        print(f"щелчков {total}: diff={d:.2f}", flush=True)
        still = still + 1 if d < 1.5 else 0
        prev = cur
        if still >= 2:
            print("кадр перестал меняться — упор приближения", flush=True)
            break
    json.dump(log, open(OUT + r"\zoom_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[2] возвращаем максимальное отдаление", flush=True)
    dv.zoom_max()
    print("готово, всего щелчков:", total, flush=True)
except dv.Aborted as e:
    print("ОСТАНОВЛЕНО:", e)
except dv.FocusLost as e:
    print("ФОКУС ПОТЕРЯН:", e)
