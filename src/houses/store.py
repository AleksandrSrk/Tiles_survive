"""SQLite с домиками: data/720/houses.sqlite.
detections - сырьё (каждая находка на каждом кадре, X:Y игровые, дробные);
houses     - дедуплицированные домики (кадры с нахлёстом дают одну и ту же находку несколько раз).
Здесь нет ни OCR, ни рисования: только хранение и слияние."""
import math
import os
import sqlite3
import time

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "720", "houses.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS detections(
  id INTEGER PRIMARY KEY, frame TEXT, X REAL, Y REAL, kind TEXT, score REAL, ts TEXT);
CREATE INDEX IF NOT EXISTS ix_det_frame ON detections(frame);
CREATE TABLE IF NOT EXISTS houses(
  id INTEGER PRIMARY KEY, X REAL, Y REAL, kind TEXT, n_seen INTEGER, score_max REAL);
"""


def connect(path=DB):
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def add_frame(con, frame_id, geo, dets):
    """dets - список detect.Detection (пиксели), geo - geo.Geo кадра. Пересохраняет кадр целиком."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    con.execute("DELETE FROM detections WHERE frame=?", (frame_id,))
    rows = []
    for d in dets:
        X, Y = geo.to_game(d.x, d.y)
        rows.append((frame_id, X, Y, d.kind, d.score, ts))
    con.executemany("INSERT INTO detections(frame,X,Y,kind,score,ts) VALUES(?,?,?,?,?,?)", rows)
    con.commit()
    return len(rows)


def merge(points, radius=1.2):
    """points = [(X, Y, kind, score)] -> [(X, Y, kind, n_seen, score_max)].
    Жадно: самая уверенная находка основа, все в радиусе (в клетках) к ней присоединяются."""
    pts = sorted(points, key=lambda p: -p[3])
    cell = max(radius, 1e-6)
    grid, out = {}, []
    for X, Y, kind, sc in pts:
        gx, gy = int(X // cell), int(Y // cell)
        hit = None
        for i in range(gx - 1, gx + 2):
            for j in range(gy - 1, gy + 2):
                for k in grid.get((i, j), ()):
                    if math.hypot(out[k][0] - X, out[k][1] - Y) <= radius:
                        hit = k
                        break
                if hit is not None:
                    break
            if hit is not None:
                break
        if hit is None:
            out.append([X, Y, kind, 1, sc])
            grid.setdefault((gx, gy), []).append(len(out) - 1)
        else:
            out[hit][3] += 1
    return [tuple(o) for o in out]


def rebuild_houses(con, radius=1.2):
    pts = con.execute("SELECT X,Y,kind,score FROM detections").fetchall()
    merged = merge(pts, radius)
    con.execute("DELETE FROM houses")
    con.executemany("INSERT INTO houses(X,Y,kind,n_seen,score_max) VALUES(?,?,?,?,?)", merged)
    con.commit()
    return len(merged)


def load_houses(con):
    return con.execute("SELECT X,Y,kind,n_seen,score_max FROM houses").fetchall()
