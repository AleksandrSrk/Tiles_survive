import cv2,numpy as np,math,json
M=cv2.imread("state720_mosaic.png");h,w=M.shape[:2]
th=math.radians(35.2);c,s=math.cos(th),math.sin(th)
A=np.array([[1/(2*c),-1/(2*s)],[1/(2*c),1/(2*s)]])
corners=np.array([[0,0],[w,0],[0,h],[w,h]],float)@A.T
mn=corners.min(0);mx=corners.max(0)
Wd,Hd=int(mx[0]-mn[0])+1,int(mx[1]-mn[1])+1
Mat=np.hstack([A,-mn[:,None]]).astype(np.float64)
G=cv2.warpAffine(M,Mat,(Wd,Hd),flags=cv2.INTER_AREA)
print(G.shape,mn)
json.dump({"A":A.tolist(),"mn":mn.tolist()},open("unwarp.json","w"))
cv2.imwrite("ground.png",G)
cv2.imwrite("ground_small.png",cv2.resize(G,None,fx=0.4,fy=0.4,interpolation=cv2.INTER_AREA))
