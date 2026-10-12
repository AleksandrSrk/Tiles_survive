import cv2,numpy as np,json,re,pytesseract
from collections import Counter
D0="/mnt/user-data/uploads/TilesSurviveMap/data/720/screens/mm_grid/"
L=json.load(open("mm_layout.json"))
rows=json.load(open("table_raw.json"))
H,W=1028,1774
mk=np.full((H,W),255,np.uint8);mk[:50,:]=0;mk[:160,:245]=0;mk[:340,1560:]=0;mk[950:,:]=0;mk[880:,1620:]=0
dt=cv2.distanceTransform(mk,cv2.DIST_L2,3)
cache={}
def frame(n):
    if n not in cache:cache[n]=cv2.imread(D0+n)
    return cache[n]
def ocr(c):
    outs=[]
    g=cv2.cvtColor(c,cv2.COLOR_BGR2GRAY)
    for fx in (4,6):
        gg=cv2.resize(g,None,fx=fx,fy=fx,interpolation=cv2.INTER_CUBIC)
        for inv in (0,1):
            _,t=cv2.threshold(gg,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            if t.mean()<127:t=255-t
            if inv:t=255-t
            t=cv2.copyMakeBorder(t,20,20,20,20,cv2.BORDER_CONSTANT,value=255)
            outs.append(pytesseract.image_to_string(t,config="--psm 7").strip())
    return outs
def tagof(s):
    s=s.replace("}","]").replace("{","[").replace("(","[").replace(")","]").replace("|[","[").replace("[ ","[").replace(" ]","]")
    m=re.search(r'\[([A-Za-z0-9А-Яа-я ]{2,5})\]',s)
    return m.group(1).replace(" ","") if m else None
res={}
for r in rows:
    bx,by=r["bx"],r["by"];cx,cy=bx+60,by+12
    cands=[]
    for n,(ox,oy) in L.items():
        x0,y0=bx-int(round(ox)),by-int(round(oy))
        if 0<=x0 and 0<=y0 and x0+190<W and y0+30<H:
            d=dt[int(y0+12),int(x0+90)]
            if d>5:cands.append((d,n,x0,y0))
    cands.sort(reverse=True)
    tags=[];txts=[]
    for d,n,x0,y0 in cands[:3]:
        im=frame(n);c=im[y0-3:y0+30,x0:x0+200]
        for t in ocr(c):
            txts.append(t);tg=tagof(t)
            if tg:tags.append(tg)
    r["frames"]=[c[1] for c in cands[:3]];r["tags_all"]=tags;r["txts"]=txts
    print(r["id"],Counter(tags).most_common(4),"| mosaic:",r["tag_raw"])
json.dump(rows,open("table_ocr2.json","w"),ensure_ascii=False)
