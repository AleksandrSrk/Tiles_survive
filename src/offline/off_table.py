import json,re,numpy as np,cv2
from collections import Counter,defaultdict
M=cv2.imread("state720_mosaic.png")
A=json.load(open("assign.json"))
def plate_color(b):
    x,y,w,h=b["x"],b["y"],b["w"],b["h"]
    cx=x+w//2
    pats=[M[y-45:y-12,cx-40:cx+40],M[y+h+12:y+h+45,cx-40:cx+40]]
    px=np.concatenate([p.reshape(-1,3) for p in pats if p.size])
    hsv=cv2.cvtColor(px.reshape(-1,1,3),cv2.COLOR_BGR2HSV).reshape(-1,3)
    ok=px[(hsv[:,1]>40)]
    if len(ok)<50: ok=px
    q=(ok//16)
    key=Counter(map(tuple,q)).most_common(1)[0][0]
    sel=ok[np.all(q==np.array(key),axis=1)]
    return np.median(sel,axis=0).astype(int)[::-1]  # RGB
rows=[]
for sid,v in A.items():
    b=v["badge"];m=re.search(r'\[([^\]]{1,6})\]',b["ocr"].replace("}","]").replace("|[","[").replace("(","[").replace(")","]"))
    tag=m.group(1).strip() if m else None
    rows.append({"id":sid,"ring":int(sid[1]),"ocr":b["ocr"],"tag_raw":tag,"rgb":plate_color(b).tolist(),"bx":b["x"],"by":b["y"]})
rows.sort(key=lambda r:(r["ring"],int(r["id"].split("-")[1])))
for r in rows:print(r["id"],r["rgb"],repr(r["tag_raw"]),"|",r["ocr"])
json.dump(rows,open("table_raw.json","w"),ensure_ascii=False)
