import sys,cv2,numpy as np,pickle,json,warnings
warnings.filterwarnings('ignore')
sys.path[:0]=['/tmp/yiyi/scripts']
from ink import ink,norm_stroke
from enx import letter
from letters import B
from comps import comps
import strokes as S
import potrace
from multiprocessing import Pool
PEN=17        # stroke half-width in font units
def trace(arr,to_font):
    """arr: uint8 image(ink>127) -> contours of ('M'/'C'/'L', pts) in font units via to_font(x,y)"""
    F=to_font; to_font=lambda p:F(p.x,p.y)
    bm=potrace.Bitmap(arr<=127)
    pl=bm.trace(turdsize=12,alphamax=1.05,opticurve=True,opttolerance=.5)
    out=[]
    for c in pl:
        segs=[('M',to_font(c.start_point))]
        for s in c.segments:
            if s.is_corner: segs.append(('L',to_font(s.c)));segs.append(('L',to_font(s.end_point)))
            else: segs.append(('C',to_font(s.c1),to_font(s.c2),to_font(s.end_point)))
        out.append(segs)
    return out
def outline_cell(m):
    n=norm_stroke(m)            # 1020 canvas
    return n
PUNCT='，。、；！？《》'
import os
OV_=json.load(open('/tmp/yiyi/override.json'))
LOWLEFT='，。、；'
def job_cell(a):
    name,e=a; ch=name[0]
    c=cv2.imread(f"/tmp/yiyi/cells/{e['pg']}_{e['r']:02d}_{e['k']:02d}.png");m,_=ink(c,OV_.get('boost',{}).get(ch,1))
    if ch in OV_.get('clip',{}):
        a_,b_,c_,d_=OV_['clip'][ch];z=np.zeros_like(m);z[a_:b_,c_:d_]=m[a_:b_,c_:d_];m=z
    n=norm_stroke(m,rmin=10.5,rmax=14.5)
    ys,xs=np.where(n>127)
    if len(ys)==0:return None
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max();w,h=x1-x0,y1-y0
    if ch in PUNCT:
        s=1.35; cx,cy=510,510; ox,oy=500,380          # keep where she placed it in the cell
        if ch in '，。、': cx,cy=x0+w/2,y0+h/2; ox,oy=210,40      # lower-left of em
        if ch in '！？；': cx,cy=x0+w/2,y0+h/2; ox,oy=500,330
        if ch in '《》': cx,cy=x0+w/2,y0+h/2; ox,oy=500,330
    else:
        size=max(w,h); target=800                        # font units; pull toward target, keep half her size variation
        s=(target/size)**.6*(1.42**.4) if False else min(target/size*(size/560)**.4,980/size)
        cx,cy=(x0+x1)/2,(y0+y1)/2
        # damp her offset from the cell centre to 35%
        cx=cx+(510-cx)*.0; ox=500+(cx-510)*.35*s*.5
        oy=360-(cy-510)*.35*s*.5
    tf=lambda x,y:(round(ox+(x-cx)*s),round(oy-(y-cy)*s))
    small=cv2.resize(n,(510,510),interpolation=cv2.INTER_AREA)
    return name,e,trace(small,lambda x,y:tf(x*2,y*2))
def cr(p,n=14):
    P=np.array(p,float)
    if len(P)==2: return np.linspace(P[0],P[1],6)
    Q=np.vstack([P[0]*2-P[1],P,P[-1]*2-P[-2]]);o=[]
    for i in range(1,len(Q)-2):
        p0,p1,p2,p3=Q[i-1:i+3]
        for t in np.linspace(0,1,n,endpoint=False):
            o.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    o.append(Q[-2]);return np.array(o)
def stroke_glyph(tb):
    """render a stroke def into outline; returns contours and bbox-derived advance"""
    ty,tv,by,bv,xs,st=tb
    sc=(tv-bv)/(by-ty)
    C=np.zeros((1100,1100),np.uint8)  # canvas 1 px = 1 unit with offset
    ox,oy=120,860
    rng=np.random.default_rng(abs(hash(str(st)))%2**31)
    for s in st:
        P=cr(s)
        dot=len(s)==2 and np.hypot(*(np.array(s[0])-np.array(s[1])))<.3
        pts=[(ox+x*sc,oy-(tv-(y-ty)*sc)) for x,y in P]
        for k,(x,y) in enumerate(pts):
            f=k/max(len(pts)-1,1)
            r=PEN*(1.45 if dot else (.92+.14*np.sin(f*3.1)))
            cv2.circle(C,(int(x),int(y)),int(r),255,-1,cv2.LINE_AA)
        for a,b in zip(pts,pts[1:]):
            cv2.line(C,tuple(map(int,a)),tuple(map(int,b)),255,int(PEN*1.9),cv2.LINE_AA)
    C=cv2.GaussianBlur(C,(0,0),3)
    return C,ox,oy
