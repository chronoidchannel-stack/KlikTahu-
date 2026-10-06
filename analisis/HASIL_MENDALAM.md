# KlikTahu - Analisis Mendalam Real-Time v3 (2026-09-24)

**Permintaan:** 254 panggilan autocomplete (Google hl=id + YouTube ds=yt, gl=id)
**Frasa unik:** 1917 (295 di luar tema) - sumber: hasil_mendalam_20260924.json

- `skor` = jml + kuat*0,7 + niat*0,9 + sains*3 + yt*0,3 (yt = frasa yang muncul di YouTube = ada yang mencari DAN menonton)
- `skor_tumbuh` = skor + rel*1,2 + kom*1,5 + vis*0,8 + ever*3
  - rel = frasa pengalaman pribadi/keseharian (relatabilitas), kom = frasa yang mengundang bercerita (komentar cepat),
  - vis = fenomena yang bisa diperlihatkan (retensi & share), ever = 1 kalau bebas frasa musiman (evergreen).
- Urutan tabel: skor_tumbuh (sinyal pertumbuhan channel), bukan volume semata.

| # | tema | jml | kuat | niat | yt | sains | rel | kom | vis | ever | skor | skor_tumbuh | status | contoh terkuat |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | gigi & mulut | 75 | 54 | 6 | 43 | 2.0 | 40 | 38 | 19 | 1.0 | 137.1 | **260.3** | SEGAR | `kenapa anak bau mulut` · `kenapa bau mulut` · `kenapa bau mulut anak tidak enak` |
| 2 | mata | 85 | 60 | 18 | 46 | 2.0 | 26 | 8 | 7 | 1.0 | 163.0 | **214.8** | SEGAR | `kenapa air mata keluar sendiri padahal tidak menangis` · `kenapa bulu mata sering rontok` · `kenapa kedutan di bawah mata kiri` |
| 3 | megalodon | 36 | 32 | 5 | 23 | 2.5 | 36 | 36 | 0 | 1.0 | 77.3 | **177.5** | antrean lama | `apakah megalodon masih hidup di indonesia` · `apakah megalodon masih hidup di palung mariana` · `apakah megalodon masih hidup sampai sekarang` |
| 4 | perut & pencernaan | 67 | 40 | 16 | 35 | 2.0 | 19 | 7 | 18 | 1.0 | 125.9 | **176.6** | Ep28 | `apa penyebab maag kambuh` · `kenapa bayi menangis terus tanpa sebab` · `kenapa bisa sakit lambung` |
| 5 | mimpi & tidur | 64 | 32 | 12 | 37 | 2.0 | 17 | 7 | 0 | 1.0 | 114.3 | **148.2** | Ep21+Ep25 | `cara mengatasi susah tidur akibat minum kopi` · `cara mengatasi susah tidur karena minum kopi` · `kenapa anak susah tidur malam` |
| 6 | baterai & hp | 60 | 26 | 11 | 41 | 1.5 | 13 | 4 | 2 | 1.0 | 104.9 | **131.1** | SEGAR | `kenapa baterai cepat habis` · `kenapa baterai cepat habis dan panas` · `kenapa baterai cepat habis iphone` |
| 7 | kulit | 49 | 37 | 6 | 28 | 1.5 | 13 | 6 | 3 | 1.0 | 93.2 | **123.2** | SEGAR | `kenapa bulu kemaluan gatal` · `kenapa jerawat batu tumbuh terus` · `kenapa jerawat bau` |
| 8 | kucing | 27 | 26 | 1 | 22 | 2.0 | 14 | 27 | 0 | 1.0 | 58.7 | **119.0** | Ep23 | `kenapa anjing takut kucing` · `kenapa anjing takut sama kucing` · `kenapa badan kucing bau busuk` |
| 9 | kram & kesemutan | 44 | 37 | 3 | 25 | 2.0 | 13 | 1 | 0 | 1.0 | 86.1 | **106.2** | Ep29 | `kenapa badan kesemutan` · `kenapa badan sering kesemutan` · `kenapa bisa kesemutan` |
| 10 | pusing & migrain | 42 | 39 | 5 | 22 | 1.5 | 11 | 1 | 0 | 1.0 | 84.9 | **102.6** | SEGAR | `kenapa bisa migrain` · `kenapa bisa terjadi migrain` · `kenapa kepala pusing badan lemas` |
| 11 | demam & imun | 29 | 11 | 5 | 14 | 2.0 | 6 | 15 | 18 | 1.0 | 51.4 | **98.5** | antrean lama | `demam anak naik turun selama 7 hari` · `kenapa anak demam hanya di kepala` · `kenapa cowok demam manja` |
| 12 | uban & rambut | 50 | 35 | 2 | 30 | 1.5 | 3 | 1 | 0 | 1.0 | 89.8 | **97.9** | antrean lama | `kenapa ada uban di usia muda` · `kenapa banyak uban di usia muda` · `kenapa ketombe ada` |
| 13 | hujan & awan | 36 | 30 | 3 | 19 | 2.5 | 4 | 2 | 15 | 0.3 | 72.9 | **93.6** | SEGAR | `google kenapa awan warnanya putih` · `kenapa ada awan putih dan hitam` · `kenapa ada awan putih di malam hari` |
| 14 | mimisan & hidung | 33 | 30 | 4 | 14 | 2.5 | 8 | 5 | 3 | 1.0 | 69.3 | **91.8** | SEGAR | `kenapa anak mimisan tiba tiba` · `kenapa anak sering mimisan` · `kenapa bisa mimisan` |
| 15 | hantu & supranatural | 39 | 37 | 0 | 26 | 2.0 | 3 | 3 | 2 | 1.0 | 78.7 | **91.4** | SEGAR | `kenapa hantu` · `kenapa hantu banyak perempuan` · `kenapa hantu berbeda di setiap negara` |
| 16 | situs misteri indonesia | 40 | 31 | 0 | 30 | 2.5 | 2 | 3 | 0 | 1.0 | 78.2 | **88.1** | antrean lama | `apa misteri gunung lawu` · `apa misteri gunung padang` · `cerita misteri gunung lawu` |
| 17 | cegukan | 29 | 24 | 13 | 17 | 2.0 | 12 | 1 | 0 | 1.0 | 68.6 | **87.5** | SEGAR | `kenapa bayi cegukan` · `kenapa bayi cegukan dan cara mengatasinya` · `kenapa bayi cegukan setelah minum asi` |
| 18 | listrik & magnet | 29 | 27 | 10 | 14 | 2.5 | 5 | 4 | 2 | 0.3 | 68.6 | **83.1** | SEGAR | `kenapa belut listrik berbahaya` · `kenapa genset tidak keluar listrik` · `kenapa hari ini mati lampu` |
| 19 | internet & sinyal | 38 | 25 | 7 | 24 | 1.5 | 6 | 0 | 0 | 0.3 | 73.5 | **81.6** | SEGAR | `kenapa di laptop tidak muncul wifi` · `kenapa internet cepat habis` · `kenapa internet indonesia lambat` |
| 20 | gerhana | 39 | 14 | 4 | 25 | 3.0 | 1 | 2 | 2 | 0.3 | 68.9 | **75.6** | SEGAR | `apa arti gerhana bulan darah` · `apa arti gerhana bulan merah` · `apa arti gerhana matahari` |
| 21 | bintang & galaksi | 30 | 23 | 0 | 17 | 3.0 | 2 | 3 | 1 | 1.0 | 60.2 | **70.9** | SEGAR | `apa itu galaksi` · `apa itu galaksi andromeda` · `apa itu galaksi bima sakti` |
| 22 | pelangi | 30 | 26 | 1 | 16 | 2.5 | 1 | 0 | 4 | 1.0 | 61.4 | **68.8** | SEGAR | `kenapa bisa terjadi pelangi` · `kenapa pelangi` · `kenapa pelangi ada 2` |
| 23 | kuping | 25 | 20 | 2 | 15 | 2.0 | 6 | 3 | 3 | 1.0 | 51.3 | **68.4** | SEGAR | `kenapa kuping berdenging` · `kenapa kuping berdenging kanan kiri` · `kenapa kuping berdenging menurut islam` |
| 24 | kuku | 20 | 20 | 1 | 4 | 1.5 | 9 | 9 | 0 | 1.0 | 40.6 | **67.9** | SEGAR | `kenapa kuku bergelombang` · `kenapa kuku berlubang` · `kenapa kuku berlubang kecil` |
| 25 | petir | 26 | 22 | 0 | 17 | 2.5 | 3 | 2 | 5 | 1.0 | 54.0 | **67.6** | antrean lama | `kenapa gunung meletus ada petir` · `kenapa gunung meletus ada petir nya` · `kenapa gunung meletus keluar petir` |
| 26 | air laut & ombak | 34 | 19 | 0 | 18 | 2.5 | 2 | 1 | 0 | 1.0 | 60.2 | **67.1** | SEGAR | `asal usul kenapa air laut asin` · `kenapa ada ombak` · `kenapa ada ombak di danau` |
| 27 | jantung & dada | 27 | 19 | 5 | 14 | 2.0 | 5 | 2 | 0 | 1.0 | 55.0 | **67.0** | SEGAR | `kenapa dada sesak` · `kenapa dada sesak dan sakit` · `kenapa dada sesak dan susah bernafas` |
| 28 | menangis & emosi | 26 | 20 | 1 | 14 | 2.0 | 4 | 5 | 0 | 1.0 | 51.1 | **66.4** | SEGAR | `gampang stres kenapa` · `keinginanmu kenapa menangis` · `kenapa anak gampang stres` |
| 29 | serangga | 25 | 21 | 0 | 20 | 2.0 | 3 | 4 | 1 | 1.0 | 51.7 | **65.1** | SEGAR | `kenapa nyamuk banyak di malam hari` · `kenapa nyamuk bisa menembus kulit` · `kenapa nyamuk diciptakan` |
| 30 | matahari | 21 | 20 | 1 | 16 | 3.0 | 3 | 3 | 4 | 1.0 | 49.7 | **64.0** | SEGAR | `kenapa harus takut pada matahari` · `kenapa luar angkasa gelap padahal ada matahari` · `kenapa matahari` |
| 31 | ngorok | 23 | 23 | 3 | 15 | 2.0 | 2 | 4 | 0 | 1.0 | 52.3 | **63.7** | Ep27 | `kenapa anak tidur ngorok` · `kenapa ayam bisa ngorok` · `kenapa ayam ngorok` |
| 32 | tekanan darah | 25 | 18 | 2 | 11 | 2.5 | 5 | 1 | 3 | 1.0 | 50.2 | **63.1** | SEGAR | `darah tinggi disebabkan oleh apa` · `kenapa bisa darah rendah` · `kenapa darah rendah` |
| 33 | piramida & mesir | 29 | 25 | 0 | 15 | 2.5 | 0 | 1 | 0 | 1.0 | 58.5 | **63.0** | SEGAR | `buku misteri piramida dan sphinx` · `doraemon misteri piramida mesir sub indo` · `kenapa piramida ada dimana mana` |
| 34 | batuk flu pilek | 24 | 14 | 2 | 10 | 1.5 | 6 | 6 | 0 | 1.0 | 43.1 | **62.3** | SEGAR | `kenapa anak flu berulang` · `kenapa batuk gak sembuh sembuh` · `kenapa batuk tidak kunjung sembuh` |
| 35 | gempa bumi | 18 | 15 | 2 | 13 | 3.0 | 6 | 1 | 0 | 1.0 | 43.2 | **54.9** | Ep22 | `kenapa ada gempa bumi` · `kenapa bisa gempa` · `kenapa bisa gempa bumi` |
| 36 | ular & reptil | 17 | 14 | 1 | 14 | 2.0 | 4 | 6 | 0 | 1.0 | 37.9 | **54.7** | SEGAR | `kenapa ular` · `kenapa ular berbisa` · `kenapa ular bisa berjalan` |
| 37 | es & salju | 25 | 19 | 0 | 16 | 2.0 | 0 | 0 | 5 | 0.3 | 49.1 | **54.0** | SEGAR | `apa yang terjadi jika es kutub mencair` · `kenapa 2026 turun salju` · `kenapa ada musim salju` |
| 38 | lubang hitam | 11 | 0 | 0 | 3 | 3.0 | 11 | 11 | 0 | 1.0 | 20.9 | **53.6** | SEGAR | `apa isi lubang hitam` · `apa itu lubang hitam` · `apa itu lubang hitam atau black hole` |
| 39 | aurora | 23 | 18 | 0 | 7 | 3.0 | 1 | 1 | 1 | 1.0 | 46.7 | **53.2** | antrean lama | `apa itu aurora` · `apa itu aurora australis` · `apa itu aurora borealis` |
| 40 | angin & badai | 22 | 16 | 1 | 12 | 2.5 | 3 | 1 | 2 | 0.3 | 45.2 | **52.8** | SEGAR | `kenapa ac tidak ada anginnya` · `kenapa ada angin` · `kenapa ada angin dalam badan` |
| 41 | gusi & rahang | 13 | 9 | 1 | 4 | 2.0 | 5 | 4 | 12 | 1.0 | 27.4 | **52.0** | SEGAR | `kenapa rahang berbunyi saat membuka mulut` · `kenapa rahang bunyi` · `kenapa rahang bunyi ketika membuka mulut` |
| 42 | kapal & mengapung | 21 | 14 | 3 | 10 | 2.5 | 3 | 0 | 0 | 1.0 | 44.0 | **50.6** | antrean lama | `kenapa es batu mengapung` · `kenapa es batu mengapung di air` · `kenapa es mengapung` |
| 43 | bulan | 21 | 11 | 2 | 14 | 2.5 | 1 | 1 | 5 | 0.3 | 42.2 | **49.8** | Ep24 | `kenapa bulan berbentuk sabit` · `kenapa bulan bercahaya` · `kenapa bulan berwarna merah` |
| 44 | anjing | 19 | 12 | 0 | 12 | 2.0 | 3 | 3 | 1 | 1.0 | 37.0 | **48.9** | SEGAR | `kenapa anjing alpha ditakuti` · `kenapa anjing alpha ditakuti anjing lain` · `kenapa anjing diharamkan oleh allah` |
| 45 | planet & roket | 12 | 11 | 0 | 5 | 3.0 | 4 | 4 | 6 | 1.0 | 30.2 | **48.8** | SEGAR | `bagaimana mesin roket bekerja` · `bagaimana roket bekerja` · `bagaimana roket kembali ke bumi` |
| 46 | burung terbang | 21 | 6 | 1 | 8 | 2.0 | 4 | 3 | 2 | 1.0 | 34.5 | **48.4** | SEGAR | `burung terbang malam hari` · `burung terbang malam hari pertanda apa` · `kenapa air radiator keluar dari selang pembuangan` |
| 47 | segitiga bermuda | 19 | 18 | 1 | 14 | 2.0 | 0 | 0 | 3 | 1.0 | 42.7 | **48.1** | SEGAR | `apa misteri segitiga bermuda` · `apakah misteri segitiga bermuda sudah terpecahkan` · `buku misteri segitiga bermuda` |
| 48 | langit & senja | 14 | 7 | 2 | 2 | 2.5 | 3 | 2 | 14 | 0.3 | 28.8 | **47.5** | SEGAR | `google kenapa langit biru` · `kenapa langit biru` · `kenapa langit biru di siang hari` |
| 49 | laut dalam | 17 | 15 | 0 | 12 | 2.5 | 1 | 1 | 0 | 1.0 | 38.6 | **44.3** | SEGAR | `kenapa laut dalam gelap` · `kenapa laut dalam gelap di dunia` · `kisah misteri laut dalam` |
| 50 | ufo & alien | 17 | 13 | 0 | 6 | 2.0 | 1 | 1 | 1 | 1.0 | 33.9 | **40.4** | SEGAR | `apa itu ufo` · `apa itu ufo dan alien` · `apa itu ufo main made` |
| 51 | pesawat | 15 | 7 | 2 | 9 | 2.5 | 3 | 1 | 0 | 1.0 | 31.9 | **40.0** | SEGAR | `kenapa pesawat berat bisa terbang` · `kenapa pesawat bisa terbang` · `kenapa pesawat bisa terbang di udara` |
| 52 | dinosaurus | 14 | 11 | 0 | 5 | 3.0 | 2 | 1 | 0 | 1.0 | 32.2 | **39.1** | Ep26 | `alasan kenapa dinosaurus punah` · `kenapa dinosaurus bisa punah` · `kenapa dinosaurus harus punah` |
| 53 | kedutan | 8 | 8 | 2 | 5 | 2.0 | 2 | 0 | 0 | 1.0 | 22.9 | **28.3** | SEGAR | `kenapa alis kiri kedutan terus` · `kenapa bibir atas kedutan` · `kenapa kedutan` |
| 54 | gunung api | 8 | 8 | 2 | 2 | 2.5 | 0 | 0 | 1 | 1.0 | 23.5 | **27.3** | SEGAR | `kenapa bisa terjadi gunung meletus` · `kenapa gunung meletus` · `kenapa gunung meletus ada apinya` |
| 55 | gula & makanan | 11 | 7 | 0 | 10 | 2.0 | 0 | 0 | 0 | 0.3 | 24.9 | **25.8** | SEGAR | `kenapa gula darah bisa rendah` · `kenapa gula darah bisa tinggi` · `kenapa gula darah puasa tinggi` |

