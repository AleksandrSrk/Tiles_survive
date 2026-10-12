import json,math,numpy as np,cv2,itertools
from shapely.geometry import Polygon
P=json.load(open("polys.json"))["polys"]
C={c["id"]:c for c in json.load(open("/mnt/user-data/uploads/TilesSurviveMap/assets/reference/map_type1_cells.json"))["cells"]}
own={o["id"]:o for o in json.load(open("layer_a_720.json"))["cells"]}
own["R7-01"]={"tag":"HoD","rgb":[100,160,90],"conf":0.5}
xs=[p[0] for v in P.values() for p in v];ys=[p[1] for v in P.values() for p in v]
x0,y0=min(xs),min(ys);side=max(max(xs)-x0,max(ys)-y0)
T={k:[((p[0]-x0)/side*1000,(p[1]-y0)/side*1000) for p in v] for k,v in P.items()}
SH={k:Polygon(v) for k,v in T.items()}
edges=[]
for a,b in itertools.combinations(sorted(T),2):
    inter=SH[a].buffer(1.5).intersection(SH[b].buffer(1.5))
    if inter.area>1.5*20:edges.append((a,b))
E0=set((min(k,n),max(k,n)) for k,c in C.items() for n in c["neighbors"] if k in T and n in T)
E1=set(edges)
print("edges",len(E1),"schema",len(E0),"common",len(E1&E0),"only mine",sorted(E1-E0),"only schema",sorted(E0-E1))
nb={k:[] for k in T}
for a,b in edges:nb[a].append(b);nb[b].append(a)
th=math.radians(35.2);c,s=math.cos(th),math.sin(th)
iso=lambda p:(c*(p[0]+p[1]),s*(p[1]-p[0]))
out={"map_type":"1","note":"шаблон перерисован по реальной карте штата 720 (макс. отдаление). Координаты ground: квадрат 0..1000, x вправо, y вниз; iso: x=cos(35.2°)*(gx+gy), y=sin(35.2°)*(gy-gx)","cells":[]}
for k in sorted(T,key=lambda k:(-int(k[1]),k)):
    r=SH[k]
    out["cells"].append({"id":k,"ring":int(k[1]),"area":round(r.area,1),"centroid":[round(r.centroid.x,1),round(r.centroid.y,1)],
        "polygon":[[round(a,1),round(b,1)] for a,b in T[k]],"iso_polygon":[[round(iso(p)[0],1),round(iso(p)[1],1)] for p in T[k]],"neighbors":sorted(nb[k]),"owner":None})
json.dump(out,open("template_type1_v2.json","w"),ensure_ascii=False,indent=1)
ringcol={7:(150,200,140),6:(205,205,255),5:(200,255,255),4:(230,205,255),3:(255,230,200),2:(200,235,205),1:(205,225,250)}
def render(mode,fn,scale=1.7):
    f=(lambda p:iso(p)) if mode=="iso" else (lambda p:p)
    pts=[f(p) for v in T.values() for p in v];mnx=min(q[0] for q in pts);mny=min(q[1] for q in pts)
    Wd=int((max(q[0] for q in pts)-mnx)*scale)+80;Hd=int((max(q[1] for q in pts)-mny)*scale)+80
    ss=2;img=np.full((Hd*ss,Wd*ss,3),(42,40,38),np.uint8)
    tr=lambda p:((f(p)[0]-mnx)*scale+40,(f(p)[1]-mny)*scale+40)
    for k,v in T.items():
        pp=np.array([[tr(p)[0]*ss,tr(p)[1]*ss] for p in v],np.int32)
        col=ringcol[int(k[1])] if "empty" in fn else tuple(own[k]["rgb"])
        cv2.fillPoly(img,[pp],tuple(int(x) for x in col[::-1]));cv2.polylines(img,[pp],True,(30,30,30),3*ss//2,cv2.LINE_AA)
    img=cv2.resize(img,(Wd,Hd),interpolation=cv2.INTER_AREA)
    for k,v in T.items():
        cc=SH[k].representative_point();q=tr((cc.x,cc.y))
        if "empty" in fn:
            cv2.putText(img,k,(int(q[0])-len(k)*4,int(q[1])+4),cv2.FONT_HERSHEY_SIMPLEX,0.5,(30,30,30),1,cv2.LINE_AA)
        else:
            lab=own[k]["tag"]
            cv2.putText(img,lab,(int(q[0])-len(lab)*5,int(q[1])+2),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),3,cv2.LINE_AA)
            cv2.putText(img,lab,(int(q[0])-len(lab)*5,int(q[1])+2),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(img,k,(int(q[0])-len(k)*3,int(q[1])+16),cv2.FONT_HERSHEY_SIMPLEX,0.34,(25,25,25),1,cv2.LINE_AA)
    cv2.imwrite(fn,img);print(fn,img.shape)
render("iso","tpl_iso_empty.png");render("iso","tpl_iso_720.png");render("ground","tpl_ground_empty.png",1.2);render("ground","tpl_ground_720.png",1.2)
