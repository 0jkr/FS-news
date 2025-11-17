# حل مشكلة Privileged Intents

## المشكلة
```
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled
```

## الحل السريع

### خطوات تفعيل MESSAGE CONTENT INTENT:

1. **اذهب إلى Discord Developer Portal:**
   - https://discord.com/developers/applications/

2. **اختر تطبيق البوت:**
   - اضغط على التطبيق الخاص ببوتك

3. **اذهب إلى قسم Bot:**
   - من القائمة الجانبية، اضغط على "Bot"

4. **فعّل Privileged Gateway Intents:**
   - ابحث عن قسم "Privileged Gateway Intents"
   - فعّل الخيار التالي:
     - ✅ **MESSAGE CONTENT INTENT** (مهم جداً!)

5. **احفظ التغييرات:**
   - اضغط على "Save Changes" في الأسفل

6. **أعد تشغيل البوت:**
   - على Railway، اضغط على "Redeploy" أو أعد تشغيل الـ deployment

## ملاحظات مهمة

- ⚠️ **MESSAGE CONTENT INTENT** مطلوب لقراءة محتوى الرسائل والأوامر
- بدون تفعيل هذا الخيار، البوت لن يتمكن من قراءة الأوامر مثل `!وريني`
- بعد التفعيل، قد تحتاج إلى إعادة تشغيل البوت

## التحقق من الإعداد

بعد التفعيل، يجب أن ترى في سجلات Railway:
```
[INFO] discord.client: logging in using static token
[INFO] discord.gateway: Shard ID None has connected to Gateway
```

بدلاً من خطأ PrivilegedIntentsRequired.

