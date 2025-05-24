from django.urls import path
from . import views

app_name = 'profil'

urlpatterns = [
    path('pengaturan-profil/', views.pengaturan_profil, name='pengaturan_profil'),
    path('ubah-password/', views.ubah_password, name='ubah_password'),
]
