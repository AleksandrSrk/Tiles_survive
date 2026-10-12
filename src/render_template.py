"""Рисует карту типа 1 (изометрия), залитую владельцами. Светлая пастельная палитра, заголовок и легенда по тегам."""
import json, math, os
from collections import Counter, defaultdict
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, box
from shapely import affinity

BASE = r"D:\PROJECT\TilesSurviveMap"
TEMPLATE = BASE + r"\assets\reference\map_type1_v2.json"
NAMES = {1: "Деревня", 2: "Завод", 3: "Городок", 4: "Мегаполис", 5: "Центр исследований", 6: "Военная база", 7: "Аркадия"}
RINGCOL = {7: (205, 228, 190), 6: (235, 235, 245), 5: (240, 240, 245), 4: (240, 240, 245), 3: (240, 240, 245), 2: (240, 240, 245), 1: (240, 240, 245)}
FB = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FR = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
INK, INK2, EDGE, BG = (28, 32, 40), (70, 76, 88), (255, 255, 255), (247, 248, 250)


def _font(sz, bold=True):
    for p in (FB if bold else FR):
        if os.path.exists(p):
            return ImageFont.truetype(p, int(sz))
    return ImageFont.load_default()


def soft(rgb, k=0.42):
    """Осветляем исходный цвет плитки: смешиваем с белым, но оттенок остаётся узнаваемым."""
    return tuple(int(c * (1 - k) + 255 * k) for c in rgb)


def render(owners, out_png, template_path=TEMPLATE, scale=2.2, title=None, subtitle=None):
    """owners: {cell_id: {"tag": str|None, "rgb": [r,g,b]|None}}."""
    T = json.load(open(template_path, encoding="utf-8"))["cells"]
    allp = [p for c in T for p in c["iso_polygon"]]
    mnx = min(p[0] for p in allp); mny = min(p[1] for p in allp)
    top = 150 if title else 40
    Wd = int((max(p[0] for p in allp) - mnx) * scale) + 120
    Hd = int((max(p[1] for p in allp) - mny) * scale) + top + 60
    tr = lambda p: ((p[0] - mnx) * scale + 60, (p[1] - mny) * scale + top)
    ss = 2
    img = np.full((Hd * ss, Wd * ss, 3), BG[::-1], np.uint8)
    for c in T:
        pp = np.array([[tr(p)[0] * ss, tr(p)[1] * ss] for p in c["iso_polygon"]], np.int32)
        o = owners.get(c["id"])
        col = soft(tuple(o["rgb"])) if o and o.get("rgb") else RINGCOL[c["ring"]]
        cv2.fillPoly(img, [pp], tuple(int(x) for x in col[::-1]))
        cv2.polylines(img, [pp], True, EDGE[::-1], 5 * ss, cv2.LINE_AA)
    img = cv2.resize(img, (Wd, Hd), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im)
    for c in T:
        poly = Polygon([tr(p) for p in c["iso_polygon"]]); inner = poly.buffer(-7)
        pl = poly.centroid
        co = list(poly.exterior.coords)[:-1]
        be = max(((co[(i + 1) % len(co)][0] - co[i][0], co[(i + 1) % len(co)][1] - co[i][1]) for i in range(len(co))), key=lambda v: math.hypot(*v))
        dx, dy = be
        if dx < 0: dx, dy = -dx, -dy
        ang = math.degrees(math.atan2(-dy, dx))
        o = owners.get(c["id"]); tag = o.get("tag") if o else None
        name = NAMES[c["ring"]]
        variants = [[name]] + ([name.split(" ", 1)] if " " in name else [])

        def attempt(tsz, var, rot):
            nsz = max(15, int(tsz * 0.5)); ft = _font(tsz); fn = _font(nsz, False)
            lines = ([(tag, ft, INK)] if tag else []) + [(t, fn, INK2) for t in var]
            dims = [d.textbbox((0, 0), t, font=f) for t, f, _ in lines]
            w = max(b[2] - b[0] for b in dims) + 12; h = sum(b[3] - b[1] + 6 for b in dims) + 8
            bx0, by0, bx1, by1 = poly.bounds; best = None
            for x in np.arange(bx0, bx1, 6):
                for y in np.arange(by0, by1, 6):
                    r = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    if rot: r = affinity.rotate(r, -ang, origin=(x, y))
                    if inner.contains(r):
                        dd = math.hypot(x - pl.x, y - pl.y)
                        if best is None or dd < best[0]: best = (dd, x, y)
            return best, lines, dims, w, h
        plan = [(t, v, False) for t in (40, 36, 32, 28, 25) for v in variants] + [(t, v, True) for t in (40, 36, 32, 28, 25, 22) for v in variants] \
            + [(t, v, False) for t in (22, 19) for v in variants] + [(t, [], r) for t in (30, 26, 22, 18) for r in (False, True)]
        for tsz, var, rot in plan:
            if not var and not tag: continue
            best, lines, dims, w, h = attempt(tsz, var, rot)
            if not best: continue
            _, x, y = best
            lay = Image.new("RGBA", (int(w) + 10, int(h) + 10), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); yy = 9
            for (t, f, colr), b in zip(lines, dims):
                tw = b[2] - b[0]
                ld.text(((lay.width - tw) / 2 - b[0], yy - b[1]), t, font=f, fill=colr + (255,))
                yy += b[3] - b[1] + 6
            if rot: lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
            im.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)
            break
    if title:
        d.text((60, 36), title, font=_font(54), fill=INK)
        if subtitle: d.text((62, 104), subtitle, font=_font(26, False), fill=INK2)
    # легенда: тег, цвет, число плиток (у каждой плитки в карте может быть свой оттенок -> берём самый частый)
    cnt = Counter(); cols = defaultdict(list)
    for cid, o in owners.items():
        if o and o.get("tag"):
            cnt[o["tag"]] += 1
            if o.get("rgb"): cols[o["tag"]].append(tuple(o["rgb"]))
    if cnt:
        items = cnt.most_common(); lf = _font(26); sf = _font(22, False)
        x0, y0, rowh = 60, top + 40, 42
        d.text((x0, y0 - 6), "Альянсы (плиток)", font=sf, fill=INK2); y0 += 36
        for i, (tg, n) in enumerate(items):
            col = soft(Counter(cols[tg]).most_common(1)[0][0]) if cols[tg] else (220, 220, 220)
            yy = y0 + i * rowh
            d.rounded_rectangle((x0, yy, x0 + 54, yy + 30), 8, fill=col, outline=(215, 218, 224))
            d.text((x0 + 68, yy - 3), f"{tg}", font=lf, fill=INK)
            d.text((x0 + 68 + 120, yy), f"{n}", font=sf, fill=INK2)
    im.save(out_png)
    return out_png
