import asyncio
import datetime
import os
import re

import discord
from discord.ext import commands

import animeDetector
import globalVar
import korwinGenerator

###############################################################################
#                                   SETUP
###############################################################################
# SET PREFIX, REMOVE COMMANDS TO REPLACE IT LATER, LOAD FILES
bot = commands.Bot(command_prefix=globalVar.bot_prefix)
bot.remove_command("help")
bot.remove_command("list")

# Load cogs - commands in different files
initial_extensions = ["basicCommands", "violationTicketCommands", "onMessageEvents"]
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


###############################################################################
#                               BACKGROUND TASK
###############################################################################
async def background_task():
    counter = 0
    papal_played = False
    current_source = ""
    while not bot.is_closed():
        queue = globalVar.mp3_queue
        counter += 1
        #######################################################################
        # Papal hour
        # Get time
        # If hour = 21.37
        if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 37 and not papal_played:
            # Find voice channel with most members
            guild = bot.get_guild(globalVar.guild_wspolnota_id)
            papal_played = True
            channel_list = [len(channel.members) for channel in guild.voice_channels]
            voice = guild.voice_client
            if voice and voice.is_connected():
                await voice.disconnect()
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()
            else:
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()

            # Play barka
            audio_source = globalVar.barka_loc
            voice = guild.voice_client
            sound_tuple = (voice, audio_source)
            globalVar.mp3_queue.append(sound_tuple)
            print("queued 2137 " + audio_source)

            # Send message
            await guild.text_channels[0].send("My God look at the time!")

        #######################################################################
        # Audio Task
        if len(queue) > 0:
            # sound tuple = voice client + audio source
            sound_tuple = queue[0]
            voice = sound_tuple[0]

            if not voice.is_playing():
                # Delete last file if it was played from youtube
                link_regex = re.compile('youtube')
                result = link_regex.search(current_source)

                # If found match delete the file
                if result and len(result) > 0:
                    os.remove(current_source)

                new_source = sound_tuple[1]
                voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(new_source)))
                globalVar.mp3_queue.pop()
                current_source = audio_source

                print("Played " + audio_source)

        #######################################################################
        # Banishment
        for i in range(len(globalVar.banished_users)):
            incremented = (
                globalVar.banished_users[i][0],
                globalVar.banished_users[i][1] + 1,
                globalVar.banished_users[i][2])

            # Check if penalty time passed
            if incremented[1] >= incremented[2]:
                globalVar.banished_users.pop(i)
                role = incremented[0].guild.get_role(globalVar.banished_role)
                await incremented[0].remove_roles(role)
                print(f"Removed from banishment {incremented[0].display_name}")
            else:
                globalVar.banished_users[i] = incremented

        await asyncio.sleep(1)


###############################################################################
# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
###############################################################################
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(globalVar.bot_prefix))
    bot.bg_task = bot.loop.create_task(background_task())
    korwinGenerator.load_list()
    animeDetector.load_lists()

    print(f"\n Logged in as: {bot.user.name} \n")


bot.run(os.getenv('BOT_TOKEN'))
