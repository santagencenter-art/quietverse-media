import sys,subprocess,math; sys.path.insert(0,'.')
from compose import *
from reel import dur,TH,U
W,H=1080,1920
def ridge(draw,y0,amp,seed,col,sc=2):
    r=random.Random(seed); ph=[r.random()*6 for _ in range(3)]
    pts=[(0,H*sc)]
    for x in range(0,W*sc+1,8*sc):
        y=sc*y0+sc*amp*(math.sin(x/(W*sc)*5+ph[0])*.5+math.sin(x/(W*sc)*11+ph[1])*.3+math.sin(x/(W*sc)*23+ph[2])*.15)
        pts.append((x,y*1))
    pts.append((W*sc,H*sc)); draw.polygon(pts,fill=col)
def static_bg(theme,seed):
    sc=2; im=Image.new('RGB',(W*sc,H*sc)); d=ImageDraw.Draw(im)
    top,bot=(10,15,48),(40,38,104)
    for y in range(H*sc):
        t=y/(H*sc); d.line([(0,y),(W*sc,y)],fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    # moon + halo
    mx,my=(880*sc,780*sc) if theme!='man' else (200*sc,800*sc)
    yy,xx=np.mgrid[0:H*sc,0:W*sc]; rr=np.sqrt((xx-mx)**2+(yy-my)**2)/(sc*1.0)
    al=(np.exp(-(rr/170)**2)*0.55)[...,None]
    arr=np.array(im).astype(np.float32); arr=arr*(1-al)+np.array((255,226,160),np.float32)*al; im=Image.fromarray(arr.astype('uint8'))
    d=ImageDraw.Draw(im); d.ellipse((mx-85*sc,my-85*sc,mx+85*sc,my+85*sc),fill=(255,236,190))
    d.ellipse((mx-45*sc,my-100*sc,mx+125*sc,my+70*sc),fill=(14,18,52)) if False else None
    if theme=='man':
        r=random.Random(seed); x=0
        while x<W*sc:
            w=r.randrange(70,170)*sc; h=r.randrange(260,620)*sc
            d.rectangle((x,H*sc-420*sc-h+300*sc,x+w,H*sc),fill=(14,16,42))
            for wy in range(int(H*sc-420*sc-h+330*sc),H*sc-60*sc,50*sc):
                for wx in range(x+12*sc,x+w-20*sc,34*sc):
                    if r.random()<.22: d.rectangle((wx,wy,wx+14*sc,wy+22*sc),fill=(255,205,120))
            x+=w+r.randrange(0,16)*sc
    else:
        ridge(d,1180*sc/sc,150*sc/sc,seed,(36,40,100),sc) if False else None
        ridge(d,1250,120,seed,(30,34,88),sc); ridge(d,1400,90,seed+1,(22,26,70),sc); ridge(d,1560,70,seed+2,(15,18,52),sc)
        # small temple silhouette
        tx,ty=230*sc,1290*sc; c=(15,18,52)
        d.rectangle((tx-60*sc,ty,tx+60*sc,ty+130*sc),fill=c); d.polygon([(tx-75*sc,ty),(tx+75*sc,ty),(tx,ty-70*sc)],fill=c); d.rectangle((tx-6*sc,ty-100*sc,tx+6*sc,ty-70*sc),fill=c)
    return np.array(im.resize((W,H),Image.LANCZOS)).astype(np.float32)
def cloud_layer(seed):
    sc=2; im=Image.new('RGBA',(W*2*sc,H*sc),(0,0,0,0)); d=ImageDraw.Draw(im); r=random.Random(seed)
    for _ in range(7):
        cx=r.randrange(300*sc,(W*2-500)*sc); cy=r.randrange(180*sc,1000*sc); 
        for k in range(5): d.ellipse((cx+k*60*sc-70*sc,cy-28*sc,cx+k*60*sc+70*sc,cy+28*sc),fill=(120,130,190,34))
    im=im.filter(ImageFilter.GaussianBlur(8)).resize((W*2,H),Image.LANCZOS)
    return np.array(im).astype(np.float32)
def glow(gc):
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt((xx-W/2)**2+(yy-1050)**2); return (np.exp(-(r/520)**2)[...,None]*np.array(gc,np.float32))
def fg_layer(who,char,text,ch_h=760,extra=None,bs=58):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); wm(im,150)
    a='left' if who=='man' else 'right'
    bubble(im,text,who,80 if a=='left' else 1000,300,maxw=780,align=a,size=bs)
    if char:
        c=CHARS[char]; s=ch_h/c.height; c=c.resize((int(c.width*s),ch_h),Image.LANCZOS)
        im.alpha_composite(c,(int(540-c.width/2),1560-ch_h))
    if extra: extra(im)
    return np.array(im).astype(np.float32)
