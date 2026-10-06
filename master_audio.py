#!/usr/bin/env python3
"""Master audio Ep21 — versi "santai": VO tidak dipercepat (agar terasa tenang),
dinamikanya dibuat lebih rata (kompresor + limiter lembut), lalu dinaikkan ke level
broadcast. Output: build/audio_master.wav (48 kHz stereo) + laporan QC.
"""
import os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg

BASE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
BUILD = os.environ.get("KT_BUILD") or os.path.join(BASE, "..", "build")
SRC = os.path.join(BUILD, "audio.wav")          # hasil build_audio.py (VO utuh)
os.makedirs(BUILD, exist_ok=True)
OUT = os.path.join(BUILD, "audio_master.wav")
TARGET_PEAK = -1.2     # dBTP kasar (dBFS) — aman untuk AAC YouTube
TARGET_LUFS = -14.0    # standar YouTube


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def read(p):
    with wave.open(p) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, w.getnchannels())
    return a.astype(np.float64) / 32768.0, sr


def db(x):
    return 20 * np.log10(max(1e-9, x))


def tambah_sfx(a, sr):
    """v11: lapisan SFX sintetis (sfx.py) dari event mesin_v11 - hanya episode v11.

    Episode lama tidak punya event -> tidak ada yang ditambahkan (audio identik).
    Nonaktifkan dengan KT_SFX=0.
    """
    if os.environ.get("KT_SFX", "1") != "1":
        return a
    tlp = os.path.join(BASE, "timeline.json")
    if not os.path.exists(tlp):
        return a
    import json
    sys.path.insert(0, BASE)
    import mesin_v11, sfx
    tl = json.load(open(tlp))
    ev = mesin_v11.events(tl["scenes"])
    ev = [e for e in ev if e[1] in sfx.KATALOG]
    if not ev or sr != sfx.SR:
        print("  SFX: tidak ada event v11 (episode lama) - dilewati")
        return a
    vo = a.mean(axis=1)
    lay = sfx.duck(sfx.lapisan(ev, len(vo) / sr, float(os.environ.get("KT_SFX_DB", "-16"))), vo)
    lay = lay[: len(vo)]
    if len(lay) < len(vo):
        lay = np.pad(lay, (0, len(vo) - len(lay)))
    out = a.copy()
    out[:, 0] += lay * 0.96
    out[:, 1] += lay * 1.00
    # limiter lembut: tekan hanya puncak yang melewati -1.2 dBFS
    lim = 10 ** (TARGET_PEAK / 20)
    pk = np.abs(out).max(axis=1)
    over = pk > lim
    if over.any():
        g = np.ones(len(out))
        g[over] = lim / pk[over]
        k = int(sr * 0.004)
        g = np.minimum.accumulate(np.lib.stride_tricks.sliding_window_view(
            np.pad(g, (k, k), constant_values=1.0), 2 * k + 1).min(axis=1)[None, :], axis=0)[0]
        out *= g[:, None]
    r_vo = np.sqrt((a ** 2).mean()); r_sx = np.sqrt((lay ** 2).mean()) + 1e-12
    print(f"  SFX: {len(ev)} event | lapisan {db(r_sx):.1f} dBFS RMS ({db(r_sx) - db(r_vo):+.1f} dB vs VO)")
    return out


def main():
    tmp = os.path.join(BUILD, "_master_tmp.wav")
    # kompresor lembut 2 tahap + limiter: menjaga cerita tetap tenang tapi terdengar penuh
    chain = ("acompressor=threshold=-20dB:ratio=2.4:attack=14:release=260:makeup=2.2,"
             "acompressor=threshold=-12dB:ratio=1.6:attack=24:release=320:makeup=1.0,"
             "equalizer=f=6800:t=q:w=1.3:g=-1.6,"      # redam desis "s" agar tidak menusuk saat naskah padat
             "bass=g=1.0:f=110,"                        # sedikit kehangatan
             "treble=g=0.9:f=5200,"                     # kejernihan secukupnya
             "loudnorm=I=-14:TP=-1.3:LRA=8:print_format=none,"
             "alimiter=limit=0.985:attack=5:release=60")
    run([FF, "-y", "-i", SRC, "-af", chain, "-ar", "48000", "-ac", "2", tmp])
    a, sr = read(tmp)
    a_vo = a.copy()
    a = tambah_sfx(a, sr)
    pk = np.abs(a).max()
    rms = np.sqrt((a ** 2).mean())
    # pastikan puncak tidak melewati target
    g = min(0.0, TARGET_PEAK - db(pk))
    if abs(g) > 0.05:
        a = np.clip(a * (10 ** (g / 20.0)), -1.0, 1.0)
    out = (a * 32767.0).astype("<i2")
    # stem VO saja (gain sama) -> qc_mp4 memeriksa keutuhan VO per adegan tanpa
    # terganggu SFX; keutuhan MP4 tetap dicek dengan korelasi ke master lengkap.
    vo_out = (np.clip(a_vo * (10 ** (g / 20.0)), -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(os.path.join(BUILD, "audio_master_vo.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(vo_out.tobytes())
    with wave.open(OUT, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(out.tobytes())
    pk2 = np.abs(a).max()
    print(f"master -> {os.path.normpath(OUT)}")
    print(f"  panjang {out.shape[0]/sr:.2f}s | RMS {db(rms):.1f} dBFS | puncak {db(pk2):.1f} dBFS "
          f"| gain akhir {g:+.2f} dB")
    # cek tidak ada clipping
    clip = int((np.abs(a) >= 0.9995).sum())
    print(f"  sample clipping: {clip}")
    if clip > 40:
        print("PERINGATAN: clipping terdeteksi")
        sys.exit(1)
    print("AUDIO MASTER OK ✔")


if __name__ == "__main__":
    main()
