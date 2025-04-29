from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('dokter-hewan/', views.dash_dokter_hewan, name='dash_dokter_hewan'),
    path('pelatih/', views.dash_pelatih, name='dash_pelatih'),
    path('pengunjung/', views.dash_pengunjung, name='dash_pengunjung'),
    path('penjaga-hewan/', views.dash_penjaga_hewan, name='dash_penjaga_hewan'),
    path('staf-admin/', views.dash_staf_admin, name='dash_staf_admin'),
]