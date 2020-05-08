import os
from random import choice

import globalVar

korwin_list = []


def load_list():
    print("Loading lists...")
    for counter, entry in enumerate(os.listdir(globalVar.korwin_loc)):
        if os.path.isfile(os.path.join(globalVar.korwin_loc, entry)):
            with open(globalVar.korwin_loc + str(counter) + ".txt", encoding='utf-8') as fp:
                korwin_list.append(fp.read().splitlines())
    print("Korwin generator loaded")


async def korwin_generator(message):
    kor = [choice(korwin_list[index]) for index in range(5)]
    await message.channel.send(" ".join(kor))
