"""Жёсткая фиксация схемы разметки штата 720 (земли + блоки 20x20) в SQLite.

Что неизменно (защищено триггерами БД + хэшем): список земель, их имена/коды/кольца,
габариты и привязка каждого блока к земле. Менять можно ТОЛЬКО:
  - plates.owner_tag / owner_updated / owner_source / owner_scan_id  (текущий союз-владелец)
  - sector_status (какие сектора сняты)
История смены владельцев пишется сама в plate_owner_history.

Команды:
  python src/map_schema_lock.py init <golden.json>   создать БД из золотого JSON (если БД ещё нет)
  python src/map_schema_lock.py verify               проверить, что геометрия не тронута
  python src/map_schema_lock.py owners [scan_id]     подтянуть владельцев из layer_a.sqlite (по умолчанию последний скан)
  python src/map_schema_lock.py show                 список земель: номер, название, владелец

Изменить геометрию осознанно: новая версия золотого JSON + НОВЫЙ файл БД (не правка старого).
"""
import hashlib, json, os, sqlite3, sys, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(BASE, "assets", "reference")
DB = os.path.join(REF, "map_schema_720.sqlite")
GOLDEN = os.path.join(REF, "map_schema_720.json")
GOLDEN_SHA = os.path.join(REF, "map_schema_720.sha256")
LAYER_A = os.path.join(BASE, "data", "720", "layer_a.sqlite")

IMMUTABLE_PLATE_COLS = "num,code,ring,ring_name,name,title,measured,status,blocks,x0,y0,x1,y1"

DDL = f"""
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE plates(
  num INTEGER PRIMARY KEY,          -- фиксированный номер земли 1..57 (сверху вниз по кольцам: 1=Аркадия)
  code TEXT NOT NULL UNIQUE,        -- код шаблона R<кольцо>-<NN>, он же cell_id в layer_a.sqlite
  ring INTEGER NOT NULL,
  ring_name TEXT NOT NULL,
  name TEXT NOT NULL,               -- фиксированное имя: Аркадия, Военная база, Центр исследований, Мегаполис, Городок, Завод, Деревня
  title TEXT NOT NULL UNIQUE,       -- уникальное имя: 'Завод 7', 'Деревня 12'
  measured INTEGER NOT NULL,        -- 1 = углы измерены тапами
  status TEXT NOT NULL,
  blocks INTEGER NOT NULL,
  x0 INTEGER, y0 INTEGER, x1 INTEGER, y1 INTEGER,   -- габарит в клетках (включительно)
  owner_tag TEXT,                   -- ИЗМЕНЯЕМОЕ: тег союза-владельца сейчас
  owner_updated TEXT,
  owner_source TEXT,
  owner_scan_id INTEGER
);
CREATE TABLE blocks(
  bx INTEGER, by INTEGER, x0 INTEGER, y0 INTEGER, land INTEGER,
  plate_num INTEGER REFERENCES plates(num),
  PRIMARY KEY(bx,by)
);
CREATE TABLE sector_status(bx INTEGER, by INTEGER, status TEXT DEFAULT 'не снят', scan_id INTEGER, updated TEXT, PRIMARY KEY(bx,by));
CREATE TABLE plate_owner_history(id INTEGER PRIMARY KEY AUTOINCREMENT, plate_num INTEGER, old_tag TEXT, new_tag TEXT, changed_at TEXT, source TEXT, scan_id INTEGER);
CREATE VIEW v_plates AS SELECT num,title,name,ring,owner_tag,owner_updated,measured,x0,y0,x1,y1,blocks FROM plates ORDER BY num;
"""

TRIGGERS = f"""
CREATE TRIGGER plates_no_insert BEFORE INSERT ON plates BEGIN SELECT RAISE(ABORT,'схема зафиксирована: земли добавлять нельзя'); END;
CREATE TRIGGER plates_no_delete BEFORE DELETE ON plates BEGIN SELECT RAISE(ABORT,'схема зафиксирована: земли удалять нельзя'); END;
CREATE TRIGGER plates_geom_lock BEFORE UPDATE OF {IMMUTABLE_PLATE_COLS} ON plates BEGIN SELECT RAISE(ABORT,'схема зафиксирована: менять можно только owner_*'); END;
CREATE TRIGGER blocks_no_insert BEFORE INSERT ON blocks BEGIN SELECT RAISE(ABORT,'схема зафиксирована: блоки менять нельзя'); END;
CREATE TRIGGER blocks_no_update BEFORE UPDATE ON blocks BEGIN SELECT RAISE(ABORT,'схема зафиксирована: блоки менять нельзя'); END;
CREATE TRIGGER blocks_no_delete BEFORE DELETE ON blocks BEGIN SELECT RAISE(ABORT,'схема зафиксирована: блоки менять нельзя'); END;
CREATE TRIGGER meta_no_update BEFORE UPDATE ON meta BEGIN SELECT RAISE(ABORT,'meta зафиксирована'); END;
CREATE TRIGGER meta_no_delete BEFORE DELETE ON meta BEGIN SELECT RAISE(ABORT,'meta зафиксирована'); END;
CREATE TRIGGER plates_owner_hist AFTER UPDATE OF owner_tag ON plates
  WHEN IFNULL(old.owner_tag,'') <> IFNULL(new.owner_tag,'')
  BEGIN INSERT INTO plate_owner_history(plate_num,old_tag,new_tag,changed_at,source,scan_id)
        VALUES(new.num,old.owner_tag,new.owner_tag,new.owner_updated,new.owner_source,new.owner_scan_id); END;
"""