def end_fg(lines=("You don't need to","feel holy to hear Him.")):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); wm(im,150); d=ImageDraw.Draw(im,'RGBA'); y=600
    for l in lines: d.text((540,y),l,font=F(FB,78),fill=(255,246,226,255),anchor='ma'); y+=105
    d.text((540,y+40),"Follow @thequietverse.ultimate",font=F(FB,44),fill=(255,203,112,255),anchor='ma')
    c=CHARS['man_pray']; s=640/c.height; c=c.resize((int(c.width*s),640),Image.LANCZOS); im.alpha_composite(c,(int(540-c.width/2),1920-640))
    return np.array(im).astype(np.float32)
def comp(base,layer,dy=0):
    if dy: layer=np.roll(layer,dy,axis=0)
    a=layer[...,3:4]/255.0; return base*(1-a)+layer[...,:3]*a
rs=random.Random(7); STARS=[(rs.randrange(W),rs.randrange(1250),rs.choice([2,3,4]),rs.random()*6.28) for _ in range(150)]
def frame(bg,cl,gl,fg,t,glc):
    f=bg.copy()
    off=int((t*14)%W); f=f*(1-cl[:,off:off+W,3:4]/255)+cl[:,off:off+W,:3]*(cl[:,off:off+W,3:4]/255)
    pulse=0.75+0.25*math.sin(t*1.6); f=f+gl*0.55*pulse
    for x,y,s,ph in STARS:
        al=0.35+0.65*(0.5+0.5*math.sin(t*2.2+ph)); f[y:y+s,x:x+s]=f[y:y+s,x:x+s]*(1-al)+255*al
    return comp(f,fg,dy=int(6*math.sin(t*1.8)))
def build(items,end,out):
    GAP=0.3;t=0.15;plan=[]
    for a,sp in items: d=dur(a); plan.append((t,d,a,sp)); t+=d+GAP
    endstart=t; total=t+2.2; fps=24; N=int(total*fps)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r',str(fps),'-i','-']
    for _,_,a,_ in plan: cmd+=['-i',a]
    fc=''.join(f'[{i+1}:a]aresample=44100,adelay={int(s*1000)}|{int(s*1000)}[a{i}];' for i,(s,_,_,_) in enumerate(plan))
    fc+=''.join(f'[a{i}]' for i in range(len(plan)))+f'amix=inputs={len(plan)}:normalize=0,apad=whole_dur={total}[aout]'
    cmd+=['-filter_complex',fc,'-map','0:v','-map','[aout]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-b:a','160k','-t',str(total),out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for f in range(N):
        ts=f/fps
        if ts>=endstart: sp=end
        else:
            sp=plan[0][3]
            for (s,d,a,x) in plan:
                if ts>=s-0.15: sp=x
        bg,cl,gl,fg,glc=sp
        p.stdin.write(frame(bg,cl,gl,fg,ts,glc).clip(0,255).astype(np.uint8)[:,:,::-1].tobytes())
    p.stdin.close(); p.wait(); print(out,total)
def sp(theme,seed,*a,**k):
    gc=(130,100,85); return (static_bg(theme,seed),cloud_layer(seed),glow(gc),fg_layer(*a,**k),gc)
