import asyncio
import discord
from discord.ext import commands
import logging
import math
import sys
import traceback
from utils.ytdl import YTDLSource

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Attempt to load opus
if not discord.opus.is_loaded():
    try:
        # Try different possible library names
        opus_libs = ['libopus.so.0', 'libopus.0.dylib', 'libopus-0.dll', 'libopus.so']
        
        for lib in opus_libs:
            try:
                discord.opus.load_opus(lib)
                if discord.opus.is_loaded():
                    print(f"Opus loaded: {lib}")
                    break
            except (OSError, TypeError):
                pass
    except Exception as e:
        # Continue without Opus - will use FFmpeg instead
        print(f"Unable to load opus: {e}")
        print("Continuing without opus support")

class MusicQueue:
    """Class to manage the music queue"""
    def __init__(self):
        self.queue = []
        self._current = None
        self.volume = 0.5
        self.loop = False
    
    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, value):
        self._current = value
    
    def add(self, item):
        self.queue.append(item)
    
    def get_next(self):
        if not self.queue:
            return None
        
        if self.loop and self.current:
            return self.current
            
        return self.queue.pop(0) if self.queue else None
    
    def clear(self):
        self.queue.clear()
        
    def size(self):
        return len(self.queue)
    
    def __bool__(self):
        return bool(self.queue)

