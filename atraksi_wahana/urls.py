from django.urls import path
from atraksi_wahana.views import *

app_name = "atraksi_wahana"

urlpatterns = [
    path("", manajemen_data, name="manajemen_data"),
    path("tambah/", tambah_atraksi, name="tambah_atraksi"),
    path("edit/<int:pk>/", edit_atraksi, name="edit_atraksi"),
    path("hapus/<int:pk>/", hapus_atraksi, name="hapus_atraksi"),
    path("get_hewan/<int:pk>/", get_hewan, name="get_hewan"),
]