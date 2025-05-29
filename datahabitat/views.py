from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection


def dictfetchall(cursor):
    "Helper untuk ambil hasil cursor sebagai list of dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

ALLOWED_ROLES = ['penjaga_hewan', 'staf_admin']

def check_role(request):
    user = request.session.get("user", {})
    return user.get("role") in ALLOWED_ROLES

def daftar_habitat(request):
    if not request.session.get("is_authenticated") or not check_role(request):
        return redirect("authentication:login")
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)
    user_role = user.get("user_role")

    
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("""
            SELECT nama, luas_area, kapasitas, status
            FROM HABITAT
            ORDER BY nama
        """)
        habitats = dictfetchall(cursor)

    return render(request, 'daftar_habitat.html', {
        'habitats': habitats,
        "user": request.session.get("user"),
        "user_role": request.session.get("user", {}).get("role"),
        "is_logged_in": request.session.get("is_authenticated", False),
        })

def tambah_habitat(request):
    if not request.session.get("is_authenticated"):
        return redirect("authentication:login")
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)
    user_role = user.get("user_role")

    if request.method == 'POST':
        nama = request.POST.get('nama_habitat', '').strip()
        luas_area = request.POST.get('luas_area', '').strip()
        kapasitas = request.POST.get('kapasitas_maksimal', '').strip()
        status = request.POST.get('status_lingkungan', '').strip()

        error_message = None
        # Validasi: semua field wajib diisi
        if not nama or not luas_area or not kapasitas or not status:
            error_message = "Semua field harus diisi."

        else:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                cursor.execute("SELECT 1 FROM habitat WHERE nama = %s", [nama])
                if cursor.fetchone():
                    error_message = "Nama habitat sudah digunakan. Gunakan nama lain."

        if error_message:
            context = {
                'habitat': {
                    'nama': nama,
                    'luas_area': luas_area,
                    'kapasitas': kapasitas,
                    'status': status,
                },
                'error_message': error_message,
                "user": request.session.get("user"),
                "user_role": request.session.get("user", {}).get("role"),
                "is_logged_in": request.session.get("is_authenticated", False),
            }
            return render(request, 'form_habitat.html', context)

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                INSERT INTO HABITAT (nama, luas_area, kapasitas, status)
                VALUES (%s, %s, %s, %s)
            """, [nama, luas_area, kapasitas, status])

        return redirect('datahabitat:daftar_habitat')

    return render(request, 'form_habitat.html', {
        "user": request.session.get("user"),
        "user_role": request.session.get("user", {}).get("role"),
        "is_logged_in": request.session.get("is_authenticated", False),


    })



def edit_habitat(request, nama):
    if not request.session.get("is_authenticated"):
        return redirect("authentication:login")
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)
    user_role = user.get("user_role")
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("SELECT * FROM habitat WHERE nama = %s", [nama])
        habitat = dictfetchall(cursor)

    if not habitat:
        return HttpResponse("Habitat tidak ditemukan", status=404)

    habitat = habitat[0]

    if request.method == 'POST':
        nama_baru = request.POST.get('nama_baru', '').strip()
        luas_area = request.POST.get('luas_area', '').strip()
        kapasitas = request.POST.get('kapasitas', '').strip()
        status = request.POST.get('status', '').strip()
        error_message = None

        # Validasi semua field harus diisi
        if not nama_baru or not luas_area or not kapasitas or not status:
            error_message = "Semua field harus diisi."

        else:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                cursor.execute("""
                    SELECT 1 FROM habitat
                    WHERE nama = %s AND nama != %s
                """, [nama_baru, nama])
                if cursor.fetchone():
                    error_message = "Nama habitat sudah digunakan oleh habitat lain."

        if error_message:
            # Kirim kembali data + error ke template
            habitat_data = {
                'nama': nama_baru,
                'luas_area': luas_area,
                'kapasitas': kapasitas,
                'status': status,
            }
            return render(request, 'edit_habitat.html', {
                'habitat': habitat_data,
                'error_message': error_message,
                "user": request.session.get("user"),
                "user_role": request.session.get("user", {}).get("role"),
                "is_logged_in": request.session.get("is_authenticated", False),
            })

        # Jika valid, baru update ke database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                UPDATE habitat
                SET nama = %s,
                    luas_area = %s,
                    kapasitas = %s,
                    status = %s
                WHERE nama = %s
            """, [nama_baru, luas_area, kapasitas, status, nama])

            if nama_baru != nama:
                cursor.execute("""
                    UPDATE HEWAN
                    SET nama_habitat = %s
                    WHERE nama_habitat = %s
                """, [nama_baru, nama])

        return redirect('datahabitat:daftar_habitat')


    return render(request, 'edit_habitat.html', {
        'habitat': habitat,
        
        "user": request.session.get("user"),
        "user_role": request.session.get("user", {}).get("role"),
        "is_logged_in": request.session.get("is_authenticated", False),})



def hapus_habitat(request, nama):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("DELETE FROM HABITAT WHERE nama = %s", [nama])

    return redirect('datahabitat:daftar_habitat')


def detail_habitat(request, nama):
    if not request.session.get("is_authenticated"):
        return redirect("authentication:login")
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)
    user_role = user.get("user_role")
    with connection.cursor() as cursor:
        # Get habitat data
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("""
            SELECT nama, luas_area, kapasitas, status
            FROM HABITAT
            WHERE nama = %s
        """, [nama])
        habitat = dictfetchall(cursor)
        if not habitat:
            return HttpResponse("Habitat not found.", status=404)
        habitat = habitat[0]

        cursor.execute("""
            SELECT nama AS nama_individu, spesies, asal_hewan,
                   tanggal_lahir, status_kesehatan
            FROM HEWAN
            WHERE nama_habitat = %s
            ORDER BY nama
        """, [nama])
        species = dictfetchall(cursor)

    return render(request, 'detail_habitat.html', {
        'habitat': habitat,
        'species_in_habitat': species,
        "user": request.session.get("user"),
        "user_role": request.session.get("user", {}).get("role"),
        "is_logged_in": request.session.get("is_authenticated", False),
    })