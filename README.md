# 🥗 Tejamkor Ro'zg'or — To'liq O'rnatish Qo'llanmasi

## Loyiha haqida
**Tejamkor Ro'zg'or** — O'zbekiston oilaviy byudjeti uchun mo'ljallangan aqlli mobil ilova.
Oilangiz bilan haftalik taomnoma tuzish, AI yordamida retseptlar olish va ovoz berish orqali taom tanlash imkonini beradi.

---

## 📁 Loyiha tuzilmasi
```
tejamkor/
├── backend/                  # Django backend
│   ├── models.py            # Ma'lumotlar bazasi modellari
│   ├── serializers.py       # API serialiazatorlar
│   ├── views.py             # API ko'rinishlari
│   ├── urls.py              # URL yo'nalishlar
│   └── ai_xizmati.py       # Google Gemini AI integratsiyasi

```

---

## 🗄️ Ma'lumotlar Bazasi Arxitekturasi (PostgreSQL)

```
Foydalanuvchi (CustomUser)
├── id (PK)
├── username
├── first_name, last_name
├── email
├── telefon
├── rol (ota/ona/farzand/boshqa)
├── avatar_emoji
└── oila_id (FK → Oila)

Oila
├── id (PK)
├── nomi
├── kod (unique, 6 belgi) — qo'shilish uchun
├── daraja (tejamkor/ortacha/tokin)
├── oylik_byudjet
└── yaratuvchi_id (FK → Foydalanuvchi)

Mahsulot
├── id (PK)
├── oila_id (FK)
├── nomi
├── miqdor
├── birlik (kg/g/l/dona...)
└── narx (ixtiyoriy)

HaftalikTaomnoma
├── id (PK)
├── oila_id (FK)
├── yaratilgan_sana
├── daraja
├── taomnoma_json (JSONField — AI javobi)
└── faol (Boolean)

KunlikTaom
├── id (PK)
├── taomnoma_id (FK)
├── kun (dushanba..yakshanba)
├── taom_nomi
├── retsept (Text)
├── ingredientlar (JSONField)
├── tayyorlash_vaqti (daqiqa)
├── qiyinlik (oson/ortacha/qiyin)
└── galaba_qozondi (Boolean)

Ovoz
├── id (PK)
├── foydalanuvchi_id (FK)
├── taom_id (FK)
└── vaqt
[UNIQUE: foydalanuvchi + taom]
```

---

## 🚀 Backend O'rnatish

### 1. Virtual muhit yaratish
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. PostgreSQL ma'lumotlar bazasi yaratish
```sql
CREATE DATABASE tejamkor_db;
CREATE USER tejamkor_user WITH PASSWORD 'parol';
GRANT ALL PRIVILEGES ON DATABASE tejamkor_db TO tejamkor_user;
```

### 4. .env fayli yaratish
```env
SECRET_KEY=django-insecure-random-string-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=tejamkor_db
DB_USER=tejamkor_user
DB_PASSWORD=parol
DB_HOST=localhost
DB_PORT=5432

GEMINI_API_KEY=sizning_bepul_api_kalitingiz
```

### 5. Google Gemini API kalitini olish (BEPUL!)
1. https://aistudio.google.com/app/apikey saytiga o'ting
2. Google akkaunt bilan kiring
3. "Create API key" tugmasini bosing
4. Kalitni .env fayliga kiriting

### 6. Django migratsiyalar
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Serverni ishga tushirish
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 📱 Frontend (React Native) O'rnatish

### 1. Kerakli kutubxonalarni o'rnatish
```bash
cd frontend
npm install

# Navigatsiya
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context

# Async Storage (token saqlash uchun)
npm install @react-native-async-storage/async-storage
```

### 2. API URL ni sozlash
`src/xizmatlar/api.js` faylida:
```javascript
// Lokal ishlab chiqish uchun:
const API_URL = 'http://localhost:8000/api';

// Android emulator uchun:
const API_URL = 'http://10.0.2.2:8000/api';

// Haqiqiy qurilma uchun:
const API_URL = 'http://SIZNING_IP:8000/api';
```

### 3. Ilovani ishga tushirish
```bash
# Android
npx react-native run-android

# iOS
npx react-native run-ios

# Expo (agar expo ishlatilsa)
expo start
```

---

## 🔑 API Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/api/auth/royxat/` | Ro'yxatdan o'tish |
| POST | `/api/auth/kir/` | Kirish (JWT token) |
| GET/PUT | `/api/auth/profil/` | Profil ko'rish/tahrirlash |
| POST | `/api/oila/yarat/` | Yangi oila yaratish |
| POST | `/api/oila/qoshil/` | Oilaga kod bilan qo'shilish |
| GET | `/api/oila/mening/` | Oila ma'lumotlari |
| GET/POST | `/api/mahsulotlar/` | Mahsulotlar ro'yxati |
| DELETE | `/api/mahsulotlar/<id>/` | Mahsulot o'chirish |
| POST | `/api/taomnoma/yarat/` | AI orqali taomnoma |
| GET | `/api/taomnoma/joriy/` | Faol taomnoma |
| POST | `/api/ovoz/` | Ovoz berish/bekor |
| GET | `/api/ovoz/natija/` | Ovoz natijalari |

---

## 🤖 AI Tizimi Qanday Ishlaydi?

1. Foydalanuvchi mahsulotlar qo'shadi
2. "AI bilan taomnoma yaratish" bosiladi
3. Backend mahsulotlar + daraja + AI promptni Gemini ga yuboradi
4. Gemini 7 kunlik taomlar va retseptlarni JSON formatda qaytaradi
5. Backend uni saqlaydi va oila a'zolariga ko'rsatadi
6. Oila a'zolari ovoz beradi → g'olib taom belgilanadi

---

## 🎮 Gamification (O'yin) Tizimi

- Har bir oila a'zosi kunlik taomga ovoz bera oladi (toggle)
- Real vaqtda ovoz soni va progress ko'rsatiladi
- Eng ko'p ovoz olgan taom 👑 g'olib sifatida belgilanadi
- Oila a'zolarining avatar emojilari ovoz berganlarni ko'rsatadi

---

## 🌿 3 Daraja Tizimi

| Daraja | Mahsulotlar | Taomlar |
|--------|-------------|---------|
| 🌱 Tejamkor | Makaron, Kartoshka, Tuxum | Qovurdoq, Sho'rva, Dimlama |
| 🏡 O'rtacha | Go'sht, Guruch, Sabzavotlar | Palov, Lag'mon, Manti |
| 👑 To'kin | Premium mahsulotlar | Norin, Qozonkabob, Hasip |

---

## 📞 Yordam

Muammolar yuzaga kelsa:
1. `DEBUG=True` qo'ying va xato xabarlarini tekshiring
2. `python manage.py check` buyrug'ini ishga tushiring
3. Gemini API kaliti to'g'ri kiritilganligini tekshiring
