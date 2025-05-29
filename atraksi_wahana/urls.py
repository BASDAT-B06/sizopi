from django.urls import path
from atraksi_wahana.views import *

app_name = "atraksi_wahana"

urlpatterns = [
    path("atraksi/", manajemen_data_atraksi, name="manajemen_data_atraksi"),
    path("atraksi/tambah/", tambah_atraksi, name="tambah_atraksi"),
    path("atraksi/edit/", edit_atraksi, name="edit_atraksi"),
    path("atraksi/hapus/", hapus_atraksi, name="hapus_atraksi"),
    path("wahana/", manajemen_data_wahana, name="manajemen_data_wahana"),
    path("wahana/tambah/", tambah_wahana, name="tambah_wahana"),
    path("wahana/edit/", edit_wahana, name="edit_wahana"),
    path("wahana/hapus/", hapus_wahana, name="hapus_wahana"),
]