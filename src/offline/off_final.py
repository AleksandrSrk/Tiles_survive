import json,sqlite3,datetime,cv2,numpy as np
from collections import Counter
rows=json.load(open("table_ocr2.json"))
C={c["id"]:c for c in json.load(open("/mnt/user-data/uploads/TilesSurviveMap/assets/reference/map_type1_cells.json"))["cells"]}
def canon(tags):
    if not tags:return None,0,0
    cnt=Counter(t.upper() if t.lower() in ("zov","bds","ult","ekt","rez","deu","fnx","sun","one") else t for t in tags)
    t,n=cnt.most_common(1)[0];return t,n,len(tags)
out=[]
for r in rows:
    t,n,tot=canon(r["tags_all"]);src="frames"
    if t is None:
        t=r["tag_raw"];src="mosaic";n=1;tot=1
    conf=round(n/tot,2) if src=="frames" else 0.5
    out.append({"id":r["id"],"ring":r["ring"],"tag":t,"rgb":r["rgb"],"votes":n,"conf":conf,"src":src,"badge_xy":[r["bx"],r["by"]]})
out.sort(key=lambda r:(r["ring"],int(r["id"].split("-")[1])))
for o in out:print(o["id"],o["tag"],o["rgb"],o["votes"],o["conf"],o["src"])
now=datetime.datetime.now().isoformat(timespec="seconds")
json.dump({"state":720,"layer":"A","map_type":1,"scanned_at":now,"cells":out},open("layer_a_720.json","w"),ensure_ascii=False,indent=1)
db=sqlite3.connect("layer_a.sqlite")
db.executescript("""CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY AUTOINCREMENT,state TEXT,layer TEXT,map_type TEXT,scanned_at TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS cell_owners(scan_id INTEGER,cell_id TEXT,ring INTEGER,tag TEXT,r INTEGER,g INTEGER,b INTEGER,confidence REAL,votes INTEGER,source TEXT,PRIMARY KEY(scan_id,cell_id));""")
cur=db.execute("INSERT INTO scans(state,layer,map_type,scanned_at,note) VALUES('720','A','1',?,?)",(now,"31 кадров по миникарте, склейка SIFT, бейджи OCR по кадрам"))
sid=cur.lastrowid
for o in out:db.execute("INSERT INTO cell_owners VALUES(?,?,?,?,?,?,?,?,?,?)",(sid,o["id"],o["ring"],o["tag"],*o["rgb"],o["conf"],o["votes"],o["src"]))
db.commit();print("scan",sid,db.execute("select count(*) from cell_owners").fetchone())
# render filled schema
img=np.full((784,1086,3),(44,42,40),np.uint8)
byid={o["id"]:o for o in out}
for cid,c in C.items():
    poly=np.array(c["polygon"],np.int32)
    o=byid.get(cid)
    col=(235,235,235) if not o else tuple(int(v) for v in o["rgb"][::-1])
    cv2.fillPoly(img,[poly],col);cv2.polylines(img,[poly],True,(30,30,30),2)
    q=c["centroid"];lab=cid if not o else f'{o["tag"]}'
    cv2.putText(img,lab,(int(q[0])-22,int(q[1])+4),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),3);cv2.putText(img,lab,(int(q[0])-22,int(q[1])+4),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
cv2.imwrite("layer_a_720_filled.png",img)
