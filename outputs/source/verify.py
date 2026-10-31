import sys,cv2,numpy as np,json
sys.path[:0]=['/tmp/yiyi/scripts']
from labels import L
from ink import ink
from PIL import Image,ImageDraw,ImageFont
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
pages=sys.argv[1:] or list(L)
for pg in pages:
    ents=[]
    for r,s in L[pg].items():
        for k,ch in enumerate(s):
            if ch=='_':continue
            c=cv2.imread(f'/tmp/yiyi/cells/{pg}_{r:02d}_{k:02d}.png')
            if c is None: print('MISSING',pg,r,k,ch);continue
            m,st=ink(c); ents.append((r,k,ch,m,st))
    cols=14;cw=94;n=len(ents);rows=(n+cols-1)//cols
    I=Image.new('RGB',(cols*cw,rows*(cw+18)),'white');D=ImageDraw.Draw(I)
    for i,(r,k,ch,m,st) in enumerate(ents):
        x,y=(i%cols)*cw,(i//cols)*(cw+18)
        t=Image.fromarray(255-m).resize((cw-4,cw-4)).convert('RGB');I.paste(t,(x+2,y+18))
        D.text((x+2,y),ch,font=f,fill='red');D.text((x+24,y+3),f'{r}.{k}',fill='blue')
    I.save(f'/tmp/yiyi/verify_{pg}.png');print(pg,n)
