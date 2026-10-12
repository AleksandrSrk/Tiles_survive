import cv2,numpy as np,glob,re,json,sys
D0="/mnt/user-data/uploads/TilesSurviveMap/data/720/screens/mm_grid/"
S="/tmp/claude-0/-home-claude/ba70449b-8666-53e8-a58d-b34a47d4b1dc/scratchpad/"
j=json.load(open("/dev/stdin")) if False else None
import os
names=[l.strip() for l in open(S+"mmlist.txt")]
P={n:(int(re.search(r'x(\d+)',n).group(1)),int(re.search(r'y([+-]\d+)',n).group(1))) for n in names}
sift=cv2.SIFT_create(6000);bf=cv2.BFMatcher()
def F(n):
    g=cv2.cvtColor(cv2.imread(D0+n),cv2.COLOR_BGR2GRAY);m=np.zeros(g.shape,np.uint8);m[170:930,240:1570]=255
    return sift.detectAndCompute(g,m)
Fe={n:F(n) for n in names}
def mode(a,b,prior,rad=120):
    ka,da=Fe[a];kb,db=Fe[b]
    ms=[m for m,n in (p for p in bf.knnMatch(da,db,k=2) if len(p)==2) if m.distance<0.8*n.distance]
    if not ms: return None,0
    d=np.float32([np.array(kb[m.trainIdx].pt)-np.array(ka[m.queryIdx].pt) for m in ms])
    d=d[np.linalg.norm(d-prior,axis=1)<rad]
    best=None;bi=0
    for x in d:
        inl=np.linalg.norm(d-x,axis=1)<2.5
        if inl.sum()>bi:bi=inl.sum();best=d[inl].mean(0)
    return best,bi
KX,KY=31.4,34.0
edges=[]
for i,a in enumerate(names):
  for b in names[i+1:]:
    dx=P[b][0]-P[a][0];dy=P[b][1]-P[a][1]
    if abs(dx)<=18 and abs(dy)<=24 and (dx,dy)!=(0,0):
        pr=np.array([-KX*dx,-KY*dy])   # content shift
        s,n=mode(a,b,pr)
        if s is not None and n>=12:
            edges.append((a,b,s,n,pr)); 
print(len(edges),"edges")
# estimate scales
xs=[(-s[0]/(P[b][0]-P[a][0])) for a,b,s,n,pr in edges if P[b][0]!=P[a][0] and n>=20]
ys=[(-s[1]/(P[b][1]-P[a][1])) for a,b,s,n,pr in edges if P[b][1]!=P[a][1] and n>=20]
print("KX med",np.median(xs),len(xs),"KY med",np.median(ys),len(ys))
json.dump([[a,b,s.tolist(),int(n)] for a,b,s,n,pr in edges],open(S+"mmedges.json","w"))
