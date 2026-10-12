"""Поиск домиков на одном кадре. Домик на этом зуме = «горшок» с цифрой уровня под ним.
Цвет: blue = союзник, white = остальные, green = моё поселение, pink = лидер союза.
Метод: цветное template matching (NCC по 3 каналам) по шаблонам из assets/houses/<вид>.png,
потом подавление не-максимумов. Координата домика = центр шаблона на кадре (px, py).
Зоны HUD (миникарта, чат, кнопки) игнорируются, там домиков не ищем."""
import glob
import os
from dataclasses import dataclass

import cv2
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL_DIR = os.path.join(BASE, "assets", "houses")

# зоны HUD в долях кадра (x0, y0, x1, y1): миникарта+легенда справа сверху, чат снизу, кнопка «Поселение»
HUD_ZONES = [(0.885, 0.0, 1.0, 0.30), (0.0, 0.935, 1.0, 1.0), (0.92, 0.88, 1.0, 1.0)]
TITLE_BAR_PX = 30      # строка заголовка окна в скриншоте
MIN_SCORE = 0.5        # порог NCC (подобран на одном скрине, при смене зума пересмотреть)


@dataclass
class Detection:
    x: int
    y: int
    score: float
    kind: str


def load_templates(tpl_dir=TPL_DIR):
    tpls = {}
    for p in sorted(glob.glob(os.path.join(tpl_dir, "*.png"))):
        tpls[os.path.splitext(os.path.basename(p))[0]] = cv2.imread(p)
    if not tpls:
        raise RuntimeError(f"нет шаблонов в {tpl_dir}; сделай их: python src/houses/tools/make_templates.py")
    return tpls


def _ncc(img, t):
    ch = [cv2.matchTemplate(img[:, :, c].astype(np.float32), t[:, :, c].astype(np.float32), cv2.TM_CCOEFF_NORMED)
          for c in range(3)]
    return sum(ch) / 3.0


def classify_color(frame_bgr, x, y, scale=1.0):
    """вид домика по цвету корпуса горшка (верхняя часть шаблона): blue / white / green / pink / other.
    Шаблоны у разных видов почти одинаковой формы, поэтому argmax шаблона для вида не годится."""
    y0, y1, dx = int(18 * scale), max(int(4 * scale), 1), max(int(8 * scale), 1)
    hsv = cv2.cvtColor(frame_bgr[max(0, y - y0):max(1, y - y1), max(0, x - dx):x + dx + 1], cv2.COLOR_BGR2HSV).reshape(-1, 3)
    hsv = hsv[hsv[:, 2] > 120]
    if len(hsv) == 0:
        return "other"
    h, s, _ = np.median(hsv, 0)
    if s < 45:
        return "white"
    if 95 <= h <= 115:
        return "blue"
    if 40 <= h <= 75:
        return "green"
    if 135 <= h <= 165:
        return "pink"
    return "other"


def detect(frame_bgr, tpls=None, min_score=MIN_SCORE, scale=1.0):
    """-> список Detection (x, y в пикселях кадра), по убыванию score"""
    tpls = tpls or load_templates()
    h, w = frame_bgr.shape[:2]
    best = None
    names = list(tpls)
    for i, n in enumerate(names):
        r = _ncc(frame_bgr, tpls[n])
        if best is None:
            best = r
        else:
            best = np.maximum(best, r)
    th, tw = next(iter(tpls.values())).shape[:2]
    # центр шаблона -> ячейка результата (смещение th/2, tw/2); обнуляем HUD
    ys, xs = np.mgrid[0:best.shape[0], 0:best.shape[1]]
    cx, cy = xs + tw // 2, ys + th // 2
    bad = cy < TITLE_BAR_PX + th // 2
    for x0, y0, x1, y1 in HUD_ZONES:
        bad |= (cx >= x0 * w) & (cx <= x1 * w) & (cy >= y0 * h) & (cy <= y1 * h)
    best = best.copy()
    best[bad] = -1
    out = []
    while True:
        _, mx, _, loc = cv2.minMaxLoc(best)
        if mx < min_score:
            break
        x, y = loc
        px, py = x + tw // 2, y + th // 2
        out.append(Detection(px, py, float(mx), classify_color(frame_bgr, px, py, scale)))
        best[max(0, y - th // 2):y + th // 2, max(0, x - tw // 2):x + tw // 2] = -1
    return out


def detect_multiscale(frame_bgr, tpls=None, scales=None, min_score=0.6):
    """Для калибровки зума (шаблоны сняты на целевом зуме, а кадр может быть дальше).
    -> [(scale, Detection)], лучшие находки без дублей между масштабами."""
    tpls = tpls or load_templates()
    scales = scales or [round(0.30 * 1.08 ** i, 3) for i in range(0, 19)]   # 0.30 .. ~1.2
    found = []
    for s in scales:
        ts = {k: cv2.resize(t, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) for k, t in tpls.items()}
        if min(t.shape[0] for t in ts.values()) < 12:
            continue
        found += [(s, d) for d in detect(frame_bgr, ts, min_score, scale=s)]
    found.sort(key=lambda sd: -sd[1].score)
    out = []
    for s, d in found:
        if all((d.x - o.x) ** 2 + (d.y - o.y) ** 2 > (22 * max(s, so)) ** 2 for so, o in out):
            out.append((s, d))
    return out
