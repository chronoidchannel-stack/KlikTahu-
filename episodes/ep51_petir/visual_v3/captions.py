"""Typography placed directly into the storm image; no paper header or floating tags."""
from __future__ import annotations
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from .palette import W,H,C,font,fit_font,clamp

TITLES={
    "hook":("PETIR BISA","MENYAMBAR LAGI"),
    "stat":("SATU GEDUNG","≈23 SAMBARAN/TAHUN"),
    "mechanism":("JALUR DARI AWAN","BERTEMU STREAMER"),
    "repeat":("BADAI BERBEDA","TITIK YANG SAMA"),
    "flicker":("SATU KILATAN","BANYAK STROKE"),
    "safety":("DENGAR GUNTUR?","MASUK SEKARANG"),
}
CAPTIONS={
    "hook":[(0.00,3.55,"Katanya petir tak pernah menyambar","tempat yang sama dua kali."),
            (3.55,5.55,"Itu mitos.","")],
    "stat":[(5.55,11.41,"Gedung Empire State di New York","rata-rata tersambar sekitar 23 kali setahun.")],
    "mechanism":[(11.41,13.10,"Kenapa bisa berulang?",""),
                  (13.10,18.40,"Saat jalur listrik dari awan mendekati tanah,","benda tinggi terisolasi dapat memicu percikan ke atas."),
                  (18.40,22.32,"Jika percikan bertemu jalur dari awan,","sambaran terjadi.")],
    "repeat":[(22.32,26.15,"Karena tinggi dan posisinya tetap,","bangunan bisa tersambar lagi"),
              (26.15,29.59,"saat badai berbeda.","Bukan kepastian—hanya lebih mungkin.")],
    "flicker":[(29.59,32.75,"Satu kilatan juga bisa berkedip:",""),
               (32.75,36.70,"beberapa stroke dapat memakai","kanal listrik yang sama."),
               (36.70,39.81,"Logam menghantarkan listrik;","bukan menarik petir.")],
    "safety":[(39.81,43.20,"Kalau terdengar guntur, segera masuk","ke bangunan kokoh"),
              (43.20,46.49,"atau kendaraan beratap keras.","Jangan berlindung di bawah pohon.")],
}


def top_vignette():
    y,x=np.mgrid[0:510,0:W].astype(np.float32)
    vertical=np.exp(-y/360)
    lateral=np.clip(1-.10*((x-W*.45)/(W*.75))**2,.72,1)
    alpha=np.uint8(np.clip(vertical*lateral*116,0,116))
    rgba=np.zeros((510,W,4),np.uint8); rgba[...,:3]=np.array([3,7,13],np.uint8); rgba[...,3]=alpha
    return Image.fromarray(rgba,"RGBA")

_TOP=top_vignette()


def title_layer(kind):
    layer=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer,"RGBA")
    shadow=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow,"RGBA")
    d.text((59,35),"KlikTahu",font=font(25,"semi"),fill=(229,237,243,220),anchor="lt")
    line1,line2=TITLES[kind]
    f1=fit_font(d,line1,930,56,"bold",42)
    f2=fit_font(d,line2,930,53,"bold",40)
    sd.text((61,91),line1,font=f1,fill=(0,0,0,142),anchor="lt")
    sd.text((61,161),line2,font=f2,fill=(0,0,0,142),anchor="lt")
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    d=ImageDraw.Draw(layer,"RGBA")
    d.text((58,88),line1,font=f1,fill=C["white"],anchor="lt")
    d.text((58,158),line2,font=f2,fill=C["accent"],anchor="lt")
    return layer


def caption_for(kind,t):
    for a,b,l1,l2 in CAPTIONS[kind]:
        if a<=t<b or (kind=="safety" and t>=b and b==46.49): return l1,l2
    return CAPTIONS[kind][-1][2:]


def _fit_size(draw,text,size,max_width=958):
    while size>30 and draw.textlength(text,font=font(size,"semi"))>max_width: size-=1
    return size


def _caption_line(draw,x,y,text,size):
    accents=("mitos","23","percikan","berbeda","stroke","Logam","guntur","pohon")
    key=next((w for w in accents if w.lower() in text.lower()),None)
    if not key:
        draw.text((x,y),text,font=font(size,"semi"),fill=C["white"],anchor="lt"); return
    idx=text.lower().find(key.lower()); before=text[:idx]; hit=text[idx:idx+len(key)]; after=text[idx+len(key):]
    f=font(size,"semi"); fb=font(size,"bold")
    draw.text((x,y),before,font=f,fill=C["white"],anchor="lt")
    x+=draw.textlength(before,font=f)
    draw.text((x,y),hit,font=fb,fill=C["accent"],anchor="lt")
    x+=draw.textlength(hit,font=fb)
    draw.text((x,y),after,font=f,fill=C["white"],anchor="lt")


def caption_layer(kind,t,source_note=None):
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    # A feathered exposure falloff, not a caption panel.
    y0=1390
    yy=np.arange(H-y0,dtype=np.float32)[:,None]
    alpha=np.clip((yy/360)**1.55*202,0,212).astype(np.uint8)
    rgba=np.zeros((H-y0,W,4),np.uint8); rgba[...,:3]=np.array([3,7,13],np.uint8); rgba[...,3]=alpha
    layer.alpha_composite(Image.fromarray(rgba,"RGBA"),(0,y0))
    l1,l2=caption_for(kind,t)
    base=39 if max(len(l1),len(l2))<48 else 36
    size1=_fit_size(ImageDraw.Draw(layer),l1,base)
    size2=_fit_size(ImageDraw.Draw(layer),l2,base) if l2 else size1
    shadow=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow,"RGBA")
    sd.text((60,1494),l1,font=font(size1,"semi"),fill=(0,0,0,142),anchor="lt")
    if l2: sd.text((60,1554),l2,font=font(size2,"semi"),fill=(0,0,0,142),anchor="lt")
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2.4)))
    d=ImageDraw.Draw(layer,"RGBA")
    _caption_line(d,58,1492,l1,size1)
    if l2: _caption_line(d,58,1552,l2,size2)
    if source_note:
        d.text((60,1640),source_note,font=font(20,"medium"),fill=(183,197,208,225),anchor="lt")
    return layer


def apply_text(im,kind,t,source_note=None):
    im.alpha_composite(_TOP,(0,0))
    im.alpha_composite(title_layer(kind))
    im.alpha_composite(caption_layer(kind,t,source_note))
    return im
