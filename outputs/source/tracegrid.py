import cv2,numpy as np,sys
sys.path[:0]=['/tmp/yiyi/scripts']
from letters import B
T={'c':B['c'],'e':B['e'],'f':B['f'],'g':B['g'],'l':B['l'],'m':B['m'],'o':('5389',2770,1300,2880,1480),'p':('5389',1700,1230,1890,1570),'r':('5391',2510,265,2640,385),'s':('5389',1015,1200,1130,1370),'t':B['t'],'u':('5392',1460,215,1570,325),'w':('5389',1170,1225,1390,1390),'H':B['H'],'A':B['A'],'C':B['C'],'E':B['E'],'i':('5391',2315,720,2390,890)}
import json;json.dump(T,open('/tmp/yiyi/trace_boxes.json','w'))
S=300;cols=6;ks=list(T);rows=(len(ks)+cols-1)//cols
C=np.full((rows*(S+24),cols*(S+10),3),255,np.uint8)
for n,k in enumerate(ks):
    p,x0,y0,x1,y1=T[k];i=cv2.imread(f'full/英语/IMG_{p}.jpg')[y0:y1,x0:x1]
    # letterbox into square so grid is uniform in photo pixels
    s=max(x1-x0,y1-y0);q=np.full((s,s,3),255,np.uint8);q[:y1-y0,:x1-x0]=i
    g=cv2.cvtColor(cv2.resize(q,(S,S),interpolation=cv2.INTER_CUBIC),cv2.COLOR_BGR2GRAY)
    g=cv2.normalize(g,None,0,255,cv2.NORM_MINMAX);c=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
    for t in range(0,11):
        cv2.line(c,(t*30,0),(t*30,S),(0,180,255) if t%5==0 else (120,220,255),1);cv2.line(c,(0,t*30),(S,t*30),(0,180,255) if t%5==0 else (120,220,255),1)
    X=(n%cols)*(S+10);Y=(n//cols)*(S+24)
    C[Y+22:Y+22+S,X:X+S]=c;cv2.putText(C,k,(X+2,Y+17),0,.65,(0,0,255),2)
cv2.imwrite('trace.png',C)
