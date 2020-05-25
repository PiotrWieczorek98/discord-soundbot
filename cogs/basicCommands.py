import os
import re
from random import choice

import discord
from discord.ext import commands
from discord.utils import get

# pylint: disable=fixme, import-error
from scripts import animeDetector, azureDatabase, globalVar


# Reload list of mp3
def load_list():
    # Clear lists
    globalVar.mp3_names.clear()
    globalVar.mp3_tuples.clear()

    # Download new mp3 if found
    print("Loading sounds...\n")
    azureDatabase.download_from_azure(globalVar.mp3_loc, globalVar.container_name_mp3, False)

    # Add mp3 to list
    for entry in os.listdir(globalVar.mp3_loc):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, entry)) and entry != ".gitkeep":
            globalVar.mp3_names.append(entry)

    globalVar.mp3_names.sort()
    counter = 0

    for entry in globalVar.mp3_names:
        counter += 1
        name = entry.split("_", 1)[0]
        globalVar.mp3_tuples.append((counter, entry, name))
    print("Sounds loaded\n")

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

    @commands.command()
    async def reload(self, ctx):
        load_list()

    @commands.command(aliases=['dc', 'leave'])
    async def disconnect(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"The bot was told  to leave")

    @commands.command(aliases=['p'])
    async def play(self, ctx, sound_name: str, voice_chat_name="none"):
        # Check if voice client is in right channel
        voice = ctx.guild.voice_client
        if voice_chat_name != "none":
            for channel in ctx.guild.voice_channels:
                if channel.name == voice_chat_name:
                    if voice and voice.is_connected():
                        await voice.disconnect()
                        await channel.connect()
                    else:
                        await channel.connect()
                    voice = ctx.guild.voice_client

        # check if it is a youtube video
        # Regex for yt link, extracts id
        # pylint: disable=fixme, anomalous-backslash-in-string
        link_regex = re.compile("http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?")
        vid_id = link_regex.findall(sound_name)

        # If found vid id
        if len(vid_id) > 0:
            link = "https://www.youtube.com/watch?v=" + vid_id[0][0]
            audio_source = animeDetector.download_youtube_audio(link)
            if audio_source:
                sound_tuple = (voice, audio_source)
                globalVar.mp3_queue.append(sound_tuple)
                print("queued {}".format(link))

        # Else check saved sounds
        else:
            # Find sound
            for entry in globalVar.mp3_tuples:
                if sound_name.isdecimal():
                    if int(sound_name) in entry:
                        audio_source = globalVar.mp3_loc + entry[1]
                        sound_tuple = (voice, audio_source)
                        globalVar.mp3_queue.append(sound_tuple)
                        print("queued {}".format(entry[1]))
                else:
                    if not sound_name.endswith(".mp3"):
                        sound_name += ".mp3"
                    if sound_name in entry:
                        audio_source = globalVar.mp3_loc + entry[1]
                        sound_tuple = (voice, audio_source)
                        globalVar.mp3_queue.append(sound_tuple)
                        print("queued {}".format(entry[1]))

    @commands.command(aliases=['ran'])
    async def random(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        entry = choice(globalVar.mp3_names)
        audio_source = globalVar.mp3_loc + entry
        sound_tuple = (voice, audio_source)
        globalVar.mp3_queue.append(sound_tuple)
        print("queued {}".format(entry[1]))

    @commands.command()
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            voice.stop()

    @commands.command(aliases=['l', 'sounds'])
    async def list(self, ctx):
        message = "```css\n[Lista Dźwięków]\n"
        previous_name = globalVar.mp3_tuples[0][2]

        for entry in globalVar.mp3_tuples:
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
        for entry in globalVar.mp3_queue:
            counter += 1
            message += f"{counter}. {entry[1]} \n"
        await ctx.send(message)

    @commands.command()
    async def reset(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
        if voice and voice.source:
            voice.source.cleanup()

        #Clear queue
        i = len(globalVar.mp3_queue)
        while i > 0:
            i -= 1
            entry = globalVar.mp3_queue.pop(i)
            if globalVar.tmp_sounds_loc in entry[1] and os.path.isfile(entry[1]):
                    os.remove(entry[1])
            
        print("Queue reset")

    @commands.command()
    async def shutdown(self, ctx):
        print("Shutting down...")
        await self.bot.close()

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(colour=discord.Colour.orange())
        embed.set_author(name='Help')
        embed.add_field(name='play, p', value='Odtwórz dźwięk z listy lub Youtube', inline=False)
        embed.add_field(name='skip', value='Pomiń odtwarzany plik', inline=False)
        embed.add_field(name='reset', value='Wyczyść kolejkę', inline=False)
        embed.add_field(name='queue, q', value='Kolejka', inline=False)
        embed.add_field(name='list, sounds, l', value='Lista dźwięków', inline=False)
        embed.add_field(name='random, r', value='Losowy dźwięk z listy', inline=False)
        embed.add_field(name='disconnect, dc, leave', value='Wyjście bota z voice chatu', inline=False)
        embed.add_field(name='ticket', value='Wystaw komuś jednego za anime. Użycie: ticket <powody> ping', inline=False)
        embed.add_field(name='check', value='Sprawdź ile ktoś ma ticketów <id lub ping>', inline=False)
        embed.add_field(name='shutdown', value='Restart bota', inline=False)


        await ctx.send(embed=embed)

    @play.before_invoke
    @random.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()


def setup(bot):
    bot.add_cog(Basic(bot))
