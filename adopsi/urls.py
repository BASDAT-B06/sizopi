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
    
    # URLs untuk Modal dan Form
    path('modal/detail/<int:animal_id>/', views.adoption_detail_modal, name='detail_modal'),
    path('modal/register/', views.register_adopter_modal, name='register_modal'),
    path('form/adopt/<int:animal_id>/<str:adopter_type>/', views.adoption_form, name='adoption_form'),
    path('form/extend/<int:animal_id>/', views.extend_adoption_form, name='extend_form'),
    path('modal/stop/', views.stop_adoption_modal, name='stop_modal'),
]
