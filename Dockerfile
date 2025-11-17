FROM python:3.11-slim

WORKDIR /app

# نسخ جميع الملفات
COPY . .

# تثبيت المكتبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python3", "main.py"]

