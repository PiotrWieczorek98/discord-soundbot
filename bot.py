import discord
from discord.ext import commands
from discord.utils import get
import os

BOT_TOKEN = 'NTk1NzIxNjQ5NzE5MDgzMDA4.Xba5Yw.kEDMTabHk8DHXzMFdLQLXrDsi7k'
BOT_PREFIX = 'boi '

bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")

    if not discord.opus.is_loaded():
        raise RunTimeError('Opus failed to load')

    await bot.change_presence(status=discord.Status.idle, activity = discord.Game('boi '))

###############################################################################
###############################################################################
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

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['dc','disconnect'])
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

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['p', 'pla'], description = "nazwa pliku bez mp3")
async def play(ctx, mp3: str):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    songLoc = "sounds/" + mp3 + ".mp3"

    if voice and voice.is_connected():
        await voice.move_to(channel)
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

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['pa', 'pau'], description = "pa, pau - wiadomo")
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
    else:
        print("Music not playing failed pause")
        await ctx.send("Jakbych coś groł, to bych to pauznoł")

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['r', 'res'], description = "r, res - wiadomo")
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
    else:
        print("Music is not paused")
        await ctx.send("Dyć już leci")

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['s', 'sto'], description = "s, sto - wiadomo")
async def stop(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
    else:
        print("No music playing failed to stop")
        await ctx.send("Jakbych coś groł, to bych to sztopnoł")

###############################################################################
###############################################################################
@bot.command(pass_context=True, aliases=['l', 'lis'],description = "l, lista - wypisuje listę dźwięków")
async def list(ctx):
    basepath = 'sounds/'
    soundsList = ""
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            soundsList += entry + "\n"
    await ctx.send(soundsList)

###############################################################################
###############################################################################
@bot.command()
async def help(ctx):
    embed = discord.Embed(colour = discord.Colour.orange())
    embed.set_author(name='Help')
    embed.add_field(name='play', value = 'Działa też p, pla. Nazwa pliku bez.mp3', inline = False)
    embed.add_field(name='list', value = 'Działa też l, lis. Lista dźwięków', inline = False)
    embed.add_field(name='join', value = 'Działa też j, joi', inline = False)
    embed.add_field(name='leave', value = 'Działa też dc, disconnect', inline = False)
    embed.add_field(name='pause', value = 'Działa też pa, pau', inline = False)
    embed.add_field(name='stop', value = 'Działa też s, sto', inline = False)
    embed.add_field(name='resume', value = 'Działa też r, res', inline = False)
    await ctx.send(embed = embed)


bot.run(BOT_TOKEN)
