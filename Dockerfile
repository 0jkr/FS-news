FROM python:3.11-slim

WORKDIR /app

# نسخ ملف المتطلبات أولاً
COPY requirements.txt /app/requirements.txt

# تثبيت المكتبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# نسخ باقي الملفات
COPY . /app/

# تشغيل البوت
CMD ["python3", "/app/main.py"]

