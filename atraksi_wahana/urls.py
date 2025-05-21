from django.urls import path
from atraksi_wahana.views import *

app_name = "atraksi_wahana"

urlpatterns = [
    path("atraksi/", manajemen_data, name="manajemen_data_atraksi"),
    path("atraksi/tambah/", tambah_atraksi, name="tambah_atraksi"),
    path("atraksi/edit/<int:pk>/", edit_atraksi, name="edit_atraksi"),
    path("atraksi/hapus/<int:pk>/", hapus_atraksi, name="hapus_atraksi"),
    path("atraksi/get_hewan/<int:pk>/", get_hewan, name="get_hewan"),
    path("wahana/", manajemen_data_wahana, name="manajemen_data_wahana"),
    path("wahana/tambah/", tambah_wahana, name="tambah_wahana"),
    path("wahana/edit/<int:pk>/", edit_wahana, name="edit_wahana"),
    path("wahana/hapus/<int:pk>/", hapus_wahana, name="hapus_wahana"),
]