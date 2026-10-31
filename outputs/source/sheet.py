import sys,glob,os
from PIL import Image,ImageDraw
d,out,cols,cell=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
fs=sorted(glob.glob(d+'/*.jpg'))
ims=[]
for f in fs:
    i=Image.open(f);i.thumbnail((cell,cell));ims.append((os.path.basename(f)[:-4],i))
rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*cell,rows*cell),'white');D=ImageDraw.Draw(S)
for n,(k,i) in enumerate(ims):
    x,y=(n%cols)*cell,(n//cols)*cell;S.paste(i,(x,y));D.rectangle((x,y,x+70,y+14),fill='yellow');D.text((x+2,y+2),k,fill='red')
S.save(out,quality=85)
