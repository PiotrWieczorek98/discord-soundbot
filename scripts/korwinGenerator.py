import os
from random import choice

from scripts import globalVars

###############################################################################
# This script generates sentences like that old man
###############################################################################
korwin_list = []


def load_list():
    for counter, entry in enumerate(os.listdir(globalVars.korwin_loc)):
        if os.path.isfile(os.path.join(globalVars.korwin_loc, entry)):
            with open(f'{globalVars.korwin_loc}{counter}.txt', encoding='utf-8') as fp:
                korwin_list.append(fp.read().splitlines())
    print("\tKorwin generator loaded")


async def korwin_generator(message):
    kor = [choice(korwin_list[index]) for index in range(5)]
    await message.channel.send(" ".join(kor))
