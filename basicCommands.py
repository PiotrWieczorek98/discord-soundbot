import os
import discord
from discord.ext import commands
from discord.utils import get
from random import choice
import globales


def reload_list():
    globales.sound_names.clear()
    globales.id_names_tuples.clear()

    for entry in os.listdir(globales.SOUNDS_LOC):
        if os.path.isfile(os.path.join(globales.SOUNDS_LOC, entry)):
            globales.sound_names.append(entry)

    globales.sound_names.sort()
    counter = 0

    for entry in globales.sound_names:
        counter += 1
        globales.id_names_tuples.append((counter, entry))
    print("Sounds loaded")


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        reload_list()

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

        for entry in globales.id_names_tuples:
            if mp3.isdecimal():
                if int(mp3) in entry:
                    audio_source = globales.SOUNDS_LOC + entry[1]
                    sound_tuple = (voice, audio_source)
                    globales.queue.append(sound_tuple)
                    print("queued {}".format(entry[1]))
            else:
                if not mp3.endswith(".mp3"):
                    mp3 += ".mp3"
                if mp3 in entry:
                    audio_source = globales.SOUNDS_LOC + entry[1]
                    sound_tuple = (voice, audio_source)
                    globales.queue.append(sound_tuple)
                    print("queued {}".format(entry[1]))

    @commands.command(aliases=['ran', 'los'])
    async def random(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        entry = choice(globales.sound_names)
        audio_source = globales.SOUNDS_LOC + entry
        sound_tuple = (voice, audio_source)
        globales.queue.append(sound_tuple)
        print("queued {}".format(entry[1]))

    @commands.command(aliases=['r', 'res'])
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            await ctx.message.add_reaction(":thumbup:")
            voice.resume()
        else:
            await ctx.send("Retard alert: Nie ma pauzy")

    @commands.command(aliases=['s', 'sto'])
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            await ctx.message.add_reaction(":thumbup:")
            voice.stop()
        else:
            await ctx.send("Retard alert: Nic nie jest grane")

    @commands.command()
    async def volume(self, ctx, value: int):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = value / 100
        await ctx.send("Zmieniono głośność na {}%".format(value))
        print("Volume changed to {}%".format(value))

    @commands.command(aliases=['ren'])
    async def rename(self, ctx, old_name, new_name):
        if os.path.isfile(os.path.join(globales.SOUNDS_LOC, old_name)):
            os.rename(os.path.join(globales.SOUNDS_LOC, old_name), os.path.join(globales.SOUNDS_LOC, new_name))
            await ctx.send(f"Zmieniono nazwę z: " + globales.SOUNDS_LOC + old_name + " na: " + new_name)
            print("Renamed: " + globales.SOUNDS_LOC + old_name + " to: " + new_name)
            reload_list()
        else:
            ctx.send("Retard alert: Nie ma takiego pliku")

    @commands.command(aliases=['del', 'delete'])
    async def remove(self, ctx, file_name):
        if os.path.isfile(os.path.join(globales.SOUNDS_LOC, file_name)):
            os.remove(os.path.join(globales.SOUNDS_LOC, file_name))
            await ctx.send(f"Usunięto: " + file_name)
            print("Removed " + globales.SOUNDS_LOC + file_name)
            reload_list()
        else:
            ctx.send("Retard alert: Nie ma takiego pliku")

    @commands.command(aliases=['l', 'sounds'])
    async def list(self, ctx):
        sounds = "```css\n[Lista Dźwięków]\n"
        for entry in globales.id_names_tuples:
            sounds += str(entry[0]) + ". " + entry[1] + "\n"

        sounds += "\n```"
        await ctx.send(sounds)

    @commands.command()
    async def help(self, ctx):
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
