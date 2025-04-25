from django.shortcuts import render

def daftar_satwa(request):
    # Dummy data instead of database query
    data = [
        {'nama_individu': 'Simba', 'spesies': 'Singa', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2018-05-12', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://placekitten.com/200/200'},
        {'nama_individu': 'Nala', 'spesies': 'Zebra', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2020-03-01', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': ''},
        {'nama_individu': 'Rio', 'spesies': 'Harimau', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2020-03-03', 'status_kesehatan': 'Sakit', 'habitat': 'Hutan Tropis', 'url_foto': 'https://placekitten.com/200/200'},
        {'nama_individu': 'Luna', 'spesies': 'Orangutan', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2019-01-10', 'status_kesehatan': 'Sehat', 'habitat': 'Hutan Tropis', 'url_foto': ''},
        {'nama_individu': 'Kara', 'spesies': 'Kuda', 'asal_hewan': 'Amerika', 'tanggal_lahir': '2021-06-15', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://placekitten.com/200/200'},
    ]
    
    return render(request, 'daftar_satwa.html', {'data': data})

def home(request):
    return render(request, 'home.html')
def tambah_satwa(request):
    return render(request, 'form_satwa.html')
def edit_satwa(request, id):
    # Dummy data to mimic editing a specific Satwa instance
    satwa = {
        'id': id,
        'nama_individu': 'Simba',
        'spesies': 'Singa',
        'asal_hewan': 'Afrika',
        'tanggal_lahir': '2018-05-12',
        'status_kesehatan': 'Sehat',
        'habitat': 'Savana',
        'url_foto': 'https://placekitten.com/200/200'  # Optional image
    }
    
    # In this case, we don't need forms because the page is static
    return render(request, 'edit_satwa.html', {'satwa': satwa})