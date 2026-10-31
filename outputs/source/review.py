import sys,cv2,numpy as np,pickle
sys.path[:0]=['/tmp/yiyi/scripts']
from ink import ink,norm_stroke
from PIL import Image,ImageDraw,ImageFont
db=pickle.load(open('/tmp/yiyi/db.pkl','rb'))
f=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16)
chs=list(db); cols=20;cw=78
pages=[chs[i:i+200] for i in range(0,len(chs),200)]
for p,cc in enumerate(pages):
    rows=(len(cc)+cols-1)//cols
    I=Image.new('RGB',(cols*cw,rows*(cw+16)),'white');D=ImageDraw.Draw(I)
    for i,ch in enumerate(cc):
        e=db[ch][0]
        c=cv2.imread(f"/tmp/yiyi/cells/{e['pg']}_{e['r']:02d}_{e['k']:02d}.png");m,_=ink(c)
        n=norm_stroke(m)
        t=Image.fromarray(255-n).resize((cw-2,cw-2),Image.LANCZOS).convert('RGB')
        x,y=(i%cols)*cw,(i//cols)*(cw+16);I.paste(t,(x+1,y+16))
        D.text((x+2,y),ch,font=f,fill='red');D.text((x+22,y+2),f"{e['pg'][2:]}.{e['r']}.{e['k']} n{len(db[ch])}",fill='blue')
    I.save(f'/tmp/yiyi/rev{p}.png')
print(len(pages))
