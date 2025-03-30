import discord
from discord.ext import commands
import asyncio
import logging
import traceback
from utils.ytdl import YTDLSource

# Fungsi music commands yang akan diimpor langsung ke bot.py

async def join(ctx, *, channel: discord.VoiceChannel = None):
    """Bergabung dengan channel suara"""
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

async def play(ctx, *, query):
    """Putar lagu dari URL atau kata kunci pencarian"""
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
            
            # Tambahkan ke antrian
            # Untuk sementara kita mainkan langsung saja tanpa antrian
            
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

async def pause(ctx):
    """Jeda lagu yang sedang diputar"""
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
        
    if ctx.voice_client.is_paused():
        return await ctx.send("Lagu sudah dijeda.")
        
    ctx.voice_client.pause()
    await ctx.send("⏸️ Menjedakan pemutaran")

async def resume(ctx):
    """Lanjutkan pemutaran lagu yang dijeda"""
    if not ctx.voice_client:
        return await ctx.send("Bot tidak terhubung ke channel suara.")
        
    if not ctx.voice_client.is_paused():
        return await ctx.send("Lagu tidak dijeda.")
        
    ctx.voice_client.resume()
    await ctx.send("▶️ Melanjutkan pemutaran")

async def skip(ctx):
    """Lewati lagu yang sedang diputar"""
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("Tidak ada lagu yang sedang diputar.")
        
    ctx.voice_client.stop()
    await ctx.send("⏭️ Melewati lagu")

async def leave(ctx):
    """Tinggalkan channel suara"""
    if not ctx.voice_client:
        return await ctx.send("Bot tidak dalam channel suara.")
        
    await ctx.voice_client.disconnect()
    await ctx.send("👋 Meninggalkan channel suara")

async def volume(ctx, volume: int):
    """Atur volume pemutaran (0-100)"""
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