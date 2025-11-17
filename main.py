import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
# intents.message_content = True  # غير مطلوب للأوامر التي تبدأ بـ prefix
bot = commands.Bot(command_prefix='!', intents=intents)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = '「📰」cyber-news'

async def generate_cyber_news():
    """إنشاء خبر سيبراني باستخدام OpenAI API"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """أنشئ خبراً سيبرانياً حديثاً ومهماً في مجال الأمن السيبراني. 
    يجب أن يكون الخبر:
    - حديث ومتعلق بالأمن السيبراني
    - مكتوب بالعربية
    - واضح ومفيد
    - يحتوي على عنوان ووصف مختصر (3-4 جمل)
    
    اكتب الخبر بالصيغة التالية:
    **العنوان**
    [الوصف هنا]
    """
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "أنت خبير في الأمن السيبراني وأخبار التكنولوجيا. تكتب أخباراً واضحة ومفيدة بالعربية."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    news_content = result['choices'][0]['message']['content']
                    return news_content
                else:
                    error_text = await response.text()
                    return f"❌ حدث خطأ في إنشاء الخبر: {error_text}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

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
    
    # بدء المهمة المجدولة
    if not send_news_periodically.is_running():
        send_news_periodically.start()

@bot.command(name='وريني')
async def show_news(ctx):
    """إرسال خبر سيبراني فوري للاختبار"""
    try:
        await ctx.send("⏳ جاري إنشاء الخبر...")
        news = await generate_cyber_news()
        
        embed = discord.Embed(
            title="📰 خبر سيبراني",
            description=news,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="بوت الأخبار السيبرانية")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: {str(e)}")

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
    elif not OPENAI_API_KEY:
        print("❌ خطأ: OPENAI_API_KEY غير موجود في ملف .env")
        print("   أضف OPENAI_API_KEY في متغيرات البيئة على Railway")
    else:
        try:
            bot.run(DISCORD_TOKEN)
        except discord.errors.PrivilegedIntentsRequired as e:
            print("\n" + "="*60)
            print("❌ خطأ: Privileged Intents غير مفعّلة!")
            print("="*60)
            print("\n📋 يجب تفعيل MESSAGE CONTENT INTENT في Discord Developer Portal:")
            print("   1. اذهب إلى: https://discord.com/developers/applications/")
            print("   2. اختر تطبيق البوت")
            print("   3. اذهب إلى 'Bot' في القائمة الجانبية")
            print("   4. في قسم 'Privileged Gateway Intents':")
            print("      ✅ فعّل 'MESSAGE CONTENT INTENT'")
            print("   5. احفظ التغييرات")
            print("   6. أعد تشغيل البوت على Railway")
            print("\n" + "="*60)
            raise
        except Exception as e:
            print(f"\n❌ حدث خطأ غير متوقع: {str(e)}")
            print(f"   نوع الخطأ: {type(e).__name__}")
            raise

