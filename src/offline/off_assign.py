import json,math,numpy as np,cv2
from scipy.optimize import linear_sum_assignment
O=[o for o in json.load(open("badges_ring.json")) if o["ring"]]
C=json.load(open("/mnt/user-data/uploads/TilesSurviveMap/assets/reference/map_type1_cells.json"))["cells"]
th=math.radians(35.2);c,s=math.cos(th),math.sin(th)
def ground(p,cen):
    x,y=p[0]-cen[0],p[1]-cen[1]
    return np.array([(x/c-y/s)/2,(x/c+y/s)/2])
cenM=np.array([2513,1850.]);cenS=np.array([537.9,387.1])
def ang(g):return math.atan2(g[1],g[0])
def cdiff(a,b):
    d=abs(a-b)%(2*math.pi);return min(d,2*math.pi-d)
asg={}
for r in range(1,7):
    S=[cc for cc in C if cc["ring"]==r];B=[o for o in O if o["ring"]==r]
    cost=np.array([[cdiff(ang(ground(cc["centroid"],cenS)),ang(ground((o["cx"],o["cy"]),cenM))) for o in B] for cc in S])
    ri,ci=linear_sum_assignment(cost)
    for i,j in zip(ri,ci):asg[S[i]["id"]]=(B[j],float(cost[i,j]))
    print(r,len(S),len(B),"mean ang err deg",round(math.degrees(np.mean([cost[i,j] for i,j in zip(ri,ci)])),1),"max",round(math.degrees(max(cost[i,j] for i,j in zip(ri,ci))),1))
M=cv2.imread("state720_mosaic.png")
for sid,(o,e) in asg.items():
    cv2.putText(M,sid,(int(o["cx"])-60,int(o["cy"])-14),cv2.FONT_HERSHEY_SIMPLEX,1.7,(255,255,255),7)
    cv2.putText(M,sid,(int(o["cx"])-60,int(o["cy"])-14),cv2.FONT_HERSHEY_SIMPLEX,1.7,(0,0,0),3)
cv2.imwrite("assign_overlay.png",cv2.resize(M,None,fx=0.35,fy=0.35,interpolation=cv2.INTER_AREA))
missing=[cc["id"] for cc in C if cc["ring"]<=6 and cc["id"] not in asg]
print("missing",missing)
json.dump({k:{"badge":v[0],"err":v[1]} for k,v in asg.items()},open("assign.json","w"),ensure_ascii=False)
