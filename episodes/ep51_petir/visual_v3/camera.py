"""Slow lens push/pan over one continuous wet city environment."""
from __future__ import annotations
import math
from PIL import Image
from .palette import W,H,C,clamp,smooth


def apply_camera(im,t,start,end,index):
    p=clamp((t-start)/max(.01,end-start))
    z0=(1.012,1.018,1.022,1.028,1.045,1.012)[index]
    z1=(1.038,1.034,1.058,1.055,1.078,1.032)[index]
    z=z0+(z1-z0)*smooth(p)
    dx=5*math.sin(p*math.pi*1.25+index*.7)
    dy=5*math.sin(p*math.pi+index*.35)
    nw,nh=round(W*z),round(H*z)
    larger=im.resize((nw,nh),Image.Resampling.BICUBIC)
    x=round((nw-W)*.5+dx); y=round((nh-H)*.5+dy)
    return larger.crop((x,y,x+W,y+H))
