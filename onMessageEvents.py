import korwinGenerator
import globalVar
import basicCommands
import azureDatabase
import animeDetector
import os
import re
from random import choice
from discord.ext import commands

violation_list = []


class OnMessageEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def issue_ticket(self, message, viol_list):
        viol_list.append(str(message.author.mention))
        viol_list.append("auto_detected")
        ticket_command = self.bot.get_command("ticket")
        ctx = await self.bot.get_context(message)

        await message.channel.send("Wykryto anime w poście " + message.author.mention + ". Uruchamiam protokół T1CK3T")
        await ctx.invoke(ticket_command, *viol_list)

    @commands.Cog.listener()
    async def on_message(self, message):
        # REACT TO SOME MESSAGES
        if self.bot.user.id != message.author.id:
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
                file_name = message.attachments[0].filename
                # if contains mp3 file
                if file_name.endswith(".mp3"):
                    # If it is a sound
                    if message.channel.id == globalVar.sounds_channel_id:
                        if file_name in globalVar.mp3_names:
                            await message.channel.send("Nazwa pliku zajęta.")
                        else:
                            file_loc = globalVar.mp3_loc + file_name
                            await message.attachments[0].save(file_loc)
                            await message.add_reaction("👌")

                            # Upload file to cloud
                            azureDatabase.upload_to_azure(file_loc, file_name, globalVar.container_name_mp3)
                            # Reload mp3 list
                            basicCommands.load_list()
                            print("Added " + globalVar.mp3_loc + file_name)

                # If contains image check if anime
                elif file_name.endswith(".png") or file_name.endswith(".jpg"):
                    print("Checking image...")
                    file_loc = globalVar.images_loc + file_name
                    await message.attachments[0].save(file_loc)

                    detected_anime = animeDetector.detect_anime_image(file_loc)
                    if detected_anime:
                        violation_list.clear()
                        violation_list.append("meme")
                        await self.issue_ticket(message, violation_list)

                    # Clean up
                    os.remove(file_loc)

                # If contains video check if anime
                elif file_name.endswith(".mp4") or file_name.endswith(".webm"):
                    print("Checking video...")
                    file_loc = globalVar.images_loc + file_name
                    await message.attachments[0].save(file_loc)

                    # Check video
                    detected_anime_vid = animeDetector.detect_anime_video(file_loc)
                    detected_anime_mp3 = animeDetector.detect_anime_music(file_loc)
                    if detected_anime_vid or detected_anime_mp3:
                        violation_list.clear()
                        if detected_anime_vid:
                            violation_list.append("meme")
                            violation_list.append("girl")
                        if detected_anime_mp3:
                            violation_list.append("music")
                            violation_list.append("related")
                        await self.issue_ticket(message, violation_list)

                    # Clean
                    os.remove(file_loc)

            # Check video from youtube
            if "youtu" in str(message.content):
                print("Checking youtube video...")
                # Regex for yt link, extracts id
                link_regex = re.compile(
                    'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?')
                vid_id = re.findall(link_regex, message.content)
                link = "https://www.youtube.com/watch?v=" + vid_id[0][0]
                file_loc = animeDetector.download_youtube(link)

                # Check video
                detected_anime_vid = animeDetector.detect_anime_video(file_loc)
                detected_anime_mp3 = animeDetector.detect_anime_music(file_loc)
                if detected_anime_vid or detected_anime_mp3:
                    violation_list.clear()
                    if detected_anime_vid:
                        violation_list.append("meme")
                        violation_list.append("girl")
                    if detected_anime_mp3:
                        violation_list.append("music")
                        violation_list.append("related")
                    await self.issue_ticket(message, violation_list)

                # Clean
                os.remove(file_loc)


def setup(bot):
    bot.add_cog(OnMessageEvent(bot))