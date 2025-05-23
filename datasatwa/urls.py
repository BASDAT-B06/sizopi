from django.urls import path
from . import views

app_name = 'datasatwa'

urlpatterns = [
    path('tambah/', views.tambah_satwa, name='tambah_satwa'),
    
    path("edit/<uuid:id>/", views.edit_satwa, name="edit_satwa"),
    path('hapus/<uuid:id>/', views.hapus_satwa, name='hapus_satwa'),
 
    path('', views.daftar_satwa, name='daftar_satwa'),  
    
]
