import os
import discord
from discord.ext import commands
from discord.utils import get
from random import choice
import globalVar
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def upload_azure(file_loc: str, file_name: str):
    # Upload to cloud
    #try:
        # Create the BlobServiceClient object which will be used to create a container client
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=globalVar.container_name_mp3, blob=file_name)

    # Upload the created file
    print("\nUploading to Azure Storage as blob: " + file_loc)
    with open(file_loc, "rb") as data:
        blob_client.upload_blob(data)
    #except:
        #print("failed uploading mp3 to azure")


def load_list():
    globalVar.mp3_names.clear()
    globalVar.mp3_names_with_id.clear()

    # Download from cloud
    try:
        # Create the BlobServiceClient object which will be used to create a container client
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Get container
        container_client = blob_service_client.get_container_client(globalVar.container_name_mp3)

        # Download files
        print("\nDownloading mp3...")
        for blob in container_client.list_blobs():
            blob_client = blob_service_client.get_blob_client(container=globalVar.container_name_mp3, blob=blob.name)
            file_loc = globalVar.mp3_loc + blob.name
            if not os.path.isfile(file_loc):
                print("Downloading blob to " + file_loc)
                with open(file_loc, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
    except:
        ("failed downloading mp3 from azure")

    for entry in os.listdir(globalVar.mp3_loc):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, entry)):
            globalVar.mp3_names.append(entry)

    globalVar.mp3_names.sort()
    counter = 0

    for entry in globalVar.mp3_names:
        counter += 1
        globalVar.mp3_names_with_id.append((counter, entry))
    print("\nSounds loaded")


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
        if os.path.isfile(os.path.join(globalVar.mp3_loc, old_name)):
            os.rename(os.path.join(globalVar.mp3_loc, old_name), os.path.join(globalVar.mp3_loc, new_name))
            await ctx.send(f"Zmieniono nazwę z: " + globalVar.mp3_loc + old_name + " na: " + new_name)
            print("Renamed: " + globalVar.mp3_loc + old_name + " to: " + new_name)
            load_list()
        else:
            ctx.send("Retard alert: Nie ma takiego pliku")

    @commands.command(aliases=['del', 'delete'])
    async def remove(self, ctx, file_name):
        if os.path.isfile(os.path.join(globalVar.mp3_loc, file_name)):
            os.remove(os.path.join(globalVar.mp3_loc, file_name))
            await ctx.send(f"Usunięto: " + file_name)
            print("Removed " + globalVar.mp3_loc + file_name)
            load_list()
        else:
            ctx.send("Retard alert: Nie ma takiego pliku")

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
