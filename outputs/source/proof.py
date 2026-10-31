from PIL import Image,ImageDraw,ImageFont,features
import sys
print('raqm',features.check('raqm'))
f=ImageFont.truetype('/tmp/yiyi/dist/YiyiHand-Regular.ttf',64)
s=ImageFont.truetype('/tmp/yiyi/dist/YiyiHand-Regular.ttf',40)
I=Image.new('RGB',(1500,900),'#fffdf6');D=ImageDraw.Draw(I)
ls=['我的爷爷每天早上五点就起床，','到小河边呼吸最新鲜的空气。','绿豆发芽了！你一定会长出白白的芽。','0123456789  12+30=42  3×8=24',
'The quick brown fox jumps over','the lazy dog. Hello, Yiyi!','ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz']
y=20
for l in ls: D.text((30,y),l,font=f,fill='#222');y+=100
I.save('/tmp/yiyi/proof.png')

import pickle
G=pickle.load(open('/tmp/yiyi/glyphs.pkl','rb'))
from fontTools.ttLib import TTFont
cm=TTFont('/tmp/yiyi/dist/YiyiHand-Regular.ttf').getBestCmap()
hz=[chr(c) for c in cm if 0x4e00<=c<=0x9fff]
lab=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',14)
cols=26;cw=58
for p in range(0,len(hz),234):
    cc=hz[p:p+234];rows=(len(cc)+cols-1)//cols
    I=Image.new('RGB',(cols*cw,rows*(cw+14)),'white');D=ImageDraw.Draw(I)
    F=ImageFont.truetype('/tmp/yiyi/dist/YiyiHand-Regular.ttf',50)
    for i,c in enumerate(cc):
        x,y=(i%cols)*cw,(i//cols)*(cw+14)
        D.text((x+1,y),c,font=lab,fill='red');D.text((x+4,y+12),c,font=F,fill='black')
    I.save(f'/tmp/yiyi/all{p//234}.png')
