import sys,pickle,cv2,numpy as np
sys.path[:0]=['/tmp/yiyi/scripts']
from gen import *
from ink import norm_stroke
from learn import her_mask
R=pickle.load(open('/tmp/yiyi/lib.pkl','rb'))
test=sys.argv[1];rows=[]
for ch in test:
    lib=Lib(R,exclude={ch});rng=np.random.default_rng(1)
    r=[x for x in R if x['ch']==ch][0]
    st,src=generate(ch,lib,rng);m=render_cell(st,lib,rng)
    real=norm_stroke(her_mask(ch,r['e']),rmin=10.5,rmax=14.5);gen_=norm_stroke((m>127).astype(np.uint8)*255,rmin=10.5,rmax=14.5)
    a=255-cv2.resize(real,(170,170),interpolation=cv2.INTER_AREA);b=255-cv2.resize(gen_,(170,170),interpolation=cv2.INTER_AREA)
    cv2.putText(b,f"{src.count('comp')}/{len(src)}",(3,14),0,.45,0,1)
    rows.append(np.hstack([a,np.full((170,4),200,np.uint8),b]))
cols=4;rows+= [np.full_like(rows[0],255)]*((-len(rows))%cols)
G=np.vstack([np.hstack([np.pad(x,6,constant_values=255) for x in rows[i:i+cols]]) for i in range(0,len(rows),cols)])
cv2.imwrite('/tmp/yiyi/loo.png',G)
