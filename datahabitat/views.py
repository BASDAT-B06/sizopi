from django.shortcuts import render, redirect
from django.http import HttpResponse

habitats = [
    {'id': 1, 'nama': 'Hutan Tropis', 'luas_area': 1500, 'kapasitas_maksimal': 1000, 'suhu': 30, 'kelembapan': 40, 'vegetasi': 'Pepohonan lebat'},
    {'id': 2, 'nama': 'Savana', 'luas_area': 2000, 'kapasitas_maksimal': 1200, 'suhu': 30, 'kelembapan': 40, 'vegetasi': 'Rumput luas'},
    {'id': 3, 'nama': 'Padang Rumput', 'luas_area': 1800, 'kapasitas_maksimal': 900, 'suhu': 32, 'kelembapan': 50, 'vegetasi': 'Terbuka tanpa kanopi'},
    {'id': 4, 'nama': 'Pantai', 'luas_area': 2500, 'kapasitas_maksimal': 1500, 'suhu': 28, 'kelembapan': 85, 'vegetasi': 'Pepohonan pantai'},
    {'id': 5, 'nama': 'Hutan Mangrove', 'luas_area': 1200, 'kapasitas_maksimal': 600, 'suhu': 27, 'kelembapan': 95, 'vegetasi': 'Mangrove'},
]


def daftar_habitat(request):
    return render(request, 'daftar_habitat.html', {'habitats': habitats})

species_in_habitat = {
    1: [{'nama_individu': 'Simba', 'spesies': 'Singa', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2018-05-12', 'status_kesehatan': 'Sehat'}],
    2: [{'nama_individu': 'Nala', 'spesies': 'Zebra', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2020-03-01', 'status_kesehatan': 'Sehat'}],
    3: [{'nama_individu': 'Rio', 'spesies': 'Harimau', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2020-03-03', 'status_kesehatan': 'Sakit'}],
    4: [{'nama_individu': 'Luna', 'spesies': 'Orangutan', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2019-01-10', 'status_kesehatan': 'Sehat'}],
    5: [{'nama_individu': 'Kara', 'spesies': 'Kuda', 'asal_hewan': 'Amerika', 'tanggal_lahir': '2021-06-15', 'status_kesehatan': 'Sehat'}],
}



def tambah_habitat(request):
    if request.method == 'POST':
        return redirect('datahabitat:daftar_habitat')
    return render(request, 'form_habitat.html')


def edit_habitat(request, pk):
    habitat = next((hab for hab in habitats if hab['id'] == pk), None)
    if habitat is None:
        return HttpResponse("Habitat not found.", status=404)
    
    if request.method == 'POST':
    
        return redirect('datahabitat:daftar_habitat')
    
    return render(request, 'edit_habitat.html', {'habitat': habitat})

def hapus_habitat(request, pk):

    habitat = next((hab for hab in habitats if hab['id'] == pk), None)
    if habitat is None:
        return HttpResponse("Habitat not found.", status=404)

    return redirect('datahabitat:daftar_habitat')


def detail_habitat(request, pk):
    habitat = next((hab for hab in habitats if hab['id'] == pk), None)
    if habitat is None:
        return HttpResponse("Habitat not found.", status=404)

    species = species_in_habitat.get(pk, [])
    
    return render(request, 'detail_habitat.html', {'habitat': habitat, 'species_in_habitat': species})
