import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import openai

# ------------ إعداداتك ------------
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
CHANNEL_NAME = "cyber-news"   # بدون الإيموجي لأن الديسكورد يشيله في الـ code
openai.api_key = OPENAI_API_KEY

# ------------ إعداد البوت ------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()


# ------------ دالة توليد خبر سيبراني ------------
def get_cyber_news():
    prompt = (
        "اعطني خبر حديث وحقيقي قدر الإمكان يتعلق بالأمن السيبراني: "
        "هجمات – ثغرات – أدوات – تحذيرات – تحديثات. "
        "اجعله موجزًا 2-3 جمل وبعنوان واضح."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=180
    )

    return response.choices[0].message.content.strip()


# ------------ نشر خبر في قناة cyber-news ------------
async def post_news():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == CHANNEL_NAME:
                news = get_cyber_news()
                await channel.send(f"📰 **خبر الأمن السيبراني:**\n{news}")
                return


# ------------ جدولة الإرسال كل 6 ساعات ------------
@scheduler.scheduled_job("interval", hours=6)
async def scheduled_job():
    await post_news()


# ------------ أمر "وريني" لاختبار البوت ------------
@bot.command()
async def وريني(ctx):
    news = get_cyber_news()
    await ctx.send(f"📰 **خبر تجريبي:**\n{news}")


# ------------ تشغيل البوت ------------
@bot.event
async def on_ready():
    print(f"{bot.user} متصل الآن!")
    scheduler.start()


bot.run(DISCORD_TOKEN)
