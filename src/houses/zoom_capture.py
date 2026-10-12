"""ОБУЧЕНИЕ зума (запускать через admin-раннер, нужна игра на экране; ScrollLock = стоп).
Камеру поставь так, чтобы в центре/рядом был посёлок с белым (чужим) домиком, не трогай мышь.
Бот: отдаляется до упора, потом приближает ПО ОДНОМУ щелчку колеса с паузой 1,5 с (домики подгружаются)
и снимает кадр после каждого щелчка: data/720/screens/zoom_house/c_NN.png (NN = число щелчков от макс. отдаления).
Останавливается, когда кадр перестал меняться (упор приближения) или после 60 щелчков.
Дальше НЕ здесь: python src\\houses\\zoom_analyze.py (без игры, обычный процесс) решает, сколько щелчков нужно."""
import os
import sys
import time

import cv2
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import driver as dv  # noqa: E402
import window_manager as wm  # noqa: E402

OUT = r"D:\PROJECT\TilesSurviveMap\data\720\screens\zoom_house"
PAUSE = 1.5        # пауза после каждого щелчка, с
MAX_CLICKS = 60


def small(img):
    return cv2.resize(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY), (320, 180),
                      interpolation=cv2.INTER_AREA).astype(np.float32)


def main():
    os.makedirs(OUT, exist_ok=True)
    if dv.abort_requested():
        print("ScrollLock включён: выключи и запусти снова")
        sys.exit(2)
    try:
        w = wm.ensure_window()
        dv.clear_popups()
        print("[1] отдаляем до упора:", dv.zoom_max(), flush=True)
        cx, cy = w.left + w.width // 2, w.top + w.height // 2
        img, _ = wm.capture_window(os.path.join(OUT, "c_00.png"), settle=1.0)
        prev, still = small(img), 0
        for k in range(1, MAX_CLICKS + 1):
            dv.safe_wheel(cx, cy, 1, delta=+120, pause=0.05)
            time.sleep(PAUSE)
            img, _ = wm.capture_window(os.path.join(OUT, f"c_{k:02d}.png"), settle=0.3)
            cur = small(img)
            d = float(np.abs(cur - prev).mean())
            print(f"щелчков {k}: diff={d:.2f}", flush=True)
            still = still + 1 if d < 1.5 else 0
            prev = cur
            if still >= 2:
                print("кадр перестал меняться: упор приближения", flush=True)
                break
        print("готово. Дальше: python src\\houses\\zoom_analyze.py", flush=True)
    except dv.Aborted as e:
        print("ОСТАНОВЛЕНО:", e)
    except dv.FocusLost as e:
        print("ФОКУС ПОТЕРЯН:", e)


if __name__ == "__main__":
    main()


