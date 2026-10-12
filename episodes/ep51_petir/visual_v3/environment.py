"""Layered, textured city and street-level shelter environments, painted procedurally."""
from __future__ import annotations
import math,random
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from .palette import W,H,C


def _field(w,h,seed,grids=((8,8,.55),(18,16,.28),(46,32,.12),(96,64,.05))):
    rng=np.random.default_rng(seed); out=np.zeros((h,w),np.float32); total=0.
    for i,(cols,rows,weight) in enumerate(grids):
        coarse=rng.normal(0,1,(rows,cols)).astype(np.float32)
        layer=np.asarray(Image.fromarray(coarse,"F").resize((w,h),Image.Resampling.BICUBIC),np.float32)
        out+=layer*weight; total+=weight
    out/=max(total,1e-6)
    return (out-out.mean())/(out.std()+1e-6)


def _poly_surface(im,points,top,bottom,seed=0,side_light=0.0,grain=1.2):
    """Matte, softly textured vertical material clipped to an architectural polygon."""
    xs=[p[0] for p in points]; ys=[p[1] for p in points]
    x0=max(0,int(min(xs))); y0=max(0,int(min(ys)))
    x1=min(W,int(max(xs))+2); y1=min(H,int(max(ys))+2)
    if x1<=x0 or y1<=y0: return
    w,h=x1-x0,y1-y0
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    q=(yy/max(1,h-1))[...,None]
    c0=np.asarray(top,np.float32); c1=np.asarray(bottom,np.float32)
    arr=c0[None,None,:]*(1-q)+c1[None,None,:]*q
    arr+=side_light*((xx/max(1,w-1))-.5)[...,None]*np.array([1.0,1.1,1.3],np.float32)[None,None,:]
    if grain:
        tex=_field(w,h,seed,((7,9,.56),(17,23,.29),(55,78,.15)))
        arr+=tex[...,None]*np.array([grain*.84,grain,grain*1.13],np.float32)[None,None,:]
    mask=Image.new("L",(w,h),0)
    d=ImageDraw.Draw(mask)
    local=[(int(round(x-x0)),int(round(y-y0))) for x,y in points]
    d.polygon(local,fill=255)
    rgba=np.zeros((h,w,4),np.uint8)
    rgba[...,:3]=np.uint8(np.clip(arr,0,255)); rgba[...,3]=np.asarray(mask)
    im.alpha_composite(Image.fromarray(rgba,"RGBA"),(x0,y0))


