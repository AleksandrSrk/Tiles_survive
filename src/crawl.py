"""Обход штата на максимальном отдалении (слой А: территории).
Идея: решётка кадров вдоль ГРАНЕЙ ромба (оси U и V под ±35.2° к горизонтали),
шаг решётки STEP px. Положение ведём замкнуто: после каждого драга меряем реальный
сдвиг карты фазовой корреляцией по пересечению кадров (окно поиска ±60 px вокруг
ожидаемого, чтобы повторяющаяся плитка не обманула) и поправляем следующий драг.
Границу штата ловим по плашке «Штат #N» (diff плашки с эталоном).
Порядок: 1) уходим -b до границы, 2) -a до границы, 3) ряд b_lo слева-направо,
4) ряд b_lo-1 (за границей) обратно, 5) остальные ряды змейкой до первого ряда за границей.
Кадры -> data/<state>/screens/crawl/, журнал -> data/<state>/crawl_journal.json
Аварийный стоп: ScrollLock.
Запуск: python crawl.py [--max-tiles N] [--skip-start]"""
import sys, os, time, json, math, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import cv2
import window_manager as wm
import driver as dv

STATE = "720"
BASE = r"D:\PROJECT\TilesSurviveMap"
OUT = BASE + rf"\data\{STATE}\screens\crawl"
JOURNAL = BASE + rf"\data\{STATE}\crawl_journal.json"
TMP = OUT + r"\_tmp.png"

THETA = math.radians(35.2)                 # измерено по 405 линиям на скринах
U = np.array([math.cos(THETA), -math.sin(THETA)])   # вид едет вправо-вверх (вдоль верх-лев. грани)
V = np.array([math.cos(THETA), math.sin(THETA)])    # вид едет вправо-вниз (вдоль ниж-лев. грани)
STEP = 620.0                               # шаг решётки; ячейка (STEP+STEP) влезает в кадр с запасом ~20%
K0 = 1.62                                  # сдвиг контента / длина драга НА МАКС-ОТДАЛЕНИИ (измерено test_drag: 492px на драг 294px)
SEG_MAX = 640.0                            # макс. длина одного драга (px вида)
PLATE_THRESH = 15.0
ROI = (240, 1570, 170, 930)                # x0,x1,y0,y1: область карты без HUD (кадр окна 1774x1028)


