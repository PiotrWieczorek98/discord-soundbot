import globalVar
import azureDatabase
import os
import discord
from discord.ext import commands
from discord.utils import get
from random import choice


# Reload list of mp3
def load_list():
    # Clear lists
    globalVar.mp3_names.clear()
    globalVar.mp3_names_with_id.clear()

    # Download new mp3 if found
    azureDatabase.download_from_azure(globalVar.mp3_loc, globalVar.container_name_mp3, False)

    # Add mp3 to list
    for entry in os.listdir(globalVar.mp3_loc):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, entry)):
            globalVar.mp3_names.append(entry)

    globalVar.mp3_names.sort()
    counter = 0

    for entry in globalVar.mp3_names:
        counter += 1
        globalVar.mp3_names_with_id.append((counter, entry))
    print("\nSounds loaded")


# Class with usable commands
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_list()

    @commands.command(aliases=['dc', 'disconnect'])
    async def leave(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"The bot was told  to leave")

    @commands.command(aliases=['pa', 'pau'])
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            await ctx.message.add_reaction(":thumbup:")
            voice.pause()
        else:
            await ctx.send("Retard alert: Nie jest grane")

    @commands.command(aliases=['p', 'pla'])
    async def play(self, ctx, mp3: str, voice_chat_name="none"):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        for channel in ctx.guild.voice_channels:
            if channel.name == voice_chat_name:
                if voice and voice.is_connected():
                    await voice.disconnect()
                    await channel.connect()
                voice = get(self.bot.voice_clients, guild=ctx.guild)

        for entry in globalVar.mp3_names_with_id:
            if mp3.isdecimal():
                if int(mp3) in entry:
                    audio_source = globalVar.mp3_loc + entry[1]
                    sound_tuple = (voice, audio_source)
                    globalVar.mp3_queue.append(sound_tuple)
                    print("queued {}".format(entry[1]))
            else:
                if not mp3.endswith(".mp3"):
                    mp3 += ".mp3"
                if mp3 in entry:
                    audio_source = globalVar.mp3_loc + entry[1]
                    sound_tuple = (voice, audio_source)
                    globalVar.mp3_queue.append(sound_tuple)
                    print("queued {}".format(entry[1]))

    @commands.command(aliases=['ran', 'los'])
    async def random(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        entry = choice(globalVar.mp3_names)
        audio_source = globalVar.mp3_loc + entry
        sound_tuple = (voice, audio_source)
        globalVar.mp3_queue.append(sound_tuple)
        print("queued {}".format(entry[1]))

    @commands.command(aliases=['r', 'res'])
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            voice.resume()
        await ctx.message.add_reaction(":thumbup:")


    @commands.command(aliases=['s', 'sto'])
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            voice.stop()
        await ctx.message.add_reaction(":thumbup:")

    @commands.command()
    async def volume(self, ctx, value: int):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = value / 100
        await ctx.send("Zmieniono głośność na {}%".format(value))
        print("Volume changed to {}%".format(value))

    @commands.command(aliases=['ren'])
    async def rename(self, ctx, old_name, new_name):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, old_name)):
            os.rename(os.path.join(globalVar.mp3_loc, old_name), os.path.join(globalVar.mp3_loc, new_name))
            load_list()

            await ctx.send(f"Zmieniono nazwę z: " + globalVar.mp3_loc + old_name + " na: " + new_name)
            print("Renamed: " + globalVar.mp3_loc + old_name + " to: " + new_name)
        else:
            ctx.send("Nie ma takiego pliku")

    @commands.command(aliases=['del', 'delete'])
    async def remove(self, ctx, file_name):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, file_name)):
            os.remove(os.path.join(globalVar.mp3_loc, file_name))
            load_list()

            await ctx.send(f"Usunięto: " + file_name)
            print("Removed " + globalVar.mp3_loc + file_name)
        else:
            ctx.send("Nie ma takiego pliku")

    @commands.command(aliases=['l', 'sounds'])
    async def list(self, ctx):
        sounds = "```css\n[Lista Dźwięków]\n"
        for entry in globalVar.mp3_names_with_id:
            sounds += str(entry[0]) + ". " + entry[1] + "\n"

        sounds += "\n```"
        await ctx.send(sounds)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(colour=discord.Colour.orange())
        embed.set_author(name='Help')
        embed.add_field(name='play, p, pla', value='Nazwa albo numer', inline=False)
        embed.add_field(name='list, l, lis', value='Lista dźwięków', inline=False)
        embed.add_field(name='random,ran, los', value='Losowy dźwięk', inline=False)
        embed.add_field(name='ticket', value='ticket przewinienie @ping', inline=False)
        embed.add_field(name='remove,delete, del', value='delete nazwa.mp3', inline=False)
        embed.add_field(name='rename, ren', value='rename stara_nazwa.mp3 nowa_nazwa.mp3', inline=False)
        embed.add_field(name='volume', value='Zmiana głośności', inline=False)
        embed.add_field(name='leave, dc, disconnect', value='Koniec dobrej zabawy', inline=False)
        embed.add_field(name='pause, pau, pa', value='Wstrzymanie dobrej zabawy', inline=False)
        embed.add_field(name='resume, r , res', value='Wznowienie dobrej zabawy', inline=False)
        embed.add_field(name='stop,s, sto', value='Kiedy "cotentyp" leci zbyt długo', inline=False)
        await ctx.send(embed=embed)

    @play.before_invoke
    @random.before_invoke
    @volume.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Nie jesteś połączony.")


def setup(bot):
    bot.add_cog(Basic(bot))
