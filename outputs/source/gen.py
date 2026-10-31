"""Generate characters she never wrote: standard stroke medians + her per-stroke deviations."""
import sys,json,pickle,cv2,numpy as np,math
sys.path[:0]=['/tmp/yiyi/scripts']
from learn import mmh,resample,A_of,ap
from scipy.spatial import cKDTree
N=24
DIC={}
for l in open('/tmp/yiyi/ext/dictionary.txt'):
    d=json.loads(l);DIC[d['character']]=d
BIN='⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻';TRI='⿲⿳'
def parse(s,i=0):
    c=s[i]
    if c in BIN:
        a,i=parse(s,i+1);b,i=parse(s,i);return (c,[a,b]),i
    if c in TRI:
        a,i=parse(s,i+1);b,i=parse(s,i);d,i=parse(s,i);return (c,[a,b,d]),i
    return c,i+1
def node_str(n):return n if isinstance(n,str) else n[0]+''.join(node_str(k) for k in n[1])
def keys(ch):
    """per stroke: list of (key, ordinal) from deepest to shallowest component"""
    d=DIC.get(ch)
    if not d or not d.get('decomposition') or d['decomposition'][0]=='？':return None
    try:tree,_=parse(d['decomposition'])
    except Exception:return None
    M=d['matches'];out=[]
    for j,p in enumerate(M):
        ks=[]
        if p:
            for depth in range(len(p),0,-1):
                pp=p[:depth];n=tree;role=[]
                okp=True
                for q in pp:
                    if isinstance(n,str) or q>=len(n[1]):okp=False;break
                    role.append(n[0]+str(q));n=n[1][q]
                if not okp:continue
                comp=node_str(n)
                if '？' in comp:continue
                ordn=sum(1 for jj in range(j) if M[jj] and M[jj][:depth]==pp)
                ks.append(((comp,'/'.join(role[-1:])),ordn))
                ks.append(((comp,'*'),ordn))
        out.append(ks)
    return out
def feat(m):
    r=resample(m,9);d=np.diff(r,axis=0);L=np.hypot(*d.T).sum()+1e-6;u=d/np.maximum(np.hypot(*d.T)[:,None],1e-6)
    c=r.mean(0)/1024
    return np.r_[u.ravel()*1.0,math.log(L/300)*1.2,c*1.5],L
class Lib:
    def __init__(s,R,exclude=None):
        s.E=[];s.comp={}
        s.params=np.array([r['params'] for r in R])
        for r in R:
            if exclude and r['ch'] in exclude:continue
            ks=keys(r['ch'])
            for j,(m,h,ok) in enumerate(zip(r['med'],r['her'],r['ok'])):
                if ok<.72:continue
                f,L=feat(m)
                e=dict(m=resample(m,N),h=resample(h,N),L=L,ch=r['ch'],ok=ok);s.E.append((f,e))
                if ks and j<len(ks):
                    for k in ks[j]:s.comp.setdefault(k,[]).append(e)
        s.T=cKDTree(np.array([f for f,_ in s.E]))
    def donor(s,m,ks,rng):
        if ks:
            for k in ks:
                c=s.comp.get(k)
                if c:return c[rng.integers(len(c))] if len(c)>1 else c[0],'comp'
        f,_=feat(m);d,i=s.T.query(f,k=4)
        return s.E[i[rng.integers(min(2,len(i)))]][1],'shape'
def frame(P):
    t=np.gradient(P,axis=0);t/=np.maximum(np.linalg.norm(t,axis=1,keepdims=True),1e-6);n=np.stack([-t[:,1],t[:,0]],1);return t,n
def transfer(mt,e):
    mt=resample(mt,N);md,hd=e['m'],e['h']
    Ld=np.hypot(*np.diff(md,axis=0).T).sum()+1e-6;Lt=np.hypot(*np.diff(mt,axis=0).T).sum()+1e-6
    td,nd=frame(md);tt,nt=frame(mt)
    D=hd-md;du=(D*td).sum(1);dv=(D*nd).sum(1)
    k=min(Lt/Ld,1.6)
    # deviations normal to the stroke are her wobble/curvature: scale with length; along-stroke = extension/shortening
    du=np.clip(du*k,-.35*Lt,.35*Lt);dv=np.clip(dv*k,-.25*Lt-15,.25*Lt+15)
    return mt+du[:,None]*tt+dv[:,None]*nt
def generate(ch,lib,rng,stats=None):
    med=mmh(ch)
    if med is None:return None
    ks=keys(ch);out=[];src=[]
    for j,m in enumerate(med):
        if len(m)<2 or np.hypot(*(m[-1]-m[0]))<4 and len(m)<3:out.append(resample(m,N));src.append('dot');continue
        e,how=lib.donor(m,ks[j] if ks and j<len(ks) else None,rng)
        out.append(transfer(m,e));src.append(how)
    return out,src
def render_cell(strokes,lib,rng,width=4.6,scale_ref=None):
    """draw in the 340px cell frame using one of her real global layouts"""
    P=lib.params[rng.integers(len(lib.params))].copy()
    med=np.median(lib.params,0)
    p=med.copy();p[1:4]=P[1:4]*.6+med[1:4]*.4   # aspect/rotation/shear from her, damped
    allp=np.vstack(strokes);c=(allp.min(0)+allp.max(0))/2
    A=A_of(p);A[:,2]=0;A[:,2]=170-ap(A,c[None])[0]
    W=1020;U=3
    img=np.zeros((W,W),np.uint8)
    for S in strokes:
        Q=ap(A,S)*U
        if np.hypot(*(Q[-1]-Q[0]))<6*U:
            cv2.circle(img,tuple(Q.mean(0).astype(int)),int(width*U*.9),255,-1,cv2.LINE_AA);continue
        n=len(Q)
        for i in range(n-1):
            f=i/(n-1);w=width*U*(.85+.25*math.sin(math.pi*f))
            cv2.line(img,tuple(Q[i].astype(int)),tuple(Q[i+1].astype(int)),255,max(1,int(w)),cv2.LINE_AA)
            cv2.circle(img,tuple(Q[i].astype(int)),max(1,int(w/2)),255,-1,cv2.LINE_AA)
    return cv2.resize(img,(340,340),interpolation=cv2.INTER_AREA)
