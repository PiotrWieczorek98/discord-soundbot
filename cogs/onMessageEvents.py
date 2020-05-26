import asyncio
import os
import re
from random import choice

import discord
from discord.ext import commands

# pylint: disable=fixme, import-error
from scripts import globalVars, korwinGenerator, azureDatabase, animeDetector, download
from cogs import basicCommands

###############################################################################
# This cog reacts to sent messages
###############################################################################

violation_list = []

class OnMessageEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def detect_violation(self, message, file_loc):
        detected_anime_vid = animeDetector.detect_anime_video(file_loc)
        detected_anime_mp3 = animeDetector.detect_anime_music(file_loc)
        if detected_anime_vid is True or detected_anime_mp3 == 1:
            violation_list.clear()
            if detected_anime_vid:
                violation_list.append("meme")
                violation_list.append("girl")
            if detected_anime_mp3:
                violation_list.append("music")
                violation_list.append("related")
            await self.issue_ticket(message, violation_list)

        elif detected_anime_mp3 == 2:
            await self.jojo_ref(message)

        # Clean
        os.remove(file_loc)

    async def issue_ticket(self, message, viol_list):
        viol_list.append(str(message.author.mention))
        viol_list.append("auto_detected")
        ticket_command = self.bot.get_command("ticket")
        ctx = await self.bot.get_context(message)

        await message.channel.send(f"Wykryto anime w poście {message.author.mention}. Uruchamiam protokół T1CK3T")
        await ctx.invoke(ticket_command, *viol_list)

    async def jojo_ref(self, message):
        ctx = await self.bot.get_context(message)
        await ctx.send(file=discord.File(f"{globalVars.images_loc} jojo.png"))

    @commands.Cog.listener()
    async def on_message(self, message):
        # REACT TO SOME MESSAGES
        if self.bot.user.id == message.author.id:
            return

        if "szymon" in message.content or \
                "Szymon" in message.content or \
                "Badura" in message.content or \
                "badura" in message.content:
            badura = ["Szymon more like pedał hehe",
                      "Badura kawał knura",
                      "Zbadurzone perfekcyjnie"]
            await message.channel.send(choice(badura))

        if "gachi" in message.content:
            await message.channel.send(f"{message.author.name} why are you gay")

        if "hitler" in message.content or \
                "Hitler" in message.content or \
                "adolf" in message.content or \
                "Adolf" in message.content:
            hitler = ["Nie ma dowodów na to, że Hitler wiedział o Holocauście",
                      "Nie można zaprzeczyć, że dbał o swój kraj",
                      "Ja, 6 milionów, fafnoście od razu",
                      "Z raz obranej drogi nie zawracaj w tył. Nie opuszczaj wiary - w dumę białej rasy"]
            await message.channel.send(choice(hitler))

        if "korwin" in message.content or \
                "Kitler" in message.content:
            await korwinGenerator.korwin_generator(message)

        # IF FILE WAS ATTACHED TO MESSAGE
        if len(message.attachments) > 0:
            file_name = message.attachments[0].filename
            #######################################################################################################
            #                                        SOUND
            #######################################################################################################
            if file_name.endswith(".mp3"):
                # If it is a sound
                if message.channel.id == globalVars.sounds_channel_id:
                    if file_name in globalVars.mp3_names:
                        await message.channel.send("Nazwa pliku zajęta.")
                    else:
                        file_loc = globalVars.mp3_loc + file_name
                        await message.attachments[0].save(file_loc)
                        await message.add_reaction("👌")

                        # Upload file to cloud
                        azureDatabase.upload_to_azure(file_loc, file_name, globalVars.container_name_mp3)
                        # Reload mp3 list
                        basicCommands.load_list()
                        print("Added " + globalVars.mp3_loc + file_name)

            #######################################################################################################
            #                                        IMAGE
            #######################################################################################################
            elif file_name.endswith(".png") or file_name.endswith(".jpg"):
                print("Checking image...")
                file_loc = globalVars.images_loc + file_name
                await message.attachments[0].save(file_loc)

                detected_anime = animeDetector.detect_anime_image(file_loc)
                if detected_anime:
                    violation_list.clear()
                    violation_list.append("meme")
                    await self.issue_ticket(message, violation_list)

                # Clean up
                os.remove(file_loc)

            #######################################################################################################
            #                                        VIDEO
            #######################################################################################################
            elif file_name.endswith(".mp4") or file_name.endswith(".webm"):
                print("Checking video...")
                file_loc = globalVars.images_loc + file_name
                await message.attachments[0].save(file_loc)

                # Check video
                await self.detect_violation(message, file_loc)

        ###########################################################################################################
        #                                           YOUTUBE
        ###########################################################################################################
        if "youtu" in str(message.content) and "boi play" not in str(message.content):
            print("Checking youtube video...")
            # Regex for yt link, extracts id
            # pylint: disable=fixme, anomalous-backslash-in-string
            link_regex = re.compile('http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?')
            vid_id = link_regex.findall(message.content)
            # If found vid id
            if vid_id[0][0] is not None:
                link = "https://www.youtube.com/watch?v=" + vid_id[0][0]
                file_loc = download.download_youtube_video(link)

                # Check video
                await self.detect_violation(message, file_loc)

        ###########################################################################################################
        #                                           GIF
        ###########################################################################################################
        if "tenor" in str(message.content) or "giphy" in str(message.content) or "gif" in str(message.content):
            # pylint: disable=fixme, anomalous-backslash-in-string
            link_regex = re.compile('http(?:s?):\/\/.*')
            match = link_regex.match(message.content)
            # If has a link
            if match.string is not None:
                print("Checking gif...")
                found_gif = False
                found_mp4 = False
                detected_anime = False
                vid_link = ""
                # Wait for the embed to load
                await asyncio.sleep(5)

                # Check if gif is embed (links from tenor)
                embed_list = message.embeds
                if embed_list[0].video.url != discord.Embed.Empty:
                    vid_link = embed_list[0].video.url
                    if vid_link.endswith("mp4"):
                        found_mp4 = True
                    else:
                        found_gif = True

                elif embed_list[0].url != discord.Embed.Empty:
                    vid_link = embed_list[0].url
                    if vid_link.endswith("mp4"):
                        found_mp4 = True
                    else:
                        found_gif = True

                if found_gif:
                    print(vid_link)
                    file_loc = globalVars.images_loc + "test.gif"
                    download.download_url(vid_link, file_loc)
                    detected_anime = animeDetector.detect_anime_gif(file_loc)
                    # Clean up
                    os.remove(file_loc)

                elif found_mp4:
                    print(vid_link)
                    file_loc = globalVars.images_loc + "test.mp4"
                    download.download_url(vid_link, file_loc)
                    detected_anime = animeDetector.detect_anime_video(file_loc)
                    # Clean up
                    os.remove(file_loc)

                if detected_anime:
                    violation_list.clear()
                    violation_list.append("meme")
                    violation_list.append("girl")
                    await self.issue_ticket(message, violation_list)


def setup(bot):
    bot.add_cog(OnMessageEvent(bot))
