from django.urls import path
from . import views

app_name = 'datasatwa'

urlpatterns = [
    path('tambah/', views.tambah_satwa, name='tambah_satwa'),
    path('daftar/', views.daftar_satwa, name='daftar_satwa'),
    path('edit/<int:id>/', views.edit_satwa, name='edit_satwa'),  
    path('', views.home, name='home'),  
    
]
