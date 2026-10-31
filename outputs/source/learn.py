"""Register her samples to Make-Me-a-Hanzi medians; build a per-stroke library of her deviations."""
import sys,json,pickle,cv2,numpy as np,warnings
warnings.filterwarnings('ignore')
sys.path[:0]=['/tmp/yiyi/scripts']
from ink import ink,clean,prune
from skimage.morphology import skeletonize
from scipy import ndimage as ndi
from scipy.optimize import minimize
from scipy.spatial import cKDTree
from multiprocessing import Pool
HW='/tmp/yiyi/ext/hwd/package/'
OV=json.load(open('/tmp/yiyi/override.json'))
def mmh(ch):
    try:d=json.load(open(HW+ch+'.json'))
    except FileNotFoundError:return None
    return [np.array([[x,900-y] for x,y in m],float) for m in d['medians']]
def resample(P,n):
    P=np.asarray(P,float);d=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]
    if d[-1]<1e-6:return np.repeat(P[:1],n,0)
    s=np.linspace(0,d[-1],n);return np.stack([np.interp(s,d,P[:,0]),np.interp(s,d,P[:,1])],1)
def her_mask(ch,e):
    c=cv2.imread(f"/tmp/yiyi/cells/{e['pg']}_{e['r']:02d}_{e['k']:02d}.png")
    m,_=ink(c,OV.get('boost',{}).get(ch,1))
    if ch in OV.get('clip',{}):
        a,b,cc,d=OV['clip'][ch];z=np.zeros_like(m);z[a:b,cc:d]=m[a:b,cc:d];m=z
    return clean(m)
def skel(m):
    u=cv2.resize(m,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    u=cv2.GaussianBlur(u,(0,0),2)>110
    sk=prune(skeletonize(u),10);ys,xs=np.where(sk);return np.stack([xs,ys],1)/2.0, u
def A_of(p):  # params -> 2x3
    s,asp,rot,sh,tx,ty=p
    R=np.array([[np.cos(rot),-np.sin(rot)],[np.sin(rot),np.cos(rot)]])
    S=np.array([[s*asp,s*sh],[0,s/asp]]);M=R@S;return np.c_[M,[tx,ty]]
def ap(A,P):return P@A[:,:2].T+A[:,2]
def register(ch,e):
    med=mmh(ch)
    if med is None:return None
    m=her_mask(ch,e)
    if m.sum()<200:return None
    sk,_=skel(m)
    if len(sk)<30:return None
    T=cKDTree(sk)
    dt=ndi.distance_transform_edt(~(np.pad(np.zeros((340,340),bool),0)|False)) if False else None
    S=np.vstack([resample(x,max(4,int(np.hypot(*np.diff(x,axis=0).T).sum()/12))) for x in med])
    # init by bbox
    x0,y0=sk.min(0);x1,y1=sk.max(0);X0,Y0=S.min(0);X1,Y1=S.max(0)
    s=((x1-x0)+(y1-y0))/((X1-X0)+(Y1-Y0)+1e-6)
    p0=[s,1,0,0,(x0+x1)/2-s*(X0+X1)/2,(y0+y1)/2-s*(Y0+Y1)/2]
    skT=cKDTree(sk)
    def cost(p):
        A=A_of(p);Q=ap(A,S)
        d1,_=skT.query(Q);d2,_=cKDTree(Q).query(sk)
        return np.mean(np.minimum(d1,12)**2)+np.mean(np.minimum(d2,12)**2)
    best=None
    for rot in (-.12,0,.12):
        p=list(p0);p[2]=rot
        r=minimize(cost,p,method='Powell',options=dict(maxiter=3000,xtol=1e-3,ftol=1e-4))
        if best is None or r.fun<best.fun:best=r
    A=A_of(best.x)
    # per-stroke: refine translation+scale, then snap samples to nearest skeleton points
    strokes=[];ok=[]
    for x in med:
        L=np.hypot(*np.diff(x,axis=0).T).sum();n=max(8,min(40,int(L/14)))
        P=ap(A,resample(x,n))
        def c2(q):
            Q=(P-P.mean(0))*q[2]+P.mean(0)+q[:2];d,_=skT.query(Q);return np.mean(np.minimum(d,10)**2)
        q=minimize(c2,[0,0,1],method='Powell',options=dict(xtol=1e-2)).x
        if not(.6<q[2]<1.6):q=np.array([0,0,1.])
        Q=(P-P.mean(0))*q[2]+P.mean(0)+q[:2]
        d,i=skT.query(Q);H=sk[i]
        good=d<7
        D=np.where(good[:,None],H-Q,np.nan)
        # fill gaps / smooth displacement along stroke
        for k in range(2):
            idx=np.arange(n);g=~np.isnan(D[:,0])
            if g.sum()<2:D[:]=0;break
            D=np.stack([np.interp(idx,idx[g],D[g,j]) for j in range(2)],1)
        D=ndi.gaussian_filter1d(D,1.2,axis=0)
        strokes.append(Q+D);ok.append(float(good.mean()))
    # back to MMH frame
    Ai=np.linalg.inv(np.vstack([A,[0,0,1]]))[:2]
    her=[ap(Ai,h) for h in strokes]
    cov=float(np.mean(cKDTree(np.vstack(strokes)).query(sk)[0]<5))
    return dict(ch=ch,e=e,A=A,params=best.x.tolist(),med=med,her=her,ok=ok,cov=cov,fit=float(best.fun))
def job(a):
    try:return register(*a)
    except Exception as ex:return None
if __name__=='__main__':
    db=pickle.load(open('/tmp/yiyi/db.pkl','rb'))
    J=[]
    for ch,v in db.items():
        if not('一'<=ch<='鿿'):continue
        ban=set(tuple(b) for b in OV.get('ban',{}).get(ch,[]))
        vv=[e for e in v if (e['pg'],e['r'],e['k']) not in ban][:3]
        pk=OV.get('pick',{}).get(ch)
        if pk:vv=[e for e in v if (e['pg'],e['r'],e['k'])==tuple(pk)]+[e for e in vv if (e['pg'],e['r'],e['k'])!=tuple(pk)][:2]
        for e in vv:
            if e['q']>=v[0]['q']*.75 or (pk and (e['pg'],e['r'],e['k'])==tuple(pk)):J.append((ch,e))
    if len(sys.argv)>1:J=[j for j in J if j[0] in sys.argv[1]]
    with Pool(8) as p:R=[r for r in p.map(job,J,chunksize=4) if r]
    pickle.dump(R,open('/tmp/yiyi/lib.pkl','wb'))
    ok=np.array([np.mean(r['ok']) for r in R]);cov=np.array([r['cov'] for r in R])
    print(len(J),len(R),'stroke-ok median',np.median(ok),'cov median',np.median(cov),'bad',(ok<.7).sum())
