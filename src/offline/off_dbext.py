import sqlite3,json
db=sqlite3.connect("layer_a.sqlite")
T=json.load(open("template_type1_v2.json"))
db.executescript("""
CREATE TABLE IF NOT EXISTS map_types(type TEXT PRIMARY KEY,name TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS states(state TEXT PRIMARY KEY,map_type TEXT REFERENCES map_types(type),note TEXT);
CREATE TABLE IF NOT EXISTS cells(map_type TEXT,cell_id TEXT,ring INTEGER,area REAL,cx REAL,cy REAL,polygon TEXT,iso_polygon TEXT,neighbors TEXT,PRIMARY KEY(map_type,cell_id));
""")
db.execute("INSERT OR REPLACE INTO map_types VALUES('1','Тип 1 (перерисован по штату 720)','57 плит: кольца 7:1 6:3 5:5 4:8 3:10 2:14 1:16')")
db.execute("INSERT OR IGNORE INTO map_types VALUES('2','Тип 2','схема в assets/reference/map_type2_*, по реальной карте ещё не перерисована')")
db.execute("INSERT OR REPLACE INTO states VALUES('720','1','подтверждено пользователем')")
for c in T["cells"]:
    db.execute("INSERT OR REPLACE INTO cells VALUES('1',?,?,?,?,?,?,?,?)",(c["id"],c["ring"],c["area"],c["centroid"][0],c["centroid"][1],json.dumps(c["polygon"]),json.dumps(c["iso_polygon"]),json.dumps(c["neighbors"])))
sid=db.execute("SELECT max(id) FROM scans WHERE state='720' AND layer='A'").fetchone()[0]
db.execute("INSERT OR REPLACE INTO cell_owners VALUES(?,?,?,?,?,?,?,?,?,?)",(sid,"R7-01",7,"HoD",100,160,90,0.5,1,"visual"))
db.executescript("""
DROP VIEW IF EXISTS v_latest_owners;
CREATE VIEW v_latest_owners AS
SELECT s.state,co.cell_id,co.ring,co.tag,co.r,co.g,co.b,co.confidence,s.scanned_at
FROM cell_owners co JOIN scans s ON s.id=co.scan_id
WHERE s.layer='A' AND s.id=(SELECT max(id) FROM scans s2 WHERE s2.state=s.state AND s2.layer='A');
DROP VIEW IF EXISTS v_owner_changes;
CREATE VIEW v_owner_changes AS
SELECT s.state,cur.cell_id,prev.tag AS old_tag,cur.tag AS new_tag,s.scanned_at
FROM cell_owners cur JOIN scans s ON s.id=cur.scan_id
JOIN cell_owners prev ON prev.cell_id=cur.cell_id AND prev.scan_id=(SELECT max(id) FROM scans p WHERE p.state=s.state AND p.layer=s.layer AND p.id<s.id)
WHERE prev.tag IS NOT cur.tag;
""")
db.commit()
print(db.execute("select count(*) from cells").fetchone(),db.execute("select count(*) from v_latest_owners").fetchone(),db.execute("select tag,count(*) from v_latest_owners group by tag order by 2 desc").fetchall())
print([r[0] for r in db.execute("select name from sqlite_master where type in('table','view')")])
