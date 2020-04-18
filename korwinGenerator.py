import os
from random import choice
import globalVar

korwin_list = []


def load_list():
    counter = 0
    print("Loading lists...")
    for entry in os.listdir(globalVar.korwin_loc):
        if os.path.isfile(os.path.join(globalVar.korwin_loc, entry)):
            with open(globalVar.korwin_loc + str(counter) + ".txt", encoding='utf-8') as fp:
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
