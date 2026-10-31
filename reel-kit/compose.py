import numpy as np, cv2, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__))+'/'
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FS='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def F(p,s): return ImageFont.truetype(p,s)
def _load(n):
    a=np.array(Image.open(D+'cut/'+n+'.png').convert('RGBA'))
    k,lab,st,_=cv2.connectedComponentsWithStats((a[:,:,3]>20).astype(np.uint8))
    keep=1+np.argmax(st[1:,4]); a[:,:,3]=np.where(lab==keep,a[:,:,3],0)
    if n=='krishna_flute': a[-30:,:,3]=0
    ys,xs=np.where(a[:,:,3]>10); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return Image.fromarray(a)
CHARS={n:_load(n) for n in ['krishna','krishna_flute','shiva','man','man_full','man_pray']}
STYLE={'man':((255,246,226),(24,28,70),'You'),'krishna':((255,203,112),(40,25,10),'Krishna'),'shiva':((200,222,246),(16,28,70),'Shiva')}
def bg(w,h,gc,gy,seed,blue=False):
    rnd=random.Random(seed)
    t=np.linspace(0,1,h)[:,None,None]
    top=np.array((8,22,52) if blue else (10,15,45)); bot=np.array((22,62,118) if blue else (36,38,100))
    a=(top+(bot-top)*t)*np.ones((1,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    r=np.sqrt((xx-w/2)**2+(yy-gy)**2)
    g=np.exp(-(r/(0.45*w))**2)[...,None]*0.55
    a=a*(1-g)+np.array(gc)*g
    im=Image.fromarray(a.clip(0,255).astype('uint8'))
    d=ImageDraw.Draw(im,'RGBA')
    for _ in range(int(w*h/9000)):
        x,y=rnd.randrange(w),rnd.randrange(h); s=rnd.choice([1,1,2,2,3]); al=rnd.randrange(120,255)
        d.ellipse((x,y,x+s,y+s),fill=(255,255,255,al))
    return im
def wm(im,y):
    d=ImageDraw.Draw(im,'RGBA'); f=F(FS,36); t='@thequietverse.ultimate'
    w=d.textlength(t,font=f); d.text(((im.width-w)/2,y),t,font=f,fill=(205,205,210,170),anchor='la')
def wrap(d,text,f,maxw):
    out=[];cur=''
    for wd in text.split():
        t=(cur+' '+wd).strip()
        if d.textlength(t,font=f)<=maxw: cur=t
        else: out.append(cur);cur=wd
    out.append(cur); return out
def bubble(im,text,who,x,y,maxw=640,align='left',tail=None,size=62,label=True):
    fill,ink,name=STYLE[who]; d=ImageDraw.Draw(im,'RGBA'); f=F(FB,size)
    lines=wrap(d,text,f,maxw); lh=int(size*1.3)
    tw=max(d.textlength(l,font=f) for l in lines); bw=int(tw+88); bh=int(len(lines)*lh+50)
    if align=='right': x=x-bw
    if label:
        d.text((x+10,y-50),name,font=F(FS,36),fill=(240,225,190,255))
    d.rounded_rectangle((x+6,y+8,x+bw+6,y+bh+8),50,fill=(0,0,0,150))
    d.rounded_rectangle((x,y,x+bw,y+bh),50,fill=fill)
    tx=tail if tail else (x+bw*0.65 if align=='right' else x+bw*0.35)
    d.polygon([(tx-24,y+bh-2),(tx+24,y+bh-2),(tx,y+bh+48)],fill=fill)
    for i,l in enumerate(lines): d.text((x+44,y+25+i*lh+size*0.0),l,font=f,fill=ink)
    return bh
def put(im,name,cx,bottom=None,top=None,height=None):
    c=CHARS[name]; s=height/c.height; c=c.resize((int(c.width*s),height),Image.LANCZOS)
    y=(bottom-height) if bottom else top
    im.paste(c,(int(cx-c.width/2),int(y)),c); return c
def dots(im,i,n=5,y=1296):
    d=ImageDraw.Draw(im,'RGBA')
    for k in range(n):
        x=480+30*k; d.ellipse((x-8,y-8,x+8,y+8),fill=(255,203,112,255) if k==i else (255,255,255,235))
def card(im,text,y,sub=None):
    d=ImageDraw.Draw(im,'RGBA'); f=F(FB,46); lines=wrap(d,text,f,820)
    w=int(max(d.textlength(l,font=f) for l in lines)+90); h=int(len(lines)*62+50)
    x=(im.width-w)//2
    d.rounded_rectangle((x+5,y+7,x+w+5,y+h+7),44,fill=(0,0,0,140))
    d.rounded_rectangle((x,y,x+w,y+h),44,fill=(255,246,226))
    for i,l in enumerate(lines): d.text((im.width/2,y+25+i*62),l,font=f,fill=(24,28,70),anchor='ma')
    return h
def story(path,who,char,text,q,seed,align='right'):
    blue=(who=='shiva'); gc=(70,120,180) if blue else (130,100,85)
    im=bg(1080,1920,gc,1050,seed,blue); wm(im,150)
    h=bubble(im,text,who,1000 if align=='right' else 80,300,maxw=600,align=align)
    hh=800 if char!='man' else 640
    put(im,char,540,bottom=1480,height=hh)
    card(im,q,1540)
    im.convert('RGB').save(path,quality=92)
def slide(path,i,seed,who,text,char,ch_h,ch_bottom=1255,align=None,top_text=None,extra=None,blue=False,cx=540,tail=None):
    gc=(70,120,180) if blue else (130,100,85)
    im=bg(1080,1350,gc,820,seed,blue); wm(im,38)
    if text:
        a=align or ('left' if who=='man' else 'right')
        bubble(im,text,who,70 if a=='left' else 1010,150,maxw=720,align=a,tail=tail,size=58)
    if extra: extra(im)
    if char: put(im,char,cx,bottom=ch_bottom,height=ch_h)
    dots(im,i); return im
