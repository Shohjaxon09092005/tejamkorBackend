# =============================================================
# Tejamkor Ro'zg'or - URL Yo'nalishlar
# =============================================================

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
