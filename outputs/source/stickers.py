import sys,os,cv2,numpy as np,math,json
sys.path[:0]=['/tmp/yiyi/scripts']
from chars import *
from PIL import Image,ImageDraw,ImageFont
from multiprocessing import Pool
OUT='/tmp/yiyi/stickers';os.makedirs(OUT,exist_ok=True)
FONT='/tmp/yiyi/dist/YiyiHand-Regular.ttf'
PI=math.pi
def sk(i): return dict(sw=lambda t:math.sin(2*PI*t),)
# name, char, expr, caption, anim, extras
SP=[('01_你好','chick','happy','你好！','wave',None),
('02_发芽啦','chick','big','发芽啦！','hop',None),
('03_好吃','chick','closed','可好吃了','wiggle','hearts'),
('04_不得了','chick','x','不得了！','shake','sweat'),
('05_想你','bunny','happy','我想你','sway','hearts'),
('06_不要','bunny','angry','不要！','shake','steam'),
('07_没有了','bunny','sad','没有了','droop','tears'),
('08_好的','bunny','wink','好的！','hop',None),
('09_一点点','ghost','closed','好像有一点','sway','blush'),
('10_等啊等','ghost','dot','等啊等','droop','sweat'),
('11_什么','ghost','big','什么？','wiggle','quest'),
('12_我来了','ghost','wink','我来了！','hop',None),
('13_风平浪静','pika','closed','风平浪静','sway','splash'),
('14_潮来了','pika','big','潮来了！','shake','splash'),
('15_早上好','pika','happy','早上好！','wave','splash'),
('16_睡了','pika','closed','我又一直等','droop','zzz')]
CH=dict(chick=chick,bunny=bunny,ghost=ghost,pika=pika)
def pose(an,t):
    s=math.sin(2*PI*t);a=abs(s);k={}
    up=0
    if an=='wave':up=.55+.4*s;k=dict(rz=.05*s)
    elif an=='hop':k=dict(dy=.32*a,sy=1+.07*(a-.5));up=.5*a
    elif an=='wiggle':k=dict(rz=.1*s,ry=.2*s)
    elif an=='shake':k=dict(dx=.05*math.sin(8*PI*t),rz=.05*math.sin(8*PI*t))
    elif an=='sway':k=dict(rz=.1*s)
    elif an=='droop':k=dict(sy=.96+.04*s,rx=.07)
    return k,up
def extras(sc,ex,t,ch):
    s=math.sin(2*PI*t);h=1.25 if ch!='pika' else 1.15
    if ex=='hearts':
        heart(sc,(-1.25,.8+.12*s,.2),1.1);heart(sc,(1.25,1.05-.12*s,.2),.8,HOT)
    elif ex=='tears':
        tear(sc,(-.5,.2-.5*(t%1),.92),.8);tear(sc,(.5,.2-.5*((t+.5)%1),.92),.8)
    elif ex=='sweat':
        tear(sc,(1.05,1.0+.08*s,.3),1.1)
    elif ex=='splash':
        o=.05*s
        squiggle(sc,[(-1.15,-1.0,.5),(-1.3,-.75,.55),(-1.08,-.58,.55),(-1.28,-.4,.5)],.07)
        squiggle(sc,[(.95,-1.05,.85),(1.05,-.9,.85),(.92,-.8,.85),(1.0,-.68,.85)],.07)
        squiggle(sc,[(1.25,-.72+o,-.2),(1.32,-.56+o,-.2),(1.2,-.47+o,-.2)],.06)
        sc.add(lambda p:ell(p,(-.25,-1.08,1.05),(.14,.05,.1)),PYEL)
def render_one(a):
    sp,t,W,ss=a
    name,ch,ex_,cap_,an,ex=sp
    k,up=pose(an,t)
    sc,x=CH[ch](ex=ex_,up=up,**k)
    extras(sc,ex,t,ch)
    cam=(0,.55,4.7) if ch!='pika' else (0,1.1,5.9)
    look=(0,-.12,0) if ch!='pika' else (0,-.12,0)
    im=render(sc,W,ss,cam=cam,look=look,seed=hash(ch)%5+1 if False else 3,fov=1.0)
    return im
