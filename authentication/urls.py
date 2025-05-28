from django.urls import path
from authentication.views import *

app_name = "authentication"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/dokter", register_dokter_view, name="register_dokter"),
    path("register/pengunjung", register_pengunjung_view, name="register_pengunjung"),
    path("register/staff", register_staf_view, name="register_staf"),
    path("logout/", logout_view, name="logout"),
]