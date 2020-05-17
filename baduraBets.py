import discord
from discord.ext import commands
from discord.utils import get

import os
import time
from riotwatcher import LolWatcher, ApiError

# Class with usable commands
class Badura(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

region = 'EUN1'
watcher = LolWatcher(os.getenv('LOL_KEY'))
badura = watcher.summoner.by_name(region, 'Kedzar')
badura_accountId = badura['id']

timeout = time.time() + 120

while time.time() < timeout:
    time.sleep(1)
    try:
        live_game = watcher.spectator.by_summoner(region, badura_accountId)
        print('game found')
        millis = int(round(time.time() * 1000))
        if live_game['mapId'] == 1 and live_game['gameStartTime'] - millis < 78000:
            print('bets open')
    except ApiError as err:
        if err.response.status_code == 404:
            print('game not found')
        else:
            raise