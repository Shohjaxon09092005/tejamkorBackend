# =============================================================
# Tejamkor Ro'zg'or - AI Xizmati (Google Gemini API)
# =============================================================
import os
import json
import logging
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger(__name__)

# Gemini API kalitini muhit o'zgaruvchisidan olish
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

def gemini_sozla():
    """Gemini API ni sozlash"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY topilmadi! .env faylini tekshiring.")
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')  # Bepul va tez model


def daraja_kontekstini_ol(daraja: str) -> str:
    """
    Byudjet darajasiga mos kontekst matnini qaytaradi.
    Bu AI ga to'g'ri yo'nalish beradi.
    """
    kontekstlar = {
        'tejamkor': """
            Bu oila TEJAMKOR (byudjetli) kategoriyasida. 
            Ular kamroq va arzonroq mahsulotlar bilan ishlaydi.
            Taomlar oddiy, arzon va to'yimli bo'lishi kerak.
            Masalan: makaron palov, qovurdoq, tuxumli osh, 
            kartoshkali sho'rva, lag'mon (go'shtsiz), 
            sabzavotli dimlama (go'shtsiz yoki ozgina go'sht bilan).
            Bir kunlik ovqat xarajati minimal bo'lishi kerak.
        """,
        'ortacha': """
            Bu oila O'RTACHA (standart) kategoriyasida.
            Ular o'rtacha miqdordagi sifatli mahsulotlar bilan ishlaydi.
            Taomlar o'zbekona an'anaviy va mazali bo'lishi kerak.
            Masalan: palov (go'shtli), sho'rva (qo'zichoq yoki mol go'shti),
            dimlama, lag'mon, manti (haftada 1-2 marta),
            somsa, chuchvara, qozonkabob.
            Balansli va sog'lom ovqatlanish muhim.
        """,
        'tokin': """
            Bu oila TO'KIN-SOCHIN (premium) kategoriyasida.
            Ular keng ko'lamli, sifatli va noyob mahsulotlar bilan ishlaydi.
            Taomlar boy, murakkab va festiv bo'lishi mumkin.
            Masalan: norin, qozonkabob (qo'zi go'shti), 
            pishiriqli manti, to'y palovi, hasip,
            tandir kabob, qovurdoq (mol eti), 
            halim, qovurma, osh ko'za.
            Sifat va rang-baranglik muhim.
        """
    }
    return kontekstlar.get(daraja, kontekstlar['ortacha'])


def haftalik_taomnoma_yarat(
    mahsulotlar: list,
    daraja: str,
    oila_azolari_soni: int = 4
) -> Optional[dict]:
    """
    Mahsulotlar ro'yxatiga asoslanib AI yordamida
    1 haftalik taomnoma va retseptlar yaratadi.
    
    Args:
        mahsulotlar: [{"nomi": "guruch", "miqdor": 2, "birlik": "kg"}, ...]
        daraja: 'tejamkor' | 'ortacha' | 'tokin'
        oila_azolari_soni: Oila a'zolari soni
    
    Returns:
        JSON formatidagi haftalik taomnoma yoki None
    """
    try:
        model = gemini_sozla()
        
        # Mahsulotlar ro'yxatini matn shaklida tayyorlash
        mahsulotlar_matni = "\n".join([
            f"- {m['nomi']}: {m['miqdor']} {m['birlik']}"
            for m in mahsulotlar
        ])
        
        daraja_kontekst = daraja_kontekstini_ol(daraja)
        
        # O'zbek tilida prompt
        prompt = f"""
Sen O'zbekiston milliy oshpaz ustozisan. Sening vazifang - berilgan mahsulotlardan 
oilaga 1 haftalik to'liq taomnoma va har bir taom uchun batafsil retsept tuzishdir.

{daraja_kontekst}

Oila a'zolari soni: {oila_azolari_soni} kishi

Mavjud mahsulotlar:
{mahsulotlar_matni}

MUHIM KO'RSATMALAR:
1. Faqat berilgan mahsulotlardan foydalaning (kichik qo'shimchalar mumkin: tuz, yog', ziravorlar)
2. Har bir kun uchun 1 ta asosiy taom (tushlik yoki kechki ovqat)
3. Retseptlar {oila_azolari_soni} kishilik bo'lsin
4. Barcha matn O'ZBEK TILIDA bo'lsin
5. Daraja: {daraja.upper()} - bunga mos taomlar tanlang

Javobni FAQAT JSON formatida bering, boshqa hech narsa yo'q:
{{
  "hafta_xulosasi": "Bu haftalik menyu haqida qisqacha izoh",
  "kunlar": [
    {{
      "kun": "Dushanba",
      "taom_nomi": "Taom nomi",
      "tayyorlash_vaqti": 30,
      "qiyinlik": "oson|ortacha|qiyin",
      "ingredientlar": [
        {{"nomi": "guruch", "miqdor": "500g"}},
        {{"nomi": "sabzi", "miqdor": "2 dona"}}
      ],
      "retsept": "Qadamba-qadam tayyorlash usuli...",
      "foydali_maslahat": "Taom haqida qo'shimcha maslahat"
    }}
  ]
}}

7 kun: Dushanba, Seshanba, Chorshanba, Payshanba, Juma, Shanba, Yakshanba
"""
        
        # AI ga so'rov yuborish
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
            )
        )
        
        # JSON ni tozalab parsing qilish
        javob_matni = response.text.strip()
        
        # JSON blokidan tozalash (agar ```json ... ``` bo'lsa)
        if '```json' in javob_matni:
            javob_matni = javob_matni.split('```json')[1].split('```')[0]
        elif '```' in javob_matni:
            javob_matni = javob_matni.split('```')[1].split('```')[0]
        
        taomnoma_data = json.loads(javob_matni.strip())
        
        logger.info(f"AI muvaffaqiyatli taomnoma yaratdi: {daraja} darajasi")
        return taomnoma_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing xatosi: {e}")
        # Agar JSON parsing muvaffaqiyatsiz bo'lsa, zaxira taomnoma qaytaramiz
        return zaxira_taomnoma_yarat(daraja)
    except Exception as e:
        logger.error(f"AI xizmati xatosi: {e}")
        return zaxira_taomnoma_yarat(daraja)


def zaxira_taomnoma_yarat(daraja: str) -> dict:
    """
    AI ishlamagan taqdirda ishlaydigan zaxira taomnoma.
    Eng keng tarqalgan o'zbek taomlaridan iborat.
    """
    TEJAMKOR_TAOMLAR = [
        {"kun": "Dushanba", "taom_nomi": "Makaron palov", "tayyorlash_vaqti": 25, "qiyinlik": "oson",
         "ingredientlar": [{"nomi": "makaron", "miqdor": "400g"}, {"nomi": "piyoz", "miqdor": "2 dona"}, {"nomi": "sabzi", "miqdor": "1 dona"}, {"nomi": "o'simlik yog'i", "miqdor": "50ml"}],
         "retsept": "1. Makaron suvda qaynatiladi. 2. Piyoz va sabzi yog'da qovuriladi. 3. Barchasi aralashtiriladi, tuz va ziravorlar qo'shiladi. 4. Yana 5 daqiqa dim qilinadi.",
         "foydali_maslahat": "Mazasini oshirish uchun pomidor qo'shsangiz bo'ladi."},
        {"kun": "Seshanba", "taom_nomi": "Tuxumli qovurdoq", "tayyorlash_vaqti": 20, "qiyinlik": "oson",
         "ingredientlar": [{"nomi": "tuxum", "miqdor": "4 dona"}, {"nomi": "kartoshka", "miqdor": "3 dona"}, {"nomi": "piyoz", "miqdor": "1 dona"}],
         "retsept": "1. Kartoshka po'sti tozalanib, mayda to'g'ralanadi. 2. Yog'da qovuriladi. 3. Tuxum uriladi va aralashtirilib pishiriladi.",
         "foydali_maslahat": "Issiq non bilan juda mazali."},
        {"kun": "Chorshanba", "taom_nomi": "Kartoshkali sho'rva", "tayyorlash_vaqti": 35, "qiyinlik": "oson",
         "ingredientlar": [{"nomi": "kartoshka", "miqdor": "4 dona"}, {"nomi": "piyoz", "miqdor": "1 dona"}, {"nomi": "sabzi", "miqdor": "1 dona"}],
         "retsept": "1. Sabzavotlar to'g'ralanadi. 2. Qozonga yog' solinib, piyoz qovuriladi. 3. Boshqa sabzavotlar qo'shiladi. 4. Suv qo'shilib 25 daqiqa qaynatiladi. 5. Tuz, ziravorlar beriladi.",
         "foydali_maslahat": "Qaymog'i bo'lsa yanada to'yimli bo'ladi."},
        {"kun": "Payshanba", "taom_nomi": "Tuxumli pomidor", "tayyorlash_vaqti": 15, "qiyinlik": "oson",
         "ingredientlar": [{"nomi": "tuxum", "miqdor": "3 dona"}, {"nomi": "pomidor", "miqdor": "2 dona"}, {"nomi": "piyoz", "miqdor": "1 dona"}],
         "retsept": "1. Piyoz va pomidor mayda to'g'ralanadi. 2. Yog'da qovuriladi. 3. Tuxum uriladi, aralashtirilib pishiriladi.",
         "foydali_maslahat": "Sabzavot faslida yanada mazali."},
        {"kun": "Juma", "taom_nomi": "Guruchli sho'rva", "tayyorlash_vaqti": 40, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "guruch", "miqdor": "200g"}, {"nomi": "sabzi", "miqdor": "1 dona"}, {"nomi": "kartoshka", "miqdor": "2 dona"}],
         "retsept": "1. Sabzavotlar to'g'ralanadi. 2. Qozonga solib suvda qaynatiladi. 3. Yuvib olingan guruch qo'shiladi. 4. 20 daqiqa qaynatiladi. 5. Tuz, ko'k piyoz beriladi.",
         "foydali_maslahat": "Salqin kunlarda juda foydali."},
        {"kun": "Shanba", "taom_nomi": "Sabzavotli lag'mon (go'shtsiz)", "tayyorlash_vaqti": 45, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "un", "miqdor": "300g"}, {"nomi": "kartoshka", "miqdor": "2 dona"}, {"nomi": "piyoz", "miqdor": "2 dona"}],
         "retsept": "1. Undan qo'lda lag'mon qilinadi yoki tayyor lag'mon qaynatiladi. 2. Sabzavotlar qovuriladi. 3. Suv qo'shilib qaynatiladi. 4. Lag'mon ustiga suyuqlik quyiladi.",
         "foydali_maslahat": "Yakshanba uchun qolgan ovqatni isitsa bo'ladi."},
        {"kun": "Yakshanba", "taom_nomi": "Makaron va tuxum kazy", "tayyorlash_vaqti": 20, "qiyinlik": "oson",
         "ingredientlar": [{"nomi": "makaron", "miqdor": "300g"}, {"nomi": "tuxum", "miqdor": "2 dona"}, {"nomi": "piyoz", "miqdor": "1 dona"}],
         "retsept": "1. Makaron qaynatiladi. 2. Tuxum urib, piyoz bilan qovuriladi. 3. Makaron qo'shilib aralashtiriladi.",
         "foydali_maslahat": "Dam olish kunida oson va tez tayyorlanadi."}
    ]

    ORTACHA_TAOMLAR = [
        {"kun": "Dushanba", "taom_nomi": "O'zbekcha palov", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "guruch", "miqdor": "500g"}, {"nomi": "sabzi", "miqdor": "3 dona"}, {"nomi": "piyoz", "miqdor": "2 dona"}, {"nomi": "mol go'shti", "miqdor": "400g"}],
         "retsept": "1. Go'sht qozonda yog'da qovuriladi. 2. Piyoz va sabzi qo'shiladi. 3. Guruch yuvilib ustiga solinadi. 4. Suv quyilib qaynatiladi. 5. Dim qilinadi.",
         "foydali_maslahat": "Juma palovi uchun qo'zichoq go'shti afzal."},
        {"kun": "Seshanba", "taom_nomi": "Sho'rva (mol go'shti bilan)", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "mol go'shti", "miqdor": "300g"}, {"nomi": "kartoshka", "miqdor": "3 dona"}, {"nomi": "sabzi", "miqdor": "2 dona"}],
         "retsept": "1. Go'sht suvda qaynatiladi. 2. Ko'pik olinadi. 3. Sabzavotlar qo'shiladi. 4. 40 daqiqa pishiriladi. 5. Ziravorlar beriladi.",
         "foydali_maslahat": "Ko'k piyoz va ukrop bilan bering."},
        {"kun": "Chorshanba", "taom_nomi": "Dimlama", "tayyorlash_vaqti": 70, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "mol go'shti", "miqdor": "400g"}, {"nomi": "kartoshka", "miqdor": "4 dona"}, {"nomi": "karam", "miqdor": "0.5 dona"}],
         "retsept": "1. Go'sht pastki qavat. 2. Sabzavotlar ustma-ust qo'yiladi. 3. Suv qo'shilmaydi. 4. Past olovda 60 daqiqa dim qilinadi.",
         "foydali_maslahat": "O'z suvida pishadi - juda mazali."},
        {"kun": "Payshanba", "taom_nomi": "Lag'mon", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "tayyor lag'mon", "miqdor": "400g"}, {"nomi": "mol go'shti", "miqdor": "300g"}, {"nomi": "sabzavotlar", "miqdor": "assorted"}],
         "retsept": "1. Go'sht va sabzavotlar qovuriladi. 2. Suv qo'shilib qaynatiladi. 3. Lag'mon alohida qaynatiladi. 4. Barchasi birlashtiriladi.",
         "foydali_maslahat": "Sirkali lozimi bilan bering."},
        {"kun": "Juma", "taom_nomi": "Juma palovi", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "guruch", "miqdor": "700g"}, {"nomi": "qo'zichoq go'shti", "miqdor": "500g"}, {"nomi": "sabzi", "miqdor": "4 dona"}],
         "retsept": "1. Qozonga yog' qizdiriladi. 2. Go'sht qovuriladi. 3. Piyoz, sabzi qo'shiladi. 4. Guruch yuvilib solinadi. 5. Suv quyiladi. 6. Dim qilinadi.",
         "foydali_maslahat": "Juma kuni butun oila birga yeydi."},
        {"kun": "Shanba", "taom_nomi": "Manti", "tayyorlash_vaqti": 80, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "un", "miqdor": "500g"}, {"nomi": "mol go'shti (qiyma)", "miqdor": "400g"}, {"nomi": "piyoz", "miqdor": "3 dona"}],
         "retsept": "1. Undan qozon qoriladi. 2. Qiyma va piyoz aralashtirilib to'ldirgich tayyorlanadi. 3. Manti shakllantiriladi. 4. Mantovarda 40 daqiqa bug'da pishiriladi.",
         "foydali_maslahat": "Smetana yoki qaymoq bilan bering."},
        {"kun": "Yakshanba", "taom_nomi": "Chuchvara", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "un", "miqdor": "400g"}, {"nomi": "qiyma", "miqdor": "300g"}, {"nomi": "piyoz", "miqdor": "2 dona"}],
         "retsept": "1. Qozon qoriladi, ingichka yoyiladi. 2. Qiyma to'ldirgich tayyorlanadi. 3. Chuchvara shakllantiriladi. 4. Qaynab turgan suvda 10 daqiqa pishiriladi.",
         "foydali_maslahat": "Guruch-sho'rva bilan ham mazali."}
    ]

    TOKIN_TAOMLAR = [
        {"kun": "Dushanba", "taom_nomi": "Qozonkabob (qo'zichoq)", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "qo'zichoq go'shti", "miqdor": "600g"}, {"nomi": "piyoz", "miqdor": "3 dona"}, {"nomi": "ziravorlar", "miqdor": "assorted"}],
         "retsept": "1. Go'sht bo'laklarga bo'linadi. 2. Qozonga solib o'z suvida qovuriladi. 3. Piyoz qo'shiladi. 4. Past olovda 40 daqiqa pishiriladi.",
         "foydali_maslahat": "Non yoki non bo'lagi bilan bering."},
        {"kun": "Seshanba", "taom_nomi": "To'y palovi", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "guruch (devzira)", "miqdor": "800g"}, {"nomi": "qo'zichoq", "miqdor": "700g"}, {"nomi": "sabzi", "miqdor": "500g"}],
         "retsept": "1. Ko'p moy qizdiriladi. 2. Go'sht qovuriladi. 3. Piyoz, sabzi qo'shiladi. 4. Devzira guruch solinadi. 5. Quritilgan o'rik yoki o'rik ham qo'shiladi. 6. Dim qilinadi.",
         "foydali_maslahat": "Bayram kunlari uchun maxsus."},
        {"kun": "Chorshanba", "taom_nomi": "Norin", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "at go'shti yoki mol go'shti", "miqdor": "500g"}, {"nomi": "un", "miqdor": "600g"}, {"nomi": "piyoz", "miqdor": "4 dona"}],
         "retsept": "1. Go'sht butun parcha qaynatiladi. 2. Osh ko'za tayyorlanadi. 3. Go'sht va piyoz ingichka to'g'ralanadi. 4. Ko'za bilan aralashtirilib beriladi.",
         "foydali_maslahat": "Norin - qadimiy milliy taom."},
        {"kun": "Payshanba", "taom_nomi": "Hasip (milliy kolbasa)", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "qo'y go'shti", "miqdor": "500g"}, {"nomi": "guruch", "miqdor": "200g"}, {"nomi": "ich-organ", "miqdor": "1 to'plam"}],
         "retsept": "1. Guruch va go'sht maydalanadi. 2. Ziravorlar qo'shiladi. 3. Hasip tayyorlanib bog'lanadi. 4. Qaynatiladi.",
         "foydali_maslahat": "O'ziga xos milliy ta'm."},
        {"kun": "Juma", "taom_nomi": "Qo'zi palovi (to'y)", "tayyorlash_vaqti": 150, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "devzira guruch", "miqdor": "1kg"}, {"nomi": "qo'zi go'shti", "miqdor": "1kg"}, {"nomi": "sabzi", "miqdor": "600g"}],
         "retsept": "1. Katta qozonda moy ko'p qizdiriladi. 2. Go'sht bo'laklarda qovuriladi. 3. Piyoz va sabzi qo'shiladi. 4. Guruch solinadi. 5. Suv quyiladi. 6. 1 soat dim qilinadi.",
         "foydali_maslahat": "Mehmonlar uchun eng yaxshi taom."},
        {"kun": "Shanba", "taom_nomi": "Tandir kabob", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha",
         "ingredientlar": [{"nomi": "qo'zichoq qabirg'a", "miqdor": "800g"}, {"nomi": "ziravorlar", "miqdor": "assorted"}, {"nomi": "piyoz", "miqdor": "2 dona"}],
         "retsept": "1. Go'sht marinadlanadi. 2. Tandirda 40-50 daqiqa kabob qilinadi. 3. Ko'klamzorlar bilan beriladi.",
         "foydali_maslahat": "Eng yaxshi dam olish kuni taomi."},
        {"kun": "Yakshanba", "taom_nomi": "Pishiriqli manti", "tayyorlash_vaqti": 100, "qiyinlik": "qiyin",
         "ingredientlar": [{"nomi": "un", "miqdor": "600g"}, {"nomi": "qo'zichoq qiyma", "miqdor": "500g"}, {"nomi": "baliqchi dum yog'i", "miqdor": "100g"}],
         "retsept": "1. Qozon qoriladi. 2. Qiyma va yog' aralashtirilib to'ldirgich tayyorlanadi. 3. Katta manti shakllantiriladi. 4. Bug'da 45 daqiqa pishiriladi.",
         "foydali_maslahat": "Bayram sofrasi uchun maxsus manti."}
    ]

    taomlar_map = {
        'tejamkor': TEJAMKOR_TAOMLAR,
        'ortacha': ORTACHA_TAOMLAR,
        'tokin': TOKIN_TAOMLAR,
    }

    return {
        "hafta_xulosasi": f"Bu hafta {daraja} darajasida 7 kunlik taomnoma tayyorlandi.",
        "kunlar": taomlar_map.get(daraja, ORTACHA_TAOMLAR)
    }
