# Simple Music Bot

Bot musik Discord sederhana yang hanya berfokus pada pemutaran audio tanpa dashboard atau elemen UI tambahan.

## Fitur

- Putar musik dari URL atau query pencarian
- Kontrol pemutaran dasar (play, pause, skip)
- Manajemen antrian untuk beberapa lagu
- Output audio yang jernih
- Antarmuka perintah sederhana

## Perintah

- `!play <url atau query pencarian>` - Putar lagu atau tambahkan ke antrian
- `!pause` - Jeda lagu yang sedang diputar
- `!resume` - Lanjutkan pemutaran lagu yang dijeda
- `!skip` - Lewati lagu yang sedang diputar
- `!queue` - Tampilkan antrian lagu saat ini
- `!clear` - Bersihkan antrian lagu
- `!volume <0-100>` - Atur level volume
- `!now` - Tampilkan lagu yang sedang diputar
- `!loop` - Aktifkan/nonaktifkan mode pengulangan untuk lagu saat ini
- `!join` - Bergabung dengan channel suara Anda
- `!leave` - Tinggalkan channel suara

## Pengaturan

1. Buat bot Discord di [Discord Developer Portal](https://discord.com/developers/applications)
2. Dapatkan token bot Anda
3. Atur token sebagai environment variable DISCORD_TOKEN di Replit
4. Undang bot ke server Anda dengan menggunakan URL undangan dari Developer Portal
   - Pastikan untuk memberikan izin `Bot` dengan izin berikut:
     - `Read Messages/View Channels`
     - `Send Messages`
     - `Connect` (untuk channel suara)
     - `Speak` (untuk channel suara)

## Cara Menggunakan

1. Bergabunglah dengan channel suara di server Discord
2. Gunakan perintah `!play` diikuti dengan URL YouTube atau kata kunci pencarian:
   ```
   !play despacito
   ```
   atau
   ```
   !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
3. Bot akan bergabung dengan channel suara Anda dan mulai memutar musik
4. Gunakan perintah lain seperti `!pause`, `!resume`, atau `!skip` untuk mengontrol pemutaran

## Kebutuhan Sistem

- Python 3.8 atau lebih tinggi
- Discord.py library
- FFmpeg (untuk pemrosesan audio)
- YT-DLP (untuk mengunduh audio dari YouTube)
- Opus codec (untuk encoding audio)

## Pemecahan Masalah

Jika bot tidak memutar audio:
1. Pastikan bot memiliki izin yang benar di server Discord
2. Verifikasi bahwa Anda berada di channel suara sebelum menggunakan perintah `!play`
3. Periksa apakah URL yang Anda berikan valid dan dapat diakses
4. Coba gunakan query pencarian sebagai alternatif untuk URL