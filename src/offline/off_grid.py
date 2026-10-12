import numpy as np,json,cv2
from shapely.geometry import box
from shapely.ops import unary_union
from scipy import ndimage as ndi
ws=np.load("ws.npy");ids=json.load(open("ws_ids.json"))
L=ws.copy()
# fill boundary pixels (-1) and 0 by nearest label
bad=(L<=0)
idx=ndi.distance_transform_edt(bad,return_distances=False,return_indices=True)
Lf=L[idx[0],idx[1]]
H,W=Lf.shape
def peaks(counts,gap=10,thr=25):
    pos=np.where(counts>=thr)[0];out=[];grp=[]
    for p in pos:
        if grp and p-grp[-1]>gap:out.append(grp);grp=[]
        grp.append(p)
    if grp:out.append(grp)
    return [float(np.average(g,weights=counts[g])) for g in out]
inner=(Lf>=2)
vx=((Lf[:,:-1]!=Lf[:,1:])&inner[:,:-1]&inner[:,1:]);vy=((Lf[:-1,:]!=Lf[1:,:])&inner[:-1,:]&inner[1:,:])
cx=peaks(vx.sum(0))
cy=peaks(vy.sum(1))
# rim extents (non-bg region)
nb=(ws>=2)
ys_,xs_=np.where(nb)
XL=float(np.median([np.where(nb[y])[0].min() for y in range(ys_.min()+60,ys_.max()-60,5) if nb[y].any()]))
XR=float(np.median([np.where(nb[y])[0].max() for y in range(ys_.min()+60,ys_.max()-60,5) if nb[y].any()]))
YT=float(np.median([np.where(nb[:,x])[0].min() for x in range(xs_.min()+60,xs_.max()-60,5) if nb[:,x].any()]))
YB=float(np.median([np.where(nb[:,x])[0].max() for x in range(xs_.min()+60,xs_.max()-60,5) if nb[:,x].any()]))
print("rim",XL,XR,YT,YB)
X=sorted(set([XL,XR]+[x for x in cx if XL+25<x<XR-25]));Y=sorted(set([YT,YB]+[y for y in cy if YT+25<y<YB-25]))
# merge too-close lines
def merge(v,g=12):
    o=[v[0]]
    for x in v[1:]:
        if x-o[-1]<g:o[-1]=(o[-1]+x)/2
        else:o.append(x)
    return o
X=merge(X);Y=merge(Y)
print(len(X),len(Y))
cells={}
for i in range(len(X)-1):
    for j in range(len(Y)-1):
        xa,xb,ya,yb=int(X[i]+3),int(X[i+1]-3),int(Y[j]+3),int(Y[j+1]-3)
        if xb<=xa or yb<=ya:continue
        blk=ws[ya:yb,xa:xb].ravel();blk=blk[blk>=2]
        tot=(xb-xa)*(yb-ya)
        if len(blk)<0.4*tot:continue
        lab=np.bincount(blk).argmax()
        cells.setdefault(lab,[]).append(box(X[i],Y[j],X[i+1],Y[j+1]))
polys={}
for lab,bs in cells.items():
    u=unary_union(bs)
    if u.geom_type!="Polygon":u=max(u.geoms,key=lambda g:g.area)
    polys[ids[lab-2]]=u.simplify(0.5)
rect={}
for k,p in polys.items():rect[k]=[[round(x,1),round(y,1)] for x,y in list(p.exterior.coords)[:-1]]
orig={ids[i]:(ws==i+2).sum() for i in range(len(ids))}
for k in sorted(polys):
    r=polys[k].area/orig[k]
    if r<0.8 or r>1.25:print("area ratio",k,round(r,2))
print("missing",[k for k in ids if k not in polys])
json.dump({"polys":rect,"X":X,"Y":Y,"rim":[XL,XR,YT,YB]},open("polys.json","w"))
vis=np.zeros((H,W,3),np.uint8);rng=np.random.RandomState(5)
for k,pp in rect.items():
    cv2.fillPoly(vis,[np.array(pp,np.int32)],tuple(int(v) for v in rng.randint(60,255,3)));cv2.polylines(vis,[np.array(pp,np.int32)],True,(0,0,0),2)
cv2.imwrite("polys_vis.png",vis[600:1850,600:1900])