def job_stroke(a):
    ch,tb,adv=a
    C,ox,oy=stroke_glyph(tb)
    ys,xs=np.where(C>127);x0,x1=xs.min(),xs.max()
    if adv: shift=(130-x0 if ch in LOWLEFT else (adv-(x1-x0))/2-x0); w=adv
    else: lsb=38;shift=lsb-x0;w=int(x1-x0+lsb*2)
    s=cv2.resize(C,(550,550),interpolation=cv2.INTER_AREA)
    return ch,w,trace(s,lambda x,y:(round(x*2+shift),round(oy-y*2)))
def job_mask(a):
    """auto-extracted letter/digit: normalise to 240px tall then re-stroke, map to font (top,bot)"""
    ch,m,top,bot=a
    from scipy import ndimage as ndi_
    lb_,n_=ndi_.label(m>0,np.ones((3,3)))
    if n_>1:
        ar_=ndi_.sum(m>0,lb_,np.arange(1,n_+1));m=(np.isin(lb_,np.where(ar_>=ar_.max()*.12)[0]+1)*255).astype(np.uint8)
    ys,xs=np.where(m>0);m=m[ys.min():ys.max()+1,xs.min():xs.max()+1]
    h=(top-bot);f=240/m.shape[0];mm=cv2.resize(m,None,fx=f,fy=f,interpolation=cv2.INTER_AREA)
    mm=cv2.copyMakeBorder(mm,50,50,50,50,cv2.BORDER_CONSTANT,value=0)
    n=norm_stroke((mm>100).astype(np.uint8)*255,rmin=17,rmax=23)
    ys,xs=np.where(n>127);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    s=h/(y1-y0);lsb=40
    tf=lambda x,y:(round(lsb+(x-x0)*s),round(bot+(y1-y)*s))
    small=cv2.resize(n,None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA)
    return ch,int((x1-x0)*s+2*lsb),trace(small,lambda x,y:tf(x*2,y*2))
DIG={'0':[('5396',43),('5396',81)],'1':[('5396',24),('5396',56)],'2':[('5396',5),('5396',27)],'3':[('5396',47),('5396',191)],'4':[('5396',29),('5396',236)],'5':[('5396',6),('5396',243)],'6':[('5396',55),('5396',124)],'7':[('5396',14),('5396',125)],'8':[('5396',7),('5396',26)],'9':[('5396',20),('5396',83)]}
def digits():
    res=[];cache={}
    for d,v in DIG.items():
        for n,(pg,i) in enumerate(v):
            if pg not in cache:
                cache[pg]=comps(f'/tmp/yiyi/full/数学/IMG_{pg}.jpg',50,170,130)
                cs=json.load(open(f'/tmp/yiyi/comp_{pg}.png.json'));cache[pg]=(cache[pg][1],cs)
            lb,cs=cache[pg];x,y,w,h,l=cs[i]
            m=((lb[y:y+h,x:x+w]==l)*255).astype(np.uint8)
            res.append((d if n==0 else f'{d}.alt',m,640,0))
    return res
AUTO={'d':(720,0),'h':(720,0),'k':(720,0),'n':(430,0),'y':(430,-260),'S':(700,0),'B':(700,0)}
if __name__=='__main__':
    db=pickle.load(open('/tmp/yiyi/db.pkl','rb'))
    OV=json.load(open('/tmp/yiyi/override.json')) if __import__('os').path.exists('/tmp/yiyi/override.json') else {}
    jobs=[]
    for ch,v in db.items():
        if ch in OV.get('drop',[]):continue
        forced=OV.get('pick',{}).get(ch)
        banned=set(tuple(b) for b in OV.get('ban',{}).get(ch,[]))
        vv=[e for e in v if (e['pg'],e['r'],e['k']) not in banned]
        if forced: vv=[e for e in v if (e['pg'],e['r'],e['k'])==tuple(forced)]+vv
        if not vv:continue
        best=vv[0];sel=[best]
        for e in vv[1:]:
            if len(sel)<3 and e['q']>best['q']*.8 and ch not in PUNCT: sel.append(e)
        for n,e in enumerate(sel): jobs.append((ch if n==0 else f'{ch}.alt{n}',e))
    with Pool(8) as p:
        hz=[r for r in p.map(job_cell,[(j[0][0],j[1]) if False else j for j in [(a[0],a[1]) for a in jobs]],chunksize=8) if r]
    print(len(hz))
    mjobs=digits()
    for k,(t,b) in AUTO.items():
        m,_=letter(*B[k]);mjobs.append((k,m,t,b))
    with Pool(8) as p: md=p.map(job_mask,mjobs)
    sj=[(k,v,None) for k,v in {**S.T,**S.F}.items()]+[(k,v[:4]+(None,v[5]),v[4]) for k,v in S.P.items()]
    with Pool(8) as p: sg=p.map(job_stroke,sj)
    pickle.dump(dict(hz=hz,md=md,sg=sg),open('/tmp/yiyi/glyphs.pkl','wb'));print(len(md),len(sg))
