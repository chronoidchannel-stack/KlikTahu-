"""Volumetric-looking storm clouds, wet atmospheric depth and multi-plane rain."""
from __future__ import annotations
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from .palette import W,H,C


def _value_noise(width,height,seed,cols,rows):
    rng=np.random.default_rng(seed)
    coarse=rng.normal(0,1,(rows,cols)).astype(np.float32)
    return np.asarray(Image.fromarray(coarse,"F").resize((width,height),Image.Resampling.BICUBIC),dtype=np.float32)


def _fbm(width,height,seed):
    fields=[_value_noise(width,height,seed+o*19,c,r) for o,(c,r) in enumerate(((6,8),(13,17),(28,34),(58,68),(116,136)))]
    result=fields[0]*.50+fields[1]*.25+fields[2]*.14+fields[3]*.08+fields[4]*.03
    result=(result-result.mean())/(result.std()+1e-6)
    return result,fields[1],fields[3]


def make_sky(seed=8):
    """Continuous dark sky with a weak city glow and restrained film grain."""
    y,x=np.mgrid[0:H,0:W].astype(np.float32); u=y/(H-1)
    top=np.array(C["night_top"],np.float32); mid=np.array(C["night_mid"],np.float32)
    horizon=np.array(C["night_horizon"],np.float32)
    q=np.clip(u/.64,0,1)[...,None]; q2=np.clip((u-.64)/.36,0,1)[...,None]
    arr=(top[None,None,:]*(1-q)+mid[None,None,:]*q)*(1-q2)+horizon[None,None,:]*q2
    glow=np.exp(-(((x-W*.55)/(W*.48))**2+((y-H*.68)/(H*.19))**2)*2.5)
    arr+=glow[...,None]*np.array([7,8,9],np.float32)[None,None,:]
    vignette=np.clip(1-.17*((x-W*.5)/(W*.72))**2-.11*((y-H*.5)/(H*.82))**2,.65,1)
    arr*=vignette[...,None]
    rng=np.random.default_rng(seed); arr+=rng.normal(0,.42,(H,W,1)).astype(np.float32)
    return Image.fromarray(np.uint8(np.clip(arr,0,255)),"RGB").convert("RGBA")


def _smooth(x):
    x=np.clip(x,0,1); return x*x*(3-2*x)


def _cloud_layer(width,height,seed,top,bottom,opacity):
    field,mid,detail=_fbm(width,height,seed)
    yy,xx=np.mgrid[0:height,0:width].astype(np.float32)
    rng=np.random.default_rng(seed+1107)
    knots=np.linspace(0,width-1,18,dtype=np.float32)
    contour=np.interp(np.arange(width,dtype=np.float32),knots,rng.normal(0,1,len(knots)).astype(np.float32))
    contour=(contour-contour.mean())/(contour.std()+1e-6)
    top_edge=top+contour[None,:]*88+mid*24
    base_edge=bottom+contour[None,:]*104+field*31
    envelope=_smooth((yy-(top_edge-86))/155)*_smooth((base_edge+142-yy)/210)
    # Turbulent density, warped in the vertical direction to avoid a level cloud shelf.
    warped=field+.20*np.sin((yy+mid*78)/132)+.10*detail
    density=_smooth((warped+.22)/.91)*envelope
    density=np.clip(density,0,1)
    gy,gx=np.gradient(warped)
    light_direction=np.clip(.53-gx*.08-gy*.17+(yy<top_edge+126)*.10,0,1)
    height_shade=np.clip(1-(yy/height)*.19,.73,1)
    bright=np.clip(.20+density*.34+light_direction*.40,0,1)*height_shade
    dark=np.array(C["cloud_shadow"],np.float32)[None,None,:]
    lit=np.array(C["cloud_lit"],np.float32)[None,None,:]
    rgb=dark*(1-bright[...,None])+lit*bright[...,None]
    silver=np.array([111,126,141],np.float32)[None,None,:]
    rim=np.exp(-((yy-top_edge-42)/102)**2)*np.clip(.10+light_direction*.22,0,.36)
    rgb=rgb*(1-rim[...,None])+silver*rim[...,None]
    rgb+=detail[...,None]*np.array([.85,1.0,1.2],np.float32)[None,None,:]
    alpha=np.clip(density*opacity*255,0,225).astype(np.uint8)
    rgba=np.uint8(np.dstack((np.clip(rgb,0,255),alpha)))
    return Image.fromarray(rgba,"RGBA").filter(ImageFilter.GaussianBlur(4.2))


class StormAtmosphere:
    """One continuous cloud volume with parallax translation and three rain depths."""
    def __init__(self,seed=149):
        cw=W+360
        cloud=_cloud_layer(cw,H,seed+8,top=260,bottom=1160,opacity=.42)
        self.layers=[(cloud,0,1.45,seed+8)]
        self.rain=self._make_rain(seed+319)

    @staticmethod
    def _make_rain(seed):
        rng=np.random.default_rng(seed); result=[]
        specs=((430,8,17,31,1,0.0),(255,17,32,53,1,.35),(96,31,54,68,2,.9))
        for i,(count,lmin,lmax,alpha,width,blur) in enumerate(specs):
            tile=Image.new("RGBA",(W,H+520),(0,0,0,0)); d=ImageDraw.Draw(tile,"RGBA")
            for _ in range(count):
                x=int(rng.integers(-25,W+25)); y=int(rng.integers(-20,H+500))
                length=int(rng.integers(lmin,lmax+1)); drift=int(rng.integers(-15,-6))
                a=int(rng.integers(max(8,alpha-20),alpha+1))
                d.line((x,y,x+drift,y+length),fill=(174,199,218,a),width=width)
            if blur:tile=tile.filter(ImageFilter.GaussianBlur(blur))
            result.append((tile,3.0+i*4.1,i*113))
        return result

    def clouds(self,im,t,scene_seed=0):
        for layer,y,speed,phase in self.layers:
            span=layer.width-W
            x=int((t*speed+phase*3.7+scene_seed*11)%max(1,span))
            im.alpha_composite(layer.crop((x,0,x+W,layer.height)),(0,y))

    def rain_over(self,im,t):
        for tile,speed,phase in self.rain:
            y=int((t*speed+phase)%520)
            im.alpha_composite(tile.crop((0,y,W,y+H)),(0,0))


def lightning_exposure(im,point,strength,seed=0):
    """Scattered flash exposure on clouds, glass and wet road; surface detail remains visible."""
    if strength<.025:return im
    cx,cy=point; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    cloud=np.exp(-(((xx-cx)/(W*.72))**2+((yy-(cy-145))/(H*.22))**2)*2.4)
    spill=np.exp(-(((xx-cx)/(W*.88))**2+((yy-(cy+210))/(H*.34))**2)*2.2)
    ground=np.clip((yy-H*.63)/(H*.37),0,1)
    field=np.clip((cloud*.38+spill*.16+ground*spill*.24)*strength,0,1)
    arr=np.asarray(im.convert("RGB"),dtype=np.float32)
    arr+=field[...,None]*np.array([55,77,101],np.float32)[None,None,:]
    arr+=field[...,None]*np.array([23,25,27],np.float32)[None,None,:]*strength
    return Image.fromarray(np.uint8(np.clip(arr,0,255)),"RGB").convert("RGBA")
