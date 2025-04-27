from django.shortcuts import render

def daftar_satwa(request):
    # Dummy data instead of database query
    data = [
        {'id': 1, 'nama_individu': 'Simba', 'spesies': 'Singa', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2018-05-12', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrOunpvF6cRJnnrnfpFksyRMhWcQyJfivzAQ&s'},
        {'id': 2, 'nama_individu': 'Nala', 'spesies': 'Zebra', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2020-03-01', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJAFJ2cCC3gFAubQ8mFa77Oj8KFexvUJkM0A&s'},
        {'id': 3, 'nama_individu': 'Rio', 'spesies': 'Harimau', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2020-03-03', 'status_kesehatan': 'Sakit', 'habitat': 'Hutan Tropis', 'url_foto': 'https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg'},
        {'id': 4, 'nama_individu': 'Luna', 'spesies': 'Orangutan', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2019-01-10', 'status_kesehatan': 'Sehat', 'habitat': 'Hutan Tropis', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhwXqM659i3j50TOxk3zGODelonIAwVmAEYQ&s'},
        {'id': 5, 'nama_individu': 'Kara', 'spesies': 'Kuda', 'asal_hewan': 'Amerika', 'tanggal_lahir': '2021-06-15', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://images.pexels.com/photos/6696645/pexels-photo-6696645.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'},
    ]
    
    return render(request, 'daftar_satwa.html', {'data': data})


def home(request):
    return render(request, 'home.html')

def tambah_satwa(request):
    return render(request, 'form_satwa.html')

def edit_satwa(request, id):
    # Dummy data to mimic editing a specific Satwa instance
    data = [
        {'id': 1, 'nama_individu': 'Simba', 'spesies': 'Singa', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2018-05-12', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrOunpvF6cRJnnrnfpFksyRMhWcQyJfivzAQ&s'},
        {'id': 2, 'nama_individu': 'Nala', 'spesies': 'Zebra', 'asal_hewan': 'Afrika', 'tanggal_lahir': '2020-03-01', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJAFJ2cCC3gFAubQ8mFa77Oj8KFexvUJkM0A&s'},
        {'id': 3, 'nama_individu': 'Rio', 'spesies': 'Harimau', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2020-03-03', 'status_kesehatan': 'Sakit', 'habitat': 'Hutan Tropis', 'url_foto': 'https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg'},
        {'id': 4, 'nama_individu': 'Luna', 'spesies': 'Orangutan', 'asal_hewan': 'Kalimantan', 'tanggal_lahir': '2019-01-10', 'status_kesehatan': 'Sehat', 'habitat': 'Hutan Tropis', 'url_foto': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhwXqM659i3j50TOxk3zGODelonIAwVmAEYQ&s'},
        {'id': 5, 'nama_individu': 'Kara', 'spesies': 'Kuda', 'asal_hewan': 'Amerika', 'tanggal_lahir': '2021-06-15', 'status_kesehatan': 'Sehat', 'habitat': 'Savana', 'url_foto': 'https://images.pexels.com/photos/6696645/pexels-photo-6696645.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'},
    ]

    # Find the satwa by id
    satwa = next((item for item in data if item["id"] == id), None)
    
    if satwa is None:
        # Handle the case where no satwa was found (e.g., show an error page)
        return render(request, 'error.html', {'message': 'Satwa not found'})

    # Render the edit form for the specific satwa
    return render(request, 'edit_satwa.html', {'satwa': satwa})
