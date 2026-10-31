import sys,cv2,numpy as np,json,pickle,collections
sys.path[:0]=['/tmp/yiyi/scripts']
from labels import L
from ink import ink
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
ref=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',200)
def refmask(ch):
    I=Image.new('L',(260,260),0);D=ImageDraw.Draw(I);D.text((30,10),ch,font=ref,fill=255);a=np.array(I)>128
    return a
def bbox(m):
    y,x=np.where(m);return x.min(),x.max()+1,y.min(),y.max()+1
def score(m,ch):
    if m.sum()<20: return 0,0
    r=refmask(ch)
    if not r.any(): return 0.5,0.5
    x0,x1,y0,y1=bbox(m>0);a=m[y0:y1,x0:x1]>0
    X0,X1,Y0,Y1=bbox(r);b=r[Y0:Y1,X0:X1]
    a=cv2.resize(a.astype(np.uint8),(128,128),interpolation=cv2.INTER_AREA)>0
    b=cv2.resize(b.astype(np.uint8),(128,128),interpolation=cv2.INTER_AREA)>0
    da=ndi.distance_transform_edt(~a); db=ndi.distance_transform_edt(~b)
    rec=(da[b]<=9).mean(); pre=(db[a]<=9).mean()
    return float(rec),float(pre)
PUNCT='，。、；！？：《》'
db=collections.defaultdict(list)
for pg,rows in L.items():
    for r,s in rows.items():
        for k,ch in enumerate(s):
            if ch=='_':continue
            c=cv2.imread(f'/tmp/yiyi/cells/{pg}_{r:02d}_{k:02d}.png')
            m,st=ink(c)
            if st['area']<8: continue
            rec,pre=score(m,ch) if ch not in PUNCT else (1,1)
            nc=ndi.label(m>0,np.ones((3,3)))[1]
            q=rec*pre*(1-min(st['red']/600,.5))*min(1,st['hi']/60)**.3*(1-min(max(nc-6,0)/20,.5))
            db[ch].append(dict(pg=pg,r=r,k=k,rec=rec,pre=pre,red=st['red'],hi=st['hi'],q=q))
for ch in db: db[ch].sort(key=lambda e:-e['q'])
pickle.dump(dict(db),open('/tmp/yiyi/db.pkl','wb'))
print(len(db),sum(len(v) for v in db.values()))
hz=[c for c in db if '一'<=c<='鿿'];print(len(hz),'hanzi')
weak=[(c,round(db[c][0]['q'],2)) for c in hz if db[c][0]['q']<.6];print(len(weak),weak[:80])
