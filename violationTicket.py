import globalVar
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import date
import discord
from discord.ext import commands


def get_ticket(violation_list: [str], user_from: str, user_to: str):
    background = Image.open(globalVar.images_loc + "background.png")
    check = Image.open(globalVar.images_loc + "check.png")
    # Checkboxes
    violation_types = [("game", 58, 195), ("meme", 419, 195), ("hentai", 782, 195), ("trap", 1052, 195),
                       ("girl", 58, 245), ("music", 419, 245), ("manga", 782, 245), ("related", 1052, 245)]
    # Fill checkboxes
    counter = 0
    ticket = background.copy()
    for entry in violation_list:
        for v_type in violation_types:
            if entry == v_type[0]:
                (name, x, y) = v_type
                area = (x, y)
                ticket.paste(check, area)
                counter += 1

    # Write text
    draw = ImageDraw.Draw(ticket)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font = ImageFont.truetype(globalVar.fonts_loc + "calibrib.ttf", 45)
    # draw.text((x, y),"Sample Text",(r,g,b))
    # Time:
    draw.text((275, 480), date.today().strftime("%d/%m/%Y"), (0, 0, 0), font=font)
    # Place:
    draw.text((275, 531), "Wspólnota KK", (0, 0, 0), font=font)
    # Issued to:
    draw.text((275, 578), user_to, (0, 0, 0), font=font)
    # Issued by:
    draw.text((275, 628), user_from, (0, 0, 0), font=font)
    # Penalty:
    if counter == 1:
        penalty = "Warning"
    elif counter == 2:
        penalty = "Confiscation of respect"
    else:
        penalty = "Silenced"
    draw.text((275, 677), penalty, (0, 0, 0), font=font)

    # Save ticket
    ticket.save(globalVar.images_loc + "ticket.png")


def load_list():
    file = open(globalVar.files_loc + "tickets.txt", encoding='utf-8')
    lines = file.read().splitlines()
    for entry in lines:
        str_tuple = entry.split(" ")
        int_tuple = (int(str_tuple[0]), int(str_tuple[1]))
        globalVar.ticket_counter.append(int_tuple)
    file.close()
    print("Ticket list loaded")


def change_counter(user_id: int, increment: bool):
    found = False
    for i in range(len(globalVar.ticket_counter)):
        if user_id == globalVar.ticket_counter[i][0]:
            found = True
            if increment:
                changed = (globalVar.ticket_counter[i][0], globalVar.ticket_counter[i][1] + 1)
            elif globalVar.ticket_counter[i][1] > 0:
                changed = (globalVar.ticket_counter[i][0], globalVar.ticket_counter[i][1] - 1)
            else:
                changed = (globalVar.ticket_counter[i][0], 0)
            globalVar.ticket_counter[i] = changed
    if not found and increment:
        globalVar.ticket_counter.append((user_id, 1))
        file = open(globalVar.files_loc + "tickets.txt", "a", encoding='utf-8')
        file.write(str(user_id) + " 1\n")
        file.close()

    # Rewrite file after update
    file = open(globalVar.files_loc + "tickets.txt", "w", encoding='utf-8')
    for entry in globalVar.ticket_counter:
        file.write(str(entry[0]) + " " + str(entry[1]) + "\n")


def get_number_of_violations(user_id: int):
    for entry in globalVar.ticket_counter:
        if user_id == entry[0]:
            return entry[1]
    return 0


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_list()

    @commands.command()
    async def ticket(self, ctx, *arg):
        v_list = []
        for entry in arg:
            v_list.append(entry)

        # Get and clean ID from mention
        target_id = v_list.pop()
        target_id = target_id.replace("<", "")
        target_id = target_id.replace(">", "")
        target_id = target_id.replace("@", "")
        target_id = target_id.replace("!", "")
        target_id = int(target_id)

        target_name = self.bot.get_user(target_id).name
        change_counter(target_id, True)
        number_of_violations = get_number_of_violations(target_id)
        get_ticket(v_list, ctx.message.author.name, target_name)

        await ctx.send(file=discord.File(globalVar.images_loc + 'ticket.png'))
        await ctx.send("To twoje " + str(number_of_violations) + " przewinienie.")

    @commands.command()
    async def increment(self, ctx, user_id):
        change_counter(int(user_id), True)
        number_of_violations = get_number_of_violations(int(user_id))
        await ctx.send("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")

    @commands.command()
    async def decrement(self, ctx, user_id):
        change_counter(int(user_id), False)
        number_of_violations = get_number_of_violations(int(user_id))
        await ctx.send("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")

    @commands.command()
    async def check(self, ctx, user_id):
        number_of_violations = get_number_of_violations(int(user_id))
        await ctx.send("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")

def setup(bot):
    bot.add_cog(Ticket(bot))
