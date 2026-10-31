import cv2,numpy as np,sys
from scipy import ndimage as ndi
def pencil(i):
    lab=cv2.cvtColor(i,cv2.COLOR_BGR2LAB).astype(np.float32);L,a,b=lab[...,0],lab[...,1],lab[...,2]
    bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((61,61))),(0,0),25)
    d=bg-L
    d=cv2.GaussianBlur(d,(0,0),1.5)
    red=cv2.dilate((((a-np.median(a))>9)).astype(np.uint8),np.ones((7,7)))>0
    blue=cv2.dilate((((np.median(b)-b)>14)).astype(np.uint8),np.ones((5,5)))>0
    p=np.percentile(d,99.7)
    dark=cv2.dilate((d>p*.62).astype(np.uint8),np.ones((5,5)))>0
    m=(d>p*.2)&~dark&~red&~blue
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((9,5)))
    lb,n=ndi.label(m,np.ones((3,3)))
    sl=ndi.find_objects(lb);ar=ndi.sum(m,lb,np.arange(1,n+1))
    keep=np.zeros(n+1,bool)
    for k,(s,a_) in enumerate(zip(sl,ar)):
        h=s[0].stop-s[0].start;w=s[1].stop-s[1].start
        if a_>220 and h>26: keep[k+1]=True
    return (keep[lb]*255).astype(np.uint8)
if __name__=='__main__':
    for p in sys.argv[1:]:
        i=cv2.imread(f'/tmp/yiyi/full/英语/IMG_{p}.jpg');m=pencil(i);cv2.imwrite(f'/tmp/yiyi/enm_{p}.png',m)
        v=cv2.cvtColor(255-m,cv2.COLOR_GRAY2BGR)
        for x in range(0,v.shape[1],200):
            cv2.line(v,(x,0),(x,v.shape[0]),(200,200,255),2);cv2.putText(v,str(x),(x+4,40),0,1.4,(0,0,255),3)
        for y in range(0,v.shape[0],200):
            cv2.line(v,(0,y),(v.shape[1],y),(200,200,255),2);cv2.putText(v,str(y),(4,y+40),0,1.4,(255,0,0),3)
        cv2.imwrite(f'/tmp/yiyi/env_{p}.jpg',cv2.resize(v,None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA))
