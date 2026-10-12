import cv2,numpy as np,json
M=cv2.imread("state720_mosaic.png")
hsv=cv2.cvtColor(M,cv2.COLOR_BGR2HSV);h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
m=((h>=106)&(h<=116)&(s>=110)&(s<=178)&(v>=115)&(v<=190)).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_RECT,(13,5)))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
B=[]
for i in range(1,n):
    x,y,w,hh,a=st[i]
    if 80<=w<=340 and 18<=hh<=40 and a>w*hh*0.35: B.append((int(x),int(y),int(w),int(hh)))
print(len(B),B)
old=json.load(open("badges.json"))
D=[]
for b in B:
    if all(abs(b[0]-d[0])>25 or abs(b[1]-d[1])>25 for d in old+D):D.append(b)
print(len(D))
json.dump(D,open("badges_blue.json","w"))
