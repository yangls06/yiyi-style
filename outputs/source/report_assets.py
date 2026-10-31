import sys,cv2,numpy as np,json,pickle,subprocess
sys.path[:0]=['/tmp/yiyi/scripts']
from ink import ink,norm_stroke
import strokes as S
from build_glyphs import cr
from PIL import Image,ImageDraw,ImageFont
R='/tmp/yiyi/report/'
def jw(a,n,q=82): cv2.imwrite(R+n,a,[cv2.IMWRITE_JPEG_QUALITY,q])
# --- layers on a page
i=cv2.imread('full/语文/IMG_5376.jpg');h,w=i.shape[:2]
c=i[int(h*.28):int(h*.62),int(w*.0):int(w*.98)]
lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32);L,a,b=lab[...,0],lab[...,1],lab[...,2]
bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((41,41))),(0,0),21);d=bg-L
red=(a-np.median(a))>9;green=((np.median(a)-a)>3.5)&(d<45);inkm=(d>28)&~red&~green
W=np.full(c.shape,255,np.uint8);W[green]=(150,200,150);W[inkm]=(120,40,20);W[red]=(40,40,230)
Hc=np.full(c.shape,255,np.uint8);Hc[cv2.GaussianBlur(inkm.astype(np.float32),(0,0),1.2)>.45]=(30,30,30)
jw(cv2.resize(c,None,fx=.42,fy=.42,interpolation=cv2.INTER_AREA),'layer_a.jpg');jw(cv2.resize(W,None,fx=.42,fy=.42,interpolation=cv2.INTER_AREA),'layer_b.jpg');jw(cv2.resize(Hc,None,fx=.42,fy=.42,interpolation=cv2.INTER_AREA),'layer_c.jpg')
# --- grid
subprocess.run(['venv/bin/python','-I','scripts/grid.py','full/语文/IMG_5376.jpg'],capture_output=True)
g=cv2.imread('dbg.jpg');jw(cv2.resize(g,None,fx=.8,fy=.8,interpolation=cv2.INTER_AREA),'grid.jpg')
s=cv2.imread('strips/5376.jpg');jw(s[160:760],'strip.jpg',80)
# --- cell stages
_db=pickle.load(open('db.pkl','rb'));rows=[('绿','5362',14,6)]+[(c,_db[c][0]['pg'],_db[c][0]['r'],_db[c][0]['k']) for c in '我雪春']
F=ImageFont.truetype('dist/YiyiHand-Regular.ttf',190)
T=240;C=np.full((len(rows)*(T+8),4*(T+8),3),255,np.uint8)
for n,(ch,p,r,k) in enumerate(rows):
    c=cv2.imread(f'cells/{p}_{r:02d}_{k:02d}.png');m,_=ink(c);o=norm_stroke(m,rmin=10.5,rmax=14.5)
    gi=Image.new('L',(T,T),255);D=ImageDraw.Draw(gi);D.text((25,25),ch,font=F,fill=0)
    P=[cv2.resize(c,(T,T),interpolation=cv2.INTER_AREA),cv2.cvtColor(255-cv2.resize(m,(T,T),interpolation=cv2.INTER_AREA),cv2.COLOR_GRAY2BGR),cv2.cvtColor(255-cv2.resize(o,(T,T),interpolation=cv2.INTER_AREA),cv2.COLOR_GRAY2BGR),cv2.cvtColor(np.array(gi),cv2.COLOR_GRAY2BGR)]
    for j,q in enumerate(P):C[n*(T+8):n*(T+8)+T,j*(T+8):j*(T+8)+T]=q
jw(C,'stages.jpg',85)
cv2.imwrite(R+'samples.png',cv2.imread('lv.png'))
# --- digits
d=cv2.imread('comp_5396.png');jw(d[:540],'digits.jpg')
p=cv2.imread('full/数学/IMG_5396.jpg');h,w=p.shape[:2];jw(cv2.resize(p[int(h*.1):int(h*.5),int(w*.3):w],None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA),'math.jpg')
# --- english
e=cv2.imread('env_5388.jpg');jw(e[230:980,920:1860],'en_fail.jpg');cv2.imwrite(R+'letters_fail.png',cv2.imread('letters.png'))
# --- trace overlay (the real check)
Tb=json.load(open('trace_boxes.json'));ks=list(Tb);Sz=300;cols=6;rw=(len(ks)+cols-1)//cols
O=np.full((rw*(Sz+24),cols*(Sz+10),3),255,np.uint8)
for n,k in enumerate(ks):
    pg,x0,y0,x1,y1=Tb[k];q=cv2.imread(f'full/英语/IMG_{pg}.jpg')[y0:y1,x0:x1];s_=max(x1-x0,y1-y0);bx=np.full((s_,s_,3),255,np.uint8);bx[:y1-y0,:x1-x0]=q
    t=cv2.resize(bx,(Sz,Sz),interpolation=cv2.INTER_CUBIC)
    for st in S.T[k][5]:
        P=(cr(st)*30).astype(np.int32);cv2.polylines(t,[P],False,(30,30,240),2,cv2.LINE_AA)
    X=(n%cols)*(Sz+10);Y=(n//cols)*(Sz+24);O[Y+22:Y+22+Sz,X:X+Sz]=t;cv2.putText(O,k,(X+2,Y+17),0,.65,(0,0,255),2)
cv2.imwrite(R+'trace_overlay.png',O);jw(O,'trace_overlay.jpg',82)
# --- side-by-side style refs
for n,p,b in [('d1','画画/IMG_5345',(180,400,1000,2200)),('d2','画画/IMG_5360',(100,900,3100,2000))]:pass
i=cv2.imread('full/画画/IMG_5345.jpg');jw(cv2.resize(i[300:2200,400:2750],None,fx=.33,fy=.33,interpolation=cv2.INTER_AREA),'draw_food.jpg')
i=cv2.imread('full/画画/IMG_5360.jpg');jw(cv2.resize(i[300:2000,700:3100],None,fx=.33,fy=.33,interpolation=cv2.INTER_AREA),'draw_char.jpg')
def cl(p,box,n):
    i=cv2.imread(f'full/手工/IMG_{p}.jpg');h,w=i.shape[:2];x0,y0,x1,y1=box;jw(cv2.resize(i[int(y0*h):int(y1*h),int(x0*w):int(x1*w)],(420,420),interpolation=cv2.INTER_AREA),n)
cl('5358',(.08,.37,.92,.78),'clay_chick.jpg');cl('5346',(.15,.28,.95,.75),'clay_bunny.jpg');cl('5354',(.2,.36,.85,.79),'clay_ghost.jpg');cl('5351',(.0,.31,1,.87),'clay_pika.jpg')
