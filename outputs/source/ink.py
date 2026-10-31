import cv2,numpy as np,sys
from skimage.morphology import skeletonize
from scipy import ndimage as ndi
S=340;A=57;B=283
def ink(c,boost=1):
    """c: BGR 340 cell. returns mask(uint8), stats dict"""
    lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32)
    L,a,b=lab[...,0],lab[...,1],lab[...,2]
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(35,35))
    bgL=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,k),(0,0),15)
    ma,mb=np.median(a),np.median(b)
    d=bgL-L
    red=(a-ma)>9
    red=cv2.dilate(red.astype(np.uint8),np.ones((3,3)))>0
    edge=np.ones(a.shape,bool); edge[A+16:B-16,A+16:B-16]=False
    green=((ma-a)>3.5)&((mb-b)<7)&(d<45)&edge
    v=d.copy(); v[red]=0; v[green&(d<45)]=0
    v=cv2.GaussianBlur(v,(0,0),.9)
    hi=np.percentile(v[A:B,A:B],99.3)
    if hi<16: return np.zeros(v.shape,np.uint8),dict(hi=hi,red=0,green=0,area=0)
    th_lo=max(9,hi*.30)*boost; th_hi=max(13,hi*.45)*boost
    lo=v>th_lo
    # erase long straight grid lines hugging the cell edge
    u=lo.astype(np.uint8)
    hl=cv2.morphologyEx(u,cv2.MORPH_OPEN,np.ones((1,110),np.uint8)); vl=cv2.morphologyEx(u,cv2.MORPH_OPEN,np.ones((110,1),np.uint8))
    band=np.zeros(u.shape,np.uint8); band[A-22:A+22,:]=1;band[B-22:B+22,:]=1
    bandv=np.zeros(u.shape,np.uint8); bandv[:,A-22:A+22]=1;bandv[:,B-22:B+22]=1
    gl=(hl&band)|(vl&bandv)
    # short/tilted fragments of the horizontal rules right on the cell edge
    tight=np.zeros(u.shape,np.uint8); tight[A-13:A+14,:]=1; tight[B-13:B+14,:]=1
    d2=cv2.dilate(u,np.ones((3,3),np.uint8))
    for t in (-.06,-.03,0,.03,.06):
        K=np.zeros((9,61),np.uint8)
        for i in range(61): K[int(round(4+t*(i-30))),i]=1
        gl|=cv2.morphologyEx(d2,cv2.MORPH_OPEN,K)&tight
    gl=cv2.dilate(gl,np.ones((5,5),np.uint8))>0
    lo=lo&~gl; v=v*(~gl)
    lab_,n=ndi.label(lo,np.ones((3,3)))
    if n==0: return np.zeros(v.shape,np.uint8),dict(hi=hi,red=0,green=0,area=0)
    keep=np.zeros(n+1,bool)
    idx=np.arange(1,n+1)
    mx=ndi.maximum(v,lab_,idx); ar=ndi.sum(lo,lab_,idx)
    sl=ndi.find_objects(lab_)
    inner=ndi.sum((lambda m:m)(np.pad(np.ones((B-A,B-A)),A)>0)&lo,lab_,idx)
    cent=np.zeros(v.shape,bool);cent[80:260,80:260]=True
    incent=ndi.sum(cent&lo,lab_,idx)
    for i in range(n):
        if mx[i]<th_hi or ar[i]<14: continue
        y,x=sl[i]
        touch=y.start<=0 or x.start<=0 or y.stop>=S or x.stop>=S
        frac=inner[i]/ar[i]
        if frac>.62 and not(touch and frac<.8): keep[i+1]=True
        elif incent[i]>0.45*ar[i]: keep[i+1]=True
    m=keep[lab_]
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    return m*255,dict(hi=float(hi),red=int((red[A:B,A:B]).sum()),green=int(green.sum()),area=int(m.sum()))
def clean(m):
    from skimage.morphology import remove_small_holes,remove_small_objects
    b=m>0
    b=remove_small_holes(b,30); b=remove_small_objects(b,16,connectivity=2)
    return (b*255).astype(np.uint8)
def prune(sk,n=14):
    """remove skeleton spurs shorter than n pixels"""
    sk=sk.astype(np.uint8)
    K=np.ones((3,3),np.float32);K[1,1]=0
    orig=sk.copy()
    cur=sk.copy()
    for _ in range(n):
        nb=cv2.filter2D(cur,-1,K,borderType=cv2.BORDER_CONSTANT)
        cur=cur&~((nb==1)&(cur==1))
    # regrow surviving ends along the original skeleton
    for _ in range(n):
        nb=cv2.dilate(cur,np.ones((3,3),np.uint8))
        ends=(cv2.filter2D(cur,-1,K,borderType=cv2.BORDER_CONSTANT)==1)&(cur==1)
        grow=cv2.dilate(ends.astype(np.uint8),np.ones((3,3),np.uint8))&orig&~cur
        cur=cur|grow
    return cur>0
def norm_stroke(m,scale=3,rmin=8.5,rmax=12.5):
    """Pen-like outline: re-stroke the skeleton, keeping part of her pressure variation."""
    u=cv2.resize(clean(m),None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    u=cv2.GaussianBlur(u,(0,0),3)>105
    sk=prune(skeletonize(u))
    dt=ndi.distance_transform_edt(u)
    w=cv2.GaussianBlur(dt.astype(np.float32),(0,0),6)
    out=np.zeros(u.shape,np.uint8)
    ys,xs=np.where(sk)
    if len(ys)==0: return out
    med=np.median(dt[sk])
    for y,x in zip(ys,xs):
        r=np.clip((rmin+rmax)/2*(dt[y,x]/max(med,1))**.6,rmin,rmax)
        cv2.circle(out,(int(x),int(y)),int(round(r)),255,-1,cv2.LINE_8)
    return cv2.GaussianBlur(out,(0,0),2.2)