## Kandidat segar teratas (belum dibahas, bukan antrean lama, cocok sains) — urut skor_tumbuh
1. **gigi & mulut** - skor_tumbuh 260.3 (skor 137.1; jml 75, kuat 54, yt 43, rel 40, kom 38, vis 19, ever 1.0) - contoh: `kenapa anak bau mulut`, `kenapa bau mulut`, `kenapa bau mulut anak tidak enak`, `kenapa bau mulut busuk`
2. **mata** - skor_tumbuh 214.8 (skor 163.0; jml 85, kuat 60, yt 46, rel 26, kom 8, vis 7, ever 1.0) - contoh: `kenapa air mata keluar sendiri padahal tidak menangis`, `kenapa bulu mata sering rontok`, `kenapa kedutan di bawah mata kiri`, `kenapa kedutan mata kanan`
3. **hujan & awan** - skor_tumbuh 93.6 (skor 72.9; jml 36, kuat 30, yt 19, rel 4, kom 2, vis 15, ever 0.3) - contoh: `google kenapa awan warnanya putih`, `kenapa ada awan putih dan hitam`, `kenapa ada awan putih di malam hari`, `kenapa awan berwarna putih`
4. **mimisan & hidung** - skor_tumbuh 91.8 (skor 69.3; jml 33, kuat 30, yt 14, rel 8, kom 5, vis 3, ever 1.0) - contoh: `kenapa anak mimisan tiba tiba`, `kenapa anak sering mimisan`, `kenapa bisa mimisan`, `kenapa hidung berdarah`
5. **hantu & supranatural** - skor_tumbuh 91.4 (skor 78.7; jml 39, kuat 37, yt 26, rel 3, kom 3, vis 2, ever 1.0) - contoh: `kenapa hantu`, `kenapa hantu banyak perempuan`, `kenapa hantu berbeda di setiap negara`, `kenapa hantu bisa ada`
6. **cegukan** - skor_tumbuh 87.5 (skor 68.6; jml 29, kuat 24, yt 17, rel 12, kom 1, vis 0, ever 1.0) - contoh: `kenapa bayi cegukan`, `kenapa bayi cegukan dan cara mengatasinya`, `kenapa bayi cegukan setelah minum asi`, `kenapa bisa cegukan terus`
7. **listrik & magnet** - skor_tumbuh 83.1 (skor 68.6; jml 29, kuat 27, yt 14, rel 5, kom 4, vis 2, ever 0.3) - contoh: `kenapa belut listrik berbahaya`, `kenapa genset tidak keluar listrik`, `kenapa hari ini mati lampu`, `kenapa listrik berbahaya`
8. **gerhana** - skor_tumbuh 75.6 (skor 68.9; jml 39, kuat 14, yt 25, rel 1, kom 2, vis 2, ever 0.3) - contoh: `apa arti gerhana bulan darah`, `apa arti gerhana bulan merah`, `apa arti gerhana matahari`, `apa besok gerhana matahari`
