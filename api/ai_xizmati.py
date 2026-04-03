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
            tandir kabob, qovurma, osh ko'za.
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
        {"kun": "Dushanba", "taom_nomi": "Makaron palov", "tayyorlash_vaqti": 25, "qiyinlik": "oson", "ingredientlar": [{"nomi": "makaron", "miqdor": "400g"}, {"nomi": "piyoz", "miqdor": "2 dona"}, {"nomi": "sabzi", "miqdor": "1 dona"}], "retsept": "Makaron qaynatiladi. Piyoz yog'da qovuriladi. Barchasi aralashtiriladi.", "foydali_maslahat": "Oddiy va tez tayyorlanadi."},
        {"kun": "Seshanba", "taom_nomi": "Tuxumli qovurdoq", "tayyorlash_vaqti": 20, "qiyinlik": "oson", "ingredientlar": [{"nomi": "tuxum", "miqdor": "4 dona"}, {"nomi": "kartoshka", "miqdor": "3 dona"}], "retsept": "Kartoshka qovuriladi va tuxum qo'shilib pishiriladi.", "foydali_maslahat": "Issiq non bilan juda mazali."},
        {"kun": "Chorshanba", "taom_nomi": "Kartoshkali sho'rva", "tayyorlash_vaqti": 35, "qiyinlik": "oson", "ingredientlar": [{"nomi": "kartoshka", "miqdor": "4 dona"}, {"nomi": "sabzi", "miqdor": "1 dona"}], "retsept": "Sabzavotlar qaynatiladi.", "foydali_maslahat": "Salqin kunlarda foydali."},
        {"kun": "Payshanba", "taom_nomi": "Sabzavotli dimlama", "tayyorlash_vaqti": 40, "qiyinlik": "oson", "ingredientlar": [{"nomi": "kartoshka", "miqdor": "3 dona"}, {"nomi": "sabzi", "miqdor": "2 dona"}], "retsept": "Sabzavotlar dim qilinadi.", "foydali_maslahat": "O'z suvida pishadi."},
        {"kun": "Juma", "taom_nomi": "Makaron va tuxum", "tayyorlash_vaqti": 20, "qiyinlik": "oson", "ingredientlar": [{"nomi": "makaron", "miqdor": "300g"}, {"nomi": "tuxum", "miqdor": "2 dona"}], "retsept": "Makaron qaynatiladi, tuxum qo'shilib pishiriladi.", "foydali_maslahat": "Oila uchun yaxshi."},
        {"kun": "Shanba", "taom_nomi": "Kartoshka plov", "tayyorlash_vaqti": 30, "qiyinlik": "oson", "ingredientlar": [{"nomi": "kartoshka", "miqdor": "4 dona"}, {"nomi": "yog'", "miqdor": "50ml"}], "retsept": "Kartoshka yog'da qovuriladi.", "foydali_maslahat": "Dam olish kuni."},
        {"kun": "Yakshanba", "taom_nomi": "Guruch sho'rva", "tayyorlash_vaqti": 35, "qiyinlik": "oson", "ingredientlar": [{"nomi": "guruch", "miqdor": "200g"}, {"nomi": "sabzi", "miqdor": "1 dona"}], "retsept": "Guruch qaynatiladi.", "foydali_maslahat": "Issiq ovqat."}
    ]
    
    ORTACHA_TAOMLAR = [
        {"kun": "Dushanba", "taom_nomi": "O'zbekcha palov", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "guruch", "miqdor": "500g"}, {"nomi": "mol go'shti", "miqdor": "300g"}], "retsept": "Go'sht qovuriladi, guruch solinadi, dim qilinadi.", "foydali_maslahat": "Juma palovi uchun qo'zichoq go'shti afzal."},
        {"kun": "Seshanba", "taom_nomi": "Sho'rva", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha", "ingredientlar": [{"nomi": "mol go'shti", "miqdor": "300g"}, {"nomi": "kartoshka", "miqdor": "3 dona"}], "retsept": "Go'sht suvda qaynatiladi, sabzavotlar qo'shiladi.", "foydali_maslahat": "Ko'k piyoz bilan bering."},
        {"kun": "Chorshanba", "taom_nomi": "Dimlama", "tayyorlash_vaqti": 70, "qiyinlik": "ortacha", "ingredientlar": [{"nomi": "mol go'shti", "miqdor": "400g"}, {"nomi": "kartoshka", "miqdor": "4 dona"}], "retsept": "Go'sht dim qilinadi sabzavot bilan.", "foydali_maslahat": "O'z suvida pishadi - juda mazali."},
        {"kun": "Payshanba", "taom_nomi": "Lag'mon", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha", "ingredientlar": [{"nomi": "tayyor lag'mon", "miqdor": "400g"}, {"nomi": "mol go'shti", "miqdor": "300g"}], "retsept": "Go'sht qovuriladi va lag'mon bilan birlashtiriladi.", "foydali_maslahat": "Sirkali lozimi bilan bering."},
        {"kun": "Juma", "taom_nomi": "Juma palovi", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "guruch", "miqdor": "700g"}, {"nomi": "qo'zichoq go'shti", "miqdor": "500g"}], "retsept": "Qo'zchoq go'shti qovuriladi, devzira solinadi, dim qilinadi.", "foydali_maslahat": "Juma kuni butun oila birga yeydi."},
        {"kun": "Shanba", "taom_nomi": "Chuchvara", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "un", "miqdor": "400g"}, {"nomi": "qiyma", "miqdor": "300g"}], "retsept": "Qozon qoriladi va chuchvara tayyorlanadi.", "foydali_maslahat": "Guruch-sho'rva bilan mazali."},
        {"kun": "Yakshanba", "taom_nomi": "Manti", "tayyorlash_vaqti": 80, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "un", "miqdor": "500g"}, {"nomi": "qiyma", "miqdor": "400g"}], "retsept": "Qozon qoriladi va manti tayyorlanadi, bug'da pishiriladi.", "foydali_maslahat": "Smetana bilan bering."}
    ]
    
    TOKIN_TAOMLAR = [
        {"kun": "Dushanba", "taom_nomi": "Qozonkabob", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha", "ingredientlar": [{"nomi": "qo'zichoq go'shti", "miqdor": "600g"}], "retsept": "Qo'zichoq go'shti qozonda qovuriladi.", "foydali_maslahat": "Non bilan bering."},
        {"kun": "Seshanba", "taom_nomi": "To'y palovi", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "devzira", "miqdor": "800g"}, {"nomi": "qo'zichoq", "miqdor": "700g"}], "retsept": "Katta qozonda palov tayyorlanadi.", "foydali_maslahat": "Bayram kunlari uchun."},
        {"kun": "Chorshanba", "taom_nomi": "Norin", "tayyorlash_vaqti": 120, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "mol go'shti", "miqdor": "500g"}, {"nomi": "un", "miqdor": "600g"}], "retsept": "Go'sht qaynatiladi va osh ko'za bilan aralashtiriladi.", "foydali_maslahat": "Qadimiy milliy taom."},
        {"kun": "Payshanba", "taom_nomi": "Hasip", "tayyorlash_vaqti": 90, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "qo'y go'shti", "miqdor": "500g"}, {"nomi": "guruch", "miqdor": "200g"}], "retsept": "Hasip tayyorlandi va qaynatiladi.", "foydali_maslahat": "Milliy kolbasa."},
        {"kun": "Juma", "taom_nomi": "Qo'zi palovi", "tayyorlash_vaqti": 150, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "devzira", "miqdor": "1kg"}, {"nomi": "qo'zi", "miqdor": "1kg"}], "retsept": "Katta qozonda palov tayyorlanadi.", "foydali_maslahat": "Mehmonlar uchun yasab beriladi."},
        {"kun": "Shanba", "taom_nomi": "Tandir kabob", "tayyorlash_vaqti": 60, "qiyinlik": "ortacha", "ingredientlar": [{"nomi": "qo'zichoq qabirg'a", "miqdor": "800g"}], "retsept": "Qo'zichoq qabirg'a tandirda kabob qilinadi.", "foydali_maslahat": "Dam olish kunining taomi."},
        {"kun": "Yakshanba", "taom_nomi": "Pishiriqli manti", "tayyorlash_vaqti": 100, "qiyinlik": "qiyin", "ingredientlar": [{"nomi": "un", "miqdor": "600g"}, {"nomi": "qo'zichoq qiyma", "miqdor": "500g"}], "retsept": "Katta manti bug'da pishiriladi.", "foydali_maslahat": "Bayram sofrasi uchun."}
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
