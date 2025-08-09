import os,re,math,logging
import random
import time

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import app_commands, TextChannel
from datetime import datetime
from itertools import zip_longest

import keep_alive

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
SERVICE_ACCOUNT_FILE = "credentials.json"

sheet_id = '1LlWii5IAM34-Dlei9wZfDm6lMjdrFvGX7F5-tJgd35s'
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

keep_alive.keep_alive()

load_dotenv()
TOKEN, GUILD_ID = os.getenv('DISCORD_TOKEN'), 1402945521957470228

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents, status=discord.Status.do_not_disturb)

TIER_EMOJIS = {
    1: "💎", 2: "👑", 3: "🏆", 4: "⭐", 5: "✨",
}

TIER_COLOURS = {
    1: 0x30a9ff, 2: 0xffcd36, 3: 0xff6f41, 4: 0xff82ad, 5: 0x886eff
}

def add_line(filename, line):
    with open(filename, 'a') as f:
        f.write(line + '\n')
def clear_file(filename):
    with open(filename, 'w') as f:
        pass
def read_lines(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


@bot.event
async def on_ready():
    # sync commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    # add roles
    for guild in bot.guilds:
        role = get(guild.roles, name="Fruitbridger 💚")

        for member in guild.members:
            # skip bots or anyone who already has it
            if member.bot or role in member.roles:
                continue
            try:
                await member.add_roles(role, reason="Startup add roles")
            except Exception as e:
                print(f"   [ERROR] Failed on {member}: {e}")


    print(f"Fruitbridge bot is now online. ({bot.user})")



############################
## CALCULATE TIER COMMAND ##
############################
'''
@bot.tree.command(
    name="calculate_tier",
    description="Calculate your tier from your list of method subtiers."
)
@app_commands.describe(
    subtiers="Type in your method subtiers! (e.g. 1.8 2.5 3.3)"
)
async def calculate_tier(interaction: discord.Interaction, subtiers: str):
    subtiers_list = subtiers.split()
    # too few methods
    if len(subtiers_list) < 3:
        await interaction.response.send_message("You must test with at least **3 methods**!", ephemeral=True)

    # invalid args
    try:
        one_dp = re.compile(r'^[0-9]+(?:\.[0-9])?$')
        subtiers = [float(m) for m in subtiers_list]
    except ValueError:
        await interaction.response.send_message("Your arguments must all be **numbers**!", ephemeral=True)
        return

    # calculate subtier
    a = 1.35
    subtiers.sort()
    calculated_subtier = 0
    for i in range(len(subtiers_list)):
        method_subtier = subtiers[i]
        calculated_subtier += method_subtier * a ** (-1 - i)

    calculated_subtier *= (a - 1)

    calculated_subtier += 6 * a ** -len(subtiers_list)


    # get full tier
    tier = math.floor(calculated_subtier)
    half_tier = math.floor(calculated_subtier * 2) % 2
    full_tier = f"HT{tier} {TIER_EMOJIS.get(tier)}" if half_tier == 0 else f"LT{tier} {TIER_EMOJIS.get(tier)}"

    await interaction.response.send_message(f"This will give **{full_tier}** with a subtier of **{calculated_subtier:.2f}**.")
    return
'''

####################
## RESULT COMMAND ##
####################

@bot.tree.command(
    name="result",
    description="Make a tier test result for Java 12b"
)
@app_commands.describe(
    ign="Minecraft username (e.g. AbyssalMC)",
    tag="Discord tag (e.g. @abyssal)",
    method1="Hardest method (e.g. Waterlog detector rail (1.2))",
    method2="Second hardest (e.g. Shear snow golem (1.3))",
    method3="Third hardest (e.g. Inventory tap PS (1.4))",
    subtier="Subtier (e.g. 1.315)",
    rank="Rank (e.g. 1)"
)
async def result(interaction: discord.Interaction,
    ign: str,
    tag: discord.Member,
    method1: str,
    method2: str,
    method3: str,
    subtier: float,
    rank: int
    ):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            content="You need permissions to use this!",
            ephemeral=True)
        return

    # strip whitespace
    m1 = method1.strip()
    m2 = method2.strip()
    m3 = method3.strip()

    # get full tier
    tier = math.floor(subtier)
    half_tier = math.floor(subtier * 2) % 2
    full_tier = f"HT{tier}  {TIER_EMOJIS.get(tier)}" if half_tier == 0 else f"LT{tier}  {TIER_EMOJIS.get(tier)}"

    embed = discord.Embed(title=f"{ign.replace("_", "\\_")} has passed **{full_tier}** 🎉",
                          colour=TIER_COLOURS.get(tier),
                          timestamp=datetime.now())

    embed.add_field(name="Hardest methods",
                    value=f"1. {m1}\n"
                          f"2. {m2}\n"
                          f"3. {m3}\n",
                    inline=False)
    embed.add_field(
        name="Tester",
        value=f"<@{interaction.user.id}>\n\n",
        inline=False)
    embed.add_field(name="Placement",
                    value=f"Subtier: **{subtier} (#{rank})**",
                    inline=False)

    embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{ign}")

    embed.set_footer(text="Fruitbridging Tierlist Discord",
                     icon_url="https://cdn.modrinth.com/data/cached_images/ae331a16111960468ad56a3db0f1d0cdd7e1b4ed.png")


    msg = await interaction.channel.send(content=f"{tag.mention}", embed=embed)
    await interaction.response.send_message(content="The result has been printed! If you made a mistake, your original command was:\n"
                                                    f"```/result ign:{ign} tag:<@{tag.id}> method1:{m1} method2:{m2} method3:{m3} subtier:{subtier} rank:{rank}```",
                                            ephemeral=True)

    for emoji in ("🔥", "✨", "🎉"):
        await msg.add_reaction(emoji)

    # remove roles
    for i in range (5):
        if i != tier - 1:
            removed_role = get(tag.guild.roles, name=f"Tier {i + 1} {TIER_EMOJIS.get(i + 1)}")
            await tag.remove_roles(removed_role)

    # add role
    role = get(interaction.guild.roles, name=f"Tier {tier} {TIER_EMOJIS.get(tier)}")
    if not (role in tag.roles or role is None) :
        await tag.add_roles(role)

    return

