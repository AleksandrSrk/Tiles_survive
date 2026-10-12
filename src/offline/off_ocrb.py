import cv2,numpy as np,json,pytesseract,re
M=cv2.imread("state720_mosaic.png")
B=json.load(open("badges.json"))
out=[]
for x,y,w,h in B:
    c=M[y-2:y+h+2,x:x+w]
    g=cv2.cvtColor(c,cv2.COLOR_BGR2GRAY)
    g=cv2.resize(g,None,fx=5,fy=5,interpolation=cv2.INTER_CUBIC)
    # text is light on red: invert thresholding
    _,t=cv2.threshold(g,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    if t.mean()<127: t=255-t
    t=cv2.copyMakeBorder(t,20,20,20,20,cv2.BORDER_CONSTANT,value=255)
    txt=pytesseract.image_to_string(t,config="--psm 7").strip()
    out.append({"x":x,"y":y,"w":w,"h":h,"ocr":txt})
    print(x,y,w,repr(txt))
json.dump(out,open("badges_ocr.json","w"),ensure_ascii=False)
