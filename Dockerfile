FROM python:3.11-slim

WORKDIR /app

# نسخ ملفات المتطلبات أولاً
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# تشغيل البوت
CMD ["python3", "main.py"]

