import numpy as np,math,sys,cv2,json
def rot(a,axis):
    c,s=math.cos(a),math.sin(a)
    return {'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[axis]
def sph(p,c,r): return np.linalg.norm(p-np.array(c),axis=-1)-r
def ell(p,c,r,R=None):
    q=p-np.array(c)
    if R is not None:q=q@R
    r=np.array(r);k0=np.linalg.norm(q/r,axis=-1);k1=np.linalg.norm(q/(r*r),axis=-1)
    return k0*(k0-1)/(k1+1e-9)
def cap(p,a,b,r):
    a=np.array(a);b=np.array(b);pa=p-a;ba=b-a
    h=np.clip((pa*ba).sum(-1)/(ba*ba).sum(),0,1)
    return np.linalg.norm(pa-ba[None,:]*h[...,None] if pa.ndim==2 else pa-ba*h[...,None],axis=-1)-r
def smin(a,b,k):
    h=np.clip(.5+.5*(b-a)/k,0,1);return b*(1-h)+a*h-k*h*(1-h)
class Scene:
    """list of (fn(p)->d, color, id). union with small smooth blend inside a group."""
    def __init__(s):s.o=[];s.col=[]
    def add(s,fn,c,blend=0):
        s.o.append((fn,blend));s.col.append(np.array(c,float)/255);return s
    def dist(s,p):
        ds=[f(p) for f,_ in s.o];D=np.stack(ds)
        return D
    def map(s,p):
        D=s.dist(p);return D.min(0)
from scipy.ndimage import map_coordinates,gaussian_filter
_V=gaussian_filter(np.random.default_rng(7).normal(0,1,(48,48,48)).astype(np.float32),1,mode='wrap');_V/=_V.std()
def n3(p,freq,seed=0):
    q=(p*freq+seed*7.3).T%48
    return map_coordinates(_V,q,order=1,mode='wrap')
def render(sc,W=640,ss=1,cam=(0,.15,4.6),fov=1.0,look=(0,.0,0),bump=1,seed=1):
    W2=W*ss
    ro=np.array(cam,float);f=np.array(look,float)-ro;f/=np.linalg.norm(f)
    r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f)
    yy,xx=np.mgrid[0:W2,0:W2].astype(np.float32);xx=(xx+.5)/W2*2-1;yy=1-(yy+.5)/W2*2
    rd=(xx[...,None]*r+yy[...,None]*u+(1/fov*1.0*2.2)*f);rd/=np.linalg.norm(rd,axis=-1,keepdims=True);rd=rd.reshape(-1,3)
    t=np.full(len(rd),2.0);hit=np.zeros(len(rd),bool);act=np.ones(len(rd),bool)
    for _ in range(70):
        idx=np.where(act)[0]
        if len(idx)==0:break
        p=ro+rd[idx]*t[idx,None];d=sc.map(p)
        t[idx]+=d*.9
        h=d<.0015;hit[idx[h]]=True;act[idx[h]]=False;act[idx[t[idx]>9]]=False
    I=np.where(hit)[0];P=ro+rd[I]*t[I,None]
    D=sc.dist(P);mid=D.argmin(0)
    col=np.stack(sc.col)[mid]
    e=.003
    def field(q):
        return sc.map(q)-bump*(.0009*n3(q,120,seed)+.0014*n3(q,55,seed+3)+.004*n3(q,6,seed+1))
    N=np.stack([field(P+np.array(v)*e)-field(P-np.array(v)*e) for v in np.eye(3)],1);N/=np.linalg.norm(N,axis=1,keepdims=True)+1e-9
    L=np.array([-.55,.75,.6]);L/=np.linalg.norm(L);L2=np.array([.7,.25,.5]);L2/=np.linalg.norm(L2)
    # soft shadow
    sh=np.ones(len(P));tt=np.full(len(P),.03)
    for _ in range(18):
        d=sc.map(P+N*.01+L*tt[...,None]);sh=np.minimum(sh,np.clip(10*d/tt,0,1));tt+=np.clip(d,.02,.25)
    ao=np.zeros(len(P))
    for k in range(1,6):
        h=.03*k;ao+=(h-sc.map(P+N*h))/(2.0**k)
    ao=np.clip(1-3.2*ao,0,1)
    V=-rd[I]
    wrap=np.clip((N@L+.35)/1.35,0,1)
    fres=np.clip(1-(N*V).sum(1),0,1)
    light=.34+.56*wrap*(.5+.5*sh)+.1*np.clip(N@L2,0,1)+.1*np.clip(N[:,1]*.5+.5,0,1)
    light*=(.55+.45*ao)
    # fuzz sheen of light clay, slight saturation in shade
    grain=1+.022*np.random.default_rng(seed).normal(0,1,len(P))
    C=col*light[...,None]*grain[...,None]+ (fres**3)[...,None]*.20*(col*.6+.4)
    C=np.clip(C,0,1)**(1/1.12)
    img=np.zeros((W2*W2,4),np.float32);img[I,:3]=C;img[I,3]=1
    img=img.reshape(W2,W2,4)
    if ss>1:img=cv2.resize(img,(W,W),interpolation=cv2.INTER_AREA)
    return img
