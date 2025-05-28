from django.urls import path
from .views import (
    PakanPerHewanView, CreatePakanView, EditPakanView, DeletePakanView, 
    UpdateStatusPakanView, RiwayatPakanPenjagaView, DaftarHewanPakanView
)

app_name = 'pakan_hewan'

urlpatterns = [
    path('', DaftarHewanPakanView.as_view(), name='daftar_hewan_pakan'),
    path('list/<uuid:id_hewan>/', PakanPerHewanView.as_view(), name='pakan_per_hewan'),
    path('create/<uuid:id_hewan>/', CreatePakanView.as_view(), name='create_pakan'),
    path('edit/<uuid:id_hewan>/', EditPakanView.as_view(), name='edit_pakan'),
    path('delete/<uuid:id_hewan>/', DeletePakanView.as_view(), name='delete_pakan'),
    path('update-status/<uuid:id_hewan>/', UpdateStatusPakanView.as_view(), name='update_status_pakan'),
    path('riwayat-penjaga/<str:username_penjaga>/', RiwayatPakanPenjagaView.as_view(), name='riwayat_pakan_penjaga'),
]