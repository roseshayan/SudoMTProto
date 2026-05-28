# SudoMTProto
![GitHub release](https://img.shields.io/github/v/release/roseshayan/SudoMTProto)
![License](https://img.shields.io/github/license/roseshayan/SudoMTProto)
![Platform](https://img.shields.io/badge/platform-linux-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)

نصب‌کننده هوشمند پروکسی MTProto تلگرام برای سرورهای Ubuntu Linux

پروژه SudoMTProto به‌صورت خودکار هسته `mtg` را نصب و تنظیم می‌کند، سرویس systemd می‌سازد، Secret معتبر Fake-TLS تولید می‌کند و لینک اتصال مستقیم تلگرام را در اختیار کاربر قرار می‌دهد.

---

# ویژگی‌ها

- نصب خودکار پروکسی MTProto
- استفاده از هسته سریع و سبک `mtg`
- تولید خودکار Secret
- ساخت خودکار سرویس systemd
- تشخیص خودکار IP سرور
- نصب تعاملی و ساده
- مناسب برای استفاده واقعی
- سبک و سریع

---

# سیستم‌عامل‌های پشتیبانی‌شده

- Ubuntu 20.04+
- Ubuntu 22.04+
- Debian Based Linux
- AMD64 / x86_64

---

# نصب سریع (پیشنهادی)

این دستور را روی سرور اجرا کنید:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/install.sh)
```

یا:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/install.sh)
```

---

# نصب دستی

## 1. نصب پیش‌نیازها

```bash
apt update
apt install -y git python3 curl wget
```

## 2. دانلود پروژه

```bash
git clone https://github.com/roseshayan/SudoMTProto.git
```

## 3. ورود به پوشه پروژه

```bash
cd SudoMTProto
```

## 4. اجرای نصب‌کننده

```bash
chmod +x installer.py
sudo python3 installer.py
```

---

# تنظیمات نصب

هنگام نصب از شما پرسیده می‌شود:

## پورت

پیش‌فرض:

```text
443
```

## دامنه Fake-TLS

پیش‌فرض:

```text
cloudflare.com
```

نمونه‌ها:

- google.com
- cloudflare.com
- amazon.com
- microsoft.com

---

# بعد از نصب

نصب‌کننده اطلاعات زیر را نمایش می‌دهد:

- IP سرور
- پورت
- Secret
- دامنه Fake-TLS
- لینک مستقیم اتصال تلگرام

مثال:

```text
https://t.me/proxy?server=1.2.3.4&port=443&secret=YOUR_SECRET
```

لینک تولیدشده را داخل تلگرام باز کنید.

---

# مدیریت سرویس

## بررسی وضعیت

```bash
systemctl status mtg
```

## ری‌استارت سرویس

```bash
systemctl restart mtg
```

## توقف سرویس

```bash
systemctl stop mtg
```

## مشاهده لاگ‌ها

```bash
journalctl -u mtg -f
```

---

# حذف کامل

```bash
systemctl stop mtg
systemctl disable mtg
rm -f /etc/systemd/system/mtg.service
rm -f /usr/local/bin/mtg
systemctl daemon-reload
```

---

# عملکرد و ظرفیت

ظرفیت واقعی بستگی دارد به:

- قدرت CPU سرور
- کیفیت شبکه
- پهنای باند
- موقعیت سرور
- فیلترینگ ISP
- Latency

ظرفیت تقریبی واقعی:

| نوع سرور | کاربران همزمان تقریبی |
|---|---|
| VPS با 1GB RAM | 300 تا 1200 |
| VPS با 2GB RAM | 2000 تا 5000 |
| Dedicated Server | بیشتر از 10000 |

خود `mtg` بسیار سبک است و معمولاً گلوگاه اصلی کیفیت شبکه است.

---

# توصیه‌های امنیتی

پیشنهاد می‌شود:

- از پورت 443 استفاده کنید
- VPS باکیفیت تهیه کنید
- فایروال فعال کنید
- ورود SSH با پسورد را غیرفعال کنید
- از SSH Key استفاده کنید
- سیستم را آپدیت نگه دارید

---

# ساختار پروژه

```text
SudoMTProto/
├── installer.py
├── install.sh
├── README.md
└── README_FA.md
```

---

# قابلیت‌های آینده

برنامه‌های توسعه آینده:

- Docker Support
- Docker Compose
- پشتیبانی ARM
- پشتیبانی IPv6
- پنل تحت وب
- Auto Update
- Multi User
- مانیتورینگ و Metrics
- Fail2Ban
- بهینه‌سازی سیستم

---

# License

MIT License
