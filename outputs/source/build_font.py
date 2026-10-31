import pickle,sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString as addfea
G=pickle.load(open('/tmp/yiyi/glyphs.pkl','rb'))
def draw(cs,pen):
    for c in cs:
        for s in c:
            if s[0]=='M': pen.moveTo(s[1])
            elif s[0]=='L':
                pen.lineTo(s[1])
            else: pen.curveTo(s[1],s[2],s[3])
        pen.closePath()
glyphs={};adv={};cmap={}
def name(ch):
    if len(ch)==1: return f'uni{ord(ch):04X}'
    base=ch.split('.')[0]
    u=f'uni{ord(base):04X}' if len(base)==1 else base
    return u+('.'+ch.split('.',1)[1] if '.' in ch else '')
def add(ch,cs,w):
    # raster traces go y-down -> flipped once by to_font, so contours are CCW; reverse for TrueType
    from fontTools.pens.reverseContourPen import ReverseContourPen
    tp=TTGlyphPen(None)
    draw(cs,Cu2QuPen(ReverseContourPen(tp) if REV else tp,1.0,reverse_direction=False))
    n=name(ch);glyphs[n]=tp.glyph();adv[n]=w
    if len(ch)==1: cmap[ord(ch)]=n
REV=False
add('.notdef'.replace('.','_'),[],500) if False else None
tp=TTGlyphPen(None);tp.moveTo((80,0));tp.lineTo((80,700));tp.lineTo((420,700));tp.lineTo((420,0));tp.closePath();glyphs['.notdef']=tp.glyph();adv['.notdef']=500
for sp,w,n in [(0x20,300,'space'),(0x3000,1000,'uni3000'),(0xA0,300,'uni00A0')]:
    glyphs[n]=TTGlyphPen(None).glyph();adv[n]=w;cmap[sp]=n
for ch,e,cs in G['hz']: add(ch,cs,1000)
for ch,w,cs in G['md']: add(ch,cs,w)
for ch,w,cs in G['sg']: add(ch,cs,w)
# ASCII aliases for full-width marks she wrote
order=['.notdef']+[g for g in glyphs if g!='.notdef']
fam=sys.argv[1] if len(sys.argv)>1 else 'Yiyi Hand'
fb=FontBuilder(1000,isTTF=True)
fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap);fb.setupGlyf({g:glyphs[g] for g in order})
gs=fb.font['glyf']
fb.setupHorizontalMetrics({g:(adv[g],getattr(gs[g],'xMin',0) or 0) for g in order})
fb.setupHorizontalHeader(ascent=900,descent=-200)
fb.setupNameTable({'familyName':{'en':fam,'zh':'Yiyi 手写体'} ,'styleName':'Regular','uniqueFontIdentifier':'YiyiHand-1.000','fullName':fam,'psName':'YiyiHand-Regular','version':'Version 1.000','description':'Built from the handwriting of Yiyi'} if False else {'familyName':fam,'styleName':'Regular','uniqueFontIdentifier':'YiyiHand-1.000','fullName':fam,'psName':'YiyiHand-Regular','version':'Version 1.000'})
fb.setupOS2(sTypoAscender=880,sTypoDescender=-120,sTypoLineGap=100,usWinAscent=1000,usWinDescent=300,sxHeight=430,sCapHeight=700)
fb.setupPost()
f=fb.font
f['name'].setName('Yiyi 手写体',1,3,1,2052);f['name'].setName('Yiyi 手写体',4,3,1,2052)
# contextual alternates
A1=[g for g in order if g.endswith('.alt1')];B1=[g[:-5] for g in A1]
A2=[g for g in order if g.endswith('.alt2')];B2=[g[:-5] for g in A2]
dig=[g for g in order if g.endswith('.alt')];dig0=[g[:-4] for g in dig]
fea=f"""
@b1=[{' '.join(B1+dig0)}];@a1=[{' '.join(A1+dig)}];
@b2=[{' '.join(B2)}];@a2=[{' '.join(A2)}];
@any=[{' '.join(g for g in order if '.' not in g and g[:3]=='uni')}];
lookup alt1 {{ sub @b1 by @a1; }} alt1;
lookup alt2 {{ sub @b2 by @a2; }} alt2;
lookup rot {{
  sub @a1 @b2' lookup alt2;
  sub @b1 @b1' lookup alt1;
  sub @a1 @any @b2' lookup alt2;
  sub @b1 @any @b1' lookup alt1;
}} rot;
feature calt {{ lookup rot; }} calt;
feature kern {{ }} kern;
""".replace("feature kern { } kern;\n","")
addfea(f,fea)
import os
os.makedirs('/tmp/yiyi/dist',exist_ok=True)
f.save('/tmp/yiyi/dist/YiyiHand-Regular.ttf')
print(len(order),'glyphs;',len(cmap),'codepoints; alts',len(A1),len(A2))
