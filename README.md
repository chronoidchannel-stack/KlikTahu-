# KlikTahu — Mesin Produksi Video (Shorts 1080×1920 & Long 16:9)

Repo ini adalah **mesin produksi** channel YouTube **KlikTahu**: fakta sains &
misteri bahasa Indonesia. Setiap video memakai judul sebagai nama publik dan
nama berkas. Mesin merangkai naskah, visual, audio narasi MP3 yang dirancang
untuk didengar, efek suara, QC otomatis, dan paket siap unggah.

> **AI/agen baru yang membuka chat?** Baca **[AGEN.md](AGEN.md)** dulu — di situ
> ada memori jangka panjang proyek, status terakhir, resep video baru, dan
> aturan yang tidak boleh dilanggar. Semua pekerjaan bisa dilanjutkan dari sana
> tanpa perlu chat lama.

---

## Aturan penting (pelajaran akun lama di-flag)

1. **Render video TIDAK dijalankan di GitHub Actions.** Render dilakukan lokal
   di sandbox agen / komputer sendiri lewat `tools/render_lokal.sh`.
   GitHub hanya untuk menyimpan kode + menjalankan uji ringan.
2. **MP4 tidak disimpan di repo maupun di Releases.**
3. **Repo ini tidak boleh menyimpan rahasia** (token, kunci API, `.env` asli).
4. Workflow di repo ini hanya uji `< 5 menit` tanpa render, tanpa jadwal cron.
5. Perubahan dikumpulkan: **satu commit bermakna per langkah**, jangan push
   beruntun berkali-kali dalam hitungan menit.

Rinciannya di [AGEN.md §14](AGEN.md) dan [docs/arsip/README.md](docs/arsip/README.md).

---

## Struktur repo

```
AGEN.md                    memori jangka panjang proyek (wajib diperbarui)
PUSTAKA.md                 indeks semua video berdasarkan judul & status rilis
LICENSE                    hak cipta (all rights reserved)
requirements.txt           pillow, numpy, imageio-ffmpeg — tidak ada lainnya
fonts/                     Poppins Bold/SemiBold/Medium/Regular + OFL.txt

render.py                  renderer Shorts (frame, kamera, transisi, HUD, finishing)
diagrams.py                primitif gambar + registry VISUALS + selftest
mesin_v11.py               paket motion "EDITOR" (tipografi kinetik, stiker, BEATS/SFX)
mesin_v11_epNN.py          modul adegan per episode (sc_*NN + tabel beat)
mesin_fx.py                lapisan FX 2026 (finishing sinematik, material, transisi)
mesin_util.py              preview_times, ink_report, sheet (montase)
process_audio.py           rapikan VO tanpa memotong isi + QC keutuhan
build_timeline.py          timeline.json + cek durasi MAXDUR
build_audio.py             menyusun VO terjadwal jadi satu trek
master_audio.py            master −14 LUFS + lapisan SFX (ducking) + limiter
sfx.py                     katalog 24 bunyi sintetis (numpy)
check_layout.py            audit tata letak/margin sebelum render
qc_mp4.py                  QC hasil akhir MP4

episodes/<legacy-key>/     sumber Shorts lama; input produksi baru audio_raw/*.mp3
pustaka/<legacy-key>/      metadata/teks lama; output publik baru tetap berbasis judul
long/mesin_long.py          mesin 16:9 (penyelarasan kata, komponen, kamera, bab, HUD)
long/render_long.py         CLI render video panjang
long/audio_long.py          master audio Long (VO + SFX)
long/<slug>/                content.json · config.env · visual.py · thumbnail.py · METADATA.md
analisis/                   mesin riset topik & metadata (v3-v6) + data hasil
tools/render_lokal.sh       render lokal; nama MP4/MP3 diambil dari judul video
tools/video_names.py        buat slug publik dari content.json:title
tools/resolve_video.py      petakan slug judul ke sumber lama tanpa nomor di CLI
tools/restore_audio.py      alat arsip WAV lama; tidak dipakai di produksi baru
tools/check_repo_hygiene.py audit media/ukuran supaya tidak masuk Git
tests/                      uji ringan alat dan sinkronisasi fakta
docs/                       dokumen teknik, prompt proyek, manifest audio, atribusi
docs/arsip/                 salinan workflow Actions lama (tidak aktif)
```

