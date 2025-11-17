import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import aiohttp
import asyncio
from dotenv import load_dotenv
import feedparser
import random
from bs4 import BeautifulSoup

load_dotenv()

intents = discord.Intents.default()
# لا نحتاج message_content للـ slash commands
# لا نحتاج command_prefix لأننا نستخدم slash commands فقط
bot = commands.Bot(command_prefix=None, intents=intents)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = '「📰」cyber-news'

# مصادر RSS للأخبار السيبرانية (مجانية تماماً)
CYBER_NEWS_RSS_FEEDS = [
    'https://feeds.feedburner.com/TheHackersNews',
    'https://www.bleepingcomputer.com/feed/',
    'https://feeds.feedburner.com/securityweek',
    'https://www.darkreading.com/rss.xml',
    'https://krebsonsecurity.com/feed/',
    'https://www.securityweek.com/rss',
]

def clean_html(text):
    """تنظيف HTML من النص"""
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

async def generate_cyber_news():
    """جلب خبر سيبراني من RSS feeds (مجاني تماماً)"""
    # اختيار مصدر عشوائي
    rss_url = random.choice(CYBER_NEWS_RSS_FEEDS)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.read()
                    feed = feedparser.parse(content)
                    
                    if feed.entries:
                        # اختيار خبر عشوائي من آخر 10 أخبار
                        entry = random.choice(feed.entries[:10])
                        
                        title = entry.get('title', 'خبر سيبراني')
                        description = entry.get('summary', entry.get('description', ''))
                        link = entry.get('link', '')
                        
                        # تنظيف النص من HTML
                        title = clean_html(title)
                        description = clean_html(description)
                        
                        # تقصير الوصف إذا كان طويلاً
                        if len(description) > 300:
                            description = description[:300] + "..."
                        
                        # تنسيق الخبر
                        news_content = f"**{title}**\n\n{description}"
                        
                        if link:
                            news_content += f"\n\n🔗 [اقرأ المزيد]({link})"
                        
                        return news_content
                    else:
                        return "❌ لم يتم العثور على أخبار في هذا المصدر."
                else:
                    # محاولة مصدر آخر
                    return await try_another_source()
    except asyncio.TimeoutError:
        return await try_another_source()
    except Exception as e:
        print(f"خطأ في جلب الخبر من {rss_url}: {str(e)}")
        return await try_another_source()

async def try_another_source():
    """محاولة مصدر آخر إذا فشل الأول"""
    # محاولة مصدرين آخرين
    remaining_feeds = [f for f in CYBER_NEWS_RSS_FEEDS if f != random.choice(CYBER_NEWS_RSS_FEEDS)]
    
    for rss_url in remaining_feeds[:2]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.read()
                        feed = feedparser.parse(content)
                        
                        if feed.entries:
                            entry = random.choice(feed.entries[:10])
                            title = clean_html(entry.get('title', 'خبر سيبراني'))
                            description = clean_html(entry.get('summary', entry.get('description', '')))
                            link = entry.get('link', '')
                            
                            if len(description) > 300:
                                description = description[:300] + "..."
                            
                            news_content = f"**{title}**\n\n{description}"
                            if link:
                                news_content += f"\n\n🔗 [اقرأ المزيد]({link})"
                            
                            return news_content
        except:
            continue
    
    return "❌ تعذر جلب الأخبار من المصادر المتاحة. يرجى المحاولة لاحقاً."

async def send_news_to_channel():
    """إرسال خبر إلى القناة المحددة"""
    try:
        news = await generate_cyber_news()
        
        for guild in bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and CHANNEL_NAME in channel.name:
                    embed = discord.Embed(
                        title="📰 خبر سيبراني جديد",
                        description=news,
                        color=discord.Color.blue(),
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text="بوت الأخبار السيبرانية")
                    await channel.send(embed=embed)
                    print(f"[{datetime.now()}] تم إرسال خبر إلى {channel.name} في {guild.name}")
                    return True
        
        print(f"[{datetime.now()}] ⚠️ لم يتم العثور على قناة '{CHANNEL_NAME}'")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] ❌ خطأ في إرسال الخبر: {str(e)}")
        return False

@bot.event
async def on_ready():
    print(f'{bot.user} تم تسجيل الدخول بنجاح!')
    print(f'البوت متصل بـ {len(bot.guilds)} سيرفر')
    
    # مزامنة slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ تم مزامنة {len(synced)} أمر slash')
    except Exception as e:
        print(f'⚠️ خطأ في مزامنة الأوامر: {e}')
    
    # بدء المهمة المجدولة
    if not send_news_periodically.is_running():
        send_news_periodically.start()

# Slash command - لا يحتاج MESSAGE_CONTENT_INTENT
@bot.tree.command(name="وريني", description="إرسال خبر سيبراني فوري للاختبار")
async def show_news(interaction: discord.Interaction):
    """إرسال خبر سيبراني فوري للاختبار"""
    try:
        await interaction.response.defer()
        news = await generate_cyber_news()
        
        embed = discord.Embed(
            title="📰 خبر سيبراني",
            description=news,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="بوت الأخبار السيبرانية")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ حدث خطأ: {str(e)}")

@tasks.loop(hours=6)
async def send_news_periodically():
    """إرسال الأخبار كل 6 ساعات"""
    print(f"[{datetime.now()}] جاري إرسال خبر سيبراني مجدول...")
    await send_news_to_channel()

@send_news_periodically.before_loop
async def before_send_news():
    await bot.wait_until_ready()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ خطأ: DISCORD_TOKEN غير موجود في ملف .env")
        print("   أضف DISCORD_TOKEN في متغيرات البيئة على Railway")
    else:
        try:
            print("🚀 بدء تشغيل البوت...")
            print("📰 البوت يستخدم مصادر RSS مجانية للأخبار السيبرانية")
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"\n❌ حدث خطأ: {str(e)}")
            print(f"   نوع الخطأ: {type(e).__name__}")
            raise

