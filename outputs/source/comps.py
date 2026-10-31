# numbered component sheet for digits / latin
import sys,cv2,numpy as np,json
from PIL import Image,ImageDraw
def comps(p,hmin,hmax,wmax,crop=None):
    img=cv2.imread(p)
    if crop: x0,y0,x1,y1=crop;img=img[y0:y1,x0:x1]
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32);L=lab[...,0];a=lab[...,1]
    bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((41,41))),(0,0),21)
    d=bg-L; red=cv2.dilate(((a-np.median(a))>10).astype(np.uint8),np.ones((5,5)))>0
    d[red]=0; d=cv2.GaussianBlur(d,(0,0),1.1)
    m=(d>max(22,np.percentile(d,99)*.35)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3)))
    n,lb,st,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    out=[]
    for i in range(1,n):
        x,y,w,h,ar=st[i]
        if hmin<=h<=hmax and w<=wmax and ar>60: out.append((x,y,w,h,i))
    return img,lb,out
if __name__=='__main__':
    p,o,hmin,hmax,wmax=sys.argv[1],sys.argv[2],*map(int,sys.argv[3:6])
    img,lb,cs=comps(p,hmin,hmax,wmax)
    cs.sort(key=lambda c:(c[0]//250,c[1]))
    cols=20;cw=78;rows=(len(cs)+cols-1)//cols
    I=Image.new('RGB',(cols*cw,max(rows,1)*(cw+12)),'white');D=ImageDraw.Draw(I)
    for n,(x,y,w,h,i) in enumerate(cs):
        c=img[max(0,y-6):y+h+6,max(0,x-6):x+w+6]
        t=Image.fromarray(c[...,::-1]);t.thumbnail((cw-2,cw-2))
        X,Y=(n%cols)*cw,(n//cols)*(cw+12);I.paste(t,(X+1,Y+12));D.text((X+2,Y),str(n),fill='red')
    I.save(o);json.dump([list(map(int,c)) for c in cs],open(o+'.json','w'));print(len(cs))
