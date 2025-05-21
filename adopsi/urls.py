from django.urls import path
from . import views

app_name = 'adoption'

urlpatterns = [
    # URLs untuk Staf Administrasi
    path('kelola-adopsi/', views.adoption_list_admin, name='admin_list'),
    path('kelola-adopter/', views.adopter_list, name='adopter_list'),
    path('adopter/<int:adopter_id>/history/', views.adopter_history, name='adopter_history'),
    
    # URLs untuk Pengunjung (Adopter)
    path('user/', views.adoption_list_user, name='user_list'),
    path('user/certificate/<int:animal_id>/', views.adoption_certificate, name='certificate'),
    path('user/report/<int:animal_id>/', views.animal_report, name='animal_report'),
]
