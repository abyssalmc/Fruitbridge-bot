import os,re,math,logging

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import app_commands
from datetime import datetime

import keep_alive

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

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

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
    a = 1.5
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

    # give role
    for i in range (5):
        removed_role = f"Tier {i + 1} {TIER_EMOJIS.get(i + 1)}"
        if removed_role in tag.roles:
            tag.remove_roles(removed_role)

    try_role = f"Tier {tier} {TIER_EMOJIS.get(tier)}"
    role = get(interaction.guild.roles, name=try_role)
    if not (role in tag.roles or role is None) :
        await tag.add_roles(role)

    return

bot.run(TOKEN)

# /result ign:AbyssalMC tag:@abyssalmc method1:Waterlog detector rail (1.2) method2:TNT ignite (1.4) method3:Survival waterlog (1.5) subtier:1.415 rank:2
