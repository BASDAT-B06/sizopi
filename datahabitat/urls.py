from django.urls import path
from . import views

app_name = 'datahabitat'

urlpatterns = [

    path('', views.daftar_habitat, name='daftar_habitat'),
    path('tambah/', views.tambah_habitat, name='tambah_habitat'),
    path('<str:nama>/edit/', views.edit_habitat, name='edit_habitat'),
    path('<str:nama>/hapus/', views.hapus_habitat, name='hapus_habitat'),
    path('<str:nama>/', views.detail_habitat, name='detail_habitat'),
]

