import discord
from discord.ext import commands
from discord.utils import get
import os
import asyncio
from random import choice

BOT_TOKEN = 'NTk1NzIxNjQ5NzE5MDgzMDA4.Xba5Yw.kEDMTabHk8DHXzMFdLQLXrDsi7k'
BOT_PREFIX = 'boi '
SOUNDS_LOC = "sounds/"

bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command("help")
queue = asyncio.Queue()
play_next_song = asyncio.Event()


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('boi '))


###############################################################################
###############################################################################
@bot.command(aliases=['dc', 'disconnect'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"To nara")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Nawet mnie tam nie ma dzbanie")


###############################################################################
###############################################################################
@bot.command(aliases=['p', 'pla'])
async def play(ctx, mp3: str):
    voice = get(bot.voice_clients, guild=ctx.guild)
    sound_loc = SOUNDS_LOC + mp3 + ".mp3"

    song_there = os.path.isfile(sound_loc)
    if not song_there:
        await ctx.send("Nie ma takiego pliku dzbanie")

    if not voice.is_playing():
        voice.play(discord.FFmpegPCMAudio(sound_loc))


###############################################################################
###############################################################################
@bot.command(aliases=['ran', 'los'])
async def random(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    sound_name = choice(os.listdir(SOUNDS_LOC))
    voice.play(discord.FFmpegPCMAudio(SOUNDS_LOC + sound_name))


###############################################################################
###############################################################################
@bot.command(aliases=['l', 'sounds'])
async def list(ctx):
    sounds_list = ""
    for entry in os.listdir(SOUNDS_LOC):
        if os.path.isfile(os.path.join(SOUNDS_LOC, entry)):
            sounds_list += entry + "\n"
    await ctx.send(sounds_list)


###############################################################################
###############################################################################
@bot.command(aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        await ctx.send(":thumbup:")
        voice.pause()
    else:
        await ctx.send("Coś się popsuło")


###############################################################################
###############################################################################
@bot.command(aliases=['r', 'res'])
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        await ctx.send(":thumbup:")
        voice.resume()
    else:
        await ctx.send("Coś się popsuło")


###############################################################################
###############################################################################
@bot.command(aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        await ctx.send(":thumbup:")
        voice.stop()
    else:
        await ctx.send("Coś się popsuło")


###############################################################################
###############################################################################
@bot.command()
async def volume(ctx, value: int):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = value/100
    await ctx.send("Zmieniono głośność na {}%".format(value))


###############################################################################
###############################################################################
@bot.command()
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.orange())
    embed.set_author(name='Help')
    embed.add_field(name='play', value='Działa też p, pla. Nazwa pliku bez.mp3', inline=False)
    embed.add_field(name='list', value='Działa też l, lis. Lista dźwięków', inline=False)
    embed.add_field(name='random', value='Działa też ran, los. Lista dźwięków', inline=False)
    embed.add_field(name='volume', value='Zmiana głośności', inline=False)
    embed.add_field(name='leave', value='Działa też dc, disconnect', inline=False)
    embed.add_field(name='pause', value='Działa też pa, pau', inline=False)
    embed.add_field(name='stop', value='Działa też s, sto', inline=False)
    embed.add_field(name='resume', value='Działa też r, res', inline=False)
    await ctx.send(embed=embed)

@play.before_invoke
@random.before_invoke
@volume.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Nie jesteś połączony.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

bot.run(BOT_TOKEN)
