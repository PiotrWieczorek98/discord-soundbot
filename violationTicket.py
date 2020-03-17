import globales
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import date
import os
import discord
from discord.ext import commands
from discord.utils import get
from random import choice


def get_ticket(violation_list: [str], user_from: str, user_to: str):
    background = Image.open(globales.IMAGES_LOC + "background.png")
    check = Image.open(globales.IMAGES_LOC + "check.png")

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
    font = ImageFont.truetype("calibrib.ttf", 45)
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
    ticket.save(globales.IMAGES_LOC + "ticket.png")


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        target = self.bot.get_user(target_id).name

        get_ticket(v_list, ctx.message.author.name, target)

        await ctx.send(file=discord.File(globales.IMAGES_LOC + 'ticket.png'))


def setup(bot):
    bot.add_cog(Ticket(bot))
