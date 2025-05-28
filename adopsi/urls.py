from django.urls import path
from . import views

app_name = 'adoption'

urlpatterns = [
    # URLs untuk Staf Administrasi
    path('kelola-adopsi/', views.adoption_list_admin, name='admin_list'),
    path('kelola-adopter/', views.adopter_list, name='adopter_list'),
    path('adopter/<str:adopter_id>/history/', views.adopter_history, name='adopter_history'),
    
    # URLs untuk Pengunjung (Adopter)
    path('', views.adoption_list_user, name='user_list'),
    path('certificate/<str:animal_id>/', views.adoption_certificate, name='certificate'),
    path('report/<str:animal_id>/', views.animal_report, name='animal_report'),
    
    # AJAX endpoints
    path('verify-adopter/', views.verify_adopter_account, name='verify_adopter'),
    path('create-adoption-individu/', views.create_adoption_individu, name='create_adoption_individu'),
    path('create-adoption-organisasi/', views.create_adoption_organisasi, name='create_adoption_organisasi'),
    path('update-payment-status/', views.update_payment_status, name='update_payment_status'),
    path('stop-adoption/', views.stop_adoption, name='stop_adoption'),
    path('delete-adopter/', views.delete_adopter, name='delete_adopter'),
    path('delete-adoption-history/', views.delete_adoption_history, name='delete_adoption_history'),
    path('extend-adoption/', views.extend_adoption, name='extend_adoption'),
]
