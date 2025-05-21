from django.urls import path
from . import views

urlpatterns = [
    path('rekam-medis/', views.list_rekam_medis, name='list_rekam_medis'),
    path('rekam-medis/create/', views.create_rekam_medis, name='create_rekam_medis'),
    path('rekam-medis/edit/', views.edit_rekam_medis, name='edit_rekam_medis'),
    path('jadwal-pemeriksaan/', views.jadwal_pemeriksaan, name='jadwal_pemeriksaan'),
    path('jadwal-pemeriksaan/create/', views.create_jadwal_pemeriksaan, name='create_jadwal_pemeriksaan'),
]