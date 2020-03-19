import discord
from discord.ext import commands
import asyncio
from random import choice

import korwinGenerator
import globalVar
import basicCommands

###############################################################################
#                                   SETUP
###############################################################################
# SET PREFIX, REMOVE COMMANDS TO REPLACE IT LATER, LOAD FILES
bot = commands.Bot(command_prefix=globalVar.bot_prefix)
bot.remove_command("help")
bot.remove_command("list")
korwinGenerator.korwin_load()

initial_extensions = ["basicCommands", "violationTicket"]
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
            sound_tuple = queue[0]
            voice = sound_tuple[0]

            if not voice.is_playing():
                audio_source = sound_tuple[1]
                voice.play(discord.FFmpegPCMAudio(audio_source))
                globalVar.mp3_queue.pop()
                print("Played " + audio_source)

        # Banishment
        for i in range(len(globalVar.banished_users)):
            incremented = (globalVar.banished_users[i][0], globalVar.banished_users[i][1] + 1, globalVar.banished_users[i][2])
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
    print("\nLogged in as: " + bot.user.name + "\n")


###############################################################################
#                                 ON MESSAGE
###############################################################################
@bot.event
async def on_message(message):
    # REACT TO SOME MESSAGES
    if bot.user.id != message.author.id:
        if "szymon" in message.content or \
                "Szymon" in message.content or \
                "Badura" in message.content or \
                "badura" in message.content:
            badura = ["Szymon more like pedał hehe",
                      "Badura kawał knura",
                      "Zbadurzone perfekcyjnie"]
            await message.channel.send(choice(badura))
        if "gachi" in message.content:
            await message.channel.send(message.author.name + " why are you gay")
        if "hitler" in message.content or \
                "Hitler" in message.content or \
                "adolf" in message.content or \
                "Adolf" in message.content:
            hitler = ["Nie ma dowodów na to, że Hitler wiedział o Holocauście",
                      "Nie można zaprzeczyć, że dbał o swój kraj",
                      "Ja, 6 milionów, fafnoście od razu",
                      "Z raz obranej drogi nie zawracaj w tył. Nie opuszczaj wiary - w dumę białej rasy"]
            await message.channel.send(choice(hitler))
        if "korwin" in message.content:
            await korwinGenerator.korwin_generator(message)

    # IF FILE WAS ATTACHED TO MESSAGE
    if len(message.attachments) > 0:
        if message.attachments[0].filename.endswith(".mp3") and message.channel.id == globalVar.sounds_channel_id:
            file_name = message.attachments[0].filename
            if file_name in globalVar.mp3_names:
                await message.channel.send("Nazwa pliku zajęta.")
            else:
                await message.attachments[0].save(globalVar.sounds_loc + file_name)
                await message.add_reaction("👌")
                print("Added " + globalVar.sounds_loc + file_name)
                basicCommands.reload_list()

    await bot.process_commands(message)

bot.run(globalVar.bot_token)
