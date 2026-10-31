import sys,pickle,numpy as np,warnings
warnings.filterwarnings('ignore')
sys.path[:0]=['/tmp/yiyi/scripts']
from gen import Lib,generate,render_cell
from build_glyphs import glyph_from_mask
from multiprocessing import Pool
R=pickle.load(open('/tmp/yiyi/lib.pkl','rb'));LIB=Lib(R)
have=set(pickle.load(open('/tmp/yiyi/db.pkl','rb')))
def job(a):
    ch,v=a;rng=np.random.default_rng(ord(ch)*7+v)
    r=generate(ch,LIB,rng)
    if r is None:return None
    st,src=r;m=render_cell(st,LIB,rng)
    g=glyph_from_mask(ch if v==0 else f'{ch}.alt{v}',(m>127).astype(np.uint8)*255)
    return None if g is None else (g[0],src.count('comp')/len(src),g[1])
if __name__=='__main__':
    L1=[]
    for h in range(0xB0,0xD8):
        for l in range(0xA1,0xFF):
            try:L1.append(bytes([h,l]).decode('gb2312'))
            except:pass
    todo=[c for c in L1 if c not in have]
    J=[(c,v) for c in todo for v in (0,1)]
    with Pool(8) as p:G=[g for g in p.map(job,J,chunksize=16) if g]
    pickle.dump(G,open('/tmp/yiyi/gen.pkl','wb'))
    base=[g for g in G if '.' not in g[0]]
    print(len(L1),'L1;',len(todo),'to generate;',len(base),'ok; comp-share',np.mean([g[1] for g in base]).round(2))
    print('missing',''.join(c for c in todo if c not in {g[0] for g in base}))
