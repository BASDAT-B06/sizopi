from django.urls import path
from . import views

urlpatterns = [
    path('pakan/create/', views.create_pemberian_pakan, name='create_pemberian_pakan'),
    path('pakan/edit/', views.edit_pemberian_pakan, name='edit_pemberian_pakan'),
    path('pakan/per-hewan/', views.pakan_per_hewan, name='pakan_per_hewan'),
    path('pakan/riwayat-penjaga/', views.riwayat_pakan_penjaga, name='riwayat_pakan_penjaga'),
]