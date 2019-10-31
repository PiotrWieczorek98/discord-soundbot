import discord
from discord.ext import commands
from discord.utils import get
import os
import asyncio
from random import choice

# BOT SETTINGS
BOT_TOKEN = 'NTk1NzIxNjQ5NzE5MDgzMDA4.Xba5Yw.kEDMTabHk8DHXzMFdLQLXrDsi7k'
BOT_PREFIX = 'boi '
SOUNDS_LOC = "sounds/"
TIMEOUT = 120

# SET PREFIX, REMOVE HELP AND LIST COMMAND TO REPLACE IT LATER
bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command("help")
bot.remove_command("list")

# CREATE QUEUE
queue = []

# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(BOT_PREFIX))
    bot.bg_task = bot.loop.create_task(audio_player_task())
    print("Logged in as: " + bot.user.name + "\n")


# BACKGROUND TASK
async def audio_player_task():
    counter = 0
    while not bot.is_closed():
        if len(queue) > 0:
            sound_tuple = queue[0]
            voice = sound_tuple[0]

            if not voice.is_playing():
                audio_source = sound_tuple[1]
                voice.play(discord.FFmpegPCMAudio(audio_source))
                queue.pop(0)
        counter += 1
        await asyncio.sleep(1)

###############################################################################
#                                   LEAVE
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
#                                   PLAY
###############################################################################
@bot.command(aliases=['p', 'pla'])
async def play(ctx, mp3: str):
    voice = get(bot.voice_clients, guild=ctx.guild)

    audio_source = SOUNDS_LOC + mp3 + ".mp3"

    song_there = os.path.isfile(audio_source)
    if not song_there:
        await ctx.send("File not found")
    else:
        sound_tuple = (voice, audio_source)
        queue.append(sound_tuple)

###############################################################################
#                                   RANDOM
###############################################################################
@bot.command(aliases=['ran', 'los'])
async def random(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    sound_name = choice(os.listdir(SOUNDS_LOC))
    voice.play(discord.FFmpegPCMAudio(SOUNDS_LOC + sound_name))


###############################################################################
#                                   LIST
###############################################################################
@bot.command(aliases=['l', 'sounds'])
async def list(ctx):
    sounds_list = ""
    for entry in os.listdir(SOUNDS_LOC):
        if os.path.isfile(os.path.join(SOUNDS_LOC, entry)):
            sounds_list += entry + "\n"
    await ctx.send(sounds_list)


###############################################################################
#                                   PAUSE
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
#                                   RESUME
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
#                                   STOP
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
#                                   VOLUME
###############################################################################
@bot.command()
async def volume(ctx, value: int):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = value/100
    await ctx.send("Zmieniono głośność na {}%".format(value))


###############################################################################
#                                   HELP
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

###############################################################################
#                                 ENSURE_VOICE
###############################################################################
@play.before_invoke
@random.before_invoke
@volume.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Nie jesteś połączony.")

bot.run(BOT_TOKEN)
