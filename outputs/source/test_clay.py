import sys,time,cv2,numpy as np
sys.path[:0]=['/tmp/yiyi/scripts']
from chars import *
for n,f,k in [('c',chick,dict(ex='happy',up=.7,rz=.1)),('b',bunny,dict(ex='dot')),('g',ghost,dict(ex='dot')),('p',pika,dict(ex='dot'))]:
    t=time.time();sc,x=f(**k);im=render(sc,420,1,cam=(0,.5,5.4) if n!='p' else (0,1.2,6.6),look=(0,0,0) if n!='p' else (0,-.2,0))
    bg=np.array([.9,.85,.75]);o=im[...,:3]*im[...,3:]+bg*(1-im[...,3:])
    cv2.imwrite(f'/tmp/yiyi/t_{n}.png',(o[...,::-1]*255).astype(np.uint8));print(n,time.time()-t,im[...,3].mean())