@bot.event
async def on_guild_channel_create(channel):
    # only text-channels, and only those with “ticket” in the name
    if isinstance(channel, TextChannel) and "ticket" in channel.name.lower():
        await channel.send(
            "Welcome to your ticket! A staff member will be with you shortly."
        )

#################
## SAY COMMAND ##
#################
@bot.tree.command(
    name="say",
    description="Make fruitbridge say something!"
)
@app_commands.describe(
    message="Your message (e.g. Hello world!)"
)
async def result(interaction: discord.Interaction,
    message: str,
    ):
    await interaction.response.send_message(content=message)
    return


######################
## FUN FACT COMMAND ##
######################
facts = [
    "between any two irrational numbers there are infinitely many rationals.\nyet the the irrational set is uncountably larger than the rationals.",
    "the sum of the reciprocals of the primes diverges (even though primes get rarer).\n1/2 + 1/3 + 1/5 + 1/7 + /11 + ... -> ∞ ",
    "the sum of the reciprocals of the squares is exactly π²/6 .\n1 + 1/4 + 1/9 + ... = π²/6",
    "the sum of the reciprocals of the factorials is eulers number e.\n1/0! + 1/1! + 1/2! + ... = e",
    "the area enclosed by e^(–x²) and the x axis is √π.",
    "1³ + 2³ + … + n³ = (1 + 2 + … + n)².",
    "bertrand's postulate: for every whole number n greater than 1, theres at least one prime between n and 2n.",
    "green–tao theorem: there are arbitrarily long arithmetic progressions of primes.\ne.g. 3, 5, 7 and 5, 11, 17, 23, 29.",
    "you can find an arbitrarily long string of consecutive composite numbers (e.g. (k + 1)! + 2, (k + 1)! + 3, …, (k + 1)! + k + 1).",
    "the borsuk–ulam theorem implies that on earth there are two antipodal points with exactly the same temperature and pressure.",
    "R(3, 3) = 6: in any group of 6 people you always find 3 mutual friends or 3 mutual strangers.",
    "every convex polyhedron satisfies V − E + F = 2 (euler's characteristic).\nin fact, for any non-overlapping graph, V - E + R = 2.",
    "lagrange's four‐square theorem: every positive integer can be represented as a sum of four integer squares.",
    "abel–ruffini theorem: there is no general algebraic solution (radical formula) to quintic equations.",
    "even perfect numbers are of the form 2^(p–1)(2^p−1) precisely when 2^p−1 is prime .",
    "prime number theorem: the number of primes ≤ n is asymptotically n / ln(n).\nfrom this, the probability of a number being prime is asymptotically 1 / ln(n).",
    "1/7 = 0.142857… and 142857k (for k = 1…6) cyclically permutes its digits (try it out!).",
    "champernowne's constant C₁₀=0.123456789101112… is provably normal in base 10.",
    "1729 is the smallest number expressible as the sum of two cubes in two different ways: 1³ + 12³ = 9³ + 10³.",
    "euler's identity e^(iπ) + 1 = 0 ties together e, π, i, 1 and 0 in one equation.",
    "we haven't been able to prove the irrationality of e + pi, e * pi, nor for many other operations between them.",
    "take any power of 2, such as 32768. the last digit (8) will be divisible by 2, the last 2 digits (68) by 4, the last 3 (768) by 8, and so on.",
    "if the sum of digits of a number is divisible by 3, then so must be the original number. the same applies for 9.",
    "x^x^x^... diverges precisely at e^(1/e).",
    "37 is the 12th prime, and its palindrome 73 is the 21st prime.",
    "if you have a coin, on average it will take 2 tosses to get heads.\n"
    "but if the probability of getting heads halves each time, 1/2 -> 1/4 -> 1/8 -> ..., then on average you will never get heads.",
    "the maximum number of intersections of edges in a pattern lock is 12. there are 6 unique ones with this property.",
    "6 = 1 + 2 + 3 = 1 * 2 * 3",
    "(6 + 9) + (6 * 9) = 69. this actually works for any two digit number ending with 9.",
    "7 * 7 = 50 - 1",
    'the term "hundred" originally referred to the number 120 instead of 100.',
    "statistically speaking the average waffle is better at clutching than fruitbridging",
    "1/89 encodes the fibonacci sequence.",
    "if something has a 1/x chance and you do it x times theres around a 63 percent chance that it happens (for large x), which asymptotically approaches 1 - 1/e.",
    "it will on average take 145 rolls to go through this whole list."
]
@bot.tree.command(
    name="fun_fact",
    description="Find an epic super cool math fact!"
)
async def result(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(facts))
    return

