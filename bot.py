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
TEXT_LOC = "files/"
TIMEOUT = 60 * 30
SZYMON_ID = 200245153586216960
TOMASZ_ID = 200245734572818432
PIECZOR_ID = 200303039863717889
SOUNDS_CHANNEL = 594937312736182313
# real channel 594937312736182313
# test channel 642374894562050059

# SET PREFIX, REMOVE HELP AND LIST COMMANDS TO REPLACE IT LATER
bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command("help")
bot.remove_command("list")

# CREATE LISTS
queue = []
sound_names = []
id_names_tuples = []
korwin_list = []

# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(BOT_PREFIX))
    bot.bg_task = bot.loop.create_task(audio_player_task())
    print("\nLogged in as: " + bot.user.name + "\n")
    # LOAD SOUNDS AND TEXTS
    reload_list()
    korwin_load(korwin_list)

###############################################################################
#                                 ON MESSAGE
###############################################################################
@bot.event
async def on_message(message):
    # REACT TO SOME MESSAGES
    if bot.user.id != message.author.id:
        if "szymon" in message.content or "Szymon" in message.content:
            await message.channel.send("Szymon more like pedał hehe")
        if "gachi" in message.content:
            await message.channel.send(message.author.name + " why are you gay")
        if "hitler" in message.content or "Hitler" in message.content or "adolf" in message.content:
            await message.channel.send("Nie ma dowodów na to, że Hitler wiedział o Holocauście")
        if "korwin powiedz coś" in message.content or "Korwin powiedz coś" in message.content \
                or "korwin powiedz cos" in message.content or "Korwin powiedz cos" in message.content:
            await korwin_generator(message)

    # IF FILE WAS ATTACHED TO MESSAGE
    if len(message.attachments) > 0:
        if message.attachments[0].filename.endswith(".mp3") and bot.get_channel(SOUNDS_CHANNEL) == message.channel:
            file_name = message.attachments[0].filename
            if file_name in sound_names:
                await message.channel.send("Nazwa pliku zajęta.")
            else:
                await message.attachments[0].save(SOUNDS_LOC + file_name)
                await message.add_reaction("👌")
                print("Added " + SOUNDS_LOC + file_name)
                reload_list()

    await bot.process_commands(message)


###############################################################################
#                               BACKGROUND TASK
###############################################################################
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
                counter = 0
                print("Playing " + audio_source)

        counter += 1
        if counter > TIMEOUT:
            counter = 0

        await asyncio.sleep(1)


###############################################################################
#                                   LEAVE
###############################################################################
@bot.command(aliases=['dc', 'disconnect'])
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"To nara")
        print(f"The bot was told  to leave")
    else:
        await ctx.send("Retard alert: bota nie ma na channelu")
        print("Bot was told to leave voice channel, but was not in one")


###############################################################################
#                                   PLAY
###############################################################################
@bot.command(aliases=['p', 'pla'])
async def play(ctx, mp3: str, voice_chat_name="none"):
    voice = get(bot.voice_clients, guild=ctx.guild)
    for channel in ctx.guild.voice_channels:
        if channel.name == voice_chat_name:
            if voice and voice.is_connected():
                await voice.disconnect()
                await channel.connect()
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
        await ctx.message.add_reaction(":thumbup:")
        voice.pause()
    else:
        await ctx.send("Retard alert: Nie jest grane")


###############################################################################
#                                   RESUME
###############################################################################
@bot.command(aliases=['r', 'res'])
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        await ctx.message.add_reaction(":thumbup:")
        voice.resume()
    else:
        await ctx.send("Retard alert: Nie ma pauzy")


###############################################################################
#                                   STOP
###############################################################################
@bot.command(aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        await ctx.message.add_reaction(":thumbup:")
        voice.stop()
    else:
        await ctx.send("Retard alert: Nic nie jest grane")


###############################################################################
#                                   VOLUME
###############################################################################
@bot.command()
async def volume(ctx, value: int):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = value / 100
    await ctx.send("Zmieniono głośność na {}%".format(value))
    print("Volume changed to {}%".format(value))


###############################################################################
#                                REMOVE FILE
###############################################################################
@bot.command(aliases=['del', 'delete'])
async def remove(ctx, file_name):
    if os.path.isfile(os.path.join(SOUNDS_LOC, file_name)):
        os.remove(os.path.join(SOUNDS_LOC, file_name))
        await ctx.send(f"Usunięto: " + file_name)
        print("Removed " + SOUNDS_LOC + file_name)
        reload_list()
    else:
        ctx.send("Retard alert: Nie ma takiego pliku")


###############################################################################
#                                RENAME FILE
###############################################################################
@bot.command(aliases=['ren'])
async def rename(ctx, old_name, new_name):
    if os.path.isfile(os.path.join(SOUNDS_LOC, old_name)):
        os.rename(os.path.join(SOUNDS_LOC, old_name),os.path.join(SOUNDS_LOC, new_name))
        await ctx.send(f"Zmieniono nazwę z: " + SOUNDS_LOC + old_name + " na: " + new_name)
        print("Renamed: " + SOUNDS_LOC + old_name + " to: " + new_name)
        reload_list()
    else:
        ctx.send("Retard alert: Nie ma takiego pliku")


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
    embed.add_field(name='remove,delete, del', value='np. delete test.mp3', inline=False)
    embed.add_field(name='rename, ren', value='rename stara_nazwa.mp3 nowa_nazwa.mp3', inline=False)
    embed.add_field(name='volume', value='Zmiana głośności', inline=False)
    embed.add_field(name='leave, dc, disconnect', value='Koniec dobrej zabawy', inline=False)
    embed.add_field(name='pause, pau, pa', value='Wstrzymanie dobrej zabawy', inline=False)
    embed.add_field(name='resume, r , res', value='Wznowienie dobrej zabawy', inline=False)
    embed.add_field(name='stop,s, sto', value='Kiedy "cotentyp" leci zbyt długo', inline=False)
    await ctx.send(embed=embed)


###############################################################################
#                             ENSURE_VOICE
###############################################################################
@play.before_invoke
@random.before_invoke
@volume.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Retard alert, Nie jesteś połączony.")


###############################################################################
#                               RELOAD LIST
###############################################################################
def reload_list():
    sound_names.clear()
    id_names_tuples.clear()

    for entry in os.listdir(SOUNDS_LOC):
        if os.path.isfile(os.path.join(SOUNDS_LOC, entry)):
            sound_names.append(entry)

    sound_names.sort()
    counter = 0

    for entry in sound_names:
        counter += 1
        id_names_tuples.append((counter, entry))
    print("Sounds list loaded")


###############################################################################
#                              KORWIN GENERATOR
###############################################################################
def korwin_load(kor_list):
    counter = 0
    for entry in os.listdir(TEXT_LOC):
        if os.path.isfile(os.path.join(TEXT_LOC, entry)):
            with open(TEXT_LOC + str(counter) + ".txt", encoding='utf-8') as fp:
                kor_list.append(fp.read().splitlines())
                counter += 1
    print("Korwin list loaded")


async def korwin_generator(message):
    kor1 = choice(korwin_list[0])
    kor2 = choice(korwin_list[1])
    kor3 = choice(korwin_list[2])
    kor4 = choice(korwin_list[3])
    kor5 = choice(korwin_list[4])
    kor6 = choice(korwin_list[5])
    await message.channel.send(kor1 + kor2 + kor3 + kor4 + kor5 + kor6)


bot.run(BOT_TOKEN)
