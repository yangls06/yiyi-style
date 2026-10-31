import cv2,numpy as np,sys,json,os
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d as g1
def greenmask(img):
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32)
    a=lab[...,1]; bg=cv2.GaussianBlur(a,(0,0),25)
    return np.clip(bg-a,0,20)
def track(gm,W=60):
    H,Wd=gm.shape
    xs=list(range(W//2,Wd-W//2,W)); pk=[]
    for x in xs:
        p=g1(gm[:,x-W//2:x+W//2].mean(1),1.5)
        i,_=find_peaks(p,height=1.0,distance=8,prominence=.6); pk.append(i)
    # link: greedy chain
    chains=[]
    for k,i in enumerate(pk):
        used=set()
        for c in chains:
            if c[-1][0]<k-6: continue
            lastk,lasty=c[-1]
            sl=0
            if len(c)>=4: sl=(c[-1][1]-c[-4][1])/(c[-1][0]-c[-4][0]+1e-6)
            pred=lasty+sl*(k-lastk)
            if len(i)==0: continue
            d=np.abs(i-pred); j=int(d.argmin())
            if d[j]<10 and j not in used: c.append((k,int(i[j]))); used.add(j)
        for j,y in enumerate(i):
            if j not in used: chains.append([(k,int(y))])
    out=[]
    for c in chains:
        if len(c)<len(xs)*.3: continue
        X=np.array([xs[k] for k,_ in c],float);Y=np.array([y for _,y in c],float)
        co=np.polyfit(X,Y,3)
        r=np.abs(np.polyval(co,X)-Y);ok=r<6
        if ok.sum()<8: continue
        co=np.polyfit(X[ok],Y[ok],3)
        out.append((co,X.min(),X.max(),ok.sum()))
    Xc=Wd/2
    out.sort(key=lambda t:np.polyval(t[0],Xc))
    return out
if __name__=='__main__':
    p=sys.argv[1]; img=cv2.imread(p); gm=greenmask(img)
    L=track(gm); print(len(L))
    v=img.copy()
    xx=np.arange(0,img.shape[1],10)
    ys=[]
    for n,(co,a,b,_) in enumerate(L):
        yy=np.polyval(co,xx); ys.append(np.polyval(co,img.shape[1]/2))
        pts=np.stack([xx,yy],1).astype(np.int32)
        cv2.polylines(v,[pts],False,(0,0,255),3); cv2.putText(v,str(n),(30+40*(n%2),int(yy[3])),0,1.2,(255,0,0),3)
    print(np.round(np.diff(ys)).astype(int).tolist())
    cv2.imwrite('/tmp/yiyi/dbg.jpg',cv2.resize(v,None,fx=.35,fy=.35))
    cv2.imwrite('/tmp/yiyi/dbg_g.jpg',cv2.resize((gm*12).astype(np.uint8),None,fx=.35,fy=.35))
