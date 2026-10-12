import json,re,numpy as np,cv2
O=json.load(open("badges_ocr.json"))
C=json.load(open("/mnt/user-data/uploads/TilesSurviveMap/assets/reference/map_type1_cells.json"))["cells"]
def ring(t):
    s=t
    if re.search(r'ccne|Uentp|Llentp|entp',s):return 5
    if re.search(r'Boen|6a3|oenH',s):return 6
    if re.search(r'Mer|eran|anon|ranon',s):return 4
    if re.search(r'opog|opoK|ТоР|Topo|fopo|Fopo',s):return 3
    if re.search(r'3a|as0|ae0|aso|a80|ae|aB0|a30',s):return 2
    if re.search(r'epes|Dep|Qep|esn|esx|ersu|Mep|epe|esu',s):return 1
    return None
for o in O:
    o["ring"]=o.get("ring_fix") or ring(o["ocr"]);o["cx"]=o["x"]+o["w"]/2;o["cy"]=o["y"]+o["h"]/2
from collections import Counter
print(Counter(o["ring"] for o in O))
print([ (o["ocr"],) for o in O if o["ring"] is None])
json.dump(O,open("badges_ring.json","w"),ensure_ascii=False)
# schema centroids
S=[(c["id"],c["ring"],np.array(c["centroid"])) for c in C if c["ring"]<=6]
Bp=[(i,o["ring"],np.array([o["cx"],o["cy"]])) for i,o in enumerate(O) if o["ring"]]
A=np.array([[4.7,0,2513-4.7*537.9],[0,4.7,1850-4.7*387.1]])
for it in range(30):
    src=[];dst=[]
    for sid,sr,sc in S:
        p=A[:,:2]@sc+A[:,2]
        cand=[(np.hypot(*(b-p)),bi,b) for bi,br,b in Bp if br==sr]
        if not cand:continue
        d,bi,b=min(cand,key=lambda t:t[0])
        if d<450:src.append(sc);dst.append(b)
    if len(src)<6:break
    src=np.array(src);dst=np.array(dst)
    M,inl=cv2.estimateAffine2D(src.astype(np.float32),dst.astype(np.float32),method=cv2.RANSAC,ransacReprojThreshold=120)
    A=M
print("pairs",len(src),"affine",A.round(3))
res=[]
for sid,sr,sc in S:
    p=A[:,:2]@sc+A[:,2]
    cand=[(np.hypot(*(b-p)),bi) for bi,br,b in Bp if br==sr]
    d,bi=min(cand) if cand else (1e9,None)
    res.append((sid,sr,round(d),bi))
print(sorted(res,key=lambda t:-t[2])[:15])
json.dump(A.tolist(),open("affine.json","w"))