## Cara render

```bash
pip install -r requirements.txt

# CLI publik memakai slug dari judul; resolver masih menemukan folder sumber lama.
# Narasi MP3 tiap adegan harus ada di folder sumber/audio_raw/<id-adegan>.mp3.
# Cek cepat menghasilkan MP3 final/narasi + timeline, tanpa render frame.
tools/render_lokal.sh shorts kenapa-bintang-berkedip-tapi-planet-tidak prep

# Shorts — render penuh; dist/kenapa-bintang-berkedip-tapi-planet-tidak.mp4
tools/render_lokal.sh shorts kenapa-bintang-berkedip-tapi-planet-tidak

# Video panjang 16:9; output dist/perjalanan-ke-dasar-laut-terdalam-di-bumi.mp4
tools/render_lokal.sh long perjalanan-ke-dasar-laut-terdalam-di-bumi
```

Setelan opsional: `CHUNKS=12` (potongan, menjaga pemakaian disk),
`JOBS=4` (proses paralel). Perkiraan waktu di 2 vCPU: Shorts ±0,6–0,9
detik/frame, Long ±0,22 detik/frame — jalankan sebagai proses latar
(±60–75 menit untuk satu Shorts).

## Uji

```bash
python mesin_v11.py                  # selftest paket motion v11
python diagrams.py                   # selftest semua visual adegan
python sfx.py                        # katalog bunyi -> build/sfx_katalog.wav
python analisis/mesin_v6.py --uji    # uji offline mesin analisis (v5/v6/pemeta/sapuan)
python -m unittest discover -s tests -v
python tools/check_repo_hygiene.py
```

Semua uji di atas juga dijalankan otomatis oleh
[`.github/workflows/selftest.yml`](.github/workflows/selftest.yml) setiap push
ke `main` dan setiap Pull Request.

## Audio untuk didengar dan dipakai di video

Produksi baru memakai **narasi MP3 per adegan**, bukan arsip WAV lama. Buat/rekam
narasi dengan pace alami, artikulasi jelas, jeda yang nyaman, dan pengucapan angka
serta istilah yang diperiksa. Simpan lokal sementara di
`<folder-sumber>/audio_raw/<id-adegan>.mp3`; semua klip harus cocok satu per satu
dengan ID adegan di `content.json`.

`tools/render_lokal.sh` memeriksa daftar klip MP3, lalu mengubahnya menjadi PCM
sementara dalam folder kerja yang diabaikan Git agar alat alignment/DSP lama tetap
bisa dipakai. Ini **bukan** audio hasil unduh atau deliverable. Berkas publik yang
dihasilkan dari proses audio adalah:

- `<judul-video>_narasi.mp3` — track narasi bersih untuk didengar;
- `<judul-video>_audio.mp3` — master narasi + efek suara yang siap dipakai;
- `<judul-video>.mp4` — audio mux akhir dikodekan AAC, bukan WAV.

File MP3/PCM/MP4 hanya disimpan lokal atau di Google Drive, bukan GitHub maupun
GitHub Releases. `.gitignore` dan `tools/check_repo_hygiene.py` mencegah media masuk
repo. Jalankan audit sebelum commit. Audio arsip WAV lama dan alat `restore_audio.py`
dipertahankan sebagai catatan kompatibilitas, tetapi **jangan dipakai untuk produksi baru**.

Batas unggah GitHub dan alasan mengeluarkan media dari repo dijelaskan di
[GitHub: About large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## Hasil yang sudah ada

Daftar video, durasi, status, dan judulnya ada di
**[PUSTAKA.md](PUSTAKA.md)**.

## Lisensi & atribusi

Kode dan isi repo ini **hak milik pemilik channel KlikTahu** (all rights
reserved) — lihat [LICENSE](LICENSE). Komponen pihak ketiga diatur terpisah:
font Poppins (SIL OFL 1.1) dan citra lubang hitam M87* (EHT Collaboration,
CC BY 4.0) — lihat [docs/ATTRIBUSI.md](docs/ATTRIBUSI.md).
