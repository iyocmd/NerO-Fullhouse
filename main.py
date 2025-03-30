from flask import Flask, render_template, jsonify
from threading import Thread
from bot import bot
import discord
import os
import logging
import signal
import sys
import time
import traceback

# Set up logging for easier debugging
logging.basicConfig(level=logging.INFO)

# Get token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Buat aplikasi Flask
app = Flask(__name__)

# Bot status variable for thread monitoring
bot_running = True
bot_thread = None
bot_connected = False
bot_status = "starting"

@app.route('/')
def home():
    """Tampilkan halaman beranda"""
    bot_status_class = "online" if bot_connected else "offline"
    bot_status_text = "Bot Aktif" if bot_connected else "Bot Offline"
    
    return f"""
    <html>
        <head>
            <title>Discord Music Bot</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    background-color: #121212;
                    color: #eee;
                }}
                h1, h2 {{
                    color: #7289DA;
                }}
                .container {{
                    background-color: #1e1e1e;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 10px;
                }}
                code {{
                    background-color: #2c2c2c;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: monospace;
                }}
                .status {{
                    display: inline-block;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .online {{
                    background-color: #43b581;
                }}
                .offline {{
                    background-color: #f04747;
                }}
                #status-refresh {{
                    margin-top: 20px;
                    font-size: 0.8em;
                    color: #888;
                }}
            </style>
            <script>
                // Auto refresh status every 30 seconds
                setTimeout(function() {{
                    window.location.reload();
                }}, 30000);
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Discord Music Bot</h1>
                <p class="status {bot_status_class}">{bot_status_text}</p>
                <p>Bot musik Discord yang mudah digunakan. Cukup tambahkan bot ke server Discord Anda dan mulai mainkan musik!</p>
                
                <h2>Perintah</h2>
                <ul>
                    <li><code>!play &lt;url atau kata kunci&gt;</code> - Putar lagu atau tambahkan ke antrian</li>
                    <li><code>!pause</code> - Jeda lagu yang sedang diputar</li>
                    <li><code>!resume</code> - Lanjutkan pemutaran lagu yang dijeda</li>
                    <li><code>!skip</code> - Lewati lagu yang sedang diputar</li>
                    <li><code>!queue</code> - Tampilkan antrian lagu saat ini</li>
                    <li><code>!clear</code> - Bersihkan antrian lagu</li>
                    <li><code>!volume &lt;0-100&gt;</code> - Atur level volume</li>
                    <li><code>!now</code> - Tampilkan lagu yang sedang diputar</li>
                    <li><code>!loop</code> - Aktifkan/nonaktifkan mode pengulangan</li>
                    <li><code>!join</code> - Bergabung dengan channel suara Anda</li>
                    <li><code>!leave</code> - Tinggalkan channel suara</li>
                </ul>
                
                <h2>Cara Menggunakan</h2>
                <ol>
                    <li>Bergabunglah dengan channel suara di server Discord</li>
                    <li>Ketik <code>!play</code> diikuti dengan URL YouTube atau kata kunci pencarian</li>
                    <li>Bot akan bergabung dengan channel suara Anda dan mulai memutar musik</li>
                    <li>Gunakan perintah lain untuk mengontrol pemutaran</li>
                </ol>
                
                <p>Situs ini hanya status web untuk bot. Bot sebenarnya berjalan melalui Discord, bukan di sini.</p>
                <p id="status-refresh">Status halaman diperbarui setiap 30 detik</p>
            </div>
        </body>
    </html>
    """

@app.route('/status')
def status():
    """Status API untuk bot"""
    global bot_connected
    
    # Update bot connected status
    bot_connected = bot and bot.is_ready() if hasattr(bot, 'is_ready') else False
    
    status_value = "online" if bot_connected else "offline"
    
    return jsonify({
        'status': status_value,
        'name': bot.user.name if bot.user else 'Unknown',
        'id': str(bot.user.id) if bot.user and bot.user else 'Unknown',
        'guilds': len(bot.guilds) if hasattr(bot, 'guilds') else 0
    })

@app.route('/uptime')
def uptime():
    """Endpoint khusus untuk UptimeRobot"""
    global bot_connected
    
    # Update bot connected status
    bot_connected = bot and bot.is_ready() if hasattr(bot, 'is_ready') else False
    
    if bot_connected:
        return "OK", 200
    else:
        return "Bot not connected", 500

@bot.event
async def on_ready():
    """Update status when bot connects"""
    global bot_connected, bot_status
    bot_connected = True
    bot_status = "online"
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

def run_flask():
    """Menjalankan server Flask"""
    # Gunakan port 5001 untuk menghindari konflik dengan workflow "Start application"
    app.run(host='0.0.0.0', port=5001)

def run_discord_bot():
    """Menjalankan bot Discord"""
    global bot_running, bot_status
    
    if not TOKEN:
        print("Error: No DISCORD_TOKEN found in environment variables")
        print("Please set your Discord bot token as an environment variable named DISCORD_TOKEN")
        bot_status = "error_no_token"
        return
    
    try:
        print("Starting music bot...")
        print(f"Discord Token available: {bool(TOKEN)}")
        print(f"Token length: {len(TOKEN) if TOKEN else 0}")
        print(f"First 5 chars of token: {TOKEN[:5]}..." if TOKEN and len(TOKEN) > 5 else "Invalid token")
        
        bot_status = "starting"
        bot.run(TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Discord login failed: {e}")
        print("Please check your Discord token and make sure it's valid")
        bot_status = "error_login_failed"
    except Exception as e:
        print(f"Bot error: {e}")
        import traceback
        traceback.print_exc()
        bot_status = "error"
    finally:
        bot_running = False
        bot_status = "stopped"

def signal_handler(sig, frame):
    """Handle process termination gracefully"""
    global bot_running
    print("Shutting down bot and webserver...")
    bot_running = False
    sys.exit(0)

# Set up signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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

if __name__ == "__main__":
    # Jalankan bot Discord di thread terpisah
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True  # Make thread a daemon so it exits when the main process exits
    bot_thread.start()
    
    # Start the monitor thread
    monitor_thread = Thread(target=monitor_bot)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Jalankan server Flask di thread utama
    run_flask()