def _conn(path=DB):
    c = sqlite3.connect(path)
    c.execute("PRAGMA foreign_keys=ON")
    return c


def geometry_hash(con):
    h = hashlib.sha256()
    for r in con.execute(f"SELECT {IMMUTABLE_PLATE_COLS} FROM plates ORDER BY num"):
        h.update(repr(tuple(r)).encode("utf-8"))
    for r in con.execute("SELECT bx,by,x0,y0,land,COALESCE(plate_num,0) FROM blocks ORDER BY bx,by"):
        h.update(repr(tuple(r)).encode("utf-8"))
    return h.hexdigest()


def file_sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def init(golden_path):
    if os.path.exists(DB):
        raise SystemExit(f"БД уже есть ({DB}) — init не перезаписывает. Геометрию менять только новой версией и новым файлом.")
    g = json.load(open(golden_path, encoding="utf-8"))
    con = _conn()
    con.executescript(DDL)
    for p in g["plates"]:
        bb = p["bbox"]
        con.execute("INSERT INTO plates(num,code,ring,ring_name,name,title,measured,status,blocks,x0,y0,x1,y1) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (p["num"], p["code"], p["ring"], p["ring_name"], p["name"], p["title"], p["measured"], p["status"], p["blocks"], *bb))
    N = g["meta"]["grid"][0]
    for bx in range(N):
        for by in range(N):
            con.execute("INSERT INTO blocks VALUES(?,?,?,?,?,?)", (bx, by, 20 + 20 * bx, 20 + 20 * by, g["blocks_land"][bx][by], g["blocks_plate"][bx][by] or None))
            if g["blocks_land"][bx][by]:
                con.execute("INSERT INTO sector_status(bx,by) VALUES(?,?)", (bx, by))
    con.executemany("INSERT INTO meta VALUES(?,?)", [
        ("state", "720"), ("version", g["meta"]["version"]), ("created", datetime.datetime.now().isoformat(timespec="seconds")),
        ("geometry_sha256", geometry_hash(con)), ("golden_json_sha256", file_sha(golden_path)),
        ("note", "геометрия зафиксирована триггерами; менять только owner_* и sector_status")])
    con.executescript(TRIGGERS)
    con.commit()
    con.close()
    open(GOLDEN_SHA, "w").write(file_sha(golden_path) + "\n")
    print("OK: БД создана и зафиксирована:", DB)


def verify(quiet=False):
    """True если геометрия БД и золотой JSON не менялись."""
    con = _conn()
    stored = dict(con.execute("SELECT key,value FROM meta"))
    ok_db = geometry_hash(con) == stored["geometry_sha256"]
    ok_json = os.path.exists(GOLDEN) and file_sha(GOLDEN) == stored["golden_json_sha256"]
    n_trg = con.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]
    con.close()
    if not quiet:
        print(f"геометрия БД: {'ОК' if ok_db else 'ИЗМЕНЕНА!'}; золотой JSON: {'ОК' if ok_json else 'ИЗМЕНЁН!'}; триггеров: {n_trg} (ожидается 9)")
    return ok_db and ok_json and n_trg == 9


def set_owner(num, tag, source="manual", scan_id=None):
    """Единственный разрешённый способ поменять владельца земли."""
    con = _conn()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    cur = con.execute("UPDATE plates SET owner_tag=?, owner_updated=?, owner_source=?, owner_scan_id=? WHERE num=?", (tag, now, source, scan_id, num))
    con.commit()
    con.close()
    return cur.rowcount == 1


def get_owner(num):
    con = _conn()
    r = con.execute("SELECT owner_tag FROM plates WHERE num=?", (num,)).fetchone()
    con.close()
    return r[0] if r else None


def refresh_owners_from_layer_a(scan_id=None, layer_a=LAYER_A):
    """Подтянуть теги владельцев из layer_a.sqlite (cell_owners.cell_id == plates.code). Берётся последний скан, если не указан."""
    la = sqlite3.connect(layer_a)
    if scan_id is None:
        scan_id = la.execute("SELECT max(scan_id) FROM cell_owners").fetchone()[0]
    rows = la.execute("SELECT cell_id,tag FROM cell_owners WHERE scan_id=?", (scan_id,)).fetchall()
    la.close()
    con = _conn()
    code2num = dict((c, n) for n, c in con.execute("SELECT num,code FROM plates"))
    now = datetime.datetime.now().isoformat(timespec="seconds")
    changed = skipped = 0
    for code, tag in rows:
        n = code2num.get(code)
        if n is None or not tag:
            skipped += 1
            continue
        cur = con.execute("UPDATE plates SET owner_tag=?, owner_updated=?, owner_source=?, owner_scan_id=? WHERE num=? AND IFNULL(owner_tag,'')<>?",
                          (tag, now, f"layer_a scan {scan_id}", scan_id, n, tag))
        changed += cur.rowcount
    con.commit()
    con.close()
    print(f"владельцы из layer_a scan {scan_id}: обновлено {changed}, пропущено {skipped}, всего строк {len(rows)}")
    return changed


def show():
    con = _conn()
    for num, title, ring, tag, meas in con.execute("SELECT num,title,ring,owner_tag,measured FROM plates ORDER BY num"):
        print(f"{num:2d}  {title:<24} [{tag or '—'}]{'  (измерено)' if meas else ''}")
    con.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "init":
        init(sys.argv[2])
    elif cmd == "verify":
        sys.exit(0 if verify() else 1)
    elif cmd == "owners":
        refresh_owners_from_layer_a(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif cmd == "show":
        show()
    else:
        print(__doc__)
