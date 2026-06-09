import discord
from discord.ext import commands
from discord.ext import tasks
import feedparser

import os

TOKEN = os.getenv("DISCORD_TOKEN")

ANNOUNCEMENT_CHANNEL_ID = 1513660892091256842
WELCOME_CHANNEL_ID = 1513663145787523142
ROLES_CHANNEL_ID = 1513869229806583948

last_video_link = None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    check_youtube.start()

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

        channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

        if channel:
            await channel.send(
                f"@everyone\n\n🎥 **New Video Uploaded!**\n{latest.title}\n{latest.link}"
            )

@bot.event
async def on_member_join(member):
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
async def roles(ctx):
    channel = bot.get_channel(ROLES_CHANNEL_ID)

    if channel:
        await channel.send(
            "**Choose your roles:**\n\n"
            "🔴 YouTube Notifications\n"
            "🟣 Stream Notifications\n"
            "🇪🇺 Europe\n"
            "🇺🇸 North America\n"
            "🎮 Gaming\n"
            "🎵 Music\n"
            "🎬 Movies & TV\n\n"
            "React to this message to get a role."
        )

bot.run(TOKEN)