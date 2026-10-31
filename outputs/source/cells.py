import cv2,numpy as np,sys,json,os,pickle
sys.path.insert(0,'/tmp/yiyi/scripts')
from grid import greenmask,track
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d as g1
PAGES='5362 5364 5375 5376 5377 5379 5380 5381 5382 5383 5384 5385 5386 5387'.split()
OUT='/tmp/yiyi/cells'; os.makedirs(OUT,exist_ok=True); os.makedirs('/tmp/yiyi/strips',exist_ok=True)
def rows(L,W):
    idx=sorted(range(len(L)),key=lambda i:np.polyval(L[i][0],W/2))
    ys=[np.polyval(L[i][0],W/2) for i in idx]
    # drop near-duplicate lines
    k=[0]
    for i in range(1,len(ys)):
        if ys[i]-ys[k[-1]]>12: k.append(i)
    ys=[ys[i] for i in k]; idx=[idx[i] for i in k]
    g=np.diff(ys); srt=np.sort(g); small=np.median(srt[:len(g)//3]); th=(small+np.median(srt[-len(g)//3:]))/2
    # drop a false line splitting one row in two
    ch=True
    while ch:
        ch=False; g=np.diff(ys)
        for i in range(1,len(g)):
            w=g[max(0,i-5):i+6]; exp=np.median(w[w>th]) if (w>th).any() else th
            if g[i-1]>small*1.5 and g[i]>small*1.5 and g[i-1]+g[i]<exp*1.3:
                del ys[i]; del idx[i]; ch=True; break
    g=np.diff(ys)
    return [(idx[i],idx[i+1]) for i in range(len(g)) if th<g[i]<small*11]
def verts(band):
    # band: green map straightened h x w; find line x at top and bottom thirds
    h,w=band.shape
    def pk(b):
        p=g1(b.mean(0),1.2); return find_peaks(p,height=.8,distance=int(h*.6),prominence=.5)[0],p
    a,_=pk(band[int(h*.05):int(h*.5)]); b,_=pk(band[int(h*.5):int(h*.95)])
    pairs=[]
    for x in a:
        if len(b)==0: continue
        j=np.abs(b-x).argmin()
        if abs(b[j]-x)<h*.12: pairs.append((float(x),float(b[j])))
    return pairs
for pg in PAGES:
    img=cv2.imread(f'/tmp/yiyi/full/语文/IMG_{pg}.jpg'); H,W=img.shape[:2]
    gm=greenmask(img); L=track(gm); R=rows(L,W)
    res=[];strips=[]
    xs=np.arange(W,dtype=np.float32)
    for r,(a,b) in enumerate(R):
        t=np.polyval(L[a][0],xs); o=np.polyval(L[b][0],xs); hh=np.median(o-t)
        bh=int(hh)
        yy=(t[None,:]+(o-t)[None,:]*(np.arange(bh)/bh)[:,None]).astype(np.float32)
        xx=np.repeat(xs[None,:],bh,0)
        band=cv2.remap(gm,xx,yy,cv2.INTER_LINEAR)
        P=verts(band)
        if len(P)<4: continue
        mid=np.array([(p+q)/2 for p,q in P])
        d=np.diff(mid); pitch=np.median(d)
        # drop intruders, fill gaps
        keep=[P[0]]
        for p in P[1:]:
            dd=((p[0]+p[1])-(keep[-1][0]+keep[-1][1]))/2
            if dd<.6*pitch: continue
            n=int(round(dd/pitch))
            for k in range(1,n):
                f=k/n; keep.append((keep[-1][0]*(n-k)/(n-k+1)+p[0]/(n-k+1),keep[-1][1]*(n-k)/(n-k+1)+p[1]/(n-k+1)))
            keep.append(p)
        # extend to page edges by pitch
        while keep[0][0]-pitch>0: keep.insert(0,(keep[0][0]-pitch,keep[0][1]-pitch))
        while keep[-1][1]+pitch<W: keep.append((keep[-1][0]+pitch,keep[-1][1]+pitch))
        def Y(xv,v): return np.polyval(L[a][0],xv)*(1-v)+np.polyval(L[b][0],xv)*v
        def XY(k,u,v):  # continuous cell coordinate (col k+u, v)
            xl=keep[k][0]*(1-v)+keep[k][1]*v; xr=keep[k+1][0]*(1-v)+keep[k+1][1]*v
            x=xl+(xr-xl)*u; return [x,Y(x,v)]
        cells=[]
        for k in range(len(keep)-1):
            m=.2
            q=np.float32([XY(k,-m,-m),XY(k,1+m,-m),XY(k,1+m,1+m),XY(k,-m,1+m)])
            S=340
            M=cv2.getPerspectiveTransform(q,np.float32([[0,0],[S,0],[S,S],[0,S]]))
            c=cv2.warpPerspective(img,M,(S,S),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
            cells.append(c)
            cv2.imwrite(f'{OUT}/{pg}_{r:02d}_{k:02d}.png',c)
        # strip: cropped inner cells side by side with col numbers
        s=64; n=len(cells); st=np.full((s+16,n*s,3),255,np.uint8)
        for k,c in enumerate(cells):
            i=c[28:312,28:312]; st[16:16+s,k*s:(k+1)*s]=cv2.resize(i,(s,s),interpolation=cv2.INTER_AREA)
            cv2.putText(st,str(k),(k*s+20,13),0,.42,(0,0,200),1,cv2.LINE_AA)
        st[:, ::s]=(0,160,0)
        res.append((r,n)); strips.append(st)
    if not strips: print(pg,'none');continue
    w=max(s.shape[1] for s in strips)+70
    tot=np.full((sum(s.shape[0]+3 for s in strips),w,3),255,np.uint8);y=0
    for (r,n),s in zip(res,strips):
        tot[y:y+s.shape[0],70:70+s.shape[1]]=s
        cv2.putText(tot,f'r{r}',(4,y+50),0,.6,(200,0,0),2,cv2.LINE_AA); y+=s.shape[0]+3
    cv2.imwrite(f'/tmp/yiyi/strips/{pg}.jpg',tot,[cv2.IMWRITE_JPEG_QUALITY,88])
    print(pg,len(L),len(R),res[:1],tot.shape,flush=True)
