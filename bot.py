import os
import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import openai

# تحميل المتغيرات من .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# إعداد البوت
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# جدول مهام
scheduler = AsyncIOScheduler()
scheduler.start()

# حدث عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# أمر بسيط: !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")

# أمر للرد باستخدام OpenAI GPT
@bot.command()
async def ask(ctx, *, question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"Error: {e}")

# مثال على مهمة مجدولة كل دقيقة
@scheduler.scheduled_job('interval', minutes=1)
async def scheduled_task():
    channel_id = int(os.getenv("CHANNEL_ID", "0"))
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send("This is a scheduled message every minute!")

# تشغيل البوت
bot.run(TOKEN)