def compose(im,cap_,ex,t,S):
    """im: float rgba W; die-cut white border + her handwriting caption"""
    a=(im[...,3]*255).astype(np.uint8);W=a.shape[0]
    rgb=(np.clip(im[...,:3],0,1)*255).astype(np.uint8)
    pad=int(W*.0)
    sc=W/512
    F=ImageFont.truetype(FONT,int(78*sc))
    base=Image.fromarray(a)
    txt=Image.new('L',(W,W),0);D=ImageDraw.Draw(txt)
    bb=D.textbbox((0,0),cap_,font=F);tw=bb[2]-bb[0]
    x0=(W-tw)/2-bb[0];y0=W*.975-bb[3]
    D.text((x0,y0),cap_,font=F,fill=255)
    if ex in('zzz','quest','steam'):
        G=ImageFont.truetype(FONT,int(58*sc))
        s={'zzz':'zZ','quest':'？','steam':'！'}[ex]
        D.text((W*.76,W*.1+W*.02*math.sin(2*PI*t)),s,font=G,fill=255)
    tx=cv2.dilate(np.array(txt),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(4*sc)|1,int(4*sc)|1)))
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(19*sc)|1,int(19*sc)|1))
    union=cv2.dilate(np.maximum(a,tx),k)
    union=cv2.GaussianBlur(union,(0,0),1.1*sc)
    out=np.zeros((W,W,4),np.uint8);out[...,:3]=255;out[...,3]=union
    al=(a/255.)[...,None];out[...,:3]=(rgb*al+255*(1-al)).astype(np.uint8)
    T=(tx/255.)[...,None];ink=np.array([38,34,34]);out[...,:3]=(out[...,:3]*(1-T)+ink*T).astype(np.uint8)
    return Image.fromarray(out).resize((S,S),Image.LANCZOS)
def task(a):
    sp,mode=a
    name=sp[0]
    if mode=='png':
        im=render_one((sp,.13,640,2));compose(im,sp[3],sp[5],.13,512).save(f'{OUT}/{name}.png');return name
    fr=[]
    for i in range(10):
        t=i/10;im=render_one((sp,t,320,2));fr.append(compose(im,sp[3],sp[5],t,240))
    pal=[]
    for f in fr:
        bg=Image.new('RGBA',f.size,(255,255,255,0));m=f.convert('RGBA')
        A=np.array(m)[...,3]
        q=m.convert('RGB').quantize(colors=200,dither=Image.Dither.NONE) if False else Image.composite(m.convert('RGB'),Image.new('RGB',m.size,(255,0,254)),Image.fromarray(((A>128)*255).astype(np.uint8))).quantize(colors=220,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
        p=q.getpalette()[:768]
        # find key index
        keyi=min(range(len(p)//3),key=lambda i:abs(p[i*3]-255)+abs(p[i*3+1])+abs(p[i*3+2]-254))
        q.info['transparency']=keyi;pal.append(q)
    pal[0].save(f'{OUT}/{name}.gif',save_all=True,append_images=pal[1:],duration=90,loop=0,disposal=2,optimize=False)
    return name
if __name__=='__main__':
    which=sys.argv[1] if len(sys.argv)>1 else 'all'
    from fontTools.ttLib import TTFont
    cm=TTFont(FONT).getBestCmap()
    for sp in SP:
        for c in sp[3]:
            if ord(c) not in cm:print('MISSING',c,sp[0])
    J=[(s,'png') for s in SP]+([(s,'gif') for s in SP] if which=='all' else [])
    with Pool(8) as p:
        for r in p.imap_unordered(task,J):pass
    from PIL import Image
    c=4;S=Image.new('RGB',(c*256,4*256),'#cfe3d4')
    for i,sp in enumerate(SP):
        t=Image.open(f'{OUT}/{sp[0]}.png').resize((256,256));S.paste(t,((i%c)*256,(i//c)*256),t)
    S.save('/tmp/yiyi/sticker_sheet.png')