class Music(commands.Cog):
    """Music commands for playing audio in voice channels"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}
        print("Music cog initialized")
        
    def get_queue(self, guild_id):
        """Get the queue for a guild, creating one if it doesn't exist"""
        if guild_id not in self.music_queues:
            self.music_queues[guild_id] = MusicQueue()
        return self.music_queues[guild_id]
    
    async def cleanup(self, guild):
        """Clean up resources after playback ends"""
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
            
        try:
            del self.music_queues[guild.id]
        except KeyError:
            pass
    
    async def play_next_song(self, ctx):
        """Play the next song in the queue"""
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        
        if not queue:
            await self.cleanup(ctx.guild)
            return
            
        # Get the next song
        next_song = queue.get_next()
        if not next_song:
            await self.cleanup(ctx.guild)
            return
            
        queue.current = next_song
        
        try:
            ctx.voice_client.play(
                next_song.source, 
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.handle_song_complete(ctx, e), self.bot.loop)
            )
            if hasattr(ctx.voice_client.source, 'volume'):
                ctx.voice_client.source.volume = queue.volume
            
            await ctx.send(f"▶️ Now playing: **{next_song.title}**")
        except Exception as e:
            logging.error(f"Error starting playback: {e}", exc_info=True)
            await ctx.send(f"Error playing song: {e}")
            await self.handle_song_complete(ctx, e)
    
    async def handle_song_complete(self, ctx, error):
        """Handle when a song finishes playing"""
        if error:
            logging.error(f"Player error: {error}")
            try:
                await ctx.send(f"An error occurred while playing: {error}")
            except:
                pass
            
        await self.play_next_song(ctx)
    
    @commands.command(name="join", help="Joins a voice channel")
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Join a voice channel"""
        if not channel and not ctx.author.voice:
            return await ctx.send("You are not connected to a voice channel.")
            
        channel = channel or ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel.id == channel.id:
                return
            await ctx.voice_client.move_to(channel)
        else:
            try:
                await channel.connect()
            except Exception as e:
                return await ctx.send(f"Could not connect to voice channel: {e}")
            
        await ctx.send(f"Joined {channel.name}")
    
    @commands.command(name="play", help="Plays a song from a URL or search query")
    async def play(self, ctx, *, query):
        """Play a song by URL or search query"""
        # Join the user's voice channel if not already in one
        if not ctx.voice_client:
            if not ctx.author.voice:
                return await ctx.send("You are not connected to a voice channel.")
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(f"Could not connect to voice channel: {e}")
        
        # Send processing message
        async with ctx.typing():
            try:
                # Get the song
                source = await YTDLSource.create_source(ctx, query, loop=self.bot.loop)
                
                # Add to queue
                queue = self.get_queue(ctx.guild.id)
                queue.add(source)
                
                if not ctx.voice_client.is_playing():
                    await self.play_next_song(ctx)
                else:
                    await ctx.send(f"Added to queue: **{source.title}**")
                    
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
                logging.error(f"Error playing song: {e}", exc_info=True)
    
    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, ctx):
        """Pause the currently playing song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")
            
        if ctx.voice_client.is_paused():
            return await ctx.send("The song is already paused.")
            
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused playback")
    
    @commands.command(name="resume", help="Resumes the currently paused song")
    async def resume(self, ctx):
        """Resume the currently paused song"""
        if not ctx.voice_client:
            return await ctx.send("I'm not connected to a voice channel.")
            
        if not ctx.voice_client.is_paused():
            return await ctx.send("The song is not paused.")
            
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed playback")
    
    @commands.command(name="skip", help="Skips the current song")
    async def skip(self, ctx):
        """Skip the current song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("Nothing is playing right now.")
            
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song")
    
    @commands.command(name="queue", help="Shows the current queue")
    async def queue(self, ctx):
        """Display the current queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if not queue or (not queue.current and not queue.queue):
            return await ctx.send("The queue is empty.")
            
        # Format the queue message
        msg = ["**Current Queue:**"]
        
        if queue.current:
            msg.append(f"▶️ Current: **{queue.current.title}**")
        
        if queue.queue:
            for i, song in enumerate(queue.queue, 1):
                msg.append(f"{i}. **{song.title}**")
        else:
            msg.append("*No songs in queue*")
            
        await ctx.send("\n".join(msg))
    
    @commands.command(name="clear", help="Clears the song queue")
    async def clear(self, ctx):
        """Clear the song queue"""
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        await ctx.send("🧹 Queue cleared")
    
    @commands.command(name="leave", help="Leaves the voice channel")
    async def leave(self, ctx):
        """Leave the voice channel and clear resources"""
        if not ctx.voice_client:
            return await ctx.send("I'm not in a voice channel.")
            
        await self.cleanup(ctx.guild)
        await ctx.send("👋 Left the voice channel")
    
    @commands.command(name="volume", help="Sets the volume of the player (0-100)")
    async def volume(self, ctx, volume: int):
        """Set the player volume"""
        if not ctx.voice_client or not getattr(ctx.voice_client, 'source', None):
            return await ctx.send("Nothing is playing right now.")
            
        if not 0 <= volume <= 100:
            return await ctx.send("Volume must be between 0 and 100.")
            
        # Convert to a float between 0 and 1
        volume_float = volume / 100
        
        # Set the volume
        queue = self.get_queue(ctx.guild.id)
        queue.volume = volume_float
        
        if hasattr(ctx.voice_client.source, 'volume'):
            ctx.voice_client.source.volume = volume_float
            
        await ctx.send(f"🔊 Volume set to {volume}%")
    
    @commands.command(name="now", help="Shows the currently playing song")
    async def now_playing(self, ctx):
        """Display the currently playing song"""
        queue = self.get_queue(ctx.guild.id)
        
        if not queue.current:
            return await ctx.send("Nothing is playing right now.")
            
        await ctx.send(f"▶️ Now playing: **{queue.current.title}**")
    
    @commands.command(name="loop", help="Toggles loop mode")
    async def loop(self, ctx):
        """Toggle loop mode"""
        queue = self.get_queue(ctx.guild.id)
        queue.loop = not queue.loop
        
        status = "enabled" if queue.loop else "disabled"
        await ctx.send(f"🔁 Loop mode {status}")
    
    async def ensure_voice(self, ctx):
        """Ensure the bot is in a voice channel before playing music"""
        if ctx.command.name != 'play':
            return
            
        if not ctx.voice_client:
            if not ctx.author.voice:
                raise commands.CommandError("You are not connected to a voice channel.")
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                raise commands.CommandError(f"Could not connect to voice channel: {e}")
    
    # Method untuk mengamankan before_invoke
    # Perintah play sudah mengecek keberadaan voice channel, jadi kita tidak perlu before_invoke
