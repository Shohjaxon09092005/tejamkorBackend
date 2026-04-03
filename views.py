# =============================================================
# Tejamkor Ro'zg'or - API Ko'rinishlari (Views)
# =============================================================
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils import timezone
import logging

from .models import Oila, Mahsulot, HaftalikTaomnoma, KunlikTaom, Ovoz
from .serializers import (
    RoyxatdanOtishSerializer, FoydalanuvchiSerializer,
    OilaYaratishSerializer, OilaSerializer,
    MahsulotSerializer, HaftalikTaomnomaSerializer,
    KunlikTaomSerializer, OvozSerializer
)
from .ai_xizmati import haftalik_taomnoma_yarat

logger = logging.getLogger(__name__)
Foydalanuvchi = get_user_model()


# ============================================================
# AUTH - Ro'yxatdan o'tish va kirish
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def royxatdan_ot(request):
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazish.
    POST /api/auth/royxat/
    """
    serializer = RoyxatdanOtishSerializer(data=request.data)
    if serializer.is_valid():
        foydalanuvchi = serializer.save()
        # JWT token yaratish
        refresh = RefreshToken.for_user(foydalanuvchi)
        return Response({
            'xabar': 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'foydalanuvchi': FoydalanuvchiSerializer(foydalanuvchi).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def kir(request):
    """
    Tizimga kirish.
    POST /api/auth/kir/
    """
    username = request.data.get('username')
    parol = request.data.get('parol')

    if not username or not parol:
        return Response(
            {'xato': 'Username va parol kiritilishi shart!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    foydalanuvchi = authenticate(username=username, password=parol)

    if foydalanuvchi:
        refresh = RefreshToken.for_user(foydalanuvchi)
        return Response({
            'xabar': 'Xush kelibsiz!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'foydalanuvchi': FoydalanuvchiSerializer(foydalanuvchi).data
        })
    return Response(
        {'xato': 'Username yoki parol noto\'g\'ri!'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def mening_profilim(request):
    """
    Joriy foydalanuvchi profili.
    GET/PUT /api/auth/profil/
    """
    if request.method == 'GET':
        serializer = FoydalanuvchiSerializer(request.user)
        return Response(serializer.data)

    serializer = FoydalanuvchiSerializer(
        request.user, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response({'xabar': 'Profil yangilandi!', 'foydalanuvchi': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# OILA - Oila yaratish va boshqarish
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def oila_yarat(request):
    """
    Yangi oila yaratish. Yaratuvchi avtomatik oilaga qo'shiladi.
    POST /api/oila/yarat/
    """
    serializer = OilaYaratishSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            oila = serializer.save(yaratuvchi=request.user)
            # Yaratuvchini oilaga qo'shish
            request.user.oila = oila
            request.user.save()
        return Response({
            'xabar': f'"{oila.nomi}" oilasi yaratildi!',
            'oila': OilaSerializer(oila).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def oilaga_qoshil(request):
    """
    Mavjud oilaga kod orqali qo'shilish.
    POST /api/oila/qoshil/ {"kod": "ABC123"}
    """
    kod = request.data.get('kod', '').upper()
    try:
        oila = Oila.objects.get(kod=kod)
    except Oila.DoesNotExist:
        return Response(
            {'xato': 'Bunday kodli oila topilmadi!'},
            status=status.HTTP_404_NOT_FOUND
        )

    request.user.oila = oila
    request.user.save()
    return Response({
        'xabar': f'"{oila.nomi}" oilasiga qo\'shildingiz!',
        'oila': OilaSerializer(oila).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mening_oilam(request):
    """
    Foydalanuvchining oila ma'lumotlari.
    GET /api/oila/mening/
    """
    if not request.user.oila:
        return Response(
            {'xato': 'Siz hali hech qaysi oilaga qo\'shilmagan ekansiz!'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = OilaSerializer(request.user.oila)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def oila_darajasini_ozgartir(request):
    """
    Oila byudjet darajasini o'zgartirish.
    PUT /api/oila/daraja/ {"daraja": "tejamkor|ortacha|tokin"}
    """
    if not request.user.oila:
        return Response({'xato': 'Oilangiz yo\'q!'}, status=status.HTTP_400_BAD_REQUEST)

    daraja = request.data.get('daraja')
    if daraja not in ['tejamkor', 'ortacha', 'tokin']:
        return Response({'xato': 'Noto\'g\'ri daraja!'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.oila.daraja = daraja
    request.user.oila.save()
    return Response({'xabar': f'Daraja "{daraja}" ga o\'zgartirildi!'})


# ============================================================
# MAHSULOTLAR - Ro'zg'or qilingan mahsulotlar
# ============================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mahsulotlar(request):
    """
    Mahsulotlar ro'yxati ko'rish va yangi qo'shish.
    GET /api/mahsulotlar/
    POST /api/mahsulotlar/ {"nomi": "guruch", "miqdor": 2, "birlik": "kg"}
    """
    if not request.user.oila:
        return Response({'xato': 'Avval oilaga qo\'shiling!'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        m_list = Mahsulot.objects.filter(oila=request.user.oila).order_by('-qoshilgan_vaqt')
        serializer = MahsulotSerializer(m_list, many=True)
        return Response(serializer.data)

    # POST - yangi mahsulot qo'shish
    # Bir vaqtda ro'yxat ham yuborish mumkin
    data = request.data
    if isinstance(data, list):
        # Bir vaqtda bir nechta mahsulot qo'shish
        natijalar = []
        for item in data:
            serializer = MahsulotSerializer(data=item)
            if serializer.is_valid():
                serializer.save(oila=request.user.oila)
                natijalar.append(serializer.data)
        return Response({'xabar': f'{len(natijalar)} ta mahsulot qo\'shildi!', 'mahsulotlar': natijalar}, status=status.HTTP_201_CREATED)

    serializer = MahsulotSerializer(data=data)
    if serializer.is_valid():
        serializer.save(oila=request.user.oila)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def mahsulot_ochir(request, pk):
    """
    Mahsulotni o'chirish.
    DELETE /api/mahsulotlar/<pk>/
    """
    try:
        mahsulot = Mahsulot.objects.get(pk=pk, oila=request.user.oila)
        mahsulot.delete()
        return Response({'xabar': 'Mahsulot o\'chirildi!'})
    except Mahsulot.DoesNotExist:
        return Response({'xato': 'Mahsulot topilmadi!'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# TAOMNOMA - AI bilan haftalik menyu yaratish
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def taomnoma_yarat(request):
    """
    AI orqali haftalik taomnoma yaratish.
    POST /api/taomnoma/yarat/
    Joriy oilaning mahsulotlari asosida taomnoma yaratadi.
    """
    if not request.user.oila:
        return Response({'xato': 'Avval oilaga qo\'shiling!'}, status=status.HTTP_400_BAD_REQUEST)

    oila = request.user.oila

    # Mahsulotlar ro'yxatini olish
    mahsulotlar_qs = Mahsulot.objects.filter(oila=oila)
    if not mahsulotlar_qs.exists():
        return Response(
            {'xato': 'Mahsulotlar ro\'yxati bo\'sh! Avval mahsulotlar qo\'shing.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    mahsulotlar_list = [
        {'nomi': m.nomi, 'miqdor': float(m.miqdor), 'birlik': m.birlik}
        for m in mahsulotlar_qs
    ]

    oila_azolari_soni = oila.azalar_soni() or 4

    try:
        # AI ga so'rov yuborish
        logger.info(f"AI taomnoma yaratmoqda: {oila.nomi}, {oila.daraja}")
        ai_natija = haftalik_taomnoma_yarat(
            mahsulotlar=mahsulotlar_list,
            daraja=oila.daraja,
            oila_azolari_soni=oila_azolari_soni
        )

        if not ai_natija:
            return Response({'xato': 'AI xizmati vaqtinchalik ishlamayapti!'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Oldingi faol taomnomani o'chirish
        HaftalikTaomnoma.objects.filter(oila=oila, faol=True).update(faol=False)

        with transaction.atomic():
            # Yangi taomnoma saqlash
            taomnoma = HaftalikTaomnoma.objects.create(
                oila=oila,
                daraja=oila.daraja,
                taomnoma_json=ai_natija,
                mahsulotlar_royxati=', '.join([m['nomi'] for m in mahsulotlar_list]),
                faol=True
            )

            # Kunlik taomlarni saqlash
            kun_map = {
                'Dushanba': 'dushanba', 'Seshanba': 'seshanba',
                'Chorshanba': 'chorshanba', 'Payshanba': 'payshanba',
                'Juma': 'juma', 'Shanba': 'shanba', 'Yakshanba': 'yakshanba'
            }

            for kun_data in ai_natija.get('kunlar', []):
                kun_key = kun_map.get(kun_data.get('kun', ''), 'dushanba')
                KunlikTaom.objects.create(
                    taomnoma=taomnoma,
                    kun=kun_key,
                    taom_nomi=kun_data.get('taom_nomi', ''),
                    retsept=kun_data.get('retsept', ''),
                    ingredientlar=kun_data.get('ingredientlar', []),
                    tayyorlash_vaqti=kun_data.get('tayyorlash_vaqti', 30),
                    qiyinlik=kun_data.get('qiyinlik', 'ortacha'),
                )

        serializer = HaftalikTaomnomaSerializer(taomnoma, context={'request': request})
        return Response({
            'xabar': 'Haftalik taomnoma muvaffaqiyatli yaratildi!',
            'hafta_xulosasi': ai_natija.get('hafta_xulosasi', ''),
            'taomnoma': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Taomnoma yaratishda xato: {e}")
        return Response({'xato': f'Xato yuz berdi: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def joriy_taomnoma(request):
    """
    Oilaning faol taomnomasi.
    GET /api/taomnoma/joriy/
    """
    if not request.user.oila:
        return Response({'xato': 'Oilangiz yo\'q!'}, status=status.HTTP_400_BAD_REQUEST)

    taomnoma = HaftalikTaomnoma.objects.filter(
        oila=request.user.oila, faol=True
    ).first()

    if not taomnoma:
        return Response({'xato': 'Faol taomnoma topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

    serializer = HaftalikTaomnomaSerializer(taomnoma, context={'request': request})
    return Response(serializer.data)


# ============================================================
# OVOZ BERISH - Gamification tizimi
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ovoz_ber(request):
    """
    Kunlik taomga ovoz berish.
    POST /api/ovoz/ {"taom_id": 5}
    """
    taom_id = request.data.get('taom_id')
    if not taom_id:
        return Response({'xato': 'Taom ID kiritilmadi!'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        taom = KunlikTaom.objects.get(pk=taom_id)
    except KunlikTaom.DoesNotExist:
        return Response({'xato': 'Taom topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

    # Ovoz berish yoki bekor qilish (toggle)
    ovoz, yaratildi = Ovoz.objects.get_or_create(
        foydalanuvchi=request.user,
        taom=taom
    )

    if not yaratildi:
        # Allaqachon ovoz berilgan - bekor qilish
        ovoz.delete()
        return Response({
            'xabar': 'Ovoz bekor qilindi!',
            'ovoz_berildi': False,
            'ovozlar_soni': taom.ovozlar.count()
        })

    return Response({
        'xabar': f'"{taom.taom_nomi}" ga ovoz berdingiz! 🎉',
        'ovoz_berildi': True,
        'ovozlar_soni': taom.ovozlar.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ovoz_berish_natijasi(request):
    """
    Bugungi ovoz berish natijalari va g'olib taom.
    GET /api/ovoz/natija/
    """
    if not request.user.oila:
        return Response({'xato': 'Oilangiz yo\'q!'}, status=status.HTTP_400_BAD_REQUEST)

    # Faol taomnomani topish
    taomnoma = HaftalikTaomnoma.objects.filter(
        oila=request.user.oila, faol=True
    ).first()

    if not taomnoma:
        return Response({'xato': 'Faol taomnoma topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

    # Barcha taomlarni ovozlar bilan olish
    taomlar = KunlikTaom.objects.filter(taomnoma=taomnoma).prefetch_related('ovozlar')

    natija = []
    galaba_qozongan = None
    max_ovoz = 0

    for taom in taomlar:
        ovoz_soni = taom.ovozlar.count()
        if ovoz_soni > max_ovoz:
            max_ovoz = ovoz_soni
            galaba_qozongan = taom

        natija.append({
            'id': taom.id,
            'kun': taom.get_kun_display(),
            'taom_nomi': taom.taom_nomi,
            'ovozlar_soni': ovoz_soni,
            'galaba_qozondi': taom.galaba_qozondi,
            'foydalanuvchi_ovoz_berganmi': taom.ovozlar.filter(
                foydalanuvchi=request.user
            ).exists()
        })

    return Response({
        'taomlar': natija,
        'galaba_qozongan': {
            'taom_nomi': galaba_qozongan.taom_nomi if galaba_qozongan else None,
            'ovozlar_soni': max_ovoz
        } if galaba_qozongan and max_ovoz > 0 else None
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def galabani_belgilaish(request):
    """
    Eng ko'p ovoz olgan taomni g'olib sifatida belgilash.
    POST /api/ovoz/galaba/ {"taomnoma_id": 1, "kun": "dushanba"}
    """
    taomnoma_id = request.data.get('taomnoma_id')
    kun = request.data.get('kun')

    taomlar = KunlikTaom.objects.filter(
        taomnoma_id=taomnoma_id, kun=kun
    ).prefetch_related('ovozlar')

    if not taomlar.exists():
        return Response({'xato': 'Taomlar topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

    # Eng ko'p ovoz olganini aniqlash
    galaba = max(taomlar, key=lambda t: t.ovozlar.count())
    galaba.galaba_qozondi = True
    galaba.save()

    return Response({
        'xabar': f'"{galaba.taom_nomi}" bu kunning g\'olibi! 🏆',
        'galaba_qozondi': KunlikTaomSerializer(galaba, context={'request': request}).data
    })
