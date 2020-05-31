###############################################################################
#                               BACKGROUND TASKS
###############################################################################
async def time_task():
    papal_played = False
    while not bot.is_closed():
        #######################################################################
        # Papal hour - play barka at 21.37
        #######################################################################
        if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 37 and not papal_played:
            papal_played = True
            # Find voice channel with most members
            guild = bot.get_guild(globalVars.guild_wspolnota_id)
            channel_list = [len(channel.members) for channel in guild.voice_channels]
            voice = guild.voice_client
            if voice and voice.is_connected():
                await voice.disconnect()
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()
            else:
                await guild.voice_channels[channel_list.index(max(channel_list))].connect()

            # Play barka
            audio_source = globalVars.barka_loc
            voice = guild.voice_client
            sound_tuple = (voice, audio_source)
            globalVars.mp3_queue.insert(0, sound_tuple)
            print("queued 2137 " + audio_source)

            # Send message
            await guild.text_channels[0].send("My God look at the time!")

        # Disconnect after a minute
        if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 38 and papal_played:
            guild = bot.get_guild(globalVars.guild_wspolnota_id)
            papal_played = False
            voice = guild.voice_client
            if voice and voice.is_connected():
                await voice.disconnect()


        #######################################################################
        # Banishment
        #######################################################################

        for i in range(len(globalVars.banished_users)):
            incremented = (
                globalVars.banished_users[i][0],
                globalVars.banished_users[i][1] + 1,
                globalVars.banished_users[i][2])

            # Check if penalty time passed
            if incremented[1] >= incremented[2]:
                globalVars.banished_users.pop(i)
                role = incremented[0].guild.get_role(globalVars.banished_role)
                await incremented[0].remove_roles(role)
                print(f"Removed from banishment {incremented[0].display_name}")
            else:
                globalVars.banished_users[i] = incremented

        await asyncio.sleep(5)

async def queue_task():
    #######################################################################
    # Audio Task - queue
    #######################################################################
    last_source = ""
    while not bot.is_closed():
        if len(globalVars.mp3_queue) > 0:
            # sound tuple = voice client + audio source
            voice = globalVars.mp3_queue[0][0]
            audio_source = globalVars.mp3_queue[0][1]

            if not voice.is_playing():
                # clean tmp file
                if globalVars.tmp_sounds_loc in last_source:
                    delete_file = True
                    # Check if sound is queued again
                    for sound_tuple in globalVars.mp3_queue:
                        if last_source in sound_tuple[1]:
                            delete_file = False

                    if delete_file:     
                        os.remove(last_source)
                        print(f"Removed {last_source}")

                # Play sound
                voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_source)))
                # Lower youtube volume
                if globalVars.tmp_sounds_loc in audio_source:
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.5
                
                # Move queue
                globalVars.mp3_queue.pop(0)
                last_source = audio_source
                print(f"Playing {audio_source}")

        await asyncio.sleep(1)

async def download_task():
    #######################################################################
    # Downloading in background
    #######################################################################
    while not bot.is_closed():
        if len(globalVars.download_queue) > 0:
            while len(globalVars.download_queue) > 0:
                voice, url = globalVars.download_queue.pop(0)
                loc = download.download_youtube_audio(url)
                if loc:
                    sound_tuple = (voice, loc)
                    globalVars.mp3_queue.append(sound_tuple)
                    print(f"Queued {loc}")

        await asyncio.sleep(1)