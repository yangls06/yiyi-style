import numpy as np,math,sys
sys.path[:0]=['/tmp/yiyi/scripts']
from clay import *
BLACK=(26,24,26);PINK=(235,88,132);HOT=(214,52,120);BUB=(236,112,180);LPK=(240,140,190)
YEL=(248,196,50);ORG=(246,176,52);WHT=(238,226,222);GRN=(140,168,62);OLV=(176,176,52);CRN=(222,194,44);BLU=(112,176,226);BRN=(120,76,56);PYEL=(250,206,28);BLUSH=(240,170,165);TEAR=(120,190,240)
class Xf:
    """global pose: rotate/squash everything except accessories placed in world"""
    def __init__(s,rz=0,ry=0,rx=0,sy=1,dy=0,dx=0):
        s.R=rot(rz,'z')@rot(ry,'y')@rot(rx,'x');s.sy=sy;s.dy=dy;s.dx=dx
    def __call__(s,p):
        q=(p-np.array([s.dx,s.dy-1,0]))@s.R
        q=q*np.array([s.sy**.5,1/s.sy,s.sy**.5])
        return q+np.array([0,-1,0])
def surf(c,R,az,el):
    return (c[0]+R*math.cos(el)*math.sin(az),c[1]+R*math.sin(el),c[2]+R*math.cos(el)*math.cos(az))
def arc(sc,x,c,R,az0,el0,w,h,r,color,n=7,up=True):
    pts=[]
    for k in range(n):
        f=k/(n-1)*2-1
        pts.append(surf(c,R,az0+f*w,el0+(1-f*f)*h*(1 if up else -1)))
    for a,b in zip(pts,pts[1:]):
        sc.add(lambda p,a=a,b=b:cap(x(p),a,b,r),color)
def eyes(sc,x,c,R,ex,az=.42,el=.2,size=.075,color=BLACK,tall=1.35):
    E=lambda s,z=1:(surf(c,R-.0,az*s,el))
    for s in (-1,1):
        kind=ex if not(ex=='wink' and s==1) else 'happy'
        if ex=='wink' and s==-1: kind='dot'
        if kind=='dot':
            sc.add(lambda p,s=s:ell(x(p),E(s),(size,size*tall,size*.5)),color)
        elif kind=='big':
            sc.add(lambda p,s=s:ell(x(p),E(s),(size*1.5,size*1.8,size*.6)),color)
            sc.add(lambda p,s=s:sph(x(p),surf(c,R+.05,az*s-.03,el+.05),size*.42),(250,250,250))
        elif kind=='happy': arc(sc,x,c,R+.005,az*s,el-.03,.13,.1,size*.42,color)
        elif kind=='sad': arc(sc,x,c,R+.005,az*s,el+.03,.12,.08,size*.42,color,up=False)
        elif kind=='closed': arc(sc,x,c,R+.005,az*s,el+.02,.14,.05,size*.42,color,up=False)
        elif kind=='angry':
            sc.add(lambda p,s=s:ell(x(p),E(s),(size,size*1.1,size*.5)),color)
            a=surf(c,R+.01,az*s-.17*s*-1,el+.26);b=surf(c,R+.01,az*s-.2*s,el+.15)
            a,b=surf(c,R+.01,az*s+.18*s,el+.3),surf(c,R+.01,az*s-.16*s,el+.17)
            sc.add(lambda p,a=a,b=b:cap(x(p),a,b,size*.42),color)
        elif kind=='x':
            for d in (1,-1):
                a=surf(c,R+.005,az*s-.09,el+.1*d);b=surf(c,R+.005,az*s+.09,el-.1*d)
                sc.add(lambda p,a=a,b=b:cap(x(p),a,b,size*.38),color)
def heart(sc,c,s,color=PINK):
    a=(c[0]-.1*s,c[1]+.08*s,c[2]);b=(c[0]+.1*s,c[1]+.08*s,c[2]);t=(c[0],c[1]-.2*s,c[2])
    sc.add(lambda p:smin(smin(sph(p,a,.13*s),sph(p,b,.13*s),.02),cap(p,(c[0],c[1]+.02*s,c[2]),t,.045*s),.14*s),color)
def tear(sc,c,s=1):
    sc.add(lambda p:smin(sph(p,(c[0],c[1]-.03*s,c[2]),.09*s),cap(p,(c[0],c[1]-.03*s,c[2]),(c[0],c[1]+.13*s,c[2]),.012*s),.07*s),TEAR)
def wing(sc,x,side,up,color,edge):
    # stub wing with scored lines, hinged at body side
    a=-side*up
    R=rot(a,'z');pv=np.array([side*1.0,.05,0])
    def tf(p):return (x(p)-pv)@R
    c=(side*.12,-.08,.0)
    sc.add(lambda p:ell(tf(p),c,(.34,.46,.27)),color)
    for dy in (-.17,.1):
        a_=(side*-.02,-.08+dy,.27);b_=(side*.36,-.1+dy+.05,.2)
        sc.add(lambda p,a_=a_,b_=b_:cap(tf(p),a_,b_,.02),edge)
def chick(ex='dot',up=0,**pose):
    sc=Scene();x=Xf(**pose);C=(0,0,0)
    sc.add(lambda p:ell(x(p),C,(1,.96,1)),YEL)
    sc.add(lambda p:smin(ell(x(p),(0,.08,.92),(.33,.31,.38)),sph(x(p),(0,.05,1.2),.1),.2),PINK)
    wing(sc,x,-1,up,ORG,(205,135,30));wing(sc,x,1,up,ORG,(205,135,30))
    sc.add(lambda p:smin(smin(ell(x(p),(-.17,1.1,0),(.15,.27,.17)),ell(x(p),(.17,1.1,0),(.15,.27,.17)),.08),ell(x(p),(0,1.15,.02),(.15,.3,.17)),.06),PINK)
    for s in (-1,1):
        sc.add(lambda p,s=s:ell(x(p),(s*.42,-.88,.42),(.27,.15,.3)),PINK)
    eyes(sc,x,C,.985,ex,az=.52,el=.42,size=.066,tall=.95)
    return sc,x
def bunny(ex='dot',up=0,**pose):
    sc=Scene();x=Xf(**pose);C=(0,0,0)
    sc.add(lambda p:ell(x(p),C,(1,.98,1)),BUB)
    for s in (-1,1):
        R=rot(s*-.5,'z')@rot(-.5,'x')
        sc.add(lambda p,s=s,R=R:ell(x(p),(s*.42,1.0,-.28),(.5,.27,.42),R),LPK)
        sc.add(lambda p,s=s,R=R:ell(x(p),(s*.44,1.06,-.2),(.34,.2,.3),R),(232,84,150))
        sc.add(lambda p,s=s:ell(x(p),(s*.3,.78,.55),(.27,.2,.13),rot(s*-.25,'z')),HOT)
        wr=rot(-s*(.3+up),'z')
        sc.add(lambda p,s=s,wr=wr:ell(x(p),(s*.6,-.02+up*.25,.74),(.15,.24,.1),wr),HOT)
        sc.add(lambda p,s=s:ell(x(p),(s*.5,-.92,.34),(.3,.16,.32)),LPK)
    sc.add(lambda p:sph(x(p),(0,.8,.62),.12),(204,44,110))
    eyes(sc,x,C,.985,ex,az=.33,el=.3,size=.07,tall=1.1)
    return sc,x
def ghost(ex='dot',up=0,**pose):
    sc=Scene();x=Xf(**pose);c=(0,-.15,0)
    lobes=[(.92*math.cos(k*.785+.3),-.9,.92*math.sin(k*.785+.3)) for k in range(8)]
    def body(p):
        q=x(p);yy=q[...,1]
        w=.72+.24*np.clip((.2-yy)/1.2,0,1)**1.2       # bell flare
        r=np.hypot(q[...,0],q[...,2])
        d=np.maximum(r-w,np.maximum(-1-yy+.0,yy-.4))*.75-.02
        d=smin(d,ell(q,(0,.3,0),(.72,.4,.72)),.2)
        for l in lobes:d=smin(d,ell(q,l,(.2,.13,.2)),.22)
        return d
    sc.add(body,WHT)
    brim=rot(.14,'z')@rot(.08,'x')
    def bfn(p):
        q=x(p);r=np.hypot(q[...,0],q[...,2]);a=np.arctan2(q[...,2],q[...,0])
        q2=q.copy();q2[...,1]=q2[...,1]+.03*np.sin(a*3)
        return ell(q2,(0,.62,0),(1.25,.17,1.16),brim)
    sc.add(bfn,GRN)
    sc.add(lambda p:ell(x(p),(-.02,.98,0),(.68,.5,.62)),CRN)
    for s in (-1,1):
        sc.add(lambda p,s=s:ell(x(p),(s*.42,.86,.48),(.38,.3,.2),rot(s*-.2,'z')),OLV)
    sc.add(lambda p:sph(x(p),(0,.84,.58),.17),(160,162,48))
    R=.8;F=(0,-.12,.0)
    eyes(sc,x,F,R,ex,az=.4,el=.28,size=.055,tall=1.6)
    for s in (-1,1):
        sc.add(lambda p,s=s:ell(x(p),surf(F,R+.03,.72*s,-.12),(.11,.07,.035)),BLUSH)
    return sc,x
def pika(ex='dot',up=0,**pose):
    sc=Scene();x=Xf(**pose);C=(0,.12,0)
    sc.add(lambda p:ell(x(p),C,(.8,.88,.8)),PYEL)
    def ear(s,tilt,ln=.72,z=0):
        R=rot(-s*tilt,'z')
        base=np.array([s*.42,.72,z])
        def yel(p):return ell((x(p)-base)@R,(0,.32,0),(.2,.4,.14))
        def tip(p):return ell((x(p)-base)@R,(0,.68,0),(.16,.2,.11))
        sc.add(tip,BRN);sc.add(yel,PYEL)
    ear(-1,.5);ear(1,.5)
    # big tail behind head
    sc.add(lambda p:ell(x(p)-np.array([.32,1.42,-.42]),(0,0,0),(.5,.24,.14),rot(.5,'z')),BRN)
    sc.add(lambda p:ell(x(p)-np.array([-.08,1.12,-.42]),(0,0,0),(.34,.2,.14),rot(.4,'z')),PYEL)
    for s in (-1,1):
        h=-.42+up*.55
        sc.add(lambda p,s=s,h=h:ell(x(p),(s*.72,h,.45),(.22,.2,.22)),PYEL)
    eyes(sc,x,C,.86,ex,az=.42,el=.22,size=.1,tall=1.1,color=(44,36,34))
    # little w mouth
    M=[surf(C,.86,a,.03+.03*abs(math.sin(a*14))) for a in (-.08,-.03,.03,.08)]
    for a,b in zip(M,M[1:]):sc.add(lambda p,a=a,b=b:cap(x(p),a,b,.014),(44,36,34))
    # float + mat are world objects
    sc.add(lambda p:ell(p,(0,-.8,0),(1.0,.4,1.0)),BLU)
    def mat(p):
        q=p-np.array([0,-1.22,0]);d=np.abs(q)-np.array([1.45,.09,1.35]);return np.linalg.norm(np.maximum(d,0),axis=-1)+np.minimum(d.max(-1),0)-.13
    sc.add(mat,BLU)
    return sc,x
def squiggle(sc,pts,r=.07,color=PYEL):
    from itertools import pairwise
    for a,b in pairwise(pts):sc.add(lambda p,a=a,b=b:cap(p,a,b,r),color)
