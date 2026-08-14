# MediDemand • نظام التنبؤ باحتياجات الأدوية

نظام ذكي متكامل لتوقع واحتساب طلبيات واحتياجات الأدوية للمستشفيات ومراكز الرعاية الصحية الأولية مبني بلغة **Python** مع دعم النشر السحابي المباشر عبر **Cloudflare Workers** و **FastAPI**.

---

## ✨ المميزات الرئيسية (Key Features)

- 🧮 **معادلة دقيقة لاحتساب الطلبيات:** تراعي متوسط الاستهلاك الشهري، فترة التغطية المطلوبة (Lead Months)، نسبة مخزون الأمان (Safety Buffer %)، مع خصم الرصيد المتوفر بالمخزن.
- 🌓 **دعم الوضعين النهاري والليلي (Day / Night Mode):** واجهة مستخدم طبية عصرية ومريحة مع تبديل سلس وحفظ التفضيلات تلقائياً.
- 🌐 **دعم كامل للغتين العربية والإنجليزية (Bilingual AR / EN):** تبديل فوري للغة مع قلب اتجاه الصفحة التلقائي (RTL / LTR).
- 💾 **تخزين محلي وسحابي:** حفظ دائم للسجلات عبر قاعدة بيانات SQLite و APIs جاهزة.
- 📊 **سجل تاريخي وتصدير:** استعراض كافة السجلات والبحث والتصفية مع إمكانية التصدير المباشر لملفات Excel / CSV باسم `MediDemand_...`.
- 🗑️ **إدارة كاملة للبيانات:** مسح وتحديث السجلات بسهولة وأمان.
- 🔒 **نظام صلاحيات ومصادقة سريعة (Auth PIN):** لتوثيق وتأكيد الطلبيات.

---

## 🚀 طرق التشغيل والنشر (Deployment Options)

### 1. تشغيل خادم FastAPI المحلي (Local Server)

```bash
# 1. تثبيت الحزم المطلوبة
pip install -r fastapi_app/requirements.txt

# 2. تشغيل السيرفر
python -m uvicorn fastapi_app.main:app --reload --port 8000
```
افتح المتصفح على: `http://127.0.0.1:8000`

---

### 2. النشر السحابي المباشر على Cloudflare Workers (Python Serverless)

```bash
cd cloudflare_worker_python
wrangler deploy
```

---

## 📁 هيكل المشروع (Project Structure)

```text
├── fastapi_app/
│   ├── main.py              # تطبيق FastAPI متكامل مع واجهة MediDemand وقاعدة البيانات
│   └── requirements.txt     # متطلبات التشغيل
├── cloudflare_worker_python/
│   ├── entrypoint.py        # كود Python العامل كـ Cloudflare Worker Serverless
│   └── wrangler.toml        # إعدادات النشر على Cloudflare
├── cloudflare_tunnel_config.yml # إعدادات النفق السحابي Cloudflare Tunnel
├── .gitignore
└── README.md
```

---

## 📜 الترخيص (License)
MIT License
