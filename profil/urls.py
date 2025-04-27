from django.urls import path
from . import views

app_name = 'profil'

urlpatterns = [
    path('pengunjung/', views.pengunjung, name='pengunjung'),
    path('dokter-hewan/', views.dokter_hewan, name='dokter_hewan'),
    path('petugas/', views.petugas, name='petugas'),
    path('ubah-password/', views.ubah_password, name='ubah_password'),
    
]
