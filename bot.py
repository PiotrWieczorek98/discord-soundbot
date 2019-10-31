import discord
from discord.ext import commands
from discord.utils import get
import os
import asyncio
import bisect
from random import choice

# BOT SETTINGS
BOT_TOKEN = 'NTk1NzIxNjQ5NzE5MDgzMDA4.Xba5Yw.kEDMTabHk8DHXzMFdLQLXrDsi7k'
BOT_PREFIX = 'boi '
SOUNDS_LOC = "sounds/"
TIMEOUT = 120
SZYMON_ID = 200245153586216960
TOMASZ_ID = 200245734572818432
PIECZOR_ID = 200303039863717889

# SET PREFIX, REMOVE HELP AND LIST COMMANDS TO REPLACE IT LATER
bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command("help")
bot.remove_command("list")

# CREATE LISTS
queue = []
sound_names = []
id_names_tuples = []

# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(BOT_PREFIX))
    bot.bg_task = bot.loop.create_task(audio_player_task())
    print("Logged in as: " + bot.user.name + "\n")

    # LOAD SOUNDS
    for entry in os.listdir(SOUNDS_LOC):
        if os.path.isfile(os.path.join(SOUNDS_LOC, entry)):
            sound_names.append(entry)
    sound_names.sort()
    counter = 0
    for entry in sound_names:
        counter += 1
        id_names_tuples.append((counter, entry))


@bot.event
async def on_message(message):
    if bot.user.id != message.author.id:
        if "szymon" in message.content or "Szymon" in message.content:
            await message.channel.send("Szymon more like pedał hehe")
        if "gachi" in message.content:
            await message.channel.send(message.author.name + " why are you gay")

#    if message.author.id == SZYMON_ID:
 #       await message.add_reaction("💩")

    await bot.process_commands(message)


# BACKGROUND TASK
async def audio_player_task():
    counter = 0
    booly = True
    while not bot.is_closed():
        if len(queue) > 0:
            sound_tuple = queue[0]
            voice = sound_tuple[0]

            if not voice.is_playing():
                audio_source = sound_tuple[1]
                voice.play(discord.FFmpegPCMAudio(audio_source))
                queue.pop(0)
        counter += 1
        if counter > 1:
            counter = 0

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

    for item in id_names_tuples:
        if mp3.isdecimal():
            if int(mp3) in item:
                audio_source = SOUNDS_LOC + item[1]
                sound_tuple = (voice, audio_source)
                queue.append(sound_tuple)
        else:
            if not mp3.endswith(".mp3"):
                mp3 += ".mp3"
            if mp3 in item:
                audio_source = SOUNDS_LOC + item[1]
                sound_tuple = (voice, audio_source)
                queue.append(sound_tuple)

###############################################################################
#                                   RANDOM
###############################################################################
@bot.command(aliases=['ran', 'los'])
async def random(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    audio_source = SOUNDS_LOC + choice(sound_names)
    sound_tuple = (voice, audio_source)
    queue.append(sound_tuple)

###############################################################################
#                                   LIST
###############################################################################
@bot.command(aliases=['l', 'sounds'])
async def list(ctx):
    sounds = "```css\n[Lista Dźwięków]\n"

    for entry in id_names_tuples:
        sounds += str(entry[0]) + ". " + entry[1] + "\n"

    sounds += "\n```"
    await ctx.send(sounds)


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
    embed.add_field(name='play, p, pla', value='Nazwa pliku bez.mp3', inline=False)
    embed.add_field(name='list, l, lis', value='Lista dźwięków', inline=False)
    embed.add_field(name='random,ran, los', value='Losowy dźwięk', inline=False)
    embed.add_field(name='volume', value='Zmiana głośności', inline=False)
    embed.add_field(name='leave, dc, disconnect', value='Koniec dobrej zabawy', inline=False)
    embed.add_field(name='pause, pau, pa', value='Wstrzymanie dobrej zabawy', inline=False)
    embed.add_field(name='resume, r , res', value='Wznowienie dobrej zabawy', inline=False)
    embed.add_field(name='stop,s, sto', value='Kiedy "cotentyp" leci zbyt długo', inline=False)
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
