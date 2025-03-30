# Panduan Menjaga Bot Discord Tetap Aktif

## Introduksi

Bot Discord Anda sudah memiliki sistem monitor dan restart otomatis yang baik. Namun, pada platform hosting seperti Replit, aplikasi dapat "tertidur" setelah tidak ada aktivitas selama beberapa waktu. Berikut adalah beberapa cara untuk menjaga bot tetap aktif.

## 1. Gunakan UptimeRobot (Disarankan - Gratis)

UptimeRobot adalah layanan pemantauan gratis yang dapat "membangunkan" aplikasi Replit Anda secara berkala.

### Langkah-langkah:

1. Buat akun di [UptimeRobot](https://uptimerobot.com)
2. Setelah login, klik "Add New Monitor"
3. Pilih "HTTP(s)" sebagai jenis monitor
4. Beri nama monitor (misalnya "Discord Bot")
5. Masukkan URL: `https://[NAMA-REPLIT-ANDA].replit.app/uptime`
6. Atur interval monitor menjadi 5 menit
7. Klik "Create Monitor"

UptimeRobot akan melakukan ping ke endpoint `/uptime` setiap 5 menit, yang akan menjaga aplikasi Replit Anda tetap aktif.

## 2. Aktifkan "Always On" di Replit (Memerlukan Langganan)

Jika Anda memiliki langganan Replit Hacker atau Pro:

1. Buka dashboard Replit Anda
2. Buka proyek bot Discord
3. Klik tombol "Always On" untuk mengaktifkannya

Fitur ini akan menjaga Replit Anda tetap berjalan bahkan tanpa adanya permintaan eksternal.

## 3. Gunakan Cron Job untuk Ping Secara Berkala

Jika Anda memiliki akses ke server dengan cron job:

```bash
*/5 * * * * curl -s https://[NAMA-REPLIT-ANDA].replit.app/uptime > /dev/null
```

## 4. Loop Pemantauan Internal (Sudah Terimplementasi)

Bot Anda sudah memiliki mekanisme monitoring internal di `main.py`. Fungsi `monitor_bot()` memeriksa setiap 10 detik apakah bot masih berjalan dan akan melakukan restart jika bot berhenti.

```python
def monitor_bot():
    """Monitor bot thread and restart if needed"""
    global bot_thread, bot_running
    
    while True:
        if bot_thread is None or not bot_thread.is_alive():
            if bot_running:
                print("Bot thread not running, restarting...")
                bot_thread = Thread(target=run_discord_bot)
                bot_thread.daemon = True
                bot_thread.start()
        time.sleep(10)  # Check every 10 seconds
```

## 5. Tangani Peristiwa Disconnect dengan Baik (Sudah Terimplementasi)

Bot Anda sudah memiliki penangan event disconnect di `bot.py`:

```python
@bot.event
async def on_disconnect():
    """Event triggered when the bot disconnects from Discord"""
    logging.warning("Bot disconnected from Discord")

@bot.event
async def on_resumed():
    """Event triggered when the bot resumes connection to Discord"""
    logging.info("Bot resumed connection to Discord")
```

## Kesimpulan

Kombinasi dari monitor internal yang sudah ada dan setup UptimeRobot adalah cara terbaik untuk menjaga bot Discord Anda aktif secara terus-menerus. Jika Anda mengalami masalah, periksa log bot untuk mengetahui kendala yang terjadi.