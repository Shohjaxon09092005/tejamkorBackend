# =============================================================
# Tejamkor Ro'zg'or - Serializerlar (API uchun ma'lumot formatlari)
# =============================================================
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Oila, Mahsulot, HaftalikTaomnoma, KunlikTaom, Ovoz
import random
import string

Foydalanuvchi = get_user_model()


class RoyxatdanOtishSerializer(serializers.ModelSerializer):
    """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
    parol = serializers.CharField(write_only=True, min_length=6)
    parol_tasdiqlash = serializers.CharField(write_only=True)

    class Meta:
        model = Foydalanuvchi
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'telefon', 'rol', 'avatar_emoji', 'parol', 'parol_tasdiqlash']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': False},
        }

    def validate(self, data):
        if data['parol'] != data['parol_tasdiqlash']:
            raise serializers.ValidationError({"parol": "Parollar mos kelmadi!"})
        return data

    def create(self, validated_data):
        validated_data.pop('parol_tasdiqlash')
        parol = validated_data.pop('parol')
        foydalanuvchi = Foydalanuvchi(**validated_data)
        foydalanuvchi.set_password(parol)
        foydalanuvchi.save()
        return foydalanuvchi


class FoydalanuvchiSerializer(serializers.ModelSerializer):
    """Foydalanuvchi profili"""
    to_liq_ism = serializers.SerializerMethodField()
    oila_nomi = serializers.SerializerMethodField()

    class Meta:
        model = Foydalanuvchi
        fields = ['id', 'username', 'first_name', 'last_name', 'to_liq_ism',
                  'email', 'telefon', 'rol', 'avatar_emoji', 'oila', 'oila_nomi']
        read_only_fields = ['id', 'username']

    def get_to_liq_ism(self, obj):
        return obj.get_full_name() or obj.username

    def get_oila_nomi(self, obj):
        return obj.oila.nomi if obj.oila else None


class OilaYaratishSerializer(serializers.ModelSerializer):
    """Yangi oila yaratish"""
    class Meta:
        model = Oila
        fields = ['id', 'nomi', 'daraja', 'oylik_byudjet', 'kod']
        read_only_fields = ['id', 'kod']

    def create(self, validated_data):
        # Avtomatik 6 belgili kod yaratish
        kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Oila.objects.filter(kod=kod).exists():
            kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        validated_data['kod'] = kod
        return super().create(validated_data)


class OilaSerializer(serializers.ModelSerializer):
    """Oila ma'lumotlari to'liq"""
    azolar = FoydalanuvchiSerializer(many=True, read_only=True)
    azolar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Oila
        fields = ['id', 'nomi', 'daraja', 'oylik_byudjet', 'kod',
                  'azolar', 'azolar_soni', 'yaratilgan_vaqt']

    def get_azolar_soni(self, obj):
        return obj.azolar.count()


class MahsulotSerializer(serializers.ModelSerializer):
    """Mahsulot ma'lumotlari"""
    class Meta:
        model = Mahsulot
        fields = ['id', 'nomi', 'miqdor', 'birlik', 'narx', 'qoshilgan_vaqt']
        read_only_fields = ['id', 'qoshilgan_vaqt']


class OvozSerializer(serializers.ModelSerializer):
    """Ovoz berish"""
    foydalanuvchi_ismi = serializers.SerializerMethodField()

    class Meta:
        model = Ovoz
        fields = ['id', 'foydalanuvchi', 'taom', 'vaqt', 'foydalanuvchi_ismi']
        read_only_fields = ['id', 'foydalanuvchi', 'vaqt']

    def get_foydalanuvchi_ismi(self, obj):
        return obj.foydalanuvchi.get_full_name() or obj.foydalanuvchi.username


class KunlikTaomSerializer(serializers.ModelSerializer):
    """Kunlik taom ma'lumotlari ovozlar bilan"""
    ovozlar_soni = serializers.SerializerMethodField()
    foydalanuvchi_ovoz_berganmi = serializers.SerializerMethodField()
    ovoz_berganlar = serializers.SerializerMethodField()

    class Meta:
        model = KunlikTaom
        fields = ['id', 'kun', 'taom_nomi', 'retsept', 'ingredientlar',
                  'tayyorlash_vaqti', 'qiyinlik', 'galaba_qozondi',
                  'ovozlar_soni', 'foydalanuvchi_ovoz_berganmi', 'ovoz_berganlar']

    def get_ovozlar_soni(self, obj):
        return obj.ovozlar.count()

    def get_foydalanuvchi_ovoz_berganmi(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.ovozlar.filter(foydalanuvchi=request.user).exists()
        return False

    def get_ovoz_berganlar(self, obj):
        ovozlar = obj.ovozlar.select_related('foydalanuvchi').all()
        return [
            {
                'ism': o.foydalanuvchi.get_full_name() or o.foydalanuvchi.username,
                'emoji': o.foydalanuvchi.avatar_emoji
            }
            for o in ovozlar
        ]


class HaftalikTaomnomaSerializer(serializers.ModelSerializer):
    """Haftalik taomnoma to'liq ma'lumotlari"""
    kunlik_taomlar = KunlikTaomSerializer(many=True, read_only=True)
    oila_nomi = serializers.SerializerMethodField()

    class Meta:
        model = HaftalikTaomnoma
        fields = ['id', 'oila', 'oila_nomi', 'yaratilgan_sana', 'daraja',
                  'mahsulotlar_royxati', 'kunlik_taomlar', 'faol']

    def get_oila_nomi(self, obj):
        return obj.oila.nomi
