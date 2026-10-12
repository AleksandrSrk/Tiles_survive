import sqlite3
d=sqlite3.connect(r"D:\PROJECT\TilesSurviveMap\data\720\layer_a.sqlite")
sid=d.execute("select max(id) from scans").fetchone()[0]
for cid,tag in (("R6-01","SUN"),("R4-02","SUN"),("R4-07","FNX"),("R7-01","HoD")):
    old=d.execute("select r,g,b from cell_owners where scan_id=1 and cell_id=?",(cid,)).fetchone() or (None,None,None)
    d.execute("update cell_owners set tag=?,r=?,g=?,b=?,confidence=0.9,votes=1,source='zoom_visual' where scan_id=? and cell_id=?",(tag,*old,sid,cid))
d.commit()
print(sid,d.execute("select cell_id,tag,r,g,b,source from cell_owners where scan_id=? and source!='ocr'",(sid,)).fetchall())
print(d.execute("select count(*) from cell_owners where scan_id=? and tag is null",(sid,)).fetchone())
