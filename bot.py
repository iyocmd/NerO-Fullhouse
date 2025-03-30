import discord
from discord.ext import commands
import logging
import os
import asyncio
import traceback
import sys

# Import modul YTDLSource dari utils.ytdl
from utils.ytdl import YTDLSource

# Konfigurasi logging untuk lebih detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Set up intents yang lengkap
intents = discord.Intents.all()  # Menggunakan semua intents yang tersedia
intents.message_content = True   # Pastikan intent untuk membaca konten pesan diaktifkan
intents.guild_messages = True    # Aktifkan intent untuk pesan-pesan server
intents.guilds = True            # Aktifkan intent untuk server
intents.voice_states = True      # Aktifkan intent untuk voice states

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ----- DEFINISI PERINTAH MUSIK -----

@bot.command(name="join", help="Bergabung dengan channel suara")
async def join(ctx, *, channel: discord.VoiceChannel = None):
    """Bergabung dengan channel suara"""
    print(f"Menjalankan perintah join dari {ctx.author}")
    # Implementasi join command
    if not channel and not ctx.author.voice:
        return await ctx.send("Kamu tidak terhubung ke channel suara.")
        
    channel = channel or ctx.author.voice.channel
    
    if ctx.voice_client:
        if ctx.voice_client.channel.id == channel.id:
            return
        await ctx.voice_client.move_to(channel)
    else:
        try:
            await channel.connect()
        except Exception as e:
            return await ctx.send(f"Tidak dapat terhubung ke channel suara: {e}")
        
    await ctx.send(f"Bergabung ke {channel.name}")

@bot.command(name="play", help="Putar lagu dari URL atau kata kunci")
async def play(ctx, *, query):
    """Putar lagu dari URL atau kata kunci pencarian"""
    print(f"Menjalankan perintah play dari {ctx.author}: {query}")
    # Bergabung dengan channel suara pengguna jika belum terhubung
    if not ctx.voice_client:
        if not ctx.author.voice:
            return await ctx.send("Kamu tidak terhubung ke channel suara.")
        try:
            await ctx.author.voice.channel.connect()
        except Exception as e:
            return await ctx.send(f"Tidak dapat terhubung ke channel suara: {e}")
    
    # Kirim pesan menunggu
    async with ctx.typing():
        try:
            # Cari lagu
            source = await YTDLSource.create_source(ctx, query, loop=ctx.bot.loop)
            
            # Mainkan atau tambahkan ke antrian
            if ctx.voice_client.is_playing():
                await ctx.send(f"Menambahkan ke antrian: **{source.title}**")
            else:
                ctx.voice_client.play(
                    source.source,
                    after=lambda e: print(f'Player error: {e}') if e else None
                )
                await ctx.send(f"▶️ Memutar: **{source.title}**")
                
        except Exception as e:
            await ctx.send(f"Terjadi kesalahan: {e}")
            traceback.print_exc()

@bot.command(name="pause", help="Jedakan lagu yang sedang diputar")
async def pause(ctx):
    """Jeda lagu yang sedang diputar"""
    print(f"Menjalankan perintah pause dari {ctx.author}")
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
        
    if ctx.voice_client.is_paused():
        return await ctx.send("Lagu sudah dijeda.")
        
    ctx.voice_client.pause()
    await ctx.send("⏸️ Menjedakan pemutaran")

@bot.command(name="resume", help="Lanjutkan pemutaran lagu yang dijeda")
async def resume(ctx):
    """Lanjutkan pemutaran lagu yang dijeda"""
    print(f"Menjalankan perintah resume dari {ctx.author}")
    if not ctx.voice_client:
        return await ctx.send("Bot tidak terhubung ke channel suara.")
        
    if not ctx.voice_client.is_paused():
        return await ctx.send("Lagu tidak dijeda.")
        
    ctx.voice_client.resume()
    await ctx.send("▶️ Melanjutkan pemutaran")

@bot.command(name="skip", help="Lewati lagu yang sedang diputar")
async def skip(ctx):
    """Lewati lagu yang sedang diputar"""
    print(f"Menjalankan perintah skip dari {ctx.author}")
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
        
    ctx.voice_client.stop()
    await ctx.send("⏭️ Melewati lagu")

@bot.command(name="leave", help="Tinggalkan channel suara")
async def leave(ctx):
    """Tinggalkan channel suara"""
    print(f"Menjalankan perintah leave dari {ctx.author}")
    if not ctx.voice_client:
        return await ctx.send("Bot tidak dalam channel suara.")
        
    await ctx.voice_client.disconnect()
    await ctx.send("👋 Meninggalkan channel suara")

@bot.command(name="volume", help="Atur volume pemutaran (0-100)")
async def volume(ctx, volume: int):
    """Atur volume pemutaran (0-100)"""
    print(f"Menjalankan perintah volume dari {ctx.author}: {volume}")
    if not ctx.voice_client or not getattr(ctx.voice_client, 'source', None):
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
        
    if not 0 <= volume <= 100:
        return await ctx.send("Volume harus antara 0 dan 100.")
        
    # Konversi ke float antara 0 dan 1
    volume_float = volume / 100
    
    # Atur volume
    if hasattr(ctx.voice_client.source, 'volume'):
        ctx.voice_client.source.volume = volume_float
        
    await ctx.send(f"🔊 Volume diatur ke {volume}%")

@bot.command(name="queue", help="Tampilkan antrian lagu")
async def queue(ctx):
    """Tampilkan antrian lagu saat ini"""
    print(f"Menjalankan perintah queue dari {ctx.author}")
    # Untuk versi sederhana ini, kita belum mengimplementasikan sistem antrian
    # Kita bisa tambahkan nanti setelah perintah dasar berfungsi
    await ctx.send("Fitur antrian belum diimplementasikan. Akan ditambahkan segera.")

