import os
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI

# ----------------------------------------------------
# Environment Variables on Railway
# ----------------------------------------------------
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client_ai = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------------------
# Discord Bot Setup
# ----------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

CHANNEL_NAME = "cyber-news"  # بدون الإيموجي

# ----------------------------------------------------
# Function: Generate Cyber Security News
# ----------------------------------------------------
def get_cyber_news():
    prompt = (
        "اعطني خبر حديث وحقيقي قدر الإمكان متعلق بالأمن السيبراني "
        "(هجمات، ثغرات، أدوات، تحديثات، تحذيرات). "
        "اكتبه بالعربية، مع عنوان واضح، ولا يتجاوز 3 جمل."
    )

    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()

# ----------------------------------------------------
# Send News to Channel
# ----------------------------------------------------
async def post_news():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == CHANNEL_NAME:
                news = get_cyber_news()
                await channel.send(f"📰 **خبر الأمن السيبراني:**\n{news}")
                return

# ----------------------------------------------------
# Scheduler: كل 6 ساعات
# ----------------------------------------------------
@scheduler.scheduled_job("interval", hours=6)
async def scheduled_job():
    await post_news()

# ----------------------------------------------------
# Command: !وريني (اختبار البوت)
# ----------------------------------------------------
@bot.command()
async def وريني(ctx):
    news = get_cyber_news()
    await ctx.send(f"📰 **خبر تجريبي:**\n{news}")

# ----------------------------------------------------
# Bot Start Event
# ----------------------------------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} شغال الآن!")
    scheduler.start()

# ----------------------------------------------------
# Run Bot
# ----------------------------------------------------
bot.run(DISCORD_TOKEN)
