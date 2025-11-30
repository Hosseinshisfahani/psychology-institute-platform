# مرکز مشاوره و خدمات روانشناسی سرمد - Psychology Institute

[![CI](https://github.com/your-username/Emamy-project/workflows/CI/badge.svg)](https://github.com/your-username/Emamy-project/actions)

یک پلتفرم جامع برای ارائه خدمات روانشناسی و مشاوره آنلاین با طراحی حرفه‌ای و پشتیبانی کامل از زبان فارسی.

## ویژگی‌های اصلی

### 1. وبلاگ و محتوای روانشناسی
- سیستم مدیریت محتوا برای مقالات روانشناسی
- دسته‌بندی و برچسب‌گذاری پیشرفته
- سیستم نظرات و لایک
- عضویت در خبرنامه

### 2. تست‌های روانشناسی
- تست‌های متنوع شخصیت، هوش و شناختی
- سیستم امتیازدهی و تفسیر نتایج
- تست‌های رایگان و پولی
- ردیابی پیشرفت کاربران

### 3. بسته‌های آموزشی
- بسته‌های روانشناسی و مشاوره
- سیستم یادگیری آنلاین
- ردیابی پیشرفت و گواهینامه
- سیستم نظرات و امتیازدهی

### 4. داشبورد کاربری
- پروفایل شخصی کامل
- مدیریت اطلاعات و تنظیمات
- سیستم اعلانات
- آمار و گزارش‌های شخصی

### 5. جلسات آنلاین
- سیستم نوبت دهی
- تقویم درمانگران
- جلسات ویدیویی آنلاین
- یادداشت‌های جلسات

### 6. سیستم پرداخت
- سبد خرید پیشرفته
- پرداخت آنلاین (ZarinPal)
- کوپن‌های تخفیف
- مدیریت سفارشات

### 7. پنل مدیریت
- داشبورد مدیریتی پیشرفته
- مدیریت کاربران و محتوا
- گزارش‌گیری و آمار
- کنترل دسترسی‌ها

### 8. گزارش‌گیری و آمار
- گزارش‌های مالی
- آمار کاربران و فروش
- نمودارهای تعاملی
- صادرات گزارش‌ها

### 9. فروش ویژه به موسسات
- بسته‌های خدمات برای موسسات
- مدیریت اشتراک‌ها
- پنل مدیریت موسسات
- گزارش‌گیری اختصاصی

## تکنولوژی‌های استفاده شده

### Backend
- **Django 4.2.24** - فریمورک اصلی
- **Django REST Framework** - API
- **PostgreSQL** - پایگاه داده (قابل تغییر به SQLite)
- **Redis** - کش و صف کارها
- **Celery** - کارهای پس‌زمینه

### Frontend
- **Bootstrap 5 RTL** - فریمورک CSS
- **Font Awesome** - آیکون‌ها
- **jQuery** - JavaScript
- **Chart.js** - نمودارها

### سایر ابزارها
- **Django Allauth** - احراز هویت
- **Django Crispy Forms** - فرم‌های زیبا
- **Pillow** - پردازش تصاویر
- **python-decouple** - مدیریت تنظیمات

## نصب و راه‌اندازی

### نصب دستی (Development)

#### پیش‌نیازها
- Python 3.9+
- pip
- Git
- PostgreSQL (اختیاری)
- Redis (اختیاری)

#### مراحل نصب

1. **کلون کردن پروژه**
```bash
git clone <repository-url>
cd psychology-institute
```

2. **ایجاد محیط مجازی**
```bash
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
```

3. **نصب وابستگی‌ها**
```bash
pip install -r dependencies/requirements.txt
```

4. **تنظیم متغیرهای محیطی**
```bash
cp dependencies/env.example .env
# فایل .env را ویرایش کنید
```

5. **اجرای مایگریشن‌ها**
```bash
python dependencies/manage.py migrate
```

6. **ایجاد ابرکاربر**
```bash
python dependencies/manage.py createsuperuser
```

7. **ایجاد داده‌های نمونه**
```bash
python dependencies/manage.py populate_sample_data
```

8. **اجرای سرور**
```bash
python dependencies/manage.py runserver
```

### تنظیم SSL (HTTPS)

برای فعال‌سازی HTTPS با Let's Encrypt:

1. **نصب Certbot**
```bash
sudo apt update
sudo apt install certbot
```

2. **دریافت گواهی SSL**
```bash
sudo certbot certonly --webroot -w /var/www/certbot -d sarmad.ir -d www.sarmad.ir
```

3. **فعال‌سازی HTTPS در Nginx**
```bash
# ویرایش فایل dependencies/nginx/nginx.conf
# حذف کامنت از بخش HTTPS server
```

4. **راه‌اندازی مجدد Nginx**
```bash
# راه‌اندازی مجدد سرویس Nginx (بسته به روش نصب شما)
sudo systemctl restart nginx
# یا
sudo service nginx restart
```

## ساختار پروژه

```
psychology_institute/
├── blog/                    # وبلاگ و محتوا
├── tests/                   # تست‌های روانشناسی
├── courses/                 # بسته‌های آموزشی
├── dashboard/               # داشبورد کاربری
# ├── therapy_sessions/        # سیستم نوبت دهی (removed)
├── payment/                 # سیستم پرداخت
├── reports/                 # گزارش‌گیری
├── sales/                   # فروش به موسسات
├── dependencies/
│   ├── templates/               # قالب‌های HTML
│   ├── static/                  # فایل‌های استاتیک
│   ├── media/                   # فایل‌های رسانه‌ای
│   ├── nginx/                   # تنظیمات Nginx
│   ├── scripts/                 # اسکریپت‌های کمکی
│   ├── requirements.txt         # وابستگی‌های Python
│   ├── env.example              # نمونه فایل متغیرهای محیطی
│   ├── README.md                # مستندات
│   └── .gitignore               # فایل‌های Git ignore
```

## تنظیمات مهم

### پایگاه داده
برای استفاده از PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'psychology_institute',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Redis
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}
```

### ایمیل
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

## ویژگی‌های امنیتی

- احراز هویت دو مرحله‌ای
- رمزگذاری داده‌های حساس
- محافظت در برابر CSRF
- محدودیت نرخ درخواست
- اعتبارسنجی ورودی‌ها

## پشتیبانی از چندزبانه

- پشتیبانی کامل از فارسی (RTL)
- قابلیت اضافه کردن زبان‌های دیگر
- ترجمه خودکار محتوا

## API

پروژه شامل API کامل RESTful است که امکان توسعه اپلیکیشن‌های موبایل و فرانت‌اند جداگانه را فراهم می‌کند.

## مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. شاخه جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## تماس

- ایمیل: info@psychology-institute.ir
- تلفن: +98 21 1234 5678
- وب‌سایت: https://psychology-institute.ir

## تغییرات اخیر

### نسخه 1.0.0
- راه‌اندازی اولیه پروژه
- پیاده‌سازی تمام ماژول‌های اصلی
- طراحی رابط کاربری فارسی
- سیستم احراز هویت کامل
- پنل مدیریت پیشرفته

---

**توجه**: این پروژه برای استفاده در محیط تولید طراحی شده و نیاز به تنظیمات امنیتی اضافی دارد.
