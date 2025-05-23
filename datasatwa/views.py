from django.shortcuts import render, redirect
from django.db import connection
from uuid import UUID 
import uuid


def dictfetchall(cursor):
    "Helper: ambil hasil cursor sebagai list of dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def daftar_satwa(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")  
        cursor.execute("""
            SELECT
                id,
                nama AS nama_individu,
                spesies,
                asal_hewan,
                tanggal_lahir,
                status_kesehatan,
                nama_habitat AS habitat,
                url_foto
            FROM HEWAN
            ORDER BY nama
        """)
        data = dictfetchall(cursor)

    return render(request, 'daftar_satwa.html', {'data': data})



def home(request):
    return render(request, 'home.html')

def tambah_satwa(request):
    # Ambil daftar habitat dari DB
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("SELECT nama FROM HABITAT ORDER BY nama")
        habitat_choices = [row[0] for row in cursor.fetchall()]

    status_choices = ["Sehat", "Sakit", "Dalam Pemantauan", "Lainnya"]

    if request.method == 'POST':
        # Ambil input dari form
        nama = request.POST.get('nama_individu') or None
        spesies = request.POST.get('spesies')
        asal = request.POST.get('asal_hewan')
        tgl_lahir = request.POST.get('tanggal_lahir') or None
        status = request.POST.get('status_kesehatan')
        habitat = request.POST.get('habitat')
        url_foto = request.POST.get('url_foto') or None

        # Validasi duplikat: cek apakah data hewan dengan kombinasi tersebut sudah ada
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT COUNT(*) FROM HEWAN
                WHERE nama = %s AND spesies = %s AND tanggal_lahir = %s
            """, [nama, spesies, tgl_lahir])
            exists = cursor.fetchone()[0] > 0

        if exists:
            return render(request, 'form_satwa.html', {
                'error': "Data hewan tersebut sudah terdaftar.",
                'habitat_choices': habitat_choices,
                'status_choices': status_choices
            })

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                INSERT INTO HEWAN (id, nama, spesies, asal_hewan, tanggal_lahir, status_kesehatan, nama_habitat, url_foto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [str(uuid.uuid4()), nama, spesies, asal, tgl_lahir, status, habitat, url_foto])

        return redirect('datasatwa:daftar_satwa')

    return render(request, 'form_satwa.html', {
        'habitat_choices': habitat_choices,
        'status_choices': status_choices
    })

def edit_satwa(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("SELECT * FROM HEWAN WHERE id = %s", [str(id)])
        result = cursor.fetchone()
        if not result:
            return HttpResponse("Satwa not found", status=404)
        columns = [col[0] for col in cursor.description]
        satwa = dict(zip(columns, result))

        cursor.execute("SELECT nama FROM HABITAT ORDER BY nama")
        habitat_choices = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        nama = request.POST.get("nama_individu")
        spesies = request.POST.get("spesies")
        asal = request.POST.get("asal_hewan")
        tgl = request.POST.get("tanggal_lahir")
        status = request.POST.get("status_kesehatan")
        habitat = request.POST.get("nama_habitat")
        foto = request.POST.get("url_foto")

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                UPDATE HEWAN
                SET nama = %s, spesies = %s, asal_hewan = %s,
                    tanggal_lahir = %s, status_kesehatan = %s,
                    nama_habitat = %s, url_foto = %s
                WHERE id = %s
            """, [nama, spesies, asal, tgl, status, habitat, foto, str(id)])
        return redirect('datasatwa:daftar_satwa')

    return render(request, 'edit_satwa.html', {
        'satwa': satwa,
        'status_choices': ["Sehat", "Sakit", "Dalam Pemantauan", "Lainnya"],
        'habitat_choices': habitat_choices
    })

def hapus_satwa(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO SIZOPI")
        cursor.execute("DELETE FROM HEWAN WHERE id = %s", [str(id)])
    return redirect('datasatwa:daftar_satwa')