def _building(im,left,right,top,bottom,seed,depth=22,lit_fraction=.12,far=False):
    rng=random.Random(seed)
    width=right-left
    top_in=max(2,int(width*.035)); bottom_in=max(0,int(width*.012))
    front=[(left+top_in,top),(right-top_in,top+int(width*.01)),
           (right-bottom_in,bottom),(left+bottom_in,bottom)]
    side=[(right-top_in,top+int(width*.01)),(right+depth,top+int(width*.04)),
          (right+depth,bottom-18),(right-bottom_in,bottom)]
    shade=rng.randint(-4,8)
    _poly_surface(im,front,(22+shade,32+shade,45+shade),(13+shade,21+shade,32+shade),seed,side_light=6,grain=2.65)
    _poly_surface(im,side,(13+shade,21+shade,33+shade),(7+shade,13+shade,23+shade),seed+1,side_light=-3,grain=1.85)
    d=ImageDraw.Draw(im,"RGBA")
    # Roof parapet and wet roof edge, mostly lost in haze on distant blocks.
    roof=(100,125,146,65 if far else 110)
    d.line((front[0][0],top,front[1][0],front[1][1]),fill=roof,width=2 if far else 3)
    if not far:
        d.line((left+8,top+22,right-10,top+22),fill=(105,124,143,54),width=1)
        for xx in range(left+16,right-12,34):
            d.line((xx,top+32,xx,bottom-18),fill=(103,124,145,22),width=1)

    # Recessed, irregularly occupied window grid, tapered with the facade perspective.
    step_x=max(13,int(width/(11 if far else 13)))
    step_y=24 if far else 27
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,"RGBA")
    for row,y in enumerate(range(top+26,bottom-18,step_y)):
        q=(y-top)/max(1,bottom-top)
        inset=int(top_in*(1-q)+bottom_in*q)
        for col,x in enumerate(range(left+inset+10,right-inset-8,step_x)):
            win_w=max(4,min(9,step_x-5)); win_h=11 if far else 15
            roll=rng.random()
            if roll<lit_fraction:
                if roll<lit_fraction*.68:
                    rgb=(255,189+rng.randint(-14,14),105+rng.randint(-10,18)); a=rng.randint(112,195)
                else:
                    rgb=(126,172,205); a=rng.randint(60,125)
                d.rectangle((x,y,x+win_w,y+win_h),fill=(5,12,22,205))
                d.rectangle((x+1,y+1,x+win_w-1,y+win_h-1),fill=(*rgb,a))
                gd.rectangle((x-3,y-4,x+win_w+3,y+win_h+5),fill=(*rgb,int(a*.19)))
                # One-pane highlights, not uniformly lit checkerboard windows.
                if rng.random()<.55:
                    d.line((x+2,y+2,x+win_w-2,y+2),fill=(230,240,246,34),width=1)
            else:
                d.rectangle((x,y,x+win_w,y+win_h),fill=(5,12,23,182))
                if rng.random()<.48:
                    d.rectangle((x+1,y+1,x+win_w-1,y+win_h-1),fill=(25,43,61,rng.randint(65,120)))
        # Dark floor slabs and fine structural mullions make the grid architectural.
        d.line((left+inset,y+step_y-2,right-inset,y+step_y-2),fill=(2,7,14,70 if not far else 38),width=1)
    if not far:
        for x in range(left+22,right-10,step_x*3):
            d.line((x,top+12,x,bottom-10),fill=(116,139,158,28),width=1)
    # Bloom is kept under the window glass; it shares the city haze.
    glow=glow.filter(ImageFilter.GaussianBlur(8 if far else 10))
    im.alpha_composite(glow)
    if not far:
        streak=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(streak,"RGBA")
        for _ in range(max(3,width//42)):
            sx=rng.randint(left+8,right-8); sy=rng.randint(top+35,max(top+36,bottom-130))
            length=rng.randint(55,190); dx=rng.randint(-3,3)
            sd.line((sx,sy,sx+dx,min(bottom-8,sy+length)),
                    fill=(154,181,199,rng.randint(7,23)),width=rng.choice((1,1,2)))
        im.alpha_composite(streak.filter(ImageFilter.GaussianBlur(.8)))


def _tier(im,cx,y0,y1,half_top,half_bottom,seed,side_depth=25):
    """One real setback band of a stepped high-rise, with separate facade and side plane."""
    left0=cx-half_top; right0=cx+half_top
    left1=cx-half_bottom; right1=cx+half_bottom
    front=[(left0,y0),(right0,y0),(right1,y1),(left1,y1)]
    side=[(right0,y0),(right0+side_depth,y0+12),(right1+side_depth,y1-5),(right1,y1)]
    _poly_surface(im,front,(37,48,60),(17,27,39),seed,side_light=9,grain=2.4)
    _poly_surface(im,side,(17,27,40),(7,14,24),seed+2,side_light=-5,grain=1.65)
    d=ImageDraw.Draw(im,"RGBA")
    d.line((left0,y0,right0,y0),fill=(141,157,170,92),width=2)
    d.line((left0+3,y1-1,right1,y1-1),fill=(2,7,13,170),width=4)
    step_x=16; step_y=24
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,"RGBA")
    for row,y in enumerate(range(y0+17,y1-9,step_y)):
        q=(y-y0)/max(1,y1-y0)
        half=half_top+(half_bottom-half_top)*q
        l=int(cx-half+8); r=int(cx+half-8)
        for x in range(l,r,step_x):
            roll=random.Random(seed+row*1307+x).random()
            ww=7; hh=13
            if roll<.20:
                if roll<.13:
                    rgb=(255,194,111); a=175
                else:
                    rgb=(142,181,208); a=100
                d.rectangle((x,y,x+ww,y+hh),fill=(4,10,18,220))
                d.rectangle((x+1,y+1,x+ww-1,y+hh-1),fill=(*rgb,a))
                gd.rectangle((x-3,y-4,x+ww+3,y+hh+4),fill=(*rgb,35))
            else:
                d.rectangle((x,y,x+ww,y+hh),fill=(7,15,25,160))
        d.line((int(cx-half+4),y+step_y-3,int(cx+half-4),y+step_y-3),fill=(3,8,15,78),width=1)
    for off in (-.58,-.31,0,.31,.58):
        x0=cx+half_top*off; x1=cx+half_bottom*off
        d.line((x0,y0+8,x1,y1-4),fill=(142,160,174,45 if off<0 else 24),width=2)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
    # Uneven sky reflections run down the panes, breaking the printed-grid appearance.
    reflections=Image.new("RGBA",(W,H),(0,0,0,0)); rd=ImageDraw.Draw(reflections,"RGBA")
    rr=random.Random(seed+801); start_y,end_y=y0,y1
    for _ in range(21):
        q=rr.uniform(-.88,.88); x0=cx+half_top*q; x1=cx+half_bottom*q
        sy=rr.randint(start_y+14,max(start_y+15,end_y-80)); length=rr.randint(80,300)
        rd.line((x0,sy,x1,min(end_y-6,sy+length)),fill=(164,190,205,rr.randint(6,19)),width=rr.choice((1,2,3)))
    im.alpha_composite(reflections.filter(ImageFilter.GaussianBlur(1.5)))


def _draw_esb(im,cx=642,seed=712):
    """Empire-State-inspired Art Deco setbacks and mast; no triangular/pyramid silhouette."""
    # The long shaft is broad and vertical; the stepped crown recedes in distinct setbacks.
    tiers=[(960,1550,169,182),(800,960,142,169),(725,800,102,142),(696,725,58,102)]
    for i,(y0,y1,ht,hb) in enumerate(tiers):
        _tier(im,cx,y0,y1,ht,hb,seed+i*9,side_depth=max(13,int(ht*.20)))
    d=ImageDraw.Draw(im,"RGBA")
    # Antenna mast and a dim, rain-softened warning beacon.
    d.line((cx,698,cx,587),fill=(170,185,197,160),width=4)
    d.line((cx-1,692,cx-1,594),fill=(224,231,235,148),width=1)
    d.ellipse((cx-4,581,cx+4,589),fill=(255,135,94,185))
    # Narrow vertical crown ribs and a few fine horizontal terrace courses.
    for dx in range(-30,31,10):
        d.line((cx+dx,706,cx+dx,776),fill=(142,158,174,80 if dx<0 else 40),width=1)
    d.line((cx-47,745,cx+47,745),fill=(149,165,179,84),width=2)
    d.line((cx-78,814,cx+78,814),fill=(131,149,164,64),width=2)
    # Rain-darkened vertical tracery through the main shaft.
    for dx in range(-128,129,32):
        d.line((cx+dx*.48,962,cx+dx,1545),fill=(117,139,157,25),width=2)


def _draw_city_haze(im,seed=11):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    noise=_field(W,H,seed,((5,8,.65),(13,18,.35)))
    density=np.exp(-((yy-1320)/280)**2)*np.clip(.12+(noise+1)*.12,0,.35)
    arr=np.zeros((H,W,4),np.uint8)
    arr[...,:3]=np.array([133,151,164],np.uint8)
    arr[...,3]=np.uint8(density*255)
    im.alpha_composite(Image.fromarray(arr,"RGBA"))


def _draw_wet_street(im,seed=19):
    y0=1450
    yy,xx=np.mgrid[0:H-y0,0:W].astype(np.float32)
    q=yy/max(1,H-y0)
    noise=_field(W,H-y0,seed,((14,18,.58),(42,54,.27),(100,110,.15)))
    top=np.array([16,23,30],np.float32); bottom=np.array([5,9,15],np.float32)
    rgb=top[None,None,:]*(1-q[...,None])+bottom[None,None,:]*q[...,None]
    rgb+=noise[...,None]*np.array([1.5,1.7,1.9],np.float32)[None,None,:]
    alpha=np.full((H-y0,W),255,np.uint8)
    im.alpha_composite(Image.fromarray(np.dstack((np.uint8(np.clip(rgb,0,255)),alpha)),"RGBA"),(0,y0))
    refl=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(refl,"RGBA")
    rng=random.Random(seed+2)
    # Stretched amber and steel reflections are broken by puddles, never neat mirror columns.
    for i in range(68):
        x=rng.randrange(25,W-25); y=rng.randrange(y0+8,H-60)
        length=rng.randint(24,210); width=rng.choice([1,2,3,5,8])
        if x<400: color=(255,183,105,rng.randint(9,29))
        else: color=(139,175,205,rng.randint(7,22))
        d.line((x,y,x+rng.randint(-7,7),min(H-1,y+length)),fill=color,width=width)
    for _ in range(33):
        x=rng.randrange(20,W-20); y=rng.randrange(y0+30,H-20)
        rx=rng.randint(8,42); ry=rng.randint(2,7)
        d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(102,128,148,rng.randint(5,18)))
    refl=refl.filter(ImageFilter.GaussianBlur(5.5))
    im.alpha_composite(refl)
    d=ImageDraw.Draw(im,"RGBA")
    d.line((0,y0,W,y0),fill=(117,137,151,40),width=2)
    # Curb lines recede into the rain-dark street.
    d.line((0,1510,450,1476),fill=(99,116,129,33),width=2)
    d.line((W,1510,640,1476),fill=(99,116,129,28),width=2)


