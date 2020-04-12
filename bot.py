import korwinGenerator
import animeDetector
import globalVar
import discord
import asyncio
import os
from discord.ext import commands

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
async def audio_task():
    counter = 0
    while not bot.is_closed():
        queue = globalVar.mp3_queue
        counter += 1

        # Audio Task
        if len(queue) > 0:
            # sound tuple = voice client + audio source
            sound_tuple = queue[0]
            voice = sound_tuple[0]

            if not voice.is_playing():
                audio_source = sound_tuple[1]
                voice.play(discord.FFmpegPCMAudio(audio_source))
                globalVar.mp3_queue.pop()
                print("Played " + audio_source)

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
                print("Removed from banishment " + str(incremented[0].display_name))
            else:
                globalVar.banished_users[i] = incremented

        await asyncio.sleep(1)


# WHEN READY CHANGE STATUS AND CREATE BACKGROUND TASK
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(globalVar.bot_prefix))
    bot.bg_task = bot.loop.create_task(audio_task())
    korwinGenerator.load_list()
    animeDetector.load_lists()

    print("\nLogged in as: " + bot.user.name + "\n")


bot.run(os.getenv('BOT_TOKEN'))