class Crawler:
    def __init__(self, max_tiles=60):
        self.k = K0
        self.pos = np.zeros(2)             # оценка положения вида (px), от старта
        self.prev = None                   # предыдущий кадр (серый, ROI)
        self.cells = {}                    # (a,b) -> запись журнала
        self.max_tiles = max_tiles
        self.ref_plate = None
        self.warns = 0
        os.makedirs(OUT, exist_ok=True)

    # ---------- низкий уровень ----------
    def _gray(self, img):
        x0, x1, y0, y1 = ROI
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY).astype(np.float32)[y0:y1, x0:x1]

    def _drag_view(self, d):
        """Сдвинуть ВИД на d (px). Контент идёт за курсором => курсор тянем на -d/k."""
        w = dv.ensure_focus()
        cx, cy = w.left + w.width // 2, w.top + w.height // 2
        h = d / (2 * self.k)
        dv.safe_drag(cx + h[0], cy + h[1], cx - h[0], cy - h[1])
        time.sleep(1.4)

    def _measure(self, prev, cur, view_pred):
        """Реальный сдвиг ВИДА между кадрами (серые ROI). SIFT + мода сдвигов около ожидаемого
        (радиус 150 px), фолбэк - фазовая корреляция. Возврат (view_shift, score) или (None, score)."""
        sift = cv2.SIFT_create(5000)
        bf = cv2.BFMatcher()
        ka, da = sift.detectAndCompute(np.clip(prev, 0, 255).astype(np.uint8), None)
        kb, db = sift.detectAndCompute(np.clip(cur, 0, 255).astype(np.uint8), None)
        if da is not None and db is not None and len(ka) > 8 and len(kb) > 8:
            ms = [m for m, n in (p for p in bf.knnMatch(da, db, k=2) if len(p) == 2) if m.distance < 0.8 * n.distance]
            if ms:
                d = np.float32([np.array(kb[m.trainIdx].pt) - np.array(ka[m.queryIdx].pt) for m in ms])
                c = np.array([-view_pred[0], -view_pred[1]])
                near = d[np.linalg.norm(d - c, axis=1) < 150]
                best, bi = None, 0
                for x in near:
                    inl = np.linalg.norm(near - x, axis=1) < 2.5
                    if inl.sum() > bi:
                        bi, best = int(inl.sum()), near[inl].mean(axis=0)
                if bi >= 10:
                    return -best, float(bi)
        return None, 0.0

    def _capture(self):
        img, _ = wm.capture_window(TMP, settle=0.5)
        return img

    def _plate_diff(self, img):
        return float(np.abs(dv._state_plate(np.array(img)) - self.ref_plate).mean())

    # ---------- перемещение ----------
    def step_to(self, target, label=""):
        """Довести вид до target (px от старта) замкнутым циклом. Возврат последнего кадра (PIL)."""
        img = None
        for _ in range(6):
            rem = target - self.pos
            dist = float(np.hypot(*rem))
            if dist < 45 and img is not None:
                break
            if dist < 45:
                img = self._capture()
                self.prev = self._gray(img)
                break
            seg = rem if dist <= SEG_MAX else rem * SEG_MAX / dist
            self._drag_view(seg)
            img = self._capture()
            cur = self._gray(img)
            if self.prev is not None:
                m, resp = self._measure(self.prev, cur, seg)
                if m is None:
                    self.warns += 1
                    print(f"    ! измерение сдвига не удалось (resp={resp:.2f}), верю команде", flush=True)
                    m = seg
                else:
                    err = float(np.hypot(*(m - seg)))
                    if err > 45:
                        print(f"    сдвиг: команда {seg.round(0)} -> факт {m.round(0)} (resp={resp:.2f})", flush=True)
                self.pos = self.pos + m
            else:
                self.pos = self.pos + seg
            self.prev = cur
        return img

    # ---------- ячейки решётки ----------
    def target(self, a, b):
        return a * STEP * U + b * STEP * V

    def ensure(self, a, b):
        """Прийти в ячейку (a,b) и, если её ещё нет, снять кадр и проверить границу."""
        if len(self.cells) >= self.max_tiles and (a, b) not in self.cells:
            raise StopIteration("достигнут лимит кадров")
        img = self.step_to(self.target(a, b))
        if (a, b) in self.cells:
            return self.cells[(a, b)]["inside"]
        diff = self._plate_diff(img)
        if diff > PLATE_THRESH:                       # перепроверка: плашку могло перекрыть всплывашкой
            time.sleep(1.0)
            img = self._capture()
            diff = self._plate_diff(img)
        inside = diff <= PLATE_THRESH
        fn = OUT + rf"\t_b{b:+03d}_a{a:+03d}.png"
        shutil.copy(TMP, fn)
        self.cells[(a, b)] = {"a": a, "b": b, "pos": [round(float(self.pos[0]), 1), round(float(self.pos[1]), 1)],
                              "inside": inside, "plate_diff": round(diff, 1), "file": fn}
        print(f"  [{a:+d},{b:+d}] {'внутри' if inside else 'ЗА ГРАНИЦЕЙ'} diff={diff:.1f}  pos=({self.pos[0]:.0f},{self.pos[1]:.0f})", flush=True)
        self.save()
        return inside

    def save(self):
        data = {"state": STATE, "step": STEP, "theta_deg": 35.2, "k": self.k, "warns": self.warns,
                "cells": [self.cells[k] for k in sorted(self.cells, key=lambda t: (t[1], t[0]))]}
        with open(JOURNAL, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

    # ---------- калибровка ----------
    def calibrate_k(self, length=400.0):
        """Драг на length вдоль U (от ближайшей границы), замер, возврат. Уточняет k."""
        img0 = self._capture()
        g0 = self._gray(img0)
        self._drag_view(length * U)
        g1 = self._gray(self._capture())
        m, resp = self._measure(g0, g1, length * U)
        if m is not None:
            ratio = float(np.hypot(*m)) / length          # факт / команда(при k0)
            k_new = self.k * ratio                         # k = контент/драг; драг был length/k0
            print(f"  калибровка: факт {m.round(1)} при команде {(length*U).round(1)}, resp={resp:.2f}, k {self.k:.3f}->{k_new:.3f}", flush=True)
            if 1.45 < k_new < 1.85:
                self.k = k_new
            else:
                print("  ! k вне разумного, оставляю прежний", flush=True)
        else:
            print("  ! калибровка не удалась, k по умолчанию", flush=True)
        self._drag_view(-length * U)                       # назад
        img = self._capture()
        self.prev = self._gray(img)
        self.pos = np.zeros(2)

    # ---------- основной обход ----------
    def run(self):
        img = self._capture()
        self.ref_plate = dv._state_plate(np.array(img))
        self.prev = self._gray(img)
        print("[обход] калибровка шага мыши", flush=True)
        self.calibrate_k()
        self.ref_plate = dv._state_plate(np.array(self._capture()))
        a0, b0 = 0, 0
        print("[обход] старт-ячейка", flush=True)
        self.ensure(a0, b0)

        print("[обход] ищем границу -b", flush=True)
        b = b0
        while True:
            b -= 1
            if not self.ensure(a0, b):
                break
            if b < -6:
                raise RuntimeError("граница -b не найдена за 6 шагов")
        b_lo = b + 1

        print("[обход] ищем границу -a", flush=True)
        a = a0
        while True:
            a -= 1
            if not self.ensure(a, b_lo):
                break
            if a < -6:
                raise RuntimeError("граница -a не найдена за 6 шагов")
        a_out_lo = a

        print(f"[обход] ряд b={b_lo} вправо до границы", flush=True)
        a = a_out_lo
        while True:
            a += 1
            if not self.ensure(a, b_lo) and a > a0:
                break
            if a > 10:
                raise RuntimeError("граница +a не найдена за 10 шагов")
        a_out_hi = a

        print(f"[обход] ряд b={b_lo - 1} (за границей) обратно", flush=True)
        for a in range(a_out_hi, a_out_lo - 1, -1):
            self.ensure(a, b_lo - 1)

        print("[обход] остальные ряды змейкой", flush=True)
        b = b_lo
        direction = +1                                   # ряд b_lo уже пройден слева направо
        for _ in range(10):
            b += 1
            rng = range(a_out_lo, a_out_hi + 1) if direction == +1 else range(a_out_hi, a_out_lo - 1, -1)
            # сначала решаем, внутри ли ряд, по первой внутренней ячейке
            probe = a_out_lo + 1 if direction == +1 else a_out_hi - 1
            row_inside = self.ensure(probe, b)
            for a in rng:
                self.ensure(a, b)
            if not row_inside:
                print(f"[обход] ряд b={b} за границей — конец", flush=True)
                break
            direction = -direction
        n_in = sum(1 for c in self.cells.values() if c["inside"])
        print(f"[обход] готово: кадров {len(self.cells)}, внутри {n_in}, предупреждений {self.warns}, k={self.k:.3f}", flush=True)
        self.save()


if __name__ == "__main__":
    max_tiles = 60
    if "--max-tiles" in sys.argv:
        max_tiles = int(sys.argv[sys.argv.index("--max-tiles") + 1])
    try:
        if dv.abort_requested():
            print("ScrollLock включён — выключи и запусти снова"); sys.exit(2)
        if "--skip-start" not in sys.argv:
            print(dv.start_position(), flush=True)
        c = Crawler(max_tiles=max_tiles)
        try:
            c.run()
        except StopIteration as e:
            print(f"[обход] остановка: {e}", flush=True)
            c.save()
    except dv.Aborted as e:
        print("ОСТАНОВЛЕНО:", e)
    except dv.FocusLost as e:
        print("ФОКУС ПОТЕРЯН:", e)
