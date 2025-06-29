from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import json
from .services import AdopsiService
from .utils import get_user_context
from django.db import connection

# Views untuk Staf Administrasi
def adoption_list_admin(request):
    """Halaman utama program adopsi untuk admin"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return redirect('/auth/login/')
    
    animals = AdopsiService.get_all_animals_with_adoption_status()
    
    context = {
        **user_context,
        'animals': animals,
        'title': 'Program Adopsi Satwa: Bantu Mereka dengan Cinta'
    }
    return render(request, 'adoption/admin/adoption_list_admin.html', context)

def adopter_list(request):
    """Halaman daftar adopter"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return redirect('/auth/login/')
    
    top_adopters = AdopsiService.get_top_adopters()
    individual_adopters = AdopsiService.get_individual_adopters()
    organization_adopters = AdopsiService.get_organization_adopters()
    
    context = {
        **user_context,
        'individual_adopters': individual_adopters,
        'organization_adopters': organization_adopters,
        'top_adopters': top_adopters,
        'title': 'Daftar Adopter'
    }
    return render(request, 'adoption/admin/adopter_list.html', context)

def adopter_history(request, adopter_id):
    """Halaman riwayat adopsi adopter"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return redirect('/auth/login/')
    
    adopter = AdopsiService.get_adopter_by_id(adopter_id)
    if not adopter:
        return HttpResponse("Adopter tidak ditemukan", status=404)
    
    history = AdopsiService.get_adopter_history(adopter_id)
    
    context = {
        **user_context,
        'adopter': adopter,
        'history': history,
        'title': f'Riwayat Adopsi - {adopter["name"]}'
    }
    return render(request, 'adoption/admin/adopter_history.html', context)

# Views untuk Pengunjung (Adopter)
def adoption_list_user(request):
    """Halaman utama program adopsi untuk user"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"]:
        return redirect('/auth/login/')
    
    if user_context["user_role"] != "pengunjung":
        return redirect('/')
    
    animals = AdopsiService.get_user_active_adoptions(user_context["username"])
    
    context = {
        **user_context,
        'animals': animals,
        'title': 'Program Adopsi Satwa: Bantu Mereka dengan Cinta'
    }
    return render(request, 'adoption/user/adoption_list_user.html', context)

def adoption_certificate(request, animal_id):
    """Halaman sertifikat adopsi - DIPERBAIKI"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"]:
        return redirect('/auth/login/')
    
    animal = AdopsiService.get_animal_adoption_info(animal_id, user_context["username"])
    if not animal:
        return HttpResponse("Data adopsi tidak ditemukan", status=404)
    
    adopter_name = AdopsiService.get_adopter_name_for_certificate(
        user_context["username"], animal_id
    )
    
    adopter = {
        'name': adopter_name if adopter_name else user_context["username"]
    }
    
    context = {
        **user_context,
        'animal': animal,
        'adopter': adopter
    }
    return render(request, 'adoption/user/adoption_certificate.html', context)

def animal_report(request, animal_id):
    """Halaman laporan kondisi hewan"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"]:
        return redirect('/auth/login/')
    
    animal = AdopsiService.get_animal_adoption_info(animal_id, user_context["username"])
    if not animal:
        return HttpResponse("Data adopsi tidak ditemukan", status=404)
    
    records = AdopsiService.get_medical_records(animal_id, animal['start_date'])
    
    context = {
        **user_context,
        'animal': animal,
        'records': records,
        'title': 'Laporan Kondisi Satwa'
    }
    return render(request, 'adoption/user/animal_report.html', context)

