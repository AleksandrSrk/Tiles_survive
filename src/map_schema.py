"""Схема разметки штата 720: блоки 20x20 клеток, земли (plates), сектора. ЗАФИКСИРОВАНА (v12).
Источник правды: assets/reference/map_schema_720.sqlite (триггеры не дают менять геометрию) и золотой
assets/reference/map_schema_720.json (его sha256 лежит в map_schema_720.sha256; при несовпадении import падает).
Менять можно только владельцев земель (plates.owner_tag) и sector_status — см. src/map_schema_lock.py.
cell->block: bx=(X-20)//20, by=(Y-20)//20. Ось X растёт вправо-вверх на экране, Y влево-вверх."""
import hashlib, json, os, sqlite3
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REF = os.path.join(BASE, "assets", "reference")
_JSON = os.path.join(_REF, "map_schema_720.json")
_SHA = os.path.join(_REF, "map_schema_720.sha256")
DB = os.path.join(_REF, "map_schema_720.sqlite")

_raw = open(_JSON, "rb").read()
if hashlib.sha256(_raw).hexdigest() != open(_SHA).read().strip():
    raise RuntimeError("map_schema_720.json изменён: схема зафиксирована, верни золотую версию (см. src/map_schema_lock.py)")
_S = json.loads(_raw.decode("utf-8"))
PLATE = np.array(_S["blocks_plate"]); LAND = np.array(_S["blocks_land"]); N = 63
PLATES = {p["num"]: p for p in _S["plates"]}
TITLE_TO_NUM = {p["title"]: p["num"] for p in _S["plates"]}


def block_of(X, Y):
    bx, by = int((X - 20) // 20), int((Y - 20) // 20)
    return (bx, by) if 0 <= bx < N and 0 <= by < N else None


def is_land(X, Y):
    b = block_of(X, Y)
    return bool(b and LAND[b])


def plate_of(X, Y):
    """номер земли или None (вода/вне штата)"""
    b = block_of(X, Y)
    return int(PLATE[b]) or None if b else None


def plate_title(num):
    """фиксированное имя земли: 'Аркадия', 'Завод 7', 'Деревня 12'..."""
    return PLATES[num]["title"]


def land_blocks():
    return [(int(bx), int(by)) for bx, by in np.argwhere(LAND == 1)]


def owner_tag(num):
    """текущий тег союза-владельца земли (или None). Меняется через map_schema_lock.set_owner / refresh_owners_from_layer_a"""
    con = sqlite3.connect("file:" + DB.replace("\\", "/") + "?mode=ro", uri=True)
    try:
        r = con.execute("SELECT owner_tag FROM plates WHERE num=?", (num,)).fetchone()
    finally:
        con.close()
    return r[0] if r else None


def owner_at(X, Y):
    """тег владельца земли под игровой точкой X:Y"""
    n = plate_of(X, Y)
    return owner_tag(n) if n else None