def make_city_arch(seed=32):
    """A continuous midtown storm skyline with atmospheric depth and a stepped landmark."""
    im=Image.new("RGBA",(W,H),(0,0,0,0)); rng=random.Random(seed)
    # Far skyline first; soften it slightly so it recedes into the same humid air as the clouds.
    far=Image.new("RGBA",(W,H),(0,0,0,0)); x=-45; idx=0
    while x<W+30:
        w=rng.randint(70,145); h=rng.randint(230,620); top=1515-h
        _building(far,x,x+w,top,1550,seed+idx*13,depth=rng.randint(9,23),lit_fraction=.075,far=True)
        x+=w-rng.randint(4,16); idx+=1
    im.alpha_composite(far.filter(ImageFilter.GaussianBlur(1.35)))
    # Mid-distance towers form a softer city canyon around the crisp landmark.
    mid_layer=Image.new("RGBA",(W,H),(0,0,0,0))
    mid=[(-38,162,880,1535),(104,252,1080,1542),(804,994,925,1540),(946,1135,1070,1530),
         (254,372,1025,1540),(766,860,1055,1538)]
    for i,(l,r,t,b) in enumerate(mid):
        _building(mid_layer,l,r,t,b,seed+90+i*23,depth=27 if r-l>120 else 18,lit_fraction=.12,far=False)
    im.alpha_composite(mid_layer.filter(ImageFilter.GaussianBlur(.55)))
    _draw_esb(im,642,seed+180)
    # A dark near-foreground roofline anchors the skyline before wet pavement.
    d=ImageDraw.Draw(im,"RGBA")
    d.polygon([(0,1422),(110,1390),(224,1428),(340,1388),(436,1415),(535,1382),(658,1416),(772,1386),(890,1422),(1000,1388),(W,1412),(W,1580),(0,1580)],fill=(8,14,22,226))
    for x in range(0,W,116):
        d.line((x,1420+rng.randint(-14,8),x+70,1415+rng.randint(-14,10)),fill=(63,78,91,45),width=2)
    _draw_wet_street(im,seed+231)
    _draw_city_haze(im,seed+304)
    # Haze is underneath foreground rain but above far façades.
    return im


