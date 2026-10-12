import cv2,numpy as np,json,re
D0="/mnt/user-data/uploads/TilesSurviveMap/data/720/screens/mm_grid/"
names=[l.strip() for l in open("mmlist.txt")]
P={n:(int(re.search(r'x(\d+)',n).group(1)),int(re.search(r'y([+-]\d+)',n).group(1))) for n in names}
E=json.load(open("mmedges.json"))
idx={n:i for i,n in enumerate(names)};N=len(names)
KX,KY=31.5,31.5
out={}
for ax in (0,1):
    A=[];b=[]
    for a,bn,s,n in E:
        r=np.zeros(N);r[idx[bn]]=1;r[idx[a]]=-1
        A.append(r*np.sqrt(n));b.append(-s[ax]*np.sqrt(n))
    for nme in names:
        r=np.zeros(N);r[idx[nme]]=1
        A.append(r*0.5);b.append((KX if ax==0 else KY)*P[nme][ax]*0.5)
    out[ax]=np.linalg.lstsq(np.array(A),np.array(b),rcond=None)[0]
V={n:(out[0][idx[n]],out[1][idx[n]]) for n in names}
res=[]
for a,bn,s,n in E:
    pred=-(np.array(V[bn])-np.array(V[a]));res.append(np.hypot(*(pred-np.array(s))))
print("edge residual med/max",np.median(res),max(res))
dev=[np.hypot(V[n][0]-KX*P[n][0],V[n][1]-KY*P[n][1]) for n in names];print("dev from click prior max",max(dev),"median",np.median(dev))
mnx=min(v[0] for v in V.values());mny=min(v[1] for v in V.values())
H,W=1028,1774
m=np.full((H,W),255,np.uint8)
m[:50,:]=0;m[:160,:245]=0;m[:340,1560:]=0;m[950:,:]=0;m[880:,1620:]=0
dt=cv2.distanceTransform(m,cv2.DIST_L2,3).astype(np.float32)
Wc=int(max(v[0] for v in V.values())-mnx+W+2);Hc=int(max(v[1] for v in V.values())-mny+H+2)
print("canvas",Wc,Hc)
can=np.zeros((Hc,Wc,3),np.uint8);best=np.zeros((Hc,Wc),np.float32)
for n in names:
    ox=int(round(V[n][0]-mnx));oy=int(round(V[n][1]-mny))
    im=cv2.imread(D0+n);sl=(slice(oy,oy+H),slice(ox,ox+W))
    u=dt>best[sl];can[sl][u]=im[u];best[sl][u]=dt[u]
cv2.imwrite("mm_mosaic_full.png",can)
sc=1800/Wc
cv2.imwrite("mm_mosaic_small.png",cv2.resize(can,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA))
json.dump({n:[V[n][0]-mnx,V[n][1]-mny] for n in names},open("mm_layout.json","w"))