# AJAX Views
def verify_adopter_account(request):
    """AJAX endpoint untuk verifikasi akun adopter"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        
        user_data = AdopsiService.verify_user_account(username)
        
        if user_data:
            return JsonResponse({
                'success': True,
                'user_data': user_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Username tidak ditemukan atau bukan pengunjung'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def create_adoption_individu(request):
    """Membuat adopsi baru untuk individu"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            animal_id = request.POST.get('animal_id')
            nik = request.POST.get('nik')
            nama = request.POST.get('nama')
            alamat = request.POST.get('alamat')
            no_telepon = request.POST.get('no_telepon')
            
            try:
                nominal = int(request.POST.get('nominal'))
                if nominal <= 0:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Nominal kontribusi harus lebih dari 0'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Nominal kontribusi harus berupa angka yang valid'
                })

            try:
                periode = int(request.POST.get('periode'))
                if periode not in [3, 6, 12]:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Periode adopsi harus 3, 6, atau 12 bulan'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Periode adopsi tidak valid'
                })
            
            if hasattr(connection.connection, 'notices'):
                connection.connection.notices.clear()
            
            success = AdopsiService.create_individual_adoption(
                username, animal_id, nik, nama, alamat, 
                no_telepon, nominal, periode
            )
            
            trigger_messages = capture_trigger_messages()

            if success:
                response_data = {'success': True}
                if trigger_messages:
                    response_data['trigger_messages'] = trigger_messages
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'message': 'Gagal mendaftarkan adopsi'})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def create_adoption_organisasi(request):
    """Membuat adopsi baru untuk organisasi"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            animal_id = request.POST.get('animal_id')
            npp = request.POST.get('npp')
            nama_organisasi = request.POST.get('nama_organisasi')
            alamat = request.POST.get('alamat')
            kontak = request.POST.get('kontak')
            
            # Validasi nominal (hapus duplikasi)
            try:
                nominal = int(request.POST.get('nominal'))
                if nominal <= 0:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Nominal kontribusi harus lebih dari 0'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Nominal kontribusi harus berupa angka yang valid'
                })
            
            # Validasi periode (hapus duplikasi)
            try:
                periode = int(request.POST.get('periode'))
                if periode not in [3, 6, 12]:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Periode adopsi harus 3, 6, atau 12 bulan'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Periode adopsi tidak valid'
                })
            
            if hasattr(connection.connection, 'notices'):
                connection.connection.notices.clear()
            
            success = AdopsiService.create_organization_adoption(
                username, animal_id, npp, nama_organisasi, 
                alamat, kontak, nominal, periode
            )
            
            trigger_messages = capture_trigger_messages()

            if success:
                response_data = {'success': True}
                if trigger_messages:
                    response_data['trigger_messages'] = trigger_messages
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'message': 'Gagal mendaftarkan adopsi'})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def update_payment_status(request):
    """Update status pembayaran adopsi"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            animal_id = data.get('animal_id')
            status = data.get('status')
            
            if hasattr(connection.connection, 'notices'):
                connection.connection.notices.clear()
            
            success = AdopsiService.update_payment_status(animal_id, status)
            
            trigger_messages = capture_trigger_messages()
            
            if success:
                response_data = {'success': True}
                if trigger_messages:
                    response_data['trigger_messages'] = trigger_messages
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'message': 'Gagal mengupdate status pembayaran'})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def stop_adoption(request):
    """Menghentikan adopsi"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            animal_id = data.get('animal_id')
            
            success = AdopsiService.stop_adoption(animal_id)
            
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Gagal menghentikan adopsi'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def delete_adopter(request):
    """Menghapus data adopter"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            adopter_id = data.get('adopter_id')
            
            success, message = AdopsiService.delete_adopter(adopter_id)
            
            return JsonResponse({
                'success': success,
                'message': message
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def delete_adoption_history(request):
    """Menghapus riwayat adopsi"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "staf_admin":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            adopter_id = data.get('adopter_id')
            animal_id = data.get('animal_id')
            start_date = data.get('start_date')

            if hasattr(connection.connection, 'notices'):
                connection.connection.notices.clear()
            
            success = AdopsiService.delete_adoption_history(adopter_id, animal_id, start_date)
            
            trigger_messages = []
            if hasattr(connection.connection, 'notices'):
                for notice in connection.connection.notices:
                    notice_text = str(notice).strip()
                    if 'SUKSES:' in notice_text:
                        clean_message = notice_text.replace('NOTICE:', '').strip()
                        trigger_messages.append(clean_message)
            
            if success:
                response_data = {'success': True}
                if trigger_messages:
                    response_data['trigger_messages'] = trigger_messages
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'message': 'Gagal menghapus riwayat adopsi'})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def capture_trigger_messages():
    """Capture PostgreSQL trigger messages"""
    trigger_messages = []
    if hasattr(connection.connection, 'notices'):
        for notice in connection.connection.notices:
            notice_text = str(notice).strip()
            if 'SUKSES:' in notice_text:
                clean_message = notice_text.replace('NOTICE:', '').strip()
                trigger_messages.append(clean_message)
    return trigger_messages

def extend_adoption(request):
    """Perpanjang periode adopsi"""
    user_context = get_user_context(request)
    if not user_context["is_logged_in"] or user_context["user_role"] != "pengunjung":
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    if request.method == 'GET':
        # Untuk menampilkan form perpanjang adopsi
        animal_id = request.GET.get('animal_id')
        if not animal_id:
            return JsonResponse({'success': False, 'message': 'Animal ID required'})
        
        # Get adopter info untuk pre-fill form
        adopter_info = AdopsiService.get_adopter_type_and_info(
            user_context["username"], animal_id
        )
        
        if not adopter_info:
            return JsonResponse({'success': False, 'message': 'Adopsi tidak ditemukan'})
        
        return JsonResponse({
            'success': True,
            'adopter_info': adopter_info
        })
    
    elif request.method == 'POST':
        try:
            username = user_context["username"]
            animal_id = request.POST.get('animal_id')
            
            # Validasi nominal
            try:
                nominal = int(request.POST.get('nominal'))
                if nominal <= 0:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Nominal kontribusi harus lebih dari 0'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Nominal kontribusi harus berupa angka yang valid'
                })
            
            # Validasi periode
            try:
                periode = int(request.POST.get('periode'))
                if periode not in [3, 6, 12]:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Periode adopsi harus 3, 6, atau 12 bulan'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': 'Periode adopsi tidak valid'
                })
            
            if hasattr(connection.connection, 'notices'):
                connection.connection.notices.clear()
            
            success, message = AdopsiService.extend_adoption(
                username, animal_id, nominal, periode
            )

            trigger_messages = capture_trigger_messages()
            
            if success:
                response_data = {'success': True, 'message': message}
                if trigger_messages:
                    response_data['trigger_messages'] = trigger_messages
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'message': message})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})