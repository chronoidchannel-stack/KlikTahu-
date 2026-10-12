"""Textured return-stroke channels with local bloom and branching leaders."""
from __future__ import annotations
import math,random
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from .palette import W,H,C,clamp


def _smooth_path(start,end,seed,segments=12,jitter=23):
    rng=np.random.default_rng(seed)
    raw=rng.normal(0,1,segments+1)
    corr=np.convolve(np.pad(raw,(2,2),mode="edge"),[.08,.20,.44,.20,.08],mode="valid")
    corr=(corr-corr.mean())/(corr.std()+1e-6)
    pts=[]
    for i in range(segments+1):
        q=i/segments
        # A long, slightly drifting trunk with a few sharper electrical branches.
        x=start[0]+(end[0]-start[0])*q
        y=start[1]+(end[1]-start[1])*q
        off=0 if i in (0,segments) else float(corr[i])*jitter
        pts.append((int(round(x+off)),int(round(y))))
    return pts


def build_lightning(start,end,seed=12,branches=True,jitter=22):
    main=_smooth_path(start,end,seed,12,jitter)
    paths=[main]
    if branches:
        rng=random.Random(seed+57)
        for idx,side in ((3,-1),(6,1),(9,-1)):
            x,y=main[idx]
            run=rng.randint(90,178); fall=rng.randint(65,150)
            mid=(x+side*rng.randint(32,73),y+rng.randint(30,76))
            stop=(x+side*run,y+fall)
            branch=[main[idx],mid]
            branch.extend(_smooth_path(mid,stop,seed+idx,4,12)[1:])
            paths.append(branch)
    return paths


def _paint_path(draw,points,scale,width,alpha):
    pts=[(int(round(x*scale)),int(round(y*scale))) for x,y in points]
    if len(pts)>1:
        draw.line(pts,fill=int(alpha),width=max(1,int(round(width*scale))),joint="curve")
        for x,y in pts[1:-1]:
            r=max(1,int(round(width*scale*.48)))
            draw.ellipse((x-r,y-r,x+r,y+r),fill=int(alpha))


class LightningBolt:
    """Cached, multi-radius lightning render; each frame only selects a pulse tier."""
    def __init__(self,paths):
        self.paths=paths
        pts=[p for path in paths for p in path]
        pad=96
        self.left=max(0,min(x for x,y in pts)-pad)
        self.top=max(0,min(y for x,y in pts)-pad)
        right=min(W,max(x for x,y in pts)+pad)
        bottom=min(H,max(y for x,y in pts)+pad)
        self.size=(max(1,right-self.left),max(1,bottom-self.top))
        s=2; size=(self.size[0]*s,self.size[1]*s)
        outer=Image.new("L",size,0); mid=Image.new("L",size,0); core=Image.new("L",size,0)
        od=ImageDraw.Draw(outer); md=ImageDraw.Draw(mid); cd=ImageDraw.Draw(core)
        for i,path in enumerate(paths):
            local=[(x-self.left,y-self.top) for x,y in path]
            if i==0:
                _paint_path(od,local,s,45,108)
                _paint_path(md,local,s,19,228)
                _paint_path(cd,local,s,6,255)
            else:
                _paint_path(od,local,s,25,86)
                _paint_path(md,local,s,10,188)
                _paint_path(cd,local,s,3,224)
        outer=outer.filter(ImageFilter.GaussianBlur(24)).resize(self.size,Image.Resampling.LANCZOS)
        mid=mid.filter(ImageFilter.GaussianBlur(5.2)).resize(self.size,Image.Resampling.LANCZOS)
        core=core.resize(self.size,Image.Resampling.LANCZOS)
        self.tiers=[]
        for gain in (.32,.66,1.0):
            result=Image.new("RGBA",self.size,(0,0,0,0))
            for mask,color,factor in ((outer,(52,111,169),.55),(mid,(130,190,228),.78),(core,C["lightning"],.98)):
                alpha=mask.point(lambda v:int(v*gain*factor))
                layer=Image.new("RGBA",self.size,tuple(color)+(0,)); layer.putalpha(alpha)
                result.alpha_composite(layer)
            self.tiers.append(result)

    def draw(self,im,strength=1.0):
        if strength<.055:return
        tier=0 if strength<.38 else 1 if strength<.77 else 2
        im.alpha_composite(self.tiers[tier],(self.left,self.top))


def draw_leader(im,paths,progress=.7):
    progress=clamp(progress)
    if progress<=0:return
    low=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(low,"RGBA")
    high=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(high,"RGBA")
    for i,path in enumerate(paths):
        if i and progress<.36:continue
        n=max(2,min(len(path),int(1+(len(path)-1)*progress)))
        points=path[:n]
        ld.line(points,fill=(84,145,192,70 if i else 118),width=10 if not i else 5,joint="curve")
        hd.line(points,fill=(189,221,242,130 if i else 198),width=2 if i else 3,joint="curve")
    im.alpha_composite(low.filter(ImageFilter.GaussianBlur(7)))
    im.alpha_composite(high)


def draw_streamer(im,start,end,progress=.7,seed=14):
    if progress<=0:return
    path=_smooth_path(start,end,seed,7,8)
    n=max(2,min(len(path),int(1+(len(path)-1)*clamp(progress))))
    pts=path[:n]
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,"RGBA")
    gd.line(pts,fill=(135,195,232,85),width=25,joint="curve")
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    core=Image.new("RGBA",(W,H),(0,0,0,0)); cd=ImageDraw.Draw(core,"RGBA")
    cd.line(pts,fill=(207,234,250,225),width=4,joint="curve")
    cd.line(pts,fill=(250,253,255,240),width=1,joint="curve")
    im.alpha_composite(core)