def _textured_tree_canopy(cx,cy,rx,ry,seed):
    w,h=rx*2,ry*2
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    nx=(xx-rx)/rx; ny=(yy-ry)/ry
    f=_field(w,h,seed,((8,9,.53),(19,24,.30),(50,58,.17)))
    angle=np.arctan2(ny,nx)
    radial=np.sqrt(nx*nx+ny*ny)+.085*f+.035*np.sin(7*angle+f)
    mask=np.clip((1-radial)*18,0,1)
    shade=np.clip(.62-.20*ny+.13*np.sin(angle*2)+f*.045,0,1)
    dark=np.array(C["tree_shadow"],np.float32); mid=np.array(C["tree_mid"],np.float32); hi=np.array(C["tree_lit"],np.float32)
    base=dark[None,None,:]*(1-shade[...,None])+mid[None,None,:]*shade[...,None]
    highlight=np.clip((f-.45)*.12,0,.1)
    base=base*(1-highlight[...,None])+hi[None,None,:]*highlight[...,None]
    rng=np.random.default_rng(seed+2)
    fleck=rng.normal(0,1,(h,w,1)).astype(np.float32)*1.1
    base+=fleck
    alpha=np.uint8(np.clip(mask*245,0,245))
    rgba=np.uint8(np.dstack((np.clip(base,0,255),alpha)))
    return Image.fromarray(rgba,"RGBA").filter(ImageFilter.GaussianBlur(1.2)),(cx-rx,cy-ry)


