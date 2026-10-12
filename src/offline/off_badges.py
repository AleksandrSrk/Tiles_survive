import cv2,numpy as np,json
M=cv2.imread("state720_mosaic.png")
hsv=cv2.cvtColor(M,cv2.COLOR_BGR2HSV)
h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
red=(((h<=8)|(h>=172))&(s>110)&(v>110)&(v<235)).astype(np.uint8)*255
red=cv2.morphologyEx(red,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_RECT,(9,5)))
n,lab,st,cen=cv2.connectedComponentsWithStats(red)
B=[]
for i in range(1,n):
    x,y,w,hh,a=st[i]
    if 60<=w<=330 and 14<=hh<=45 and a>w*hh*0.35:
        B.append((int(x),int(y),int(w),int(hh)))
print(len(B))
B.sort(key=lambda b:(b[1],b[0]))
# dedupe
D=[]
for b in B:
    if all(abs(b[0]-d[0])>25 or abs(b[1]-d[1])>25 for d in D):D.append(b)
print(len(D))
json.dump(D,open("badges.json","w"))
ov=M.copy()
for x,y,w,hh in D: cv2.rectangle(ov,(x,y),(x+w,y+hh),(0,255,0),4)
cv2.imwrite("badges_overlay.png",cv2.resize(ov,None,fx=0.35,fy=0.35,interpolation=cv2.INTER_AREA))
print(sorted([(b[2],b[3]) for b in D])[:5],sorted([(b[2],b[3]) for b in D])[-5:])
