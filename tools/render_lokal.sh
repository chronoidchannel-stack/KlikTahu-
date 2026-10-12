#!/usr/bin/env bash
# ============================================================================
#  tools/render_lokal.sh — render KlikTahu di komputer sendiri / sandbox agen.
#
#  PENTING: render video memang TIDAK dijalankan di GitHub Actions (lihat
#  AGEN.md §14). Actions hanya untuk uji ringan (selftest.yml).
#
#  Pakai:
#      tools/render_lokal.sh shorts <judul-slug>      # render penuh
#      tools/render_lokal.sh shorts <judul-slug> prep # berhenti sebelum render frame
#      tools/render_lokal.sh long   <judul-slug>      # video panjang 16:9
#
#  Variabel opsional:
#      CHUNKS=12        jumlah potongan (menjaga pemakaian disk frame PNG)
#      JOBS=4           proses paralel per potongan (bawaan: jumlah CPU)
#      KEEP_FRAMES=1    jangan hapus frame setelah tiap potongan di-encode
#
#  Berkas publik di dist/ memakai slug dari judul video, bukan nomor episode:
#  <judul>.mp4, <judul>_audio.mp3, <judul>_narasi.mp3, metadata, dan thumbnail.
#  WAV hanya PCM kerja sementara di folder build/ yang diabaikan Git.
# ============================================================================
set -euo pipefail

MODE="${1:-}"
SLUG="${2:-}"
PHASE="${3:-full}"

die() { printf '\n[GAGAL] %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "$1 tidak ditemukan di PATH"; }

usage() {
  sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

[ -n "$MODE" ] && [ -n "$SLUG" ] || usage
case "$MODE" in shorts|long) ;; *) die "mode harus 'shorts' atau 'long'";; esac

cd "$(dirname "$0")/.."          # selalu di akar repo
ROOT="$(pwd)"
need python3

DIR="$(python3 tools/resolve_video.py "$MODE" "$SLUG")" || die "video tidak ditemukan dari slug judul: $SLUG"
[ -f "$DIR/config.env" ] || die "tidak ada $DIR/config.env"
SOURCE_KEY="$(basename "$DIR")"