def draw_tree(im,cx=220,base=1490,seed=41):
    """Foreground tree with bark, branching structure and continuous textured foliage."""
    d=ImageDraw.Draw(im,"RGBA")
    # Bark is a tapered, shaded form rather than a flat icon stroke.
    trunk=[(cx-18,base+14),(cx+18,base+14),(cx+11,base-265),(cx+2,base-420),(cx-8,base-414),(cx-13,base-280)]
    _poly_surface(im,trunk,(64,57,49),(31,29,28),seed,side_light=6,grain=4.2)
    branches=[((cx,base-228),(cx-48,base-360),(cx-122,base-454)),
              ((cx+4,base-260),(cx+62,base-390),(cx+139,base-477)),
              ((cx-1,base-318),(cx-26,base-492),(cx-42,base-590)),
              ((cx+2,base-337),(cx+57,base-503),(cx+89,base-600)),
              ((cx-3,base-283),(cx-120,base-390),(cx-170,base-430))]
    for a,b,c in branches:
        d.line((a,b,c),fill=(46,43,38,230),width=12,joint="curve")
        d.line((a[0]-2,a[1],b[0]-2,b[1]),fill=(104,91,70,95),width=2)
    canopy,pos=_textured_tree_canopy(cx,base-530,205,184,seed+9)
    im.alpha_composite(canopy,pos)
    # Irregular leaf flecks break the crown into small, storm-lit clusters.
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl,"RGBA")
    rng=random.Random(seed+15)
    for _ in range(1050):
        x=rng.randint(cx-198,cx+198); y=rng.randint(base-710,base-374)
        if ((x-cx)/202)**2+((y-(base-530))/182)**2<.98:
            light=max(0,min(1,.55-(y-(base-530))/500+(x-cx)/900))
            if rng.random()<.21+light*.23:
                color=(82,109,83,rng.randint(26,61))
            else:
                color=(8,22,20,rng.randint(22,58))
            w=rng.choice((2,3,4,5)); h=rng.choice((1,2,3))
            gd.ellipse((x,y,x+w,y+h),fill=color)
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(.45)))
    bark=Image.new("RGBA",(W,H),(0,0,0,0)); bd=ImageDraw.Draw(bark,"RGBA")
    for _ in range(28):
        bx=rng.randint(cx-10,cx+10); by=rng.randint(base-250,base-24)
        bd.line((bx,by,bx+rng.randint(-3,3),min(base+5,by+rng.randint(18,72))),
                fill=(130,112,88,rng.randint(15,46)),width=1)
    im.alpha_composite(bark)


