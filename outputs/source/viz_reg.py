import pickle,cv2,numpy as np,sys
sys.path[:0]=['/tmp/yiyi/scripts']
from learn import ap
R=pickle.load(open('/tmp/yiyi/lib.pkl','rb'));out=[]
for r in R[:int(sys.argv[1]) if len(sys.argv)>1 else 12]:
    e=r['e'];c=cv2.imread(f"/tmp/yiyi/cells/{e['pg']}_{e['r']:02d}_{e['k']:02d}.png")
    a=c.copy();b=c.copy()
    for m in r['med']:cv2.polylines(a,[ap(r['A'],m).astype(np.int32)],False,(255,0,0),2,cv2.LINE_AA)
    for h in r['her']:cv2.polylines(b,[ap(r['A'],h).astype(np.int32)],False,(0,0,255),2,cv2.LINE_AA)
    t=np.hstack([a,b]);cv2.putText(t,f"{np.mean(r['ok']):.2f} {r['cov']:.2f}",(4,20),0,.6,(0,120,0),2);out.append(cv2.resize(t,None,fx=.6,fy=.6))
cv2.imwrite('/tmp/yiyi/reg.png',np.vstack([np.hstack(out[i:i+3]) for i in range(0,len(out)-len(out)%3,3)]))
