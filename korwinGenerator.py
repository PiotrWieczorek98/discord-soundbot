import os
from random import choice
import globales

korwin_list = []


def korwin_load():
    counter = 0
    for entry in os.listdir(globales.TEXT_LOC):
        if os.path.isfile(os.path.join(globales.TEXT_LOC, entry)):
            with open(globales.TEXT_LOC + str(counter) + ".txt", encoding='utf-8') as fp:
                korwin_list.append(fp.read().splitlines())
                counter += 1
    print("Korwin generator loaded")


async def korwin_generator(message):
    kor1 = choice(korwin_list[0])
    kor2 = choice(korwin_list[1])
    kor3 = choice(korwin_list[2])
    kor4 = choice(korwin_list[3])
    kor5 = choice(korwin_list[4])
    kor6 = choice(korwin_list[5])
    await message.channel.send(kor1 + kor2 + kor3 + kor4 + kor5 + kor6)