######################
## TIERLIST COMMAND ##
######################

@bot.tree.command(
    name="tierlist",
    description="Send the tierlist document, containing methods and leaderboard rankings!"
)

async def result(interaction: discord.Interaction):
    await interaction.response.send_message("The tierlist can be found in <#1145284239126958131>, or by following [this link](https://docs.google.com/spreadsheets/d/1LlWii5IAM34-Dlei9wZfDm6lMjdrFvGX7F5-tJgd35s/).")
    return

#####################
## TICKET HANDLING ##
#####################

@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, TextChannel) and "ticket" in channel.name.lower():
        time.sleep(2)
        await channel.send(
            "Hello! A staff member will be with you shortly.\n\n"
            "Send clips of your hardest methods, alongside your Minecraft username and the country you'd like to represent.\n"
            "-# (this is an automated message)"
        )

#########################
## LEADERBOARD COMMAND ##
#########################

''',
    app_commands.Choice(name="Classic 360 distance", value="fruitbridge_distance"),
    app_commands.Choice(name="Ladder distance", value="fruitbridge_distance"),
    app_commands.Choice(name="Waterlog distance", value="fruitbridge_distance"),
    app_commands.Choice(name="Powder snow distance", value="fruitbridge_distance"),
    app_commands.Choice(name="Detector rail distance", value="fruitbridge_distance")'''
'''
def trim_trailing_empty(lst):
    while lst and (not lst[-1] or lst[-1][0].strip() == ''):
        lst.pop()
    return lst

def get_12b_data():
    shit = sheet.values().get(spreadsheetId=sheet_id, range='B3:Y34').execute().get('values', [])
    shit = list(zip_longest(*shit, fillvalue=""))

    countries = shit[0] + shit[5] + shit[10] + shit[15] + shit[20]
    names = shit[2] + shit[7] + shit[12] + shit[17] + shit[22]
    values = shit[3] + shit[8] + shit[13] + shit[18] + shit[23]

    countries = [s for s in countries if s.strip()]
    names = [s for s in names if s.strip()]
    values = [s for s in values if s.strip()]

    return [countries, names, values]

@bot.tree.command(
    name="leaderboard",
    description="Print the leaderboard for the specified category"
)
@app_commands.describe(
    category="Enter the category you'd like to see",
)
@app_commands.choices(category=[
    app_commands.Choice(name="Java 12b", value="java_12b")
])

async def result(interaction: discord.Interaction,
    category: app_commands.Choice[str]
    ):

    type = "leaderboard" if category.name == "Java 12b" else "distance"

    embed = discord.Embed(title=f"{category.name} {type}  🏆 ✨",
                          url="https://docs.google.com/spreadsheets/d/1LlWii5IAM34-Dlei9wZfDm6lMjdrFvGX7F5-tJgd35s",
                          colour=TIER_COLOURS.get(2)
                          )

    countries, names, values = get_12b_data()

    print(len(values), len(names), len(countries))
    lb_string = ""

    for i in range(min(10, len(values))):
        if category.name == "Java 12b":
            lb_string += f"`{values[i]}`ﾠ{names[i]} {countries[i]}\n"
        else:
            lb_string += f"`{values[i]}`ﾠ{names[i]} {countries[i]}\n"

    title = "Top 10 players" if category.name == "Java 12b" else "Top 10 records"
    embed.add_field(name=title,
                value=lb_string,
                inline=False)


    embed.add_field(name="Full leaderboard",
                    value="[Fruitbridging Tierlist](https://docs.google.com/spreadsheets/d/1LlWii5IAM34-Dlei9wZfDm6lMjdrFvGX7F5-tJgd35s)",
                    inline=False)
    embed.set_footer(text="Fruitbridging Tierlist Discord",
                     icon_url="https://cdn.modrinth.com/data/cached_images/ae331a16111960468ad56a3db0f1d0cdd7e1b4ed.png")

    await interaction.response.send_message(embed=embed)

    return
'''
#################
## MEMBER ROLE ##
#################

@bot.event
async def on_member_join(member: discord.Member):
    role = get(member.guild.roles, name="Fruitbridger 💚")

    try:
        await member.add_roles(role, reason="Auto-assign on join")
    except Exception as e:
        print(f"[ERROR] Failed to add role: {e}")




bot.run(TOKEN)


# /result ign:AbyssalMC tag:@abyssalmc method1:Waterlog detector rail (1.2) method2:TNT ignite (1.4) method3:Survival waterlog (1.5) subtier:1.415 rank:2
