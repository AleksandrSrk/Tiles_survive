import sqlite3,sys
d=sqlite3.connect(r"D:\PROJECT\TilesSurviveMap\data\720\layer_a.sqlite")
for sid in map(int,sys.argv[1:]):
    d.execute("delete from cell_owners where scan_id=?",(sid,)); d.execute("delete from scans where id=?",(sid,))
d.commit(); print(d.execute("select id,note from scans").fetchall())
