from django.contrib import admin
from .models import Foydalanuvchi, Oila, Mahsulot, HaftalikTaomnoma, KunlikTaom, Ovoz


@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'telefon', 'rol', 'oila']
    list_filter = ['rol', 'oila', 'yaratilgan_vaqt']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['yaratilgan_vaqt', 'last_login', 'date_joined']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'telefon')
        }),
        ('Rol va Oila', {
            'fields': ('rol', 'avatar_emoji', 'oila')
        }),
        ('Xavfsizlik', {
            'fields': ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('last_login', 'date_joined', 'yaratilgan_vaqt'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Oila)
class OilaAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'kod', 'daraja', 'oylik_byudjet', 'azolar_soni', 'yaratilgan_vaqt']
    list_filter = ['daraja', 'yaratilgan_vaqt']
    search_fields = ['nomi', 'kod']
    readonly_fields = ['kod', 'yaratilgan_vaqt']
    fieldsets = (
        ('Oila ma\'lumotlari', {
            'fields': ('nomi', 'kod', 'daraja', 'oylik_byudjet')
        }),
        ('Boshqarish', {
            'fields': ('yaratuvchi', 'yaratilgan_vaqt')
        }),
    )

    def azolar_soni(self, obj):
        return obj.azolar.count()
    azolar_soni.short_description = "A'zolar soni"


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'oila', 'miqdor', 'birlik', 'narx', 'qoshilgan_vaqt']
    list_filter = ['oila', 'birlik', 'qoshilgan_vaqt']
    search_fields = ['nomi', 'oila__nomi']
    readonly_fields = ['qoshilgan_vaqt']
    fieldsets = (
        ('Mahsulot ma\'lumotlari', {
            'fields': ('oila', 'nomi', 'miqdor', 'birlik', 'narx')
        }),
        ('Vaqt', {
            'fields': ('qoshilgan_vaqt',),
            'classes': ('collapse',)
        }),
    )


@admin.register(HaftalikTaomnoma)
class HaftalikTaomnomaAdmin(admin.ModelAdmin):
    list_display = ['oila', 'daraja', 'yaratilgan_sana', 'faol', 'taomlar_soni']
    list_filter = ['daraja', 'faol', 'yaratilgan_sana']
    search_fields = ['oila__nomi', 'mahsulotlar_royxati']
    readonly_fields = ['yaratilgan_sana', 'taomnoma_json']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('oila', 'daraja', 'yaratilgan_sana', 'faol')
        }),
        ('Taomnoma', {
            'fields': ('mahsulotlar_royxati', 'taomnoma_json'),
        }),
    )

    def taomlar_soni(self, obj):
        return obj.kunlik_taomlar.count()
    taomlar_soni.short_description = "Taomlar soni"


@admin.register(KunlikTaom)
class KunlikTaomAdmin(admin.ModelAdmin):
    list_display = ['taom_nomi', 'taomnoma', 'kun', 'tayyorlash_vaqti', 'qiyinlik', 'galaba_qozondi']
    list_filter = ['kun', 'qiyinlik', 'galaba_qozondi', 'taomnoma']
    search_fields = ['taom_nomi', 'retsept']
    readonly_fields = ['ingredientlar']
    fieldsets = (
        ('Taom ma\'lumotlari', {
            'fields': ('taomnoma', 'kun', 'taom_nomi', 'qiyinlik', 'tayyorlash_vaqti')
        }),
        ('Retsept', {
            'fields': ('retsept', 'ingredientlar'),
        }),
        ('Ovoz berish', {
            'fields': ('galaba_qozondi',),
        }),
    )


@admin.register(Ovoz)
class OvozAdmin(admin.ModelAdmin):
    list_display = ['foydalanuvchi', 'taom', 'vaqt']
    list_filter = ['vaqt', 'taom__taomnoma']
    search_fields = ['foydalanuvchi__username', 'taom__taom_nomi']
    readonly_fields = ['vaqt']
    fieldsets = (
        ('Ovoz ma\'lumotlari', {
            'fields': ('foydalanuvchi', 'taom', 'vaqt')
        }),
    )
