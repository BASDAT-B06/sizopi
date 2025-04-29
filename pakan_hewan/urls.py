from django.urls import path
from . import views

app_name = 'pakan_hewan'

urlpatterns = [
    path('create/', views.create_pemberian_pakan, name='create_pemberian_pakan'),
    path('edit/', views.edit_pemberian_pakan, name='edit_pemberian_pakan'),
    path('per-hewan/6f8f52c4-90cc-4cf2-aa82-15b673efbc9c', views.pakan_per_hewan, name='pakan_per_hewan'),
    path('riwayat-penjaga/', views.riwayat_pakan_penjaga, name='riwayat_pakan_penjaga'),
]