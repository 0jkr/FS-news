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
from deep_translator import GoogleTranslator

load_dotenv()

intents = discord.Intents.default()
# نستخدم slash commands فقط، لكن command_prefix مطلوب
bot = commands.Bot(command_prefix='!', intents=intents)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = '「📰」cyber-news'

# مصادر RSS للأخبار السيبرانية - تركز على الاختراقات والثغرات الجديدة
CYBER_NEWS_RSS_FEEDS = [
    'https://feeds.feedburner.com/TheHackersNews',  # أخبار الاختراقات والثغرات
    'https://www.bleepingcomputer.com/feed/',  # اختراقات وثغرات أمنية
    'https://krebsonsecurity.com/feed/',  # اختراقات مهمة
    'https://www.darkreading.com/rss.xml',  # ثغرات واختراقات حديثة
    'https://feeds.feedburner.com/securityweek',  # أخبار أمنية حديثة
    'https://www.securityweek.com/rss',  # ثغرات واختراقات
    'https://www.csoonline.com/index.rss',  # أخبار أمنية واختراقات
]

def clean_html(text):
    """تنظيف HTML من النص"""
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

def translate_to_arabic(text):
    """ترجمة النص إلى العربية"""
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        # محاولة الترجمة
        translator = GoogleTranslator(source='auto', target='ar')
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"خطأ في الترجمة: {str(e)}")
        # في حالة فشل الترجمة، إرجاع النص الأصلي
        return text

