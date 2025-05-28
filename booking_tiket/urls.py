from django.urls import path
from booking_tiket.views import *

app_name = "booking_tiket"

urlpatterns = [
    # path("", main_view, name="main"),
    path("reservasi/", reservasi, name="reservasi"),
    path("reservasi/edit_reservasi/", edit_reservasi, name="edit_reservasi"),
    # path("reservasi/<int:pk>/", reservasi_detail, name="reservasi_detail"),
    path("reservasi/create_reservasi/", create_reservasi, name="create_reservasi"),
    # path("reservasi/<int:pk>/update/", update_reservasi, name="update_reservasi"),
    path("reservasi/cancel/", cancel_reservasi, name="cancel_reservasi"),
    path("manajemen-reservasi/", manajemen_data_reservasi, name="manajemen_data_reservasi"),
]