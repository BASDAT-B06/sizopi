from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection


def dictfetchall(cursor):
    "Helper untuk ambil hasil cursor sebagai list of dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def daftar_habitat(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("""
            SELECT nama, luas_area, kapasitas, status
            FROM HABITAT
            ORDER BY nama
        """)
        habitats = dictfetchall(cursor)

    return render(request, 'daftar_habitat.html', {'habitats': habitats})


def tambah_habitat(request):
    if request.method == 'POST':
        nama = request.POST.get('nama_habitat')
        luas_area = request.POST.get('luas_area')
        kapasitas = request.POST.get('kapasitas_maksimal')
        status = request.POST.get('status_lingkungan')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")  # kalau pakai schema
            cursor.execute("""
                INSERT INTO HABITAT (nama, luas_area, kapasitas, status)
                VALUES (%s, %s, %s, %s)
            """, [nama, luas_area, kapasitas, status])

        return redirect('datahabitat:daftar_habitat')

    return render(request, 'form_habitat.html')



def edit_habitat(request, nama):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("SELECT * FROM habitat WHERE nama = %s", [nama])
        habitat = dictfetchall(cursor)
    if not habitat:
        return HttpResponse("Habitat not found.", status=404)
    habitat = habitat[0]

    if request.method == 'POST':
        luas_area = request.POST.get('luas_area')
        kapasitas = request.POST.get('kapasitas')
        status = request.POST.get('status')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                UPDATE habitat
                SET luas_area = %s, kapasitas = %s, status = %s
                WHERE nama = %s
            """, [luas_area, kapasitas, status, nama])

        return redirect('datahabitat:daftar_habitat')

    return render(request, 'edit_habitat.html', {'habitat': habitat})



def hapus_habitat(request, nama):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("DELETE FROM HABITAT WHERE nama = %s", [nama])

    return redirect('datahabitat:daftar_habitat')


def detail_habitat(request, nama):
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
        'species_in_habitat': species
    })
