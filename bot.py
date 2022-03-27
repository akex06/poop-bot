import discord
import sqlite3
import PIL
import random
import json

from random import randint
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

conn = sqlite3.connect("./files/poop.db")
c = conn.cursor()

def get_prefix(client, message):
    result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (message.guild.id, )).fetchone()
    if not result:
        c.execute("INSERT INTO prefixes VALUES (?, ?)", ("p!", message.guild.id))
        conn.commit()
        return "p!"
    return result[0]

client = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all())

@client.event
async def on_ready():
    print(f"[ READY ]: {client.user}")
    c.execute("CREATE TABLE IF NOT EXISTS prefixes (prefix STRING, guild INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS poop (member int, guild int, poop1 int, poop2 int, poop3 int, poop4 int, poop5 int, toilet int)")
    conn.commit()

@client.event
async def on_guild_join(guild):
    print(f"[ GUILD+ ]: {guild.name}")
    result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id, )).fetchone()

    if not result:
        c.execute("INSERT INTO prefixes VALUES (?, ?)", ("p!", guild.id))
        conn.commit()

@client.event
async def on_guild_leave(guild):
    print(f"[ GUILD- ]: {guild.name}")

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        prefix = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (message.guild.id, )).fetchone()
        await message.reply(f"My prefix: `{prefix[0]}`")

    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Use p!help for a list of all commands")

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Wait {round(error.retry_after, 2)} seconds for using this command again")

@client.command(aliases = ["bal"])
async def poopbal(ctx, member : discord.Member = None):
    member = member or ctx.author

    data = await getPoops(member)
    toiletLevel = await getToilet(member)
   
    fondo = Image.open("./files/images/fondo.png")
    toilet = Image.open(f"./files/images/toilet{toiletLevel}.png").resize((90, 90))
    fondo.paste(toilet, (485, 360), toilet)
    font = ImageFont.truetype("./files/font.otf", size = 50)
    d = ImageDraw.Draw(fondo)
    d.text((150, 124), str(data[0]), font = font, fill = (255, 255, 255))
    d.text((150, 250), str(data[1]), font = font, fill = (255, 255, 255))
    d.text((150, 376), str(data[2]), font = font, fill = (255, 255, 255))
    d.text((590, 250), str(data[3]), font = font, fill = (255, 255, 255))
    d.text((590, 124), str(data[4]), font = font, fill = (255, 255, 255))
    d.text((590, 376), f"Level {toiletLevel}", font = font, fill = (255, 255, 255))

    fondo.save("./files/images/fondo-last.png")

    await ctx.send(file = discord.File("./files/images/fondo-last.png"))

def get_cooldown(message):
    with open("./files/poop.json", "r") as f:
        data = json.load(f)

    result = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?", (message.author.id, message.guild.id)).fetchone()[0]

    return commands.Cooldown(1, data["cooldowns"][f"toilet{result}"])


@client.command()
@commands.dynamic_cooldown(get_cooldown, commands.BucketType.user)
async def poop(ctx):
    await checkPoops(ctx.author)

    toilet = await getToilet(ctx.author)

    obtained_poops = await addPoop(ctx.author, toilet)
    
    with open("./files/poop.json", "r") as f:
        data = json.load(f)
    
    n = 0
    string = ""

    for i in obtained_poops:
        n += 1
        string += f"{data['poops'][f'poop{n}']['name']}: +{i} <:poop{n}:{data['emoji'][f'poop{n}']}>\n"


    embed = discord.Embed(description = f"Poops Obtained: {string}", color = discord.Color.green())
    embed.set_author(icon_url = client.user.avatar.url, name = "Satisfying Poop")
    

    await ctx.send(embed = embed)

@client.command()
async def levelup(ctx):
    member = ctx.author
    await checkPoops(member)

    with open("./files/poop.json", "r") as f:
        data = json.load(f)

    poops = await getPoops(member)

    toilet = await getToilet(member)
    embed = discord.Embed(title = "Level Up", description = f"Use p!help for a list of all the commands", color = discord.Colour.green())
    if toilet == 5:
        embed.add_field(name = "Level up :white_check_mark:", value = "You already have the max toilet level <:toilet5:957708789442830397>")
        await ctx.send(embed = embed)
        return

    n = 0
    string = ""
    l = []

    for i in data["levelup"][str(toilet)].values():
        n += 1
        string += f"{data['poops'][f'poop{n}']['name']} <:{data['emoji'][f'poop{n}']}:{data['emoji'][f'poop{n}']}> **{poops[n - 1]}**/**{i}**\n"
        l.append(poops[n - 1] >= i)
    
    if all(i == True for i in l):
        embed.add_field(name = "Level Up :white_check_mark:", value = f"You have a level {toilet + 1} toilet <:toilet{toilet + 1}:{data['emoji'][f'toilet{toilet + 1}']}>")
        levelup = data["levelup"][str(toilet)].values()
        sql = f"UPDATE poop SET toilet = toilet + 1, {', '.join([f'{x} = {x} - ?' for x in data['levelup'][str(toilet)]])}"
        val = tuple([x for x in data["levelup"][str(toilet)].values()])
        c.execute(sql, val)
        conn.commit()
    else:
        embed.add_field(name = "Poops Needed", value = string)

    await ctx.send(embed = embed)

async def checkPoops(member):
    result = c.execute("SELECT member FROM poop WHERE member = ? AND guild = ?", (member.id, member.guild.id)).fetchone()
    if not result:
        c.execute("INSERT INTO poop VALUES (?, ?, 0, 0, 0, 0, 0, 1)", (member.id, member.guild.id))
        conn.commit()

async def getPoops(member):
    await checkPoops(member)
    
    result = c.execute("SELECT poop1, poop2, poop3, poop4, poop5 FROM poop WHERE member = ? AND guild = ?", (member.id, member.guild.id)).fetchone()
    return result

async def getToilet(member):
    result = c.execute("SELECT toilet FROM poop WHERE member = ? AND guild = ?", (member.id, member.guild.id)).fetchone()
    return result[0]

async def addPoop(member, toilet):
    with open("./files/poop.json", "r") as f:
        data = json.load(f)

    string = "UPDATE poop SET " + ", ".join([f"{x} = {x} + ?" for x in data["winnings"][str(toilet)]])
    val = tuple([random.randint(x[0], x[1]) for x in data["winnings"][str(toilet)].values()], )

    c.execute(string, val)
    conn.commit()

    return val

client.run("OTU3NjIzOTc5MTczMTE3OTgz.YkBe1A.FRvgun74_CoZD12i6k8UEO9UYcQ")