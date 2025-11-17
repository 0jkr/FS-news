#!/usr/bin/env python3
"""
سكريبت للتحقق من إعداد البوت
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_setup():
    """التحقق من إعداد البوت"""
    print("🔍 التحقق من إعداد البوت...\n")
    
    errors = []
    warnings = []
    
    # التحقق من ملف .env
    if not os.path.exists('.env'):
        errors.append("❌ ملف .env غير موجود! انسخ .env.example إلى .env")
    else:
        print("✅ ملف .env موجود")
    
    # التحقق من DISCORD_TOKEN
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token or discord_token == 'your_discord_bot_token_here':
        errors.append("❌ DISCORD_TOKEN غير موجود أو غير صحيح في ملف .env")
    else:
        print("✅ DISCORD_TOKEN موجود")
    
    # التحقق من OPENAI_API_KEY
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your_openai_api_key_here':
        errors.append("❌ OPENAI_API_KEY غير موجود أو غير صحيح في ملف .env")
    else:
        print("✅ OPENAI_API_KEY موجود")
    
    # التحقق من المتطلبات
    try:
        import discord
        print("✅ discord.py مثبت")
    except ImportError:
        errors.append("❌ discord.py غير مثبت. قم بتشغيل: pip install -r requirements.txt")
    
    try:
        import aiohttp
        print("✅ aiohttp مثبت")
    except ImportError:
        errors.append("❌ aiohttp غير مثبت. قم بتشغيل: pip install -r requirements.txt")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv مثبت")
    except ImportError:
        errors.append("❌ python-dotenv غير مثبت. قم بتشغيل: pip install -r requirements.txt")
    
    # النتيجة
    print("\n" + "="*50)
    if errors:
        print("❌ تم العثور على أخطاء:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ كل شيء جاهز! يمكنك تشغيل البوت الآن.")
        print("\nلتشغيل البوت:")
        print("  python main.py")
        return True

if __name__ == "__main__":
    check_setup()

