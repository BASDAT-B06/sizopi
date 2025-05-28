from django.urls import path
from . import views

app_name = 'kesehatan_hewan'
urlpatterns = [
    path('', views.DaftarHewanView.as_view(), name='daftar_hewan'),
    
    path('rekam-medis/<uuid:id_hewan>/', views.RekamMedisListView.as_view(), name='list_rekam_medis'),
    path('rekam-medis/<uuid:id_hewan>/create/', views.CreateRekamMedisView.as_view(), name='create_rekam_medis'),
    path('rekam-medis/<uuid:id_hewan>/edit/<str:tanggal>/', views.EditRekamMedisView.as_view(), name='edit_rekam_medis'),
    path('rekam-medis/<uuid:id_hewan>/delete/<str:tanggal>/', views.DeleteRekamMedisView.as_view(), name='delete_rekam_medis'),

    path('jadwal/<uuid:id_hewan>/', views.JadwalPemeriksaanView.as_view(), name='jadwal_pemeriksaan'),
    path('jadwal/<uuid:id_hewan>/create/', views.CreateJadwalView.as_view(), name='create_jadwal'),
    path('jadwal/<uuid:id_hewan>/edit/', views.EditJadwalView.as_view(), name='edit_jadwal'),
    path('jadwal/<uuid:id_hewan>/delete/', views.DeleteJadwalView.as_view(), name='delete_jadwal'),
    path('jadwal/<uuid:id_hewan>/frekuensi/', views.EditFrekuensiView.as_view(), name='edit_frekuensi'),
]