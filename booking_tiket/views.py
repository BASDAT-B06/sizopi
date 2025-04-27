from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from datetime import datetime, timedelta

# Create your views here.
def reservasi(request):
    """
    View untuk menampilkan halaman reservasi atraksi
    """
    # Dummy data for prototype
    # In a real implementation, this would come from the database
    atraksi_list = [
        {
            'pk': 1,
            'nama': "Pertunjukan Lumba-lumba",
            'lokasi': "Kolam Utama",
            'jadwal': "14:00",
        },
        {
            'pk': 2,
            'nama': "Atraksi Simpanse",
            'lokasi': "Panggung A",
            'jadwal': "10:30",
        },
        {
            'pk': 3,
            'nama': "Parade Gajah",
            'lokasi': "Area Tengah",
            'jadwal': "16:00",
        }
    ]
    
    # Dummy reservasi data (in a real implementation, this would be the user's reservations)
    # For prototyping, let's just create a few reservations
    today = datetime.now().date()
    reservasi_list = [
        {
            'id': 101,
            'nama_atraksi': "Pertunjukan Lumba-lumba",
            'lokasi': "Kolam Utama",
            'jam': "14:00",
            'tanggal': (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 3,
            'status': "Terjadwal"
        },
        {
            'id': 102,
            'nama_atraksi': "Atraksi Simpanse",
            'lokasi': "Panggung A",
            'jam': "10:30",
            'tanggal': (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 2,
            'status': "Terjadwal"
        },
        {
            'id': 103,
            'nama_atraksi': "Parade Gajah",
            'lokasi': "Area Tengah",
            'jam': "16:00",
            'tanggal': (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 4,
            'status': "Dibatalkan"
        }
    ]
    
    context = {
        'atraksi_list': atraksi_list,
        'reservasi_list': reservasi_list
    }
    
    return render(request, 'reservasi.html', context)

def reservasi_detail(request, pk):
    """
    View untuk menampilkan detail reservasi berdasarkan ID
    """
    # In a real implementation, this would fetch the reservation detail from the database
    # For prototype, we'll just return a JSON response with dummy data
    
    # Pretend we're looking up the reservation
    today = datetime.now().date()
    
    if pk == 101:
        detail = {
            'id': 101,
            'nama_atraksi': "Pertunjukan Lumba-lumba",
            'lokasi': "Kolam Utama",
            'jam': "14:00",
            'tanggal': (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 3,
            'status': "Terjadwal"
        }
    elif pk == 102:
        detail = {
            'id': 102,
            'nama_atraksi': "Atraksi Simpanse",
            'lokasi': "Panggung A",
            'jam': "10:30",
            'tanggal': (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 2,
            'status': "Terjadwal"
        }
    elif pk == 103:
        detail = {
            'id': 103,
            'nama_atraksi': "Parade Gajah",
            'lokasi': "Area Tengah",
            'jam': "16:00",
            'tanggal': (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 4,
            'status': "Dibatalkan"
        }
    else:
        # Return 404 if not found
        return JsonResponse({'error': 'Reservasi tidak ditemukan'}, status=404)
    
    return JsonResponse(detail)

def create_reservasi(request):
    """
    View untuk membuat reservasi baru
    """
    if request.method == 'POST':
        # In a real implementation, this would create a new reservation in the database
        # For prototype, we'll just redirect back to the appropriate page
        
        # Process form data
        # atraksi_id = request.POST.get('atraksi')
        # tanggal = request.POST.get('tanggal')
        # jumlah_tiket = request.POST.get('jumlah_tiket')
        # username = request.POST.get('username')
        
        # Create new reservation
        # ...
        
        # Determine the referrer to redirect appropriately
        referer = request.META.get('HTTP_REFERER', '')
        if 'manajemen-reservasi' in referer:
            return redirect('booking_tiket:manajemen_data_reservasi')
        else:
            return redirect('booking_tiket:reservasi')
    
    # If not POST, redirect to referrer or default page
    referer = request.META.get('HTTP_REFERER', '')
    if 'manajemen-reservasi' in referer:
        return redirect('booking_tiket:manajemen_data_reservasi')
    else:
        return redirect('booking_tiket:reservasi')

def update_reservasi(request, pk):
    """
    View untuk mengupdate reservasi
    """
    if request.method == 'POST':
        # In a real implementation, this would update the reservation in the database
        # For prototype, we'll just redirect back to the appropriate page
        
        # Process form data
        # atraksi_id = request.POST.get('atraksi')
        # tanggal = request.POST.get('tanggal')
        # jumlah_tiket = request.POST.get('jumlah_tiket')
        
        # Update reservation
        # ...
        
        # Determine the referrer to redirect appropriately
        referer = request.META.get('HTTP_REFERER', '')
        if 'manajemen-reservasi' in referer:
            return redirect('booking_tiket:manajemen_data_reservasi')
        else:
            return redirect('booking_tiket:reservasi')
    
    # If not POST, redirect to referrer or default page
    referer = request.META.get('HTTP_REFERER', '')
    if 'manajemen-reservasi' in referer:
        return redirect('booking_tiket:manajemen_data_reservasi')
    else:
        return redirect('booking_tiket:reservasi')

def cancel_reservasi(request, pk):
    """
    View untuk membatalkan reservasi
    """
    if request.method == 'POST':
        # In a real implementation, this would set the reservation status to 'Dibatalkan'
        # For prototype, we'll just redirect back to the appropriate page
        
        # Update reservation status
        # ...
        
        # Determine the referrer to redirect appropriately
        referer = request.META.get('HTTP_REFERER', '')
        if 'manajemen-reservasi' in referer:
            return redirect('booking_tiket:manajemen_data_reservasi')
        else:
            return redirect('booking_tiket:reservasi')
    
    # If not POST, redirect to referrer or default page
    referer = request.META.get('HTTP_REFERER', '')
    if 'manajemen-reservasi' in referer:
        return redirect('booking_tiket:manajemen_data_reservasi')
    else:
        return redirect('booking_tiket:reservasi')

def manajemen_data_reservasi(request):
    """
    View untuk menampilkan halaman manajemen data reservasi
    """
    # Dummy data for prototype
    # In a real implementation, this would come from the database
    atraksi_list = [
        {
            'pk': 1,
            'nama': "Pertunjukan Lumba-lumba",
            'lokasi': "Kolam Utama",
            'jadwal': "14:00",
        },
        {
            'pk': 2,
            'nama': "Atraksi Simpanse",
            'lokasi': "Panggung A",
            'jadwal': "10:30",
        },
        {
            'pk': 3,
            'nama': "Parade Gajah",
            'lokasi': "Area Tengah",
            'jadwal': "16:00",
        }
    ]
    
    # Dummy reservasi data with username added
    today = datetime.now().date()
    reservasi_list = [
        {
            'id': 101,
            'username': 'johndoe123',
            'nama_atraksi': "Pertunjukan Lumba-lumba",
            'lokasi': "Kolam Utama",
            'jam': "14:00",
            'tanggal': (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 3,
            'status': "Terjadwal"
        },
        {
            'id': 102,
            'username': 'janedoe456',
            'nama_atraksi': "Atraksi Simpanse",
            'lokasi': "Panggung A",
            'jam': "10:30",
            'tanggal': (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 2,
            'status': "Terjadwal"
        },
        {
            'id': 103,
            'username': 'bobsmith789',
            'nama_atraksi': "Parade Gajah",
            'lokasi': "Area Tengah",
            'jam': "16:00",
            'tanggal': (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            'jumlah_tiket': 4,
            'status': "Dibatalkan"
        }
    ]
    
    context = {
        'atraksi_list': atraksi_list,
        'reservasi_list': reservasi_list
    }
    
    return render(request, 'manajemen_data_reservasi.html', context)