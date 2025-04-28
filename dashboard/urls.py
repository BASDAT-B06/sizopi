from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/dokter-hewan/', views.dash_dokter_hewan, name='dash_dokter_hewan'),
    path('dashboard/pelatih/', views.dash_pelatih, name='dash_pelatih'),
    path('dashboard/pengunjung/', views.dash_pengunjung, name='dash_pengunjung'),
    path('dashboard/penjaga-hewan/', views.dash_penjaga_hewan, name='dash_penjaga_hewan'),
    path('dashboard/staf-admin/', views.dash_staf_admin, name='dash_staf_admin'),
]