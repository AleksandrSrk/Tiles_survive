import cv2,numpy as np,json
G=cv2.imread("ground.png");f=0.4
g=cv2.resize(G,None,fx=f,fy=f,interpolation=cv2.INTER_AREA)
U=json.load(open("unwarp.json"));A=np.array(U["A"]);mn=np.array(U["mn"])
rows=json.load(open("table_ocr2.json"))
def tog(p):return (A@np.array(p,float)-mn)*f
gg=g.copy()
seeds={};rgbs={}
for r in rows:
    bx,by=r["bx"],r["by"]
    # find real badge bbox from badges_ocr (w,h)
for o in json.load(open("badges_ocr.json")):
    pass
bb={ (o["x"],o["y"]):o for o in json.load(open("badges_ocr.json"))}
for r in rows:
    o=bb[(r["bx"],r["by"])]
    x,y,w,h=o["x"],o["y"],o["w"],o["h"]
    pts=np.array([tog((x-6,y-6)),tog((x+w+6,y-6)),tog((x+w+6,y+h+6)),tog((x-6,y+h+6))],np.int32)
    col=tuple(int(c) for c in r["rgb"][::-1])
    cv2.fillPoly(gg,[pts],col)
    seeds[r["id"]]=tog((x+w/2,y+h/2))
    rgbs[r["id"]]=np.array(r["rgb"][::-1])
cenG=tog((2513,1850.))
def match(p,col,tol=28):
    x,y=int(p[0]),int(p[1])
    if x<6 or y<6 or x>g.shape[1]-7 or y>g.shape[0]-7:return False
    patch=g[y-4:y+5,x-4:x+5].reshape(-1,3).astype(int)
    return (np.abs(patch-col).max(1)<tol).mean()>0.7
for cid in list(seeds):
    p=np.array(seeds[cid]);d=cenG-p;d/=np.hypot(*d)
    q=p.copy()
    for k in range(0,200,3):
        q=p+d*k
        if match(q,rgbs[cid]):break
    seeds[cid]=q
seeds["R7-01"]=cenG
rgbs["R7-01"]=np.array([100,160,90])
hsv=cv2.cvtColor(gg,cv2.COLOR_BGR2HSV)
colored=(hsv[...,1]>55)&(hsv[...,2]>80)
x0,x1,y0,y1=640,1860,640,1815
box=np.zeros(colored.shape,bool);box[y0:y1,x0:x1]=True
mk=np.zeros(colored.shape,np.int32)
bgm=~(colored&box);bgm=cv2.erode(bgm.astype(np.uint8),np.ones((9,9),np.uint8)).astype(bool)
mk[bgm]=1
ids=list(seeds)
for i,cid in enumerate(ids):
    x,y=seeds[cid];cv2.circle(mk,(int(x),int(y)),7,i+2,-1)
gb=cv2.GaussianBlur(gg,(0,0),1.0)
ws=cv2.watershed(gb,mk.copy())
np.save("ws.npy",ws);json.dump(ids,open("ws_ids.json","w"))
vis=np.zeros_like(g);rng=np.random.RandomState(3)
for i,cid in enumerate(ids):
    vis[ws==i+2]=rng.randint(50,255,3)
cv2.imwrite("ws_vis.png",cv2.resize(vis,None,fx=0.75,fy=0.75))
for i,cid in enumerate(ids):
    m=(ws==i+2);ys,xs=np.where(m)
    print(cid,m.sum(),xs.min(),xs.max(),ys.min(),ys.max())
