import globalVar
import azureDatabase
import discord
import re

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import date
from discord.ext import commands


def load_list():
    azureDatabase.download_from_azure(globalVar.files_loc, globalVar.container_name_txt, True)

    file = open(globalVar.files_loc + globalVar.tickets_txt, encoding='utf-8')
    lines = file.read().splitlines()
    for entry in lines:
        str_tuple = entry.split(" ")
        int_tuple = (int(str_tuple[0]), int(str_tuple[1]))
        globalVar.ticket_counter.append(int_tuple)
    file.close()
    print("Ticket list loaded")


def get_number_of_violations(user_id: int):
    for entry in globalVar.ticket_counter:
        if user_id == entry[0]:
            return entry[1]
    return 0


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

    # Add new id if not found
    if not found and increment:
        globalVar.ticket_counter.append((user_id, 1))
        file = open(globalVar.files_loc + "tickets.txt", "a", encoding='utf-8')
        file.write(str(user_id) + " 1\n")
        file.close()

    # Rewrite file after update
    file = open(globalVar.files_loc + "tickets.txt", "w", encoding='utf-8')
    for entry in globalVar.ticket_counter:
        file.write(str(entry[0]) + " " + str(entry[1]) + "\n")
    file.close()

    # Upload files to cloud
    file_name = "tickets.txt"
    file_loc = globalVar.files_loc + file_name
    azureDatabase.upload_to_azure(file_loc, file_name, globalVar.container_name_txt)


async def banishment(target, penalty):
    # Add role
    role = target.guild.get_role(globalVar.banished_role)
    if role is not None:
        await target.add_roles(role)
    # Add to timer
    found = False
    for i in range(len(globalVar.banished_users)):
        if target == globalVar.banished_users[i][0]:
            globalVar.banished_users[i] = (target, 0, penalty)
            found = True

    if not found:
        globalVar.banished_users.append((target, 0, penalty))


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
    font = ImageFont.truetype(globalVar.fonts_loc + "calibrib.ttf", 45)
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
        penalty = "Cringe"
    elif counter == 2:
        penalty = "Confiscation of respect"
    else:
        penalty = "Dick flattening"
    draw.text((275, 677), penalty, (0, 0, 0), font=font)

    # Save ticket
    ticket.save(globalVar.images_loc + "ticket.png")


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_list()

    @commands.command()
    async def ticket(self, ctx, *arg):
        target_id = 0
        auto_detected = False
        v_list = []

        # Regular expressions to check args
        id_regex = re.compile('^[0-9]+$')
        mention_regex = re.compile('^<@![0-9]+>$')
        viol_regex = re.compile('^[a-z]+$')

        issued_from = ctx.message.author.name
        for entry in arg:

            if entry == "auto_detected":
                issued_from = "AAA"
                auto_detected = True

            elif mention_regex.match(entry):
                # clean ID from mention
                target_id = entry
                target_id = target_id.replace("<", "")
                target_id = target_id.replace("@", "")
                target_id = target_id.replace("!", "")
                target_id = target_id.replace(">", "")

            elif id_regex.match(entry):
                target_id = entry

            elif viol_regex.match(entry):
                v_list.append(entry)

        # Get member from id
        target_id = int(target_id)
        if not auto_detected:
            target = ctx.message.mentions[0]
        else:
            target = ctx.message.author
        change_counter(target_id, True)

        # Generate image
        issued_to = target.display_name
        get_ticket(v_list, issued_from, issued_to)

        # Upload files to cloud
        file_name = "tickets.txt"
        file_loc = globalVar.files_loc + file_name
        azureDatabase.upload_to_azure(file_loc, file_name, globalVar.container_name_txt)

        number_of_violations = get_number_of_violations(target_id)
        message = "To twoje " + str(number_of_violations) + " przewinienie."
        # Penalty every 3 violations
        if number_of_violations % 3 == 0:
            penalty = 30
            await banishment(target, penalty)
            message += "\nZ powodu " + str(number_of_violations) + " naruszen dostajesz banicje na " \
                       + str(penalty) + " min."
            print("Banished " + str(target.display_name))

        await ctx.send(content=message, file=discord.File(globalVar.images_loc + 'ticket.png'))
        print("id: " + str(target_id) + " ma teraz " + str(number_of_violations) + " przewinien(Ticket).")


    @commands.command()
    async def increment(self, ctx, user_id):
        change_counter(int(user_id), True)
        number_of_violations = get_number_of_violations(int(user_id))
        print("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")
        await ctx.send("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")

    @commands.command()
    async def decrement(self, ctx, user_id):
        change_counter(int(user_id), False)
        number_of_violations = get_number_of_violations(int(user_id))
        print("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")
        await ctx.send("id: " + str(user_id) + " ma teraz " + str(number_of_violations) + " przewinien.")

    @commands.command()
    async def check(self, ctx, user_id):
        mentions = ctx.message.mentions
        if len(mentions) > 0:
            target = mentions[0]
            number_of_violations = get_number_of_violations(int(target.id))

            await ctx.send("id: " + str(target.nick) + " ma " + str(number_of_violations) + " przewinien.")
            print("id: " + str(target.id) + " ma " + str(number_of_violations) + " przewinien.")
        else:
            number_of_violations = get_number_of_violations(int(user_id))

            await ctx.send("id: " + str(user_id) + " ma " + str(number_of_violations) + " przewinien.")
            print(str(user_id) + " ma " + str(number_of_violations) + " przewinien.")


def setup(bot):
    bot.add_cog(Ticket(bot))
