import asyncio
import datetime
import os

import discord
from discord.ext import commands

from scripts import globalVars, korwinGenerator, download #,animeDetector <- disabled until a good model will be made

###############################################################################
#                                   SETUP
###############################################################################
# SET PREFIX, REMOVE COMMANDS TO REPLACE IT LATER, LOAD FILES
print("Bot starts up...\n")

bot = commands.Bot(command_prefix=globalVars.bot_prefix)
bot.remove_command("help")
bot.remove_command("list")

# Load cogs - commands in different files
initial_extensions = ["cogs.basicCommands", "cogs.violationTicketCommands", "cogs.onMessageEvents"]
for extension in initial_extensions:
    try:
        print(f"Loading {extension}...")
        bot.load_extension(extension)
        print(f"Loaded {extension}.\n")

    except Exception as e:
        print(f"Failed to load extension {extension}.")
        print(e)


###############################################################################
#                               BACKGROUND TASKS
###############################################################################
async def time_task():
    papal_played = False
    while not bot.is_closed():
        #######################################################################
        # Papal hour - play barka at 21.37
        #######################################################################
        if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 37 and not papal_played:
            papal_played = True
            # Find voice_client channel with most members
            guild = bot.get_guild(globalVars.guild_wspolnota_id)
            channel_list = [len(channel.members) for channel in guild.voice_channels]
            voice_client = guild.voice_client

            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()
            else:
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()

            # Play barka
            audio_source = globalVars.barka_loc
            voice_client = guild.voice_client
            sound_tuple = (voice_client, audio_source)
            globalVars.mp3_queue.insert(0, sound_tuple)
            print("queued 2137 " + audio_source)

            # Send message
            await guild.text_channels[0].send("My God look at the time!")

        # Disconnect after a minute
        if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 38 and papal_played:
            guild = bot.get_guild(globalVars.guild_wspolnota_id)
            papal_played = False
            voice_client = guild.voice_client

            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()

        #######################################################################
        # Banishment
        #######################################################################

        for i in range(len(globalVars.banished_users)):
            incremented = (
                globalVars.banished_users[i][0],
                globalVars.banished_users[i][1] + 1,
                globalVars.banished_users[i][2])

            # Check if penalty time passed
            if incremented[1] >= incremented[2]:
                globalVars.banished_users.pop(i)
                role = incremented[0].guild.get_role(globalVars.banished_role)
                await incremented[0].remove_roles(role)
                print(f"Removed from banishment {incremented[0].display_name}")
            else:
                globalVars.banished_users[i] = incremented

        await asyncio.sleep(5)


#######################################################################
# Voice channel play queue
#######################################################################
async def queue_task():
    last_source = ""
    while not bot.is_closed():
        if len(globalVars.mp3_queue) > 0:
            # sound tuple (placed in mp3 queue) = voice client + audio source
            voice_client = globalVars.mp3_queue[0][0]
            audio_source = globalVars.mp3_queue[0][1]

            if not voice_client.is_playing():
                # clean tmp file
                if globalVars.tmp_sounds_loc in last_source:
                    delete_file = True
                    # Check if sound is queued again
                    for sound_tuple in globalVars.mp3_queue:
                        if last_source in sound_tuple[1]:
                            delete_file = False

                    if delete_file:
                        os.remove(last_source)
                        print(f"Removed {last_source}")

                # Play sound
                voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_source)))
                # Lower youtube volume
                if globalVars.tmp_sounds_loc in audio_source:
                    voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                    voice_client.source.volume = 0.5

                # Move queue
                globalVars.mp3_queue.pop(0)
                last_source = audio_source
                print(f"Playing {audio_source}")

        await asyncio.sleep(1)


#######################################################################
# Downloading in background queue
#######################################################################
async def download_task():
    while not bot.is_closed():
        if len(globalVars.download_queue) > 0:
            voice_client, url = globalVars.download_queue.pop(0)
            loc = download.download_youtube_audio(url)
            if loc:
                sound_tuple = (voice_client, loc)
                globalVars.mp3_queue.append(sound_tuple)
                print(f"Queued {loc}")

        await asyncio.sleep(1)


###############################################################################
# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
###############################################################################
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(globalVars.bot_prefix))
    bot.loop.create_task(time_task())
    bot.loop.create_task(queue_task())
    bot.loop.create_task(download_task())

    print("Loading lists...")
    korwinGenerator.load_list()
    #animeDetector.load_lists()

    print(f"\nLogged in as: {bot.user.name}\n")


bot.run(os.getenv('BOT_TOKEN'))
