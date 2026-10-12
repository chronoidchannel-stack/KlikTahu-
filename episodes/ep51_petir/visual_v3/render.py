#!/usr/bin/env python3
"""Integrated, realistic-inspired procedural render of the Petir Short.

The scene is painted from one continuous weather/city environment. Typography
is composited directly over the image; there is no paper banner, poster panel,
or third-party footage. Output from this renderer is intentionally silent.
"""
from __future__ import annotations
import argparse,math,os,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
from .palette import W,H,FPS,DURATION,NFRAMES,C,clamp,smooth,ease_out,SCENES,TRANSITION
from .clouds import StormAtmosphere,make_sky,lightning_exposure
from .environment import make_city_arch,draw_shelter_entry,draw_tree,draw_person
from .lightning import build_lightning,LightningBolt,draw_leader,draw_streamer
from .camera import apply_camera
from .captions import apply_text

ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/"build"
FFMPEG=os.environ.get("FFMPEG_BIN") or imageio_ffmpeg.get_ffmpeg_exe()


def pulse(t,centers,width=.095):
    return max((math.exp(-((t-c)/width)**2) for c in centers),default=0.0)


ATM=StormAtmosphere(149)
SKY=make_sky(72)
CITY_ARCH=make_city_arch(32)
SAFETY_ARCH=make_city_arch(32)
draw_shelter_entry(SAFETY_ARCH,seed=51)
draw_tree(SAFETY_ARCH,cx=220,base=1490,seed=41)
BOLTS={
    "hook":LightningBolt(build_lightning((610,350),(642,590),seed=16,jitter=18)),
    "stat":LightningBolt(build_lightning((718,385),(642,590),seed=29,branches=False,jitter=17)),
    "mechanism":LightningBolt(build_lightning((570,366),(642,548),seed=51,jitter=17)),
    "repeat":LightningBolt(build_lightning((612,355),(642,590),seed=64,jitter=18)),
    "flicker":LightningBolt(build_lightning((657,344),(642,590),seed=87,jitter=16)),
    "safety":LightningBolt(build_lightning((260,330),(220,776),seed=73,branches=False,jitter=18)),
}
LEADER=BOLTS["mechanism"].paths


def _flash_for(kind,t):
    if kind=="hook":return pulse(t,[1.15,2.20,3.35,4.70],.085),(642,670)
    if kind=="stat":return pulse(t,[7.35,8.75],.12),(642,650)
    if kind=="mechanism":return pulse(t,[19.62,20.35],.105),(642,625)
    if kind=="repeat":return pulse(t,[25.35,27.60],.105),(642,670)
    if kind=="flicker":return pulse(t,[30.05,30.42,31.05,31.80,32.60,33.50],.075),(642,660)
    return pulse(t,[41.00,43.20],.115),(220,812)


def _world_frame(t,idx):
    start,end,kind=SCENES[idx]
    p=clamp((t-start)/max(1e-6,end-start))
    im=SKY.copy()
    ATM.clouds(im,t,scene_seed=idx*13)
    im.alpha_composite(SAFETY_ARCH if kind=="safety" else CITY_ARCH)
    if kind=="safety":
        draw_person(im,594,1500,ease_out(p))
    strength,point=_flash_for(kind,t)
    if kind=="mechanism":
        progress=ease_out(clamp((p-.06)/.66))
        if strength<.12:
            draw_leader(im,LEADER,progress)
            if p>.22:
                draw_streamer(im,(642,590),(642,548),ease_out((p-.22)/.40),seed=8)
        else:
            # At the return stroke, replace the dim leader with one matching bright channel.
            draw_streamer(im,(642,590),(642,548),1.0,seed=8)
    if strength>.025:
        im=lightning_exposure(im,point,strength,seed=idx)
    if kind!="mechanism" and strength>.045:
        BOLTS[kind].draw(im,strength)
    elif kind=="mechanism" and p>.70 and strength>.055:
        BOLTS[kind].draw(im,strength)
    ATM.rain_over(im,t)
    return im,p


def _render_scene(t,idx):
    start,end,kind=SCENES[idx]
    im,_=_world_frame(t,idx)
    im=apply_camera(im,t,start,end,idx)
    note=("U.S. National Weather Service · Empire State Building; contoh, bukan statistik Indonesia."
          if kind=="stat" else None)
    apply_text(im,kind,t,source_note=note)
    return im.convert("RGB")


def render_frame(t):
    t=clamp(t,0,DURATION-1/FPS)
    idx=next((i for i,(a,b,_) in enumerate(SCENES) if a<=t<b),len(SCENES)-1)
    start,_,_=SCENES[idx]
    current=_render_scene(t,idx)
    if idx>0 and t-start<TRANSITION:
        previous=_render_scene(max(0,start-1/FPS),idx-1)
        return Image.blend(previous,current,smooth((t-start)/TRANSITION))
    return current


def make_qc():
    times=[1.2,8.75,15.4,20.35,25.35,31.05,43.2]
    out=BUILD/"qc-petir-v3";out.mkdir(parents=True,exist_ok=True)
    sheet=Image.new("RGB",(1080,1920),(9,13,18))
    for i,t in enumerate(times):
        frame=render_frame(t)
        frame.save(out/f"frame-{t:.2f}s.png")
        thumb=frame.resize((360,640),Image.Resampling.LANCZOS)
        sheet.paste(thumb,((i%3)*360,(i//3)*640))
        print(f"QC {i+1}/{len(times)} · {t:.2f}s",flush=True)
    sheet.save(out/"contact-v3.jpg",quality=94)
    print(f"Wrote {out/'contact-v3.jpg'}")


def render_video(dest,seconds=None):
    dest.parent.mkdir(parents=True,exist_ok=True)
    count=NFRAMES if seconds is None else math.ceil(seconds*FPS)
    cmd=[FFMPEG,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
         "-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-an","-c:v","libx264",
         "-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-r",str(FPS),
         "-movflags","+faststart",str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(count):
            proc.stdin.write(render_frame(n/FPS).tobytes())
            if n%300==0:print(f"rendered {n}/{count} frames",flush=True)
        proc.stdin.close()
        err=proc.stderr.read().decode("utf-8","replace")
        code=proc.wait()
        if code:raise RuntimeError(f"ffmpeg exit {code}: {err[-3000:]}")
    except Exception:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
        proc.kill();raise
    print(f"Wrote {dest}: {count} frames, {count/FPS:.3f}s @ {FPS} fps")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--qc",action="store_true")
    ap.add_argument("--preview",action="store_true",help="render a 12-second silent preview")
    ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    if args.qc:make_qc();return
    if args.preview:
        render_video(args.out or BUILD/"ep51_petir_v3_preview_silent_60fps.mp4",12.0);return
    render_video(args.out or BUILD/"ep51_petir_v3_silent_60fps.mp4")

if __name__=="__main__":main()
