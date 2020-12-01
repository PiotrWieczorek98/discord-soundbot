import os, urllib, re
from random import choice

import discord
from discord.ext import commands
from discord.utils import get

from scripts import azureDatabase, globalVars, download


###############################################################################
# This cog contains bot's basic commands
###############################################################################

# Reload list of mp3
def load_list():
    # Clear lists
    globalVars.mp3_names.clear()
    globalVars.mp3_tuples.clear()

    # Download new mp3 if found
    print("\tLoading sounds...")
    azureDatabase.download_from_azure(globalVars.mp3_loc, globalVars.container_name_mp3, False)

    # Add mp3 to list
    for entry in os.listdir(globalVars.mp3_loc):
        if os.path.isfile(os.path.join(globalVars.mp3_loc, entry)) and entry != ".gitkeep":
            globalVars.mp3_names.append(entry)

    globalVars.mp3_names.sort()
    counter = 0

    for entry in globalVars.mp3_names:
        counter += 1
        name = entry.split("_", 1)[0]
        globalVars.mp3_tuples.append((counter, entry, name))
    print("\tSounds loaded")


def volume(self, ctx, value: int):
    voice = get(self.bot.voice_clients, guild=ctx.guild)
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = value / 100
    print("Volume changed to {}%".format(value))


# Class with usable commands
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_list()

    @commands.command(aliases=['p'])
    async def play(self, ctx, *args):
        #########################################################################################
        # Check if voice client is in right channel
        #########################################################################################
        #sound_name: str, voice_chat_name="none"

        # Check if channel name was given as argument
        args_list = list(args)
        voice_chat_name = args_list[-1]

        found_voice_chat = False
        for voice_chat in ctx.guild.voice_channels:
            if voice_chat_name == voice_chat.name:
                found_voice_chat = True
                args_list.pop()

        # If not try to find channel where message author is
        if not found_voice_chat:
            if ctx.author.voice:
                found_voice_chat = True
                voice_chat_name = ctx.author.voice.channel.name

        # Try to connect to given voice channel
        for voice_channel in ctx.guild.voice_channels:
            if voice_channel.name == voice_chat_name:
                if ctx.voice_client and voice_channel.name != ctx.voice_client.channel.name:
                    await ctx.voice_client.disconnect()
                    await voice_channel.connect()
                    break
                elif not ctx.voice_client:
                    await voice_channel.connect()
                    break

        if not found_voice_chat:
            return
        voice = ctx.voice_client

        #########################################################################################
        # Check local files
        #########################################################################################
        separator = '+'
        sound_name = separator.join(args_list)
        if sound_name.isdecimal():
            # Find sound in local files
            for entry in globalVars.mp3_tuples:
                if int(sound_name) in entry:
                    audio_source = globalVars.mp3_loc + entry[1]
                    sound_tuple = (voice, audio_source)
                    globalVars.mp3_queue.append(sound_tuple)
                    print(f"Queued {entry[1]}")

        #########################################################################################
        # Find video on youtube
        #########################################################################################
        else:
            # If it's a link to video
            if "https://" in sound_name:
                # if it is a playlist get urls of videos in it
                if "&list=" in sound_name:
                    urls = download.get_youtube_playlist_urls(sound_name)
                    if urls:
                        for url in urls:
                            globalVars.download_queue.append((voice, url))
                else:
                    globalVars.download_queue.append((voice, sound_name))
            # If it's not a link, find first youtube search result
            else:
                html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + sound_name)
                video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                sound_name = "https://www.youtube.com/watch?v=" + video_ids[0]
                globalVars.download_queue.append((voice, sound_name))


    # Play random local sound
    @commands.command(aliases=['ran'])
    async def random(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        await ctx.author.voice.channel.connect()

        voice = ctx.voice_client
        entry = choice(globalVars.mp3_names)
        audio_source = globalVars.mp3_loc + entry
        sound_tuple = (voice, audio_source)
        globalVars.mp3_queue.append(sound_tuple)
        print(f"Queued {entry[1]}")

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        voice = ctx.voice_client
        if voice and voice.is_playing():
            voice.stop()

    @commands.command(aliases=['list', 'sounds', 'l'])
    async def lista(self, ctx):
        message = "```css\n[Lista Dźwięków]\n"
        previous_name = globalVars.mp3_tuples[0][2]

        for entry in globalVars.mp3_tuples:
            if entry[0] < 10:
                number = str(entry[0]) + ".  "
            else:
                number = str(entry[0]) + ". "
            title = entry[1]
            name = entry[2]

            # Separate names
            if name != previous_name:
                previous_name = name
                new_line = "\n" + number + title + "\n"
            else:
                new_line = number + title + "\n"

            # Split messages every 2000 char
            if len(message) + len(new_line) < 1997:
                message += new_line
            else:
                message += "```"
                await ctx.send(message)
                message = "```css\n"

        message += "```"
        await ctx.send(message)
        print("Sent List")

    @commands.command(aliases=['q', 'kolejka'])
    async def queue(self, ctx):
        message = "Kolejka:\n"
        counter = 0
        for entry in globalVars.mp3_queue:
            counter += 1
            message += f"{counter}. {entry[1]} \n"
        if counter > 0:
            await ctx.send(message)
        else:
            await ctx.send("Kolejka jest pusta")

    @commands.command(aliases=['dc', 'leave'])
    async def disconnect(self, ctx):
        voice = ctx.voice_client
        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"The bot was told  to leave")

    @commands.command()
    async def stop(self, ctx):
        i = len(globalVars.mp3_queue)
        while i > 0:
            i -= 1
            entry = globalVars.mp3_queue.pop(i)
            if globalVars.tmp_sounds_loc in entry[1] and os.path.isfile(entry[1]):
                os.remove(entry[1])

        print("Queue reset")
        await ctx.send("Kolejka wyczyszczona.")

    @commands.command()
    async def shutdown(self, ctx):
        print("Shutting down...")
        await self.bot.close()

    @commands.command()
    async def badura(self,ctx):
        globalVars.badura_absent = True
        i = 0
        while i <= 200:
            i += 1
            await ctx.invoke(self.bot.get_command('play'), 'https://youtu.be/hb6A1ASWaN8')


    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Help", colour=discord.Colour.blue())
        embed.add_field(name='play, p', value='Odtwórz dźwięk z listy lub Youtube', inline=False)
        embed.add_field(name='skip, s', value='Pomiń odtwarzany plik', inline=False)
        embed.add_field(name='stop', value='Wyczyść kolejkę', inline=False)
        embed.add_field(name='queue, q', value='Kolejka', inline=False)
        embed.add_field(name='list, sounds, l', value='Lista dźwięków', inline=False)
        embed.add_field(name='random, r', value='Losowy dźwięk z listy', inline=False)
        embed.add_field(name='disconnect, dc, leave', value='Wyjście bota z voice chatu', inline=False)
        embed.add_field(name='ticket', value='Wystaw komuś jednego za anime. Użycie: ticket <powody> ping',
                        inline=False)
        embed.add_field(name='check', value='Sprawdź ile ktoś ma ticketów <id lub ping>', inline=False)
        embed.add_field(name='shutdown', value='Restart bota', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Basic(bot))
