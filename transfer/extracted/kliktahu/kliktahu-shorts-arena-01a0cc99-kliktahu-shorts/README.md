# KlikTahu — Mesin Render Shorts (GitHub Actions, paralel)

> **AI/agen baru membuka chat?** Baca dulu **[AGEN.md](AGEN.md)** — konteks lengkap, status,
> resep episode baru, dan aturan channel. Semua bisa dilanjutkan dari sana tanpa chat lama.

Mesin ini membuat video Shorts 1080×1920 · 60 fps dari data episode (naskah VO + diagram).
Render dijalankan **di GitHub Actions**: frame dibagi ke banyak runner sekaligus, jadi cepat
dan tidak membebani komputer sendiri.

> **Agen (Arena) yang mengendalikan semuanya.** Repo ini dibuat **terpisah** dari repo lain
> milik pemilik akun dan tidak menyentuh repo mana pun selain dirinya. Alur yang dijalankan
> agen dari sisi ini (lihat `tools/gh_control.sh`):
> `list` → `mkrepo` → `push` → `render 12 4` → `watch` → `fetch` (unduh hasil ke workspace).

## Struktur

```
.github/workflows/render.yml     sistem render paralel (prep → render ×N → merge)
.github/workflows/preview.yml    cek cepat: 8 frame + montase (1 menit)
episodes/<slug>/
    content.json                 naskah + setelan per adegan (badge, aksen, visual, VO)
    config.env                   FPS, supersampling, bitrate, jumlah potongan, dll.
    audio_raw/*.wav              klip voice over (8 buah: intro, f1..f6, outro)
    METADATA.md                  judul, deskripsi, tag, peta adegan
engine (root repo)               render.py · diagrams.py · build_*.py · process_audio.py
                                 master_audio.py · qc_mp4.py · check_layout.py · mesin_util.py
tools/run_local.sh               jalankan alur yang sama di komputer sendiri
```

## Cara render di GitHub (dijalankan agen)

1. Buka repo → tab **Actions** → **Render Shorts (paralel)** → **Run workflow**.
2. Isi: `episode` = `ep24_bulan_merah`, `chunks` = `12`, `jobs` = `4`, lalu **Run workflow**.
3. Tunggu ±6–10 menit. Hasilnya muncul di:
   - **Artifacts** → `final-KlikTahu_Ep24_...` (mp4 + metadata)
   - **Releases** → otomatis dibuat, video bisa langsung diunduh

Ingin pratinjau dulu (tanpa render penuh)? Jalankan **Pratinjau cepat (QC visual)** —
keluar montase 8 frame berlabel.

## Kenapa cepat

| | Cara lama (1 proses) | Cara GitHub Actions |
|---|---|---|
| Proses | 1 inti, urut | `chunks` (12) job paralel × `jobs` (4) proses per job |
| 4.839 frame | ±68 menit | ±5–8 menit |
| Memori | terbatas di satu mesin | terbagi ke 12 mesin |

Setiap potongan langsung di-encode dengan setelan **sama** (`preset slow`, `tune animation`,
`-b:v 9500k -maxrate 15000k`), lalu digabung tanpa re-encode (`concat -c copy`) — jadi
kualitasnya identik dengan render satu proses (sudah diuji: frame hasil paralel **bit-identical**).

## Menambah episode baru

1. Buat `episodes/<slug>/` → salin `content.json` + `config.env` dari episode sebelumnya.
2. Taruh 8 klip VO ke `audio_raw/` (nama: `intro.wav, f1..f6.wav, outro.wav`).
3. Sesuaikan `SPEED` (tempo VO santai ±1,13) dan `OUT_NAME`.
4. Jalankan workflow dengan `episode=<slug>`.

## Menjalankan lokal (opsional)

```bash
bash tools/run_local.sh ep24_bulan_merah                 # render penuh
ONLY=preview bash tools/run_local.sh ep24_bulan_merah    # cuma pratinjau + audit tata letak
CHUNKS=6 JOBS=2 bash tools/run_local.sh ep24_bulan_merah # lebih ringan
```

Dependensi: `pip install pillow imageio-ffmpeg numpy`.

## Catatan kualitas

- 1080×1920 · 60 fps · H.264 high@4.2 · ~9,5 Mbps (target ±90–100 MB untuk ±80 detik)
- Supersampling 1,5× + penajam 45 → teks & garis tetap tajam
- Audio: VO dinormalisasi, kompresor 2 lapis, loudnorm −14 LUFS, limiter, 0 clipping
- QC otomatis sebelum unggah: durasi, kesinkronan VO per adegan, margin aman elemen teks,
  dan korelasi audio MP4 vs master
