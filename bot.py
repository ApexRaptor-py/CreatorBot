import discord
from discord.ext import commands
from discord.ext import tasks
import feedparser
import requests 

import os

TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

ANNOUNCEMENT_CHANNEL_ID = 1513660892091256842
WELCOME_CHANNEL_ID = 1513663145787523142
ROLES_CHANNEL_ID = 1513869229806583948
YOUTUBE_CHANNEL_ID = 1513906449066229850
TWITCH_CHANNEL_ID = 1513907039968034886
VERIFY_CHANNEL_ID = 1513922042821349516

last_video_link = None
twitch_is_live = False
REACTION_ROLES = {
    "✅": "Pack Member",
    "🔴": "YouTube Notifications",
    "🟣": "Stream Notifications",
    "🇪🇺": "Europe",
    "🇺🇸": "North America",
    "🎮": "Gaming",
    "🎵": "Music",
    "🎬": "Movies & TV",
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    check_youtube.start()
    check_twitch.start()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def links(ctx):
    await ctx.send(
        "YouTube: https://www.youtube.com/@Apexx_Raptorr\n"
        "Twitch: https://www.twitch.tv/apexx_raptorr\n"
        "TikTok: https://www.tiktok.com/@apexx_raptorr"
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, link, *, message):
    await ctx.message.delete()

    await ctx.send(
        f"📢 **Announcement**\n\n"
        f"{message}\n\n"
        f"🔗 {link}"
    )

@bot.command()
async def latestvideo(ctx):
    feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCYzJkeCjGHmtHqYue7Pq5lQ"

    feed = feedparser.parse(feed_url)

    latest = feed.entries[0]

    await ctx.send(
        f"🎥 Latest Video:\n{latest.title}\n{latest.link}"
    )

@tasks.loop(minutes=5)
async def check_youtube():

    global last_video_link

    feed = feedparser.parse(
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCYzJkeCjGHmtHqYue7Pq5lQ"
    )

    latest = feed.entries[0]

    if last_video_link is None:
        last_video_link = latest.link
        return

    if latest.link != last_video_link:

        last_video_link = latest.link

        channel = bot.get_channel(YOUTUBE_CHANNEL_ID)

        if channel:
           await channel.send(
    f"@everyone\n\n"
    f"🎥 **New video from Apexx_Raptorr!**\n\n"
    f"**{latest.title}**\n\n"
    f"🔗 {latest.link}"
)

@bot.event
async def on_member_join(member):

    role = discord.utils.get(member.guild.roles, name="Hatchling")

    if role:
        await member.add_roles(role)

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        await channel.send(
            f"🎉 Welcome {member.mention}!\n\n"
            f"Thanks for joining the Apex Raptor community!\n"
            f"Be sure to check out #announcements and enjoy your stay!"
        )
@bot.command()
async def testwelcome(ctx):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        await channel.send(
            f"Welcome {ctx.author.mention}! 🎉\n"
            f"Thanks for joining the server!"
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def setuproles(ctx):
    channel = bot.get_channel(ROLES_CHANNEL_ID)

    if channel:
        message = await channel.send(
            "**Choose your roles:**\n\n"
            "🔴 YouTube Notifications\n"
            "🟣 Stream Notifications\n"
            "🇪🇺 Europe\n"
            "🇺🇸 North America\n"
            "🎮 Gaming\n"
            "🎵 Music\n"
            "🎬 Movies & TV\n\n"
            "React to this message to get or remove a role."
        )

        for emoji in ["🔴", "🟣", "🇪🇺", "🇺🇸", "🎮", "🎵", "🎬"]:
            await message.add_reaction(emoji)

        await ctx.send("✅ Permanent role message created.")

def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"

    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, params=params)
    data = response.json()

    return data["access_token"]

def is_twitch_live():
    access_token = get_twitch_access_token()

    url = "https://api.twitch.tv/helix/streams"

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "user_login": "apexx_raptorr"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return len(data["data"]) > 0

@tasks.loop(minutes=2)
async def check_twitch():
    global twitch_is_live

    live_now = is_twitch_live()

    if live_now and not twitch_is_live:
        twitch_is_live = True

        channel = bot.get_channel(TWITCH_CHANNEL_ID)

        if channel:
            await channel.send(
                "@everyone\n\n"
                "🔴 **Apexx_Raptorr is LIVE on Twitch!**\n\n"
                "Come join the stream!\n\n"
                "🔗 https://www.twitch.tv/apexx_raptorr"
            )

    if not live_now:
        twitch_is_live = False

@bot.event
async def on_raw_reaction_add(payload):

    if payload.user_id == bot.user.id:
        return

    emoji = str(payload.emoji)

    if emoji not in REACTION_ROLES:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    role_name = REACTION_ROLES[emoji]
    role = discord.utils.get(guild.roles, name=role_name)

    if role:
        if role:
            await member.add_roles(role)

    if role_name == "Pack Member":
        hatchling_role = discord.utils.get(guild.roles, name="Hatchling")

        if hatchling_role:
            await member.remove_roles(hatchling_role)

@bot.event
async def on_raw_reaction_remove(payload):

    emoji = str(payload.emoji)

    if emoji not in REACTION_ROLES:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    role_name = REACTION_ROLES[emoji]
    role = discord.utils.get(guild.roles, name=role_name)

    if role:
        await member.remove_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def setupverify(ctx):
    channel = bot.get_channel(VERIFY_CHANNEL_ID)

    if channel:
        message = await channel.send(
            "🦖 **Join the Pack**\n\n"
            "Welcome, Hatchling!\n\n"
            "Please read the rules, then react with ✅ to become a **Pack Member** "
            "and unlock the rest of the server."
        )

        await message.add_reaction("✅")

        await ctx.send("✅ Verification message created.")

bot.run(TOKEN)