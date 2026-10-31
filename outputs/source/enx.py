import sys,cv2,numpy as np
sys.path[:0]=['/tmp/yiyi/scripts']
from letters import B
from scipy import ndimage as ndi
def letter(p,x0,y0,x1,y1,pad=14):
    i=cv2.imread(f'/tmp/yiyi/full/英语/IMG_{p}.jpg')
    W_=240
    X0=max(0,x0-W_);X1=min(i.shape[1],x1+W_);Y0=y0-40;Y1=y1+40
    c=i[Y0:Y1,X0:X1]
    lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32);L,a=lab[...,0],lab[...,1]
    bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((51,51))),(0,0),21)
    d=cv2.GaussianBlur(bg-L,(0,0),1.6); d[cv2.dilate(((a-np.median(a))>9).astype(np.uint8),np.ones((5,5)))>0]=0
    cut=d[:,x0-X0:x1-X0]; hi=np.percentile(cut,98.5); u=(d>hi*.40).astype(np.uint8)
    H,W=u.shape
    # find tilt with the sharpest row projection
    best=(0,0)
    for t in np.linspace(-.1,.1,21):
        M=np.float32([[1,0,0],[t,1,-t*W/2]]);r=cv2.warpAffine(u,M,(W,H),flags=cv2.INTER_NEAREST)
        v=r.mean(1).max()
        if v>best[0]:best=(v,t)
    t=best[1];M=np.float32([[1,0,0],[t,1,-t*W/2]])
    r=cv2.warpAffine(u,M,(W,H),flags=cv2.INTER_NEAREST); prof=r.mean(1)
    rows=np.where(prof>.33)[0]
    for y in rows:
        lo=max(0,y-9);hi_=min(H,y+10)
        for x in range(W):
            if not r[y,x]:continue
            a0=y
            while a0>0 and r[a0-1,x]:a0-=1
            b0=y
            while b0<H-1 and r[b0+1,x]:b0+=1
            if b0-a0<=16: r[a0:b0+1,x]=2
    r=(r==1).astype(np.uint8)
    u2=cv2.warpAffine(r,cv2.invertAffineTransform(M),(W,H),flags=cv2.INTER_NEAREST)
    u2=u2[:,x0-X0-pad:x1-X0+pad]
    u2=cv2.morphologyEx(u2,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,17)))
    lb,n=ndi.label(u2,np.ones((3,3)))
    if n==0:return u2*255,40
    ar=ndi.sum(u2,lb,np.arange(1,n+1));keep=np.zeros(n+1,bool)
    H,W=u2.shape;sl=ndi.find_objects(lb)
    for k,s_ in enumerate(sl):
        cx=(s_[1].start+s_[1].stop)/2
        if ar[k]>110 and pad*.8<cx<W-pad*.8: keep[k+1]=True
    return (keep[lb]*255).astype(np.uint8),40
if __name__=='__main__':
    from PIL import Image,ImageDraw
    ks=list(B);cw=150;cols=8;I=Image.new('RGB',(cols*cw,((len(ks)+cols-1)//cols)*cw),'white');D=ImageDraw.Draw(I)
    for n,k in enumerate(ks):
        m,_=letter(*B[k]);t=Image.fromarray(255-m);t.thumbnail((cw-6,cw-20))
        x,y=(n%cols)*cw,(n//cols)*cw;I.paste(t.convert('RGB'),(x+3,y+18));D.text((x+3,y+2),k,fill='red')
    I.save('/tmp/yiyi/letters.png')
