import json,cv2,time,sys
sys.stdout.reconfigure(encoding="utf-8")
import easyocr
M=cv2.imread(r"D:\PROJECT\TilesSurviveMap\data\720\mosaic_20261011.png")
gt=json.load(open(r"D:\PROJECT\TilesSurviveMap\data\720\tmp_badges_gt.json",encoding="utf-8"))
t=time.time();r=easyocr.Reader(["ru","en"],gpu=False);print("init",round(time.time()-t,1),flush=True)
t=time.time()
for o in gt[:14]:
    c=M[o["y"]-2:o["y"]+o["h"]+2,o["x"]:o["x"]+o["w"]]
    c=cv2.resize(c,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
    res=r.readtext(c,detail=0,paragraph=False)
    print(o["ocr"],"=>",res,flush=True)
print("per",round((time.time()-t)/14,2))
