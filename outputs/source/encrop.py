import cv2,sys
# page,x0,y0,x1,y1 in preview-fraction
import numpy as np
items=[('5388',.45,.25,.9,.88),('5389',.2,.45,.75,.75),('5390',.0,.0,1,.7),('5391',.4,.05,1,.8),('5392',.1,.0,1,.95),('5393',.3,.1,1,.8),('5394',.1,.0,.8,1),('5395',.2,.25,1,1)]
for p,a,b,c,d in items:
    i=cv2.imread(f'full/英语/IMG_{p}.jpg');h,w=i.shape[:2]
    cr=i[int(b*h):int(d*h),int(a*w):int(c*w)]
    print(p,i.shape,cr.shape)
    cv2.imwrite(f'en_{p}.jpg',cv2.resize(cr,None,fx=.55,fy=.55,interpolation=cv2.INTER_AREA))