def draw_shelter_entry(im,seed=51):
    """Street-level, recessed building entrance with masonry and glazed door."""
    # Tall masonry facade occupies the right third, tied to the skyline's same wet material.
    wall=[(535,750),(W,680),(W,1535),(535,1535)]
    _poly_surface(im,wall,(39,47,54),(17,24,32),seed,side_light=5,grain=2.8)
    d=ImageDraw.Draw(im,"RGBA"); rng=random.Random(seed)
    # Fine masonry joints / cladding seams; low contrast keeps them natural at phone size.
    for y in range(780,1535,68):
        d.line((540,y,1080,y-45),fill=(3,8,14,65),width=2)
        for x in range(566+(y//68%2)*34,1080,68):
            d.line((x,y,x-5,y+65),fill=(133,143,149,19),width=1)
    # Upper windows carry the same cool rain reflections and warm interior light.
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,"RGBA")
    for row,y in enumerate((830,965,1100)):
        for col,x in enumerate((630,760,890,1020)):
            ww=54; hh=66
            d.rectangle((x,y,x+ww,y+hh),fill=(5,12,19,230),outline=(115,130,140,95),width=2)
            color=(255,191,112,125) if (row+col)%4==0 else (40,64,82,168)
            d.rectangle((x+5,y+5,x+ww-5,y+hh-5),fill=(*color[:3],color[3]))
            d.line((x+ww*.58,y+4,x+ww*.58,y+hh-4),fill=(135,151,164,65),width=2)
            if color[0]>200: gd.rectangle((x-9,y-9,x+ww+9,y+hh+9),fill=(255,174,91,26))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
    # Recessed entrance, soffit, drip edge, jambs and glass create real depth.
    d=ImageDraw.Draw(im,"RGBA")
    d.polygon([(676,1214),(913,1186),(925,1534),(676,1534)],fill=(5,10,16,245))
    d.polygon([(662,1191),(910,1162),(925,1190),(676,1220)],fill=(51,61,68,255))
    d.line((667,1191,914,1162),fill=(154,169,176,130),width=3)
    d.rectangle((708,1231,866,1528),fill=(16,27,37,255),outline=(143,159,169,170),width=3)
    d.rectangle((720,1245,854,1492),fill=(20,43,57,230))
    d.line((787,1247,787,1490),fill=(122,151,170,95),width=2)
    d.line((723,1497,852,1497),fill=(204,169,119,145),width=2)
    d.ellipse((839,1373,846,1380),fill=(255,205,133,225))
    # Warm interior light falls softly over the wet threshold, not as a flat yellow rectangle.
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    pool=np.exp(-(((xx-786)/180)**2+((yy-1472)/170)**2)*2.4)
    arr=np.zeros((H,W,4),np.uint8); arr[...,:3]=np.array([255,173,91],np.uint8)
    arr[...,3]=np.uint8(np.clip(pool*28,0,28))
    im.alpha_composite(Image.fromarray(arr,"RGBA"))
    # Door glazing comes back over the warm spill.
    d=ImageDraw.Draw(im,"RGBA")
    d.rectangle((720,1245,854,1492),fill=(31,50,60,95))
    d.line((727,1252,727,1484),fill=(207,221,228,35),width=2)
    d.line((845,1250,845,1484),fill=(0,5,12,95),width=3)


def draw_person(im,x=594,base=1500,progress=.0):
    """Rain-dark walking figure approaching the recessed entrance."""
    q=max(0,min(1,progress)); x=x+int(82*q)
    d=ImageDraw.Draw(im,"RGBA"); stride=math.sin(q*math.pi*2)*9
    # Narrow ground shadow and reflection first.
    d.ellipse((x-34,base-3,x+32,base+9),fill=(2,5,10,140))
    d.line((x,base+4,x+8,base+58),fill=(138,163,178,42),width=8)
    # Coat silhouette with light from the open doorway outlining the right edge.
    d.ellipse((x-13,base-178,x+15,base-150),fill=(35,34,32,255))
    d.polygon([(x-13,base-150),(x+13,base-150),(x+25,base-68),(x+18,base-56),
               (x-20,base-56),(x-26,base-76)],fill=(27,39,47,255))
    d.line((x+11,base-143,x+20,base-77),fill=(153,172,183,90),width=2)
    # A bent arm reaches for the doorway; limbs remain understated and proportionate.
    d.line((x-12,base-128,x-34,base-78),fill=(31,40,46,255),width=10)
    d.line((x+12,base-128,x+37,base-155),fill=(41,48,51,255),width=9)
    d.line((x-7,base-58,x-16+stride,base-5),fill=(20,27,32,255),width=10)
    d.line((x+8,base-58,x+16-stride,base-5),fill=(17,23,28,255),width=10)
    d.line((x-1,base-57,x-7+stride,base-8),fill=(135,155,168,74),width=2)
    # Shoulder and head catch a restrained warm rim from the vestibule.
    d.arc((x-16,base-181,x+18,base-146),190,340,fill=(192,155,117,130),width=2)
