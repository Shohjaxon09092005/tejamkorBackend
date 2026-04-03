# =============================================================
# Tejamkor Ro'zg'or - Ma'lumotlar bazasi modellari
# =============================================================
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Foydalanuvchi(AbstractUser):
    """
    Kengaytirilgan foydalanuvchi modeli.
    Oila a'zolari uchun rol va profil ma'lumotlari.
    """
    ROL_TANLOVLARI = [
        ('ota', 'Ota'),
        ('ona', 'Ona'),
        ('farzand', 'Farzand'),
        ('boshqa', 'Boshqa'),
    ]

    telefon = models.CharField(max_length=15, blank=True, null=True, unique=True)
    rol = models.CharField(max_length=10, choices=ROL_TANLOVLARI, default='boshqa')
    avatar_emoji = models.CharField(max_length=10, default='👤')  # Oddiy emoji avatar
    oila = models.ForeignKey(
        'Oila',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='azolar'
    )
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"


class Oila(models.Model):
    """
    Oila modeli. Har bir oilaning nomi, kodi va byudjet darajasi.
    """
    DARAJA_TANLOVLARI = [
        ('tejamkor', 'Tejamkor (Byudjetli)'),
        ('ortacha', "O'rtacha (Standart)"),
        ('tokin', "To'kin-sochin (Premium)"),
    ]

    nomi = models.CharField(max_length=100, verbose_name="Oila nomi")
    kod = models.CharField(max_length=8, unique=True, verbose_name="Qo'shilish kodi")
    daraja = models.CharField(
        max_length=10,
        choices=DARAJA_TANLOVLARI,
        default='ortacha',
        verbose_name="Byudjet darajasi"
    )
    oylik_byudjet = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Oylik byudjet (so'm)"
    )
    yaratuvchi = models.ForeignKey(
        Foydalanuvchi,
        on_delete=models.CASCADE,
        related_name='yaratgan_oila',
        null=True
    )
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oila"
        verbose_name_plural = "Oilalar"

    def __str__(self):
        return f"{self.nomi} ({self.get_daraja_display()})"

    def azolar_soni(self):
        return self.azolar.count()


class Mahsulot(models.Model):
    """
    Oila xarid qilgan mahsulotlar ro'yxati.
    Har bir mahsulot miqdori va taxminiy narxi bilan saqlanadi.
    """
    BIRLIK_TANLOVLARI = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Litr'),
        ('ml', 'Millilitr'),
        ('dona', 'Dona'),
        ('boshqalar', 'Boshqalar'),
    ]

    oila = models.ForeignKey(Oila, on_delete=models.CASCADE, related_name='mahsulotlar')
    nomi = models.CharField(max_length=100, verbose_name="Mahsulot nomi")
    miqdor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Miqdor")
    birlik = models.CharField(max_length=10, choices=BIRLIK_TANLOVLARI, default='kg')
    narx = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Narx (so'm)"
    )
    qoshilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return f"{self.nomi} - {self.miqdor} {self.birlik}"


class HaftalikTaomnoma(models.Model):
    """
    AI tomonidan yaratilgan haftalik taomnoma.
    JSON formatida saqlanadi.
    """
    oila = models.ForeignKey(Oila, on_delete=models.CASCADE, related_name='taomnomalar')
    yaratilgan_sana = models.DateField(default=timezone.now)
    taomnoma_json = models.JSONField(verbose_name="Taomnoma ma'lumotlari")
    daraja = models.CharField(max_length=10, verbose_name="Daraja")
    mahsulotlar_royxati = models.TextField(verbose_name="Ishlatilgan mahsulotlar")
    faol = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Haftalik Taomnoma"
        verbose_name_plural = "Haftalik Taomnomalar"
        ordering = ['-yaratilgan_sana']

    def __str__(self):
        return f"{self.oila.nomi} - {self.yaratilgan_sana}"


class KunlikTaom(models.Model):
    """
    Taomnomaning har bir kuni uchun taomlar.
    Ovoz berish tizimi shu model orqali ishlaydi.
    """
    KUN_TANLOVLARI = [
        ('dushanba', 'Dushanba'),
        ('seshanba', 'Seshanba'),
        ('chorshanba', 'Chorshanba'),
        ('payshanba', 'Payshanba'),
        ('juma', 'Juma'),
        ('shanba', 'Shanba'),
        ('yakshanba', 'Yakshanba'),
    ]

    taomnoma = models.ForeignKey(
        HaftalikTaomnoma,
        on_delete=models.CASCADE,
        related_name='kunlik_taomlar'
    )
    kun = models.CharField(max_length=12, choices=KUN_TANLOVLARI)
    taom_nomi = models.CharField(max_length=200)
    retsept = models.TextField(verbose_name="Retsept")
    ingredientlar = models.JSONField(verbose_name="Ingredientlar ro'yxati")
    tayyorlash_vaqti = models.PositiveIntegerField(
        default=30,
        verbose_name="Tayyorlash vaqti (daqiqa)"
    )
    qiyinlik = models.CharField(
        max_length=10,
        choices=[('oson', 'Oson'), ('ortacha', "O'rtacha"), ('qiyin', 'Qiyin')],
        default='ortacha'
    )
    galaba_qozondi = models.BooleanField(default=False)  # Ovoz berish g'olibi

    class Meta:
        verbose_name = "Kunlik Taom"
        verbose_name_plural = "Kunlik Taomlar"

    def ovozlar_soni(self):
        return self.ovozlar.count()

    def __str__(self):
        return f"{self.kun}: {self.taom_nomi}"


class Ovoz(models.Model):
    """
    Oila a'zolarining ovoz berish tizimi.
    Har bir a'zo kuniga bir marta ovoz bera oladi.
    """
    foydalanuvchi = models.ForeignKey(
        Foydalanuvchi,
        on_delete=models.CASCADE,
        related_name='ovozlar'
    )
    taom = models.ForeignKey(
        KunlikTaom,
        on_delete=models.CASCADE,
        related_name='ovozlar'
    )
    vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ovoz"
        verbose_name_plural = "Ovozlar"
        # Bir foydalanuvchi bir taomga faqat bir marta ovoz bera oladi
        unique_together = ['foydalanuvchi', 'taom']

    def __str__(self):
        return f"{self.foydalanuvchi.username} -> {self.taom.taom_nomi}"
