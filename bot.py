import discord
from discord.ext import commands
from discord.utils import get
import os

TOKEN = 'NTk1NzIxNjQ5NzE5MDgzMDA4.XbXrTQ.cPlF8NwvYR9EmqDTBcnJa1io8xQ'
BOT_PREFIX = 'boi '

bot = commands.Bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"No cześć")


@bot.command(pass_context=True, aliases=['l', 'dc','disconnect'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"To nara")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Nawet mnie tam nie ma dbanie")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, mp3: str):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    songLoc = "sounds/" + mp3 + ".mp3"

    if voice and voice.is_connected():
        await voice.move_to(channel)
        await ctx.send(f"No siema")
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    song_there = os.path.isfile(songLoc)
    try:
        if not song_there:
            await ctx.send("Nie ma takiego pliku dzbanie")
    except PermissionError:
        await ctx.send("ERROR")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)

    voice.play(discord.FFmpegPCMAudio(songLoc), after=lambda e: print("Song done!"))
    #voice.source = discord.PCMVolumeTransformer(voice.source)
    #voice.source.volume = 0.07

@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
    else:
        print("Music not playing failed pause")
        await ctx.send("Jakbych coś groł, to bych to pauznoł")


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
    else:
        print("Music is not paused")
        await ctx.send("Dyć już leci")


@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
    else:
        print("No music playing failed to stop")
        await ctx.send("Jakbych coś groł, to bych to sztopnoł")
bot.run(TOKEN)