# --- audio sumber: narasi MP3 yang bisa didengar, bukan arsip WAV lama ------
shopt -s nullglob
AUDIO_CLIPS=( "$DIR"/audio_raw/*.mp3 )
if [ "${#AUDIO_CLIPS[@]}" -eq 0 ]; then
  die "narasi MP3 belum tersedia: isi $DIR/audio_raw/ dengan satu klip MP3 per adegan.
       Arsip WAV lama adalah bahan historis dan tidak dipakai untuk produksi baru."
fi

# --- konfigurasi produksi ---------------------------------------------------
# shellcheck disable=SC1090
set -a; source "$DIR/config.env"; set +a
: "${FPS:?config.env belum mengisi FPS}"

FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
VIDEO_TITLE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["title"])' "$DIR/content.json")"
TITLE_SLUG="$(python3 tools/video_names.py "$DIR/content.json")"

# Pastikan setiap adegan punya tepat satu sumber MP3 sebelum menulis apa pun.
python3 - "$DIR/content.json" "$DIR/audio_raw" <<'PY'
import json, pathlib, sys
content = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
audio_dir = pathlib.Path(sys.argv[2])
expected = {scene["id"] for scene in content.get("scenes", [])}
actual = {path.stem for path in audio_dir.glob("*.mp3")}
missing, extra = sorted(expected - actual), sorted(actual - expected)
if missing or extra:
    if missing:
        print("[GAGAL] MP3 adegan hilang:", ", ".join(missing), file=sys.stderr)
    if extra:
        print("[GAGAL] MP3 tidak dikenal:", ", ".join(extra), file=sys.stderr)
    raise SystemExit(1)
PY
printf '[info] %d klip narasi MP3 untuk “%s”\n' "${#AUDIO_CLIPS[@]}" "$VIDEO_TITLE"
CHUNKS="${CHUNKS:-12}"
JOBS="${JOBS:-$( (nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2) )}"
DISK_FRAMES="frames"

echo "=========================================================================="
echo " KlikTahu · $MODE · $VIDEO_TITLE"
echo " FPS=$FPS  SS=${SS:-?}  potongan=$CHUNKS  proses/potongan=$JOBS  fase=$PHASE"
echo "=========================================================================="

# ============================================================ 1) audio + naskah
mkdir -p audio audio_proc build dist
cp "$DIR/content.json" .
# Decode MP3 only into ignored PCM scratch files for the existing alignment/DSP tools.
for source in "${AUDIO_CLIPS[@]}"; do
  stem="$(basename "${source%.mp3}")"
  "$FF" -y -loglevel error -i "$source" -vn -ar 48000 -ac 2 -c:a pcm_s16le "audio/${stem}.wav"
done
export KT_BUILD=build

echo "--- process_audio.py (rapikan VO + QC keutuhan)"
SPEED="$SPEED" TARGET_WPS="${TARGET_WPS:-1.90}" python3 process_audio.py
echo "--- build_timeline.py"
MAXDUR="${MAXDUR:-180}" python3 build_timeline.py
echo "--- build_audio.py"
SPEED="$SPEED" python3 build_audio.py
echo "--- master_audio.py (loudnorm + SFX)"
python3 master_audio.py

if [ "$MODE" = shorts ]; then
  echo "--- check_layout.py (audit margin)"
  python3 check_layout.py
else
  echo "--- align kata + audio Long + thumbnail"
  python3 long/render_long.py --slug "$SOURCE_KEY" --align
  mkdir -p build/mix
  python3 long/audio_long.py --slug "$SOURCE_KEY" --out build/mix/audio_master.wav
  python3 "$DIR/thumbnail.py" --out build/thumbnail.jpg
  AUDIO_MASTER="build/mix/audio_master.wav"
  export KT_AUDIO_SRC="$AUDIO_MASTER"
fi
[ "$MODE" = shorts ] && AUDIO_MASTER="build/audio_master.wav" && export KT_AUDIO_SRC="$AUDIO_MASTER"

# Audio yang diberikan kepada manusia adalah MP3 ter-master; WAV tetap hanya scratch PCM.
AUDIO_MP3="dist/${TITLE_SLUG}_audio.mp3"
NARRATION_MP3="dist/${TITLE_SLUG}_narasi.mp3"
"$FF" -y -loglevel error -i "$AUDIO_MASTER" -vn -c:a libmp3lame -b:a "${MP3_BITRATE:-256k}" \
  -ar 48000 -ac 2 -metadata title="$VIDEO_TITLE — audio final" -metadata artist="KlikTahu" \
  -metadata album="KlikTahu · audio video" "$AUDIO_MP3"
"$FF" -y -loglevel error -i build/audio_master_vo.wav -vn -c:a libmp3lame -b:a "${VOICE_BITRATE:-192k}" \
  -ar 48000 -ac 2 -metadata title="$VIDEO_TITLE — narasi" -metadata artist="KlikTahu" \
  -metadata album="KlikTahu · narasi video" "$NARRATION_MP3"
echo "audio final MP3 -> $AUDIO_MP3"
echo "narasi MP3 -> $NARRATION_MP3"

if [ "$PHASE" = prep ]; then
  echo
  echo "[prep] selesai — audio, timeline, dan QC tata letak lolos."
  echo "       Jalankan tanpa argumen 'prep' untuk render penuh."
  exit 0
fi

# ============================================================ 2) hitung frame
TOTAL="$(python3 - "$FPS" <<'PY'
import json, sys
fps = float(sys.argv[1])
tl = json.load(open("timeline.json"))
print(int(round(tl["total"] * fps)))
PY
)"
[ "$TOTAL" -gt 0 ] || die "timeline kosong (total frame = 0)"
PER=$(( (TOTAL + CHUNKS - 1) / CHUNKS ))
echo "[info] $TOTAL frame -> $CHUNKS potongan x ~$PER frame"

# ============================================================ 3) render potongan
rm -rf parts "$DISK_FRAMES"; mkdir -p parts
: > list.txt
for i in $(seq 0 $((CHUNKS - 1))); do
  LO=$(( i * PER )); HI=$(( LO + PER ))
  [ "$HI" -gt "$TOTAL" ] && HI="$TOTAL"
  [ "$LO" -ge "$TOTAL" ] && continue
  echo "--- potongan $i: frame $LO..$((HI - 1))"
  rm -rf "$DISK_FRAMES"; mkdir -p "$DISK_FRAMES"
  if [ "$MODE" = shorts ]; then
    python3 render.py --fps "$FPS" --ss "${SS:-1.5}" --sharpen "${SHARPEN:-52}" \
            --jobs "$JOBS" --range "$LO:$HI" --outdir "$DISK_FRAMES"
    "$FF" -y -loglevel error -framerate "$FPS" -start_number "$LO" -i "$DISK_FRAMES/f_%05d.png" \
          -frames:v "$((HI - LO))" -an -c:v libx264 -preset "${PRESET:-slow}" -tune "${TUNE:-animation}" \
          -b:v "${VBITRATE:-6400k}" -maxrate "${MAXRATE:-11000k}" -bufsize "${BUFSIZE:-16000k}" \
          -pix_fmt yuv420p -profile:v high -level 4.2 "parts/part_$i.mp4"
  else
    python3 long/render_long.py --slug "$SOURCE_KEY" --timeline timeline.json --fps "$FPS" --ss "${SS:-1.25}" \
            --jobs "$JOBS" --range "$LO:$HI" --vb "${VBITRATE:-9000k}" --maxrate "${MAXRATE:-14000k}" \
            --bufsize "${BUFSIZE:-20000k}" --preset "${PRESET:-slow}" --tune "${TUNE:-animation}" \
            --out "parts/part_$i.mp4"
  fi
  [ -s "parts/part_$i.mp4" ] || die "potongan $i tidak menghasilkan mp4"
  echo "file parts/part_$i.mp4" >> list.txt
  [ "${KEEP_FRAMES:-0}" = 1 ] || rm -rf "$DISK_FRAMES"
done
rm -rf "$DISK_FRAMES"

# ============================================================ 4) gabung + mux
echo "--- gabung potongan (tanpa re-encode) + mux audio"
"$FF" -y -loglevel error -f concat -safe 0 -i list.txt -c copy video_master.mp4
VIDEO_MP4="dist/${TITLE_SLUG}.mp4"
"$FF" -y -loglevel error -i video_master.mp4 -i "$AUDIO_MASTER" \
      -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a "${ABITRATE:-256k}" -ar 48000 \
      -movflags +faststart -shortest "$VIDEO_MP4"
ls -la "$VIDEO_MP4"

# ============================================================ 5) QC + serah terima
echo "--- QC akhir (qc_mp4.py)"
python3 qc_mp4.py "$VIDEO_MP4"

cp "$DIR/METADATA.md" "dist/${TITLE_SLUG}_metadata.md" 2>/dev/null || echo "[warn] METADATA.md belum ada di $DIR"
cp "$DIR/content.json" "dist/${TITLE_SLUG}_content.json"
if [ "$MODE" = long ] && [ -f build/thumbnail.jpg ]; then
  cp build/thumbnail.jpg "dist/${TITLE_SLUG}_thumbnail.jpg"
fi
# OUT_NAME hanya dipakai sebagai alias arsip internal untuk menemukan teks lama.
P=""
if [ -n "${OUT_NAME:-}" ]; then P="pustaka/${OUT_NAME#KlikTahu_}"; fi
if [ -n "$P" ] && [ -f "$P/SIAP_TEMPEL.md" ]; then
  cp "$P/SIAP_TEMPEL.md" "dist/${TITLE_SLUG}_siap-tempel.md"
fi

echo
echo "=========================================================================="
echo " SELESAI — berkas siap unggah ada di dist/:"
ls -la dist/
echo "=========================================================================="
