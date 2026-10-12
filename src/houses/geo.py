"""Геометрия кадра: пиксели <-> игровые X:Y для ОДНОГО зума.
Ось экрана: u = X - Y (вправо), v = X + Y (вверх).  px = a*u + p0 ;  py = -b*v + q0.
a, b (пикселей на единицу u и v) зависят только от зума, p0, q0 - от положения камеры (у каждого кадра свои).
Калибровка по известным домикам: fit(points) -> Geo. Для обхода: scale (a, b) фиксируем один раз,
а p0, q0 каждого кадра берём из якоря (координата центра кадра) через Geo.anchored."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Geo:
    a: float
    b: float
    p0: float
    q0: float

    def to_px(self, X, Y):
        return self.a * (X - Y) + self.p0, -self.b * (X + Y) + self.q0

    def to_game(self, px, py):
        u = (px - self.p0) / self.a
        v = (self.q0 - py) / self.b
        return (u + v) / 2.0, (v - u) / 2.0

    def anchored(self, px, py, X, Y):
        """тот же масштаб, но кадр сдвинут так, что пиксель (px,py) = игровая точка X:Y"""
        return Geo(self.a, self.b, px - self.a * (X - Y), py + self.b * (X + Y))


def fit(points):
    """points = [((px, py), (X, Y)), ...], минимум 3. -> (Geo, макс. невязка в пикселях)"""
    P = np.array([p for p, _ in points], float)
    G = np.array([g for _, g in points], float)
    u, v = G[:, 0] - G[:, 1], G[:, 0] + G[:, 1]
    A = np.c_[u, np.ones(len(u))]
    (a, p0), *_ = np.linalg.lstsq(A, P[:, 0], rcond=None)
    B = np.c_[-v, np.ones(len(v))]
    (b, q0), *_ = np.linalg.lstsq(B, P[:, 1], rcond=None)
    geo = Geo(float(a), float(b), float(p0), float(q0))
    err = max(np.hypot(*(np.array(geo.to_px(*g)) - p)) for p, g in points)
    return geo, float(err)
