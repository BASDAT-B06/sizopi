from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Dummy data untuk frontend
animals = [
    {
        'id': 1,
        'name': 'Melly',
        'type': 'Gajah',
        'condition': 'Sehat',
        'image': 'https://via.placeholder.com/300x200',
        'habitat': 'Hutan Tropis',
        'is_adopted': True,
        'adopter': 'Bambang',
        'start_date': '2025-02-26',
        'end_date': '2025-08-26',
        'contribution': 850000,
        'payment_status': 'lunas'
    },
    {
        'id': 2,
        'name': 'Simba',
        'type': 'Singa',
        'condition': 'Sehat',
        'image': 'https://via.placeholder.com/300x200',
        'habitat': 'Savana',
        'is_adopted': True,
        'adopter': 'Cindy',
        'start_date': '2024-07-10',
        'end_date': '2024-10-10',
        'contribution': 500000,
        'payment_status': 'lunas'
    },
    {
        'id': 3,
        'name': 'Rio',
        'type': 'Harimau',
        'condition': 'Pemulihan',
        'image': 'https://via.placeholder.com/300x200',
        'habitat': 'Hutan Hujan',
        'is_adopted': False,
        'adopter': None,
        'start_date': None,
        'end_date': None,
        'contribution': None,
        'payment_status': None
    }
]

adopters = [
    {
        'id': 1,
        'name': 'Bambang',
        'type': 'individual',
        'nik': '3175021234567890',
        'address': 'Jl. Merdeka No. 123, Jakarta',
        'phone': '081234567890',
        'total_contribution': 5000000
    },
    {
        'id': 2,
        'name': 'Cindy',
        'type': 'individual',
        'nik': '3175021234567891',
        'address': 'Jl. Sudirman No. 45, Jakarta',
        'phone': '081234567891',
        'total_contribution': 3500000
    },
    {
        'id': 3,
        'name': 'PT Hijau Lestari',
        'type': 'organization',
        'npp': '123456789012345',
        'address': 'Jl. Gatot Subroto No. 78, Jakarta',
        'phone': '021987654321',
        'total_contribution': 10000000
    }
]

adoption_history = [
    {
        'id': 1,
        'animal_name': 'Melly',
        'animal_type': 'Gajah',
        'start_date': '2025-02-26',
        'end_date': '2025-08-26',
        'contribution': 850000,
        'status': 'ongoing',
        'adopter_id': 1
    },
    {
        'id': 2,
        'animal_name': 'Simba',
        'animal_type': 'Singa',
        'start_date': '2024-07-10',
        'end_date': '2024-10-10',
        'contribution': 500000,
        'status': 'completed',
        'adopter_id': 2
    },
    {
        'id': 3,
        'animal_name': 'Nala',
        'animal_type': 'Zebra',
        'start_date': '2023-12-12',
        'end_date': '2024-12-12',
        'contribution': 1200000,
        'status': 'completed',
        'adopter_id': 1
    }
]

medical_records = [
    {
        'animal_id': 1,
        'date': '2025-04-01',
        'doctor': 'Dr. Siti Aminah',
        'health_status': 'Sakit',
        'diagnosis': 'Infeksi saluran pernapasan',
        'treatment': 'Antibiotik selama 7 hari',
        'notes': 'Evaluasi kondisi perbaikan ventilasi kandang.'
    },
    {
        'animal_id': 1,
        'date': '2025-04-15',
        'doctor': 'Dr. Budi Santoso',
        'health_status': 'Membaik',
        'diagnosis': 'Pemulihan dari infeksi',
        'treatment': 'Vitamin dan suplemen',
        'notes': 'Pantau asupan makanan.'
    }
]

# Views untuk Staf Administrasi
def adoption_list_admin(request):
    context = {
        'animals': animals,
        'title': 'Program Adopsi Satwa: Bantu Mereka dengan Cinta'
    }
    return render(request, 'adoption/admin/adoption_list_admin.html', context)

def adopter_list(request):
    context = {
        'adopters': sorted(adopters, key=lambda x: x['total_contribution'], reverse=True),
        'title': 'Daftar Adopter'
    }
    return render(request, 'adoption/admin/adopter_list.html', context)

def adopter_history(request, adopter_id):
    adopter = next((a for a in adopters if a['id'] == adopter_id), None)
    history = [h for h in adoption_history if h['adopter_id'] == adopter_id]
    
    context = {
        'adopter': adopter,
        'history': history,
        'title': f'Riwayat Adopsi - {adopter["name"]}'
    }
    return render(request, 'adoption/admin/adopter_history.html', context)

# Views untuk Pengunjung (Adopter)
def adoption_list_user(request):
    user_id = 1
    user_adoptions = [a for a in animals if a['is_adopted'] and a['adopter'] == next((ad['name'] for ad in adopters if ad['id'] == user_id), None)]
    
    context = {
        'animals': user_adoptions,
        'title': 'Program Adopsi Satwa: Bantu Mereka dengan Cinta'
    }
    return render(request, 'adoption/user/adoption_list_user.html', context)

def adoption_certificate(request, animal_id):
    animal = next((a for a in animals if a['id'] == animal_id), None)
    user_id = 1
    adopter = next((a for a in adopters if a['id'] == user_id), None)
    
    context = {
        'animal': animal,
        'adopter': adopter
    }
    return render(request, 'adoption/user/adoption_certificate.html', context)

def animal_report(request, animal_id):
    animal = next((a for a in animals if a['id'] == animal_id), None)
    records = [r for r in medical_records if r['animal_id'] == animal_id]
    
    context = {
        'animal': animal,
        'records': records,
        'title': 'Laporan Kondisi Satwa'
    }
    return render(request, 'adoption/user/animal_report.html', context)

# Modal dan Form Views 
def adoption_detail_modal(request, animal_id):
    animal = next((a for a in animals if a['id'] == animal_id), None)
    
    context = {
        'animal': animal
    }
    return render(request, 'adoption/components/adoption_detail_modal.html', context)

def register_adopter_modal(request):
    return render(request, 'adoption/components/register_adopter_modal.html')

def adoption_form(request, animal_id, adopter_type):
    animal = next((a for a in animals if a['id'] == animal_id), None)
    
    context = {
        'animal': animal,
        'adopter_type': adopter_type
    }
    return render(request, 'adoption/components/adoption_form.html', context)

def extend_adoption_form(request, animal_id):
    animal = next((a for a in animals if a['id'] == animal_id), None)
    user_id = 1
    adopter = next((a for a in adopters if a['id'] == user_id), None)
    
    context = {
        'animal': animal,
        'adopter': adopter
    }
    return render(request, 'adoption/components/extend_adoption_form.html', context)

def stop_adoption_modal(request):
    return render(request, 'adoption/components/stop_adoption_modal.html')