def extract_image_url(entry):
    """استخراج رابط الصورة من الخبر"""
    # محاولة جلب الصورة من حقول مختلفة
    if 'media_content' in entry and entry['media_content']:
        return entry['media_content'][0].get('url', '')
    if 'media_thumbnail' in entry and entry['media_thumbnail']:
        return entry['media_thumbnail'][0].get('url', '')
    if 'links' in entry:
        for link in entry['links']:
            if link.get('type', '').startswith('image'):
                return link.get('href', '')
    
    # البحث عن صور في HTML
    summary = entry.get('summary', entry.get('description', ''))
    if summary:
        soup = BeautifulSoup(summary, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img.get('src')
    
    return None

async def fetch_full_article(url):
    """جلب محتوى المقال الكامل من الرابط"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # إزالة scripts وstyles
                    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    
                    # محاولة العثور على المحتوى الرئيسي
                    # البحث في tags شائعة للمحتوى
                    content_tags = ['article', 'main', '.content', '.post-content', '.entry-content', 
                                   '.article-content', '#content', '.story-body']
                    
                    article_text = ""
                    for tag in content_tags:
                        if tag.startswith('.'):
                            elements = soup.select(tag)
                        elif tag.startswith('#'):
                            elements = soup.select(tag)
                        else:
                            elements = soup.find_all(tag)
                        
                        if elements:
                            for element in elements:
                                text = element.get_text(separator='\n', strip=True)
                                if len(text) > 200:  # محتوى ذو معنى
                                    article_text = text
                                    break
                        
                        if article_text:
                            break
                    
                    # إذا لم نجد محتوى محدد، نجلب كل النصوص
                    if not article_text or len(article_text) < 200:
                        article_text = soup.get_text(separator='\n', strip=True)
                    
                    # تنظيف النص
                    lines = article_text.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 20:  # تجاهل الأسطر القصيرة
                            cleaned_lines.append(line)
                    
                    full_text = '\n\n'.join(cleaned_lines)
                    
                    # تقصير إذا كان طويلاً جداً (Discord limit ~4000 chars)
                    if len(full_text) > 3500:
                        full_text = full_text[:3500] + "..."
                    
                    return full_text
    except Exception as e:
        print(f"خطأ في جلب المقال الكامل: {str(e)}")
        return None
    
    return None

async def generate_cyber_news():
    """جلب خبر سيبراني من RSS feeds وترجمته إلى العربية (مجاني تماماً)"""
    # اختيار مصدر عشوائي
    rss_url = random.choice(CYBER_NEWS_RSS_FEEDS)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    content = await response.read()
                    feed = feedparser.parse(content)
                    
                    if feed.entries:
                        # فلترة الأخبار للتركيز على الاختراقات والثغرات
                        keywords = ['hack', 'breach', 'vulnerability', 'exploit', 'zero-day', 'cyber attack', 
                                   'data breach', 'ransomware', 'malware', 'phishing', 'security flaw',
                                   'CVE', 'exploit', 'hacker', 'leak', 'compromise', 'intrusion']
                        
                        # البحث عن أخبار تحتوي على كلمات مفتاحية مهمة
                        relevant_entries = []
                        for entry in feed.entries[:20]:
                            title = entry.get('title', '').lower()
                            summary = entry.get('summary', entry.get('description', '')).lower()
                            text = title + ' ' + summary
                            
                            if any(keyword in text for keyword in keywords):
                                relevant_entries.append(entry)
                        
                        # إذا وجدنا أخبار ذات صلة، نختار منها، وإلا نختار عشوائياً
                        if relevant_entries:
                            entry = random.choice(relevant_entries[:10])
                        else:
                            entry = random.choice(feed.entries[:10])
                        
                        title_en = entry.get('title', 'Cyber News')
                        description_en = entry.get('summary', entry.get('description', ''))
                        link = entry.get('link', '')
                        
                        # تنظيف النص من HTML
                        title_en = clean_html(title_en)
                        description_en = clean_html(description_en)
                        
                        # جلب المحتوى الكامل من المقال
                        full_content = await fetch_full_article(link) if link else None
                        
                        # إذا لم نتمكن من جلب المحتوى الكامل، نستخدم الوصف
                        if not full_content or len(full_content) < 200:
                            content_to_translate = description_en
                        else:
                            content_to_translate = full_content
                        
                        # ترجمة إلى العربية
                        title_ar = translate_to_arabic(title_en)
                        description_ar = translate_to_arabic(content_to_translate)
                        
                        # استخراج رابط الصورة
                        image_url = extract_image_url(entry)
                        
                        # إرجاع معلومات الخبر
                        return {
                            'title': title_ar,
                            'description': description_ar,
                            'link': link,
                            'image': image_url,
                            'title_en': title_en  # للرجوع إليه إذا فشلت الترجمة
                        }
                    else:
                        return None
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
    used_url = random.choice(CYBER_NEWS_RSS_FEEDS)
    remaining_feeds = [f for f in CYBER_NEWS_RSS_FEEDS if f != used_url]
    
    for rss_url in remaining_feeds[:2]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        content = await response.read()
                        feed = feedparser.parse(content)
                        
                        if feed.entries:
                            # نفس الفلترة للتركيز على الاختراقات والثغرات
                            keywords = ['hack', 'breach', 'vulnerability', 'exploit', 'zero-day', 'cyber attack', 
                                       'data breach', 'ransomware', 'malware', 'phishing', 'security flaw',
                                       'CVE', 'exploit', 'hacker', 'leak', 'compromise', 'intrusion']
                            
                            relevant_entries = []
                            for entry in feed.entries[:20]:
                                title = entry.get('title', '').lower()
                                summary = entry.get('summary', entry.get('description', '')).lower()
                                text = title + ' ' + summary
                                
                                if any(keyword in text for keyword in keywords):
                                    relevant_entries.append(entry)
                            
                            if relevant_entries:
                                entry = random.choice(relevant_entries[:10])
                            else:
                                entry = random.choice(feed.entries[:10])
                            
                            title_en = clean_html(entry.get('title', 'Cyber News'))
                            description_en = clean_html(entry.get('summary', entry.get('description', '')))
                            link = entry.get('link', '')
                            
                            # جلب المحتوى الكامل من المقال
                            full_content = await fetch_full_article(link) if link else None
                            
                            # إذا لم نتمكن من جلب المحتوى الكامل، نستخدم الوصف
                            if not full_content or len(full_content) < 200:
                                content_to_translate = description_en
                            else:
                                content_to_translate = full_content
                            
                            # ترجمة إلى العربية
                            title_ar = translate_to_arabic(title_en)
                            description_ar = translate_to_arabic(content_to_translate)
                            
                            # استخراج رابط الصورة
                            image_url = extract_image_url(entry)
                            
                            return {
                                'title': title_ar,
                                'description': description_ar,
                                'link': link,
                                'image': image_url,
                                'title_en': title_en
                            }
        except:
            continue
    
    return None

async def send_news_to_channel():
    """إرسال خبر إلى القناة المحددة"""
    try:
        news = await generate_cyber_news()
        
        if not news:
            print(f"[{datetime.now()}] ⚠️ لم يتم جلب خبر")
            return False
        
        for guild in bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and CHANNEL_NAME in channel.name:
                    embed = discord.Embed(
                        title=f"📰 {news.get('title', 'خبر سيبراني')}",
                        description=news.get('description', 'لا يوجد وصف'),
                        color=discord.Color.blue(),
                        timestamp=datetime.now()
                    )
                    
                    # إضافة رابط المقال
                    if news.get('link'):
                        embed.url = news['link']
                        embed.add_field(name="🔗", value=f"[اقرأ المزيد]({news['link']})", inline=False)
                    
                    # إضافة الصورة إذا كانت متوفرة
                    if news.get('image'):
                        embed.set_image(url=news['image'])
                    
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
        
        if not news:
            await interaction.followup.send("❌ تعذر جلب الخبر. يرجى المحاولة لاحقاً.")
            return
        
        embed = discord.Embed(
            title=f"📰 {news.get('title', 'خبر سيبراني')}",
            description=news.get('description', 'لا يوجد وصف'),
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # إضافة رابط المقال
        if news.get('link'):
            embed.url = news['link']
            embed.add_field(name="🔗", value=f"[اقرأ المزيد]({news['link']})", inline=False)
        
        # إضافة الصورة إذا كانت متوفرة
        if news.get('image'):
            embed.set_image(url=news['image'])
        
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

