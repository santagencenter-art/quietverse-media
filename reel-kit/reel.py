import sys,subprocess; sys.path.insert(0,'.')
from compose import *
U='/mnt/user-data/uploads/projects/'
TH=U+'Thu 12 Nov flow with the 5 clips/New tts node (%d).mp3'; SA=U+'Sat 14 Nov flow with the other 4 clips/New tts node%s.mp3'
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
def scene(who,char,text,seed,ch_h=760,extra=None,bubble_size=58):
    blue=(who=='shiva'); gc=(70,120,180) if blue else (130,100,85)
    im=bg(1080,1920,gc,1100,seed,blue); wm(im,150)
    a='left' if who=='man' else 'right'
    bubble(im,text,who,80 if a=='left' else 1000,300,maxw=780,align=a,size=bubble_size)
    put(im,char,540,bottom=1560,height=ch_h)
    if extra: extra(im)
    return np.array(im.convert('RGB'))[:,:,::-1]
def endcard(l1,l2,seed):
    im=bg(1080,1920,(130,100,85),900,seed); wm(im,150); d=ImageDraw.Draw(im,'RGBA')
    y=620
    for l in l1: d.text((540,y),l,font=F(FB,78),fill=(255,246,226),anchor='ma'); y+=105
    d.text((540,y+40),l2,font=F(FB,44),fill=(255,203,112),anchor='ma')
    put(im,'man_pray',540,bottom=1920,height=640)
    return np.array(im.convert('RGB'))[:,:,::-1]
def build(name,items,end,outdir):
    # items: (audio,img)
    GAP=0.3; t=0.15; plan=[]
    for a,img in items:
        d=dur(a); plan.append((t,d,a,img)); t+=d+GAP
    endstart=t; total=t+2.2
    fps=24; N=int(total*fps)
    out=outdir+'reel-with-voice.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r',str(fps),'-i','-']
    for _,_,a,_ in plan: cmd+=['-i',a]
    fc=''.join(f'[{i+1}:a]aresample=44100,adelay={int(s*1000)}|{int(s*1000)}[a{i}];' for i,(s,_,_,_) in enumerate(plan))
    fc+=''.join(f'[a{i}]' for i in range(len(plan)))+f'amix=inputs={len(plan)}:normalize=0,apad=whole_dur={total}[aout]'
    cmd+=['-filter_complex',fc,'-map','0:v','-map','[aout]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-b:a','160k','-t',str(total),out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for f in range(N):
        ts=f/fps
        if ts>=endstart: img=end; s0=endstart; sd=2.2
        else:
            img=plan[0][3]; s0=0; sd=plan[0][0]+plan[0][1]+GAP
            for (s,d,a,im) in plan:
                if ts>=s-0.15: img=im; s0=s-0.15; sd=d+GAP+0.15
        z=1.0+0.035*min(1,(ts-s0)/max(sd,0.5))
        h,w=img.shape[:2]; cw,ch=int(w/z),int(h/z); x0=(w-cw)//2; y0=(h-ch)//2
        fr=cv2.resize(img[y0:y0+ch,x0:x0+cw],(w,h),interpolation=cv2.INTER_LINEAR)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print(out,total)
if __name__=='__main__':
    # Thu 12 Nov
    O1=D+'out/2026-11-12_not-holy-reel/'; os.makedirs(O1,exist_ok=True)
    sc=[(TH%4,scene('krishna','krishna',"You do not need to feel holy to hear Me.",31)),
        (TH%5,scene('man','man_full',"I haven't prayed in months. I get angry. I doubt.",32)),
        (TH%6,scene('krishna','krishna_flute',"Come as you are. Doubt, anger, tired. I hear it all.",33)),
        (TH%7,scene('man','man',"Even now?",34,ch_h=600)),
        (TH%8,scene('krishna','krishna',"Especially now.",35))]
    build('holy',sc,endcard(["You don't need to","feel holy to hear Him."],"Follow @thequietverse.ultimate",36),O1)
    # Sat 14 Nov
    O2=D+'out/2026-11-14_raat-ka-sawaal-1-reel/'; os.makedirs(O2,exist_ok=True)
    def clock(im):
        d=ImageDraw.Draw(im,'RGBA'); d.text((540,1640),"2:07 AM",font=F(FB,64),fill=(255,203,112),anchor='ma')
    sc=[(SA%'',scene('man','man_full',"It's two in the morning, and I'm replaying tomorrow's meeting for the third time.",41,extra=clock,bubble_size=54)),
        (SA%' (1)',scene('krishna','krishna',"Tomorrow has not happened yet. Why are you already tired of it?",42)),
        (SA%' (2)',scene('man','man',"Because what if I get it wrong?",43,ch_h=600)),
        (SA%' (3)',scene('krishna','krishna_flute',"Then you learn. Tonight, you only need to sleep.",44))]
    build('raat',sc,endcard(["Raat ka Sawaal","Part 1"],"Follow @thequietverse.ultimate",45),O2)
