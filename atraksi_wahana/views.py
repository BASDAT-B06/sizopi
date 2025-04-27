from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json

class DummyWahana:
    def __init__(self, pk, nama, kapasitas, jadwal, peraturan):
        self.pk = pk
        self.nama = nama
        self.kapasitas = kapasitas
        self.jadwal = jadwal
        self.peraturan = peraturan
        # JSON-encoded string for JavaScript
        self.peraturan_json = json.dumps(peraturan)

class DummyPelatih:
    def __init__(self, id, nama):
        self.id = id
        self.nama = nama

class DummyHewan:
    def __init__(self, id, nama, jenis):
        self.id = id
        self.nama = nama
        self.jenis = jenis

class DummyAtraksi:
    def __init__(self, pk, nama, lokasi, kapasitas, jadwal, hewan, pelatih, pelatih_id):
        self.pk = pk
        self.nama = nama
        self.lokasi = lokasi
        self.kapasitas = kapasitas
        self.jadwal = jadwal
        self.hewan = hewan
        self.pelatih = pelatih
        self.pelatih_id = pelatih_id

def manajemen_data(request):
    """
    View untuk menampilkan halaman manajemen data atraksi
    """
    # Dummy data untuk prototype
    pelatih_list = [
        DummyPelatih(1, "Ahmad Zaki"),
        DummyPelatih(2, "Budi Santoso"),
        DummyPelatih(3, "Cindy Wijaya")
    ]
    
    hewan_list = [
        DummyHewan(1, "Leo", "Singa"),
        DummyHewan(2, "Simba", "Singa"),
        DummyHewan(3, "Jumbo", "Gajah"),
        DummyHewan(4, "Flipper", "Lumba-lumba"),
        DummyHewan(5, "Koko", "Simpanse")
    ]
    
    atraksis = [
        DummyAtraksi(
            pk=1,
            nama="Pertunjukan Lumba-lumba",
            lokasi="Kolam Utama",
            kapasitas=100,
            jadwal="14:00",
            hewan="Flipper",
            pelatih="Ahmad Zaki",
            pelatih_id=1
        ),
        DummyAtraksi(
            pk=2,
            nama="Atraksi Simpanse",
            lokasi="Panggung A",
            kapasitas=50,
            jadwal="10:30",
            hewan="Koko",
            pelatih="Cindy Wijaya",
            pelatih_id=3
        )
    ]
    
    context = {
        'atraksis': atraksis,
        'pelatih_list': pelatih_list,
        'hewan_list': hewan_list
    }
    
    return render(request, 'manajemen_data_atraksi.html', context)

def tambah_atraksi(request):
    """
    View untuk menangani penambahan atraksi (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan menangani form submission
    # dan menyimpan atraksi baru ke database
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data'))

def edit_atraksi(request, pk):
    """
    View untuk menangani edit atraksi (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan menangani form submission
    # dan memperbarui atraksi di database
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data'))

def hapus_atraksi(request, pk):
    """
    View untuk menangani penghapusan atraksi (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan menangani penghapusan
    # atraksi dari database
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data'))

def get_hewan(request, pk):
    """
    View untuk mendapatkan data hewan terkait atraksi (dummy API endpoint)
    """
    # Dummy data hewan IDs untuk atraksi dengan pk=1
    if pk == 1:
        hewan_ids = [4]  # ID untuk Flipper
    # Dummy data hewan IDs untuk atraksi dengan pk=2
    elif pk == 2:
        hewan_ids = [5]  # ID untuk Koko
    else:
        hewan_ids = []
    
    return JsonResponse({'hewan_ids': hewan_ids})

def manajemen_data_wahana(request):
    """
    View untuk menampilkan halaman manajemen data wahana
    """
    # Dummy data untuk prototype
    wahanas = [
        DummyWahana(
            pk=1,
            nama="Roller Coaster",
            kapasitas=24,
            jadwal="10:00 - 17:00",
            peraturan=["Minimal tinggi 120cm", "Dilarang membawa barang", "Wajib memasang sabuk pengaman"]
        ),
        DummyWahana(
            pk=2,
            nama="Ferris Wheel",
            kapasitas=40,
            jadwal="09:00 - 18:00",
            peraturan=["Dilarang bergoyang", "Dilarang membawa makanan/minuman"]
        ),
        DummyWahana(
            pk=3,
            nama="Rumah Hantu",
            kapasitas=15,
            jadwal="16:00 - 22:00",
            peraturan=["Tidak direkomendasikan untuk pengidap jantung", "Dilarang memotret"]
        )
    ]
    
    context = {
        'wahanas': wahanas
    }
    
    return render(request, 'manajemen_data_wahana.html', context)

def tambah_wahana(request):
    """
    View untuk menangani penambahan wahana (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan:
    # 1. Mengambil data dari form (nama, kapasitas, jadwal, peraturan[])
    # 2. Memproses array peraturan
    # 3. Menyimpan wahana baru ke database
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data_wahana'))

def edit_wahana(request, pk):
    """
    View untuk menangani edit wahana (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan:
    # 1. Mengambil data dari form (nama, kapasitas, jadwal, peraturan[])
    # 2. Memproses array peraturan
    # 3. Memperbarui wahana di database berdasarkan pk
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data_wahana'))

def hapus_wahana(request, pk):
    """
    View untuk menangani penghapusan wahana (dummy, hanya redirect)
    """
    # Dalam implementasi sebenarnya, di sini akan:
    # 1. Mencari wahana berdasarkan pk
    # 2. Menghapus wahana dari database
    
    return HttpResponseRedirect(reverse('atraksi_wahana:manajemen_data_wahana'))