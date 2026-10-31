import numpy as np,cv2,math,os,json
OUT='/tmp/yiyi/emoji'
INK='#141416';BLUE='#1f55b8'
SS=4;N=512
def cr(P,n=10,closed=False):
    P=np.array(P,float)
    if len(P)<3:return P
    Q=np.vstack([P[-1],P,P[0],P[1]]) if closed else np.vstack([P[0]*2-P[1],P,P[-1]*2-P[-2]])
    o=[]
    for i in range(1,len(Q)-2):
        a,b,c,d=Q[i-1:i+3]
        for t in np.linspace(0,1,n,endpoint=False):
            o.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    if not closed:o.append(Q[-2])
    return np.array(o)
class E:
    def __init__(s,name,seed,tilt=0):
        s.name=name;s.r=np.random.default_rng(seed);s.it=[];s.tilt=tilt
    def wob(s,P,amp=.55):
        P=np.array(P,float);n=len(P)
        if n<4:return P
        d=np.cumsum(np.r_[0,np.hypot(*np.diff(P,axis=0).T)])
        ph=s.r.uniform(0,6.3,4);f=s.r.uniform(.05,.12,2)
        P=P.copy()
        P[:,0]+=amp*(np.sin(d*f[0]+ph[0])+.5*np.sin(d*f[1]*2.3+ph[1]))
        P[:,1]+=amp*(np.sin(d*f[1]+ph[2])+.5*np.sin(d*f[0]*2.1+ph[3]))
        return P
    def L(s,P,w=1.25,closed=False,smooth=True,color=INK,over=True,amp=.55):
        """hand line; closed shapes are left slightly unjoined/overshooting like hers"""
        P=np.array(P,float)
        if smooth:
            C=cr(P,10,closed)
        else:
            C=[]
            Q=np.vstack([P,P[0]]) if closed else P
            for a,b in zip(Q,Q[1:]):
                n=max(3,int(np.hypot(*(b-a))/1.2));C+= [a+(b-a)*t for t in np.linspace(0,1,n,endpoint=False)]
            C.append(Q[-1]);C=np.array(C)
        if closed and smooth:
            C=np.vstack([C,C[:int(s.r.integers(1,5))]])
        C=s.wob(C,amp)
        if over and not closed and len(C)>3:
            v=(C[-1]-C[-2]);C=np.vstack([C,C[-1]+v*s.r.uniform(.4,1.2)])
        s.it.append(('l',C,w,color))
    def F(s,P,color,smooth=True):
        C=cr(P,8,True) if smooth else np.array(P,float)
        s.it.append(('f',s.wob(C,.35),color))
    def D(s,x,y,r,color=INK,rx=None):
        a=np.linspace(0,6.283,26,endpoint=False);rr=r*(1+.045*np.sin(a*3+s.r.uniform(0,6))+.02*np.sin(a*5))
        s.it.append(('f',np.stack([x+(rx or r)/r*rr*np.cos(a),y+rr*np.sin(a)],1),color))
    def O(s,x,y,r,ry=None,**k):
        a=np.linspace(0,6.283,14,endpoint=False);s.L(np.stack([x+r*np.cos(a),y+(ry or r)*np.sin(a)],1),closed=True,**k)
    def dots(s,pts,r=1.1):
        for x,y in pts:s.D(x,y,r*s.r.uniform(.7,1.25))
    def tf(s,P):
        P=np.array(P,float);t=math.radians(s.tilt);c,sn=math.cos(t),math.sin(t);p=(P-50)*.84
        return np.stack([p[:,0]*c-p[:,1]*sn,p[:,0]*sn+p[:,1]*c],1)+50
    def raster(s):
        S=N*SS/100;W=N*SS
        ink=np.zeros((W,W),np.uint8)
        col=np.zeros((W,W,3),np.uint8);col[:]=255
        def hexc(c):return tuple(int(c[i:i+2],16) for i in (5,3,1))
        for it in s.it:
            if it[0]=='f':
                p=(s.tf(it[1])*S).astype(np.int32);cv2.fillPoly(col,[p],hexc(it[2]),cv2.LINE_AA);cv2.fillPoly(ink,[p],255)
            else:
                C=s.tf(it[1])*S;w=it[2]*S
                n=len(C)
                for k in range(n-1):
                    f=k/max(n-1,1);pr=.82+.28*np.sin(f*9+n)   # pen pressure
                    t=max(1,int(w*pr))
                    cv2.line(col,tuple(C[k].astype(int)),tuple(C[k+1].astype(int)),hexc(it[3]),t,cv2.LINE_AA)
                    cv2.line(ink,tuple(C[k].astype(int)),tuple(C[k+1].astype(int)),255,t,cv2.LINE_AA)
        # scissor-cut paper: dilate, simplify to straight snips
        k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(8.5*S),int(8.5*S)))
        d=cv2.dilate(cv2.morphologyEx(ink,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(22*S),int(22*S)))),k)
        cs,_=cv2.findContours((d>127).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=cv2.contourArea)
        ap=cv2.approxPolyDP(c,1.5*S,True)
        paper=np.zeros((W,W),np.uint8);cv2.fillPoly(paper,[ap],255,cv2.LINE_AA)
        # slight lift shadow
        sh=cv2.GaussianBlur(cv2.warpAffine(paper,np.float32([[1,0,.5*S],[0,1,.8*S]]),(W,W)),(0,0),1.1*S)*.22
        rgb=col.astype(np.float32)
        paper_c=np.array([240,244,246],np.float32)
        white=(col.min(2)>=250)
        rgb[white]=paper_c
        # paper grain
        g=cv2.GaussianBlur(s.r.normal(0,1,(W//2,W//2)).astype(np.float32),(0,0),1.2);g=cv2.resize(g,(W,W))
        rgb+=(g*6)[...,None]*white[...,None]
        rgba=np.dstack([np.zeros((W,W,3),np.float32),sh.astype(np.float32)])
        a=(paper/255.)[...,None]
        out=np.dstack([rgb*a[...,0][...,None]*1,0*a])
        A=a[...,0]+(1-a[...,0])*sh/255.
        RGB=(rgb*a)/np.maximum(A[...,None],1e-3)
        res=np.dstack([np.clip(RGB,0,255),A*255])
        res=cv2.resize(res,(N,N),interpolation=cv2.INTER_AREA).astype(np.uint8)
        cv2.imwrite(f'{OUT}/{s.name}.png',res)
        s.ap=(ap[:,0]/S)
        s.svg()
    def svg(s):
        t=f'translate(50 50) rotate({s.tilt}) scale(.84) translate(-50 -50)'
        o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512">',
           f'<polygon fill="#f6f4f0" stroke="#d9d9d9" stroke-width=".25" points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in s.ap)}"/>',f'<g transform="{t}" stroke-linecap="round" stroke-linejoin="round">']
        for it in s.it:
            if it[0]=='f':o.append(f'<polygon fill="{it[2]}" points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in it[1])}"/>')
            else:o.append(f'<polyline fill="none" stroke="{it[3]}" stroke-width="{it[2]:.2f}" points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in it[1])}"/>')
        o.append('</g></svg>');open(f'{OUT}/{s.name}.svg','w').write('\n'.join(o))
# ---------------- food (hers + new in her manner)
def pizza():
    e=E('pizza',1,-9);B=[(14,28),(86,24),(89,72),(12,76)]
    e.L(B,1.5,True,False);e.L([(18,32),(83,28),(85,68),(16,71)],1,True,False)
    c=(50,50)
    for p in [(18,32),(50,29),(83,28),(85,50),(85,68),(50,70),(16,71),(17,52)]:e.L([c,p],1.1,smooth=False)
    e.O(38,38,6,3.4);e.O(30,37,3.4,2);e.O(62,37,3,4);e.O(58,41,1.6);e.D(72,40,2.4);e.L([(70,35),(76,38),(72,43)],.8)
    e.L([(24,44),(26,38),(28,44),(30,38),(33,45)],.9);e.O(28,58,3.2);e.D(29,58,1.2);e.O(41,62,3)
    e.L([(55,60),(60,58),(64,63)],.8);e.L([(57,65),(62,63)],.8);e.D(68,61,2);e.dots([(72,55),(76,57),(74,62),(71,50),(78,51)],.9);return e
def boba():
    e=E('boba',2,8);e.L([(28,24),(32,84),(70,84),(74,24)],1.5,smooth=False)
    e.O(51,23,25,4.4,w=1.3);e.L([(53,22),(60,6),(70,4)],1.3,smooth=False);e.L([(56,22),(63,7)],1.1,smooth=False);e.O(53,23,3.2,1.8,w=.9)
    pts=[(36+7*(k%5)+(3 if (k//5)%2 else 0)+e.r.uniform(-1,1),60+5.5*(k//5)+e.r.uniform(-1.2,1.2)) for k in range(20)];e.dots(pts,1.7);return e
def cone():
    e=E('icecream',3,16);e.L([(26,44),(50,92),(74,44)],1.5,smooth=False)
    for a,b in [((34,47),(52,84)),((44,44),(60,72)),((56,44),(46,80)),((68,46),(40,70))]:e.L([a,b],1.1,smooth=False)
    e.L([(22,44),(20,34),(30,28),(32,16),(46,18),(52,8),(62,16),(72,20),(74,30),(82,36),(78,46),(26,46)],1.5,True);e.L([(36,30),(40,38)],1);e.L([(56,26),(60,34)],1);e.L([(68,34),(66,40)],1);return e
def donut():
    e=E('donut',4,-7);e.O(50,50,36,33,w=1.5);e.O(50,48,11,9,w=1.3)
    e.L([(20,44),(26,60),(34,58),(42,68),(52,64),(62,72),(72,62),(80,56),(82,40)],1.1)
    for x,y,a in [(30,34,.5),(42,28,-.6),(60,30,.4),(72,38,-.5),(28,48,1),(70,50,.3),(56,60,-.7),(38,58,.8)]:
        e.L([(x,y),(x+3*math.cos(a),y+3*math.sin(a))],1.3,smooth=False,color=BLUE,over=False)
    return e
def burger():
    e=E('burger',5,6);e.L([(14,42),(18,22),(50,12),(82,22),(86,42)],1.5,smooth=True);e.L([(14,42),(86,42)],1.4,smooth=False)
    e.L([(10,50),(20,46),(30,52),(40,46),(50,52),(60,46),(70,52),(80,46),(90,50)],1.2);e.L([(16,56),(84,56),(82,64),(18,64)],1.4,True,False)
    e.L([(16,70),(84,70),(80,84),(50,88),(20,84)],1.5,True);e.dots([(34,26),(46,20),(58,28),(68,24),(42,32),(54,18)],.9)
    for x in range(22,80,10):e.L([(x,59),(x+4,61)],.8,smooth=False,over=False)
    return e
def melon():
    e=E('watermelon',6,-14);e.L([(10,36),(50,84),(90,36)],1.5,smooth=False);e.L([(10,36),(90,36)],1.5,smooth=False);e.L([(18,42),(82,42)],1,smooth=False)
    e.dots([(32,50),(48,48),(64,50),(40,60),(56,60),(49,70)],1.8);e.L([(84,41),(92,30),(92,40)],.9);return e
def berry():
    e=E('strawberry',7,10);e.L([(50,92),(22,60),(20,36),(36,28),(50,32),(66,28),(80,36),(78,60)],1.5,True)
    e.L([(30,28),(42,26),(36,16),(48,22),(52,10),(56,22),(68,16),(60,26),(72,28),(60,34),(50,30),(40,34)],1.2,True,False)
    r=e.r
    for x,y in [(34,44),(48,42),(62,44),(40,56),(56,56),(30,54),(68,54),(48,68),(38,68),(60,68),(49,80)]:
        e.L([(x,y),(x+.8,y+2.4)],1.2,smooth=False,over=False)
    return e
def cake():
    e=E('cake',8,-6);e.L([(16,48),(84,44),(86,84),(14,86)],1.5,True,False);e.L([(16,48),(22,60),(30,50),(38,62),(46,50),(56,62),(64,48),(74,60),(84,46)],1.2)
    e.L([(15,72),(85,70)],1,smooth=False);e.dots([(26,78),(40,78),(52,77),(66,77),(76,76)],1)
    for x in (34,50,66):
        e.L([(x,47),(x-1,28),(x+3,28),(x+3,46)],1.2,smooth=False);e.L([(x+1,26),(x-2,20),(x+1,14),(x+4,20),(x+1,26)],1,color=BLUE)
    return e
# ---------------- her googly character
def head(e,lash=True):
    e.L([(24,50),(26,28),(40,14),(60,14),(74,28),(76,50),(72,72),(58,86),(42,86),(28,72)],1.4,True)
    if lash:
        for a,b in [((38,13),(36,6)),((46,11),(45,4)),((54,11),(55,4)),((62,13),(64,6))]:e.L([a,b],.9,smooth=False,over=False)
def eyes(e,lx=(38.5,44),rx=(61.5,44),r=11,pl=(-4,3),pr=(4,3),pup=6.2):
    e.O(*lx,r);e.O(*rx,r);e.D(lx[0]+pl[0],lx[1]+pl[1],pup);e.D(rx[0]+pr[0],rx[1]+pr[1],pup)
def beak(e,y=61,c=BLUE):
    e.F([(44,y),(50,y-3),(56,y),(54,y+5),(50,y+7),(46,y+5)],c)
def smile():
    e=E('face_smile',11,-5);head(e);eyes(e);e.L([(40,66),(50,74),(60,66)],1.3);return e
def love():
    e=E('face_love',12,6);head(e)
    for x in (37,63):
        e.F([(x,54),(x-9.5,43),(x-8,34),(x-3,34),(x,38),(x+3,34),(x+8,34),(x+9.5,43)],BLUE);e.L([(x,54),(x-9.5,43),(x-8,34),(x-3,34),(x,38),(x+3,34),(x+8,34),(x+9.5,43)],1.2,True)
    e.L([(42,68),(50,74),(58,68)],1.3);return e
def cry():
    e=E('face_cry',13,-4);head(e,False);eyes(e,pl=(0,6),pr=(0,6),pup=6.5);e.L([(42,74),(50,68),(58,74)],1.3)
    for x in (32,68):e.F([(x,58),(x-4,70),(x,76),(x+4,70)],BLUE)
    e.F([(x+6,76),(x+3,84),(x+6,88),(x+9,84)],BLUE);return e
def angry():
    e=E('face_angry',14,5);head(e,False);eyes(e,pl=(3,2),pr=(-3,2),pup=6.5);e.L([(22,26),(46,36)],2.2,smooth=False);e.L([(78,26),(54,36)],2.2,smooth=False);e.L([(40,72),(46,68),(50,72),(54,68),(60,72)],1.3,smooth=False);
    e.L([(80,14),(88,10),(84,18),(92,18)],1.1,smooth=False,color=BLUE);return e
def sleep():
    e=E('face_sleepy',15,-8);head(e,False);e.L([(24,46),(36,52),(48,46)],1.5);e.L([(52,46),(64,52),(76,46)],1.5);e.O(50,70,3.5,4.5)
    e.L([(78,20),(88,20),(78,30),(88,30)],1.2,smooth=False,color=BLUE);e.L([(66,6),(73,6),(66,13),(73,13)],1,smooth=False,color=BLUE);return e
def shock():
    e=E('face_shock',16,3);head(e);eyes(e,r=11.5,pl=(0,0),pr=(0,0),pup=3.2);e.O(50,72,6,7,w=1.4);e.L([(12,24),(14,34)],1.1,color=BLUE);e.L([(8,30),(10,38)],1.1,color=BLUE);return e
def wink():
    e=E('face_wink',17,-6);head(e);e.O(38.5,44,11);e.D(34.5,47,6.2);e.L([(52,46),(62,40),(74,46)],1.5);e.L([(40,66),(50,74),(60,66)],1.3);e.L([(50,70),(54,80),(60,74)],1.2,color=BLUE);return e
def yum():
    e=E('face_yum',18,4);head(e);eyes(e,pl=(4,-4),pr=(-4,-4));e.L([(38,66),(50,72),(62,66)],1.3);e.F([(46,70),(54,70),(55,78),(50,80),(45,78)],BLUE);return e
def braid():
    e=E('face_braid',19,-10);head(e,False);eyes(e)
    e.L([(38,20),(30,28),(26,44)],1.1);beak(e,62)
    for sx,dx in ((24,-1),(76,1)):
        for k in range(5):
            x=sx+dx*(4+k*3.2);y=62+k*5
            e.L([(x-2.4,y-1),(x+2.4,y+1.6)],1,smooth=False);e.L([(x+2.4,y-1),(x-2.4,y+1.6)],1,smooth=False)
    return e
def peanut():
    e=E('buddy',20,-4)
    e.L([(30,28),(36,12),(62,12),(70,28),(62,42),(76,58),(76,82),(60,94),(40,94),(24,82),(24,58),(38,42)],1.4,True)
    e.O(42,27,9.6);e.O(60,27,9.6);e.D(39,29,5.6);e.D(63,29,5.6);beak(e,38)
    e.L([(38,60),(44,70),(36,70),(38,60)],1.2,smooth=False);e.L([(62,60),(56,70),(64,70),(62,60)],1.2,smooth=False);return e
# ---------------- objects
def heart():
    e=E('heart',21,-10);P=[(50,84),(16,48),(16,30),(32,20),(50,34),(68,20),(84,30),(84,48)];e.F(P,BLUE);e.L(P,1.5,True);e.L([(26,32),(32,28)],1.3,color='#ffffff');return e
def star():
    e=E('star',22,12);P=[]
    for k in range(10):
        a=-1.57+k*.628;r=40 if k%2==0 else 17;P.append((50+r*math.cos(a),52+r*math.sin(a)))
    e.L(P,1.5,True,False);e.dots([(46,50),(54,52),(50,44),(50,60)],1);return e
def pencil():
    e=E('pencil',23,38);e.L([(40,14),(60,14),(60,70),(50,92),(40,70)],1.5,True,False);e.L([(40,70),(44,66),(48,71),(52,66),(56,71),(60,70)],1.1,smooth=False);e.F([(47,84),(53,84),(50,92)],INK,False);e.L([(40,24),(60,24)],1.2,smooth=False);e.L([(47,28),(47,64)],.9,smooth=False);e.F([(40,14),(60,14),(60,24),(40,24)],BLUE,False);return e
def book():
    e=E('book',24,-8);e.L([(10,26),(30,22),(50,30),(70,22),(90,26),(90,76),(70,72),(50,80),(30,72),(10,76)],1.5,True,False);e.L([(50,30),(50,80)],1.2,smooth=False)
    for y in (36,44,52,60):e.L([(18,y),(42,y+3)],1,smooth=False);e.L([(58,y+3),(82,y)],1,smooth=False)
    return e
def sun():
    e=E('sun',25,9);e.O(50,50,20,w=1.5);e.D(43,48,2.4);e.D(57,48,2.4);e.L([(44,56),(50,60),(56,56)],1.2)
    for k in range(10):
        a=k*.628;e.L([(50+27*math.cos(a),50+27*math.sin(a)),(50+39*math.cos(a+.08),50+39*math.sin(a+.08))],1.4,smooth=False)
    return e
def rain():
    e=E('rain',26,-6);e.L([(20,50),(14,40),(22,30),(30,30),(36,18),(54,16),(64,26),(78,26),(86,38),(80,50)],1.5,True)
    for x,y in [(30,62),(46,68),(62,62),(38,78),(56,82),(72,76)]:e.F([(x,y),(x-3,y+7),(x,y+10),(x+3,y+7)],BLUE)
    return e
ALL=[pizza,boba,cone,donut,burger,melon,berry,cake,smile,love,cry,angry,sleep,shock,wink,yum,braid,peanut,heart,star,pencil,book,sun,rain]
if __name__=='__main__':
    for f in ALL:f().raster()
    import glob
    from PIL import Image
    fs=[f"{OUT}/{f().name}.png" for f in ALL];c=6;S=Image.new('RGB',(c*256,4*256),'#e9dcc4')
    for i,p in enumerate(fs):
        t=Image.open(p).resize((256,256));S.paste(t,((i%c)*256,(i//c)*256),t)
    S.save('/tmp/yiyi/emoji_sheet.png');print(len(fs))
