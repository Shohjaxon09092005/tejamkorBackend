# =============================================================
# Tejamkor Ro'zg'or - URL Yo'nalishlar
# =============================================================
# urls.py

from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('auth/royxat/', views.royxatdan_ot, name='royxat'),
    path('auth/kir/', views.kir, name='kir'),
    path('auth/profil/', views.mening_profilim, name='profil'),

    # OILA
    path('oila/yarat/', views.oila_yarat, name='oila-yarat'),
    path('oila/qoshil/', views.oilaga_qoshil, name='oilaga-qoshil'),
    path('oila/mening/', views.mening_oilam, name='mening-oilam'),
    path('oila/daraja/', views.oila_darajasini_ozgartir, name='oila-daraja'),

    # MAHSULOTLAR
    path('mahsulotlar/', views.mahsulotlar, name='mahsulotlar'),
    path('mahsulotlar/<int:pk>/', views.mahsulot_ochir, name='mahsulot-ochir'),

    # TAOMNOMA (AI)
    path('taomnoma/yarat/', views.taomnoma_yarat, name='taomnoma-yarat'),
    path('taomnoma/joriy/', views.joriy_taomnoma, name='joriy-taomnoma'),

    # OVOZ BERISH
    path('ovoz/', views.ovoz_ber, name='ovoz-ber'),
    path('ovoz/natija/', views.ovoz_berish_natijasi, name='ovoz-natija'),
    path('ovoz/galaba/', views.galabani_belgilaish, name='galaba'),
]


# =============================================================
# settings.py uchun muhim sozlamalar (qo'shing)
# =============================================================
"""
# settings.py ga qo'shing:

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'tejamkor',  # ilovangiz nomi
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

AUTH_USER_MODEL = 'tejamkor.Foydalanuvchi'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8081",  # React Native
]
CORS_ALLOW_ALL_ORIGINS = True  # Development uchun

# Google Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'tejamkor_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
"""