@bot.command(name="now", help="Tampilkan lagu yang sedang diputar")
async def now_playing(ctx):
    """Tampilkan informasi lagu yang sedang diputar"""
    print(f"Menjalankan perintah now dari {ctx.author}")
    # Untuk versi sederhana ini, kita belum menyimpan info lagu yang sedang diputar
    # Kita bisa tambahkan nanti setelah perintah dasar berfungsi
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
    
    await ctx.send("Fitur menampilkan lagu yang sedang diputar belum sepenuhnya diimplementasikan.")

# ----- PERINTAH UMUM -----

@bot.command(name="ping", help="Test if bot is responding")
async def ping(ctx):
    """Simple command to test if bot is responding"""
    try:
        await ctx.send("Pong! 🏓")
    except Exception as e:
        print(f"Error dalam perintah ping: {e}")
        traceback.print_exc()

@bot.command(name="help", help="Menampilkan daftar perintah yang tersedia")
async def help_command(ctx):
    """Menampilkan daftar perintah yang tersedia"""
    try:
        embed = discord.Embed(
            title="Ner-O Music Bot - Perintah",
            description="Berikut adalah daftar perintah yang tersedia:",
            color=0x7289DA
        )
        
        # Perintah musik
        music_commands = [
            "`!play <url/kata kunci>` - Putar lagu atau tambahkan ke antrian",
            "`!pause` - Jeda lagu yang sedang diputar",
            "`!resume` - Lanjutkan pemutaran lagu",
            "`!skip` - Lewati lagu yang sedang diputar",
            "`!queue` - Tampilkan antrian lagu",
            "`!now` - Tampilkan lagu yang sedang diputar",
            "`!volume <0-100>` - Atur volume pemutaran",
            "`!join` - Bergabung dengan channel suara",
            "`!leave` - Tinggalkan channel suara"
        ]
        
        # Perintah umum
        general_commands = [
            "`!help` - Menampilkan pesan bantuan ini",
            "`!info` - Menampilkan informasi tentang bot",
            "`!ping` - Menguji respons bot"
        ]
        
        embed.add_field(name="Perintah Musik", value="\n".join(music_commands), inline=False)
        embed.add_field(name="Perintah Umum", value="\n".join(general_commands), inline=False)
        embed.set_footer(text="Prefix: ! | Contoh: !play lagu favorit")
        
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error dalam perintah help: {e}")
        await ctx.send(f"Error: {e}")
        traceback.print_exc()

@bot.command(name="info", help="Menampilkan informasi tentang bot musik")
async def info(ctx):
    """Menampilkan informasi tentang bot"""
    try:
        embed = discord.Embed(
            title="Ner-O Music Bot",
            description="Bot musik Discord yang mudah digunakan",
            color=0x7289DA
        )
        
        embed.add_field(name="Server", value=f"{len(bot.guilds)}", inline=True)
        embed.add_field(name="Prefix", value="!", inline=True)
        embed.add_field(name="Commands", value=f"{len(bot.commands)}", inline=True)
        embed.set_footer(text=f"ID: {bot.user.id}")
        
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error dalam perintah info: {e}")
        await ctx.send(f"Error: {e}")
        traceback.print_exc()

# ----- EVENT HANDLERS -----

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord"""
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")
    print(f"Discord API version: {discord.__version__}")
    print(f"Jumlah server: {len(bot.guilds)}")
    print(f"Daftar perintah saat ini: {[c.name for c in bot.commands]}")
    
    # Tambahkan status custom  
    print("Mengubah presence bot...")  
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="!help | !play"
    ))
    print("Presence bot berhasil diubah")

@bot.event
async def on_disconnect():
    """Event triggered when the bot disconnects from Discord"""
    logging.warning("Bot disconnected from Discord")

@bot.event
async def on_resumed():
    """Event triggered when the bot resumes connection to Discord"""
    logging.info("Bot resumed connection to Discord")

@bot.event
async def on_message(message):
    """Event triggered when a message is received"""
    # Ignore messages from bots to prevent potential loops
    if message.author.bot:
        return
        
    # Log all messages received for debugging
    print(f"Pesan diterima: {message.content} dari {message.author}")
    
    # Proses perintah bot jika ini adalah perintah
    if message.content.startswith('!'):
        print(f"Mencoba menjalankan perintah: {message.content}")
        await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for command errors"""
    print(f"Command error detected: {error}")
    
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Perintah tidak ditemukan. Ketik `!help` untuk melihat daftar perintah.")
        return
        
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Parameter wajib tidak ada: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Parameter tidak valid: {error}")
    elif isinstance(error, commands.CommandInvokeError):
        # Check if the error is a voice connection error
        if "Cannot connect to voice" in str(error):
            await ctx.send("❌ Tidak dapat terhubung ke channel suara. Coba lagi nanti.")
        else:
            logging.error(f"Command invoke error: {error}", exc_info=True)
            await ctx.send(f"Terjadi kesalahan: {error}")
    else:
        logging.error(f"Command error: {error}", exc_info=True)
        await ctx.send(f"Terjadi kesalahan: {error}")
    
    # Cetak traceback untuk semua error
    traceback.print_exc()

# Additional helper method to check if the bot is connected and ready
def is_ready():
    """Return True if the bot is connected to Discord and ready"""
    return bot.is_closed() is False and hasattr(bot, 'user') and bot.user is not None
