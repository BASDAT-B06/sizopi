from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from datetime import datetime, timedelta
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2 import pool
from urllib.parse import urlparse


load_dotenv(override=True)

# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     options="-c search_path=sizopi"
# )

db_url = os.getenv("DATABASE_URL")
parsed = urlparse(db_url)

DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname=parsed.path.lstrip('/'),
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port,
    options='-c search_path=sizopi'
)

def get_db_connection():
    conn = DB_POOL.getconn()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sizopi")
    return conn

def release_db_connection(conn):
    DB_POOL.putconn(conn)

def check_role(request, allowed_roles):
    user_role = request.session.get('role')
    if user_role not in allowed_roles:
        return False
    return True

def reservasi(request):
    if not check_role(request, ['pengunjung', 'staf_admin']):
        return HttpResponseForbidden("You do not have permission to access this page.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Ambil semua atraksi
            cur.execute("""
                SELECT f.nama, f.jadwal, a.lokasi, f.kapasitas_max, 
                       COALESCE(SUM(r.jumlah_tiket), 0) AS total_tiket_terpesan
                FROM FASILITAS f
                JOIN ATRAKSI a ON f.nama = a.nama_atraksi
                LEFT JOIN RESERVASI r ON f.nama = r.nama_fasilitas
                GROUP BY f.nama, f.jadwal, a.lokasi, f.kapasitas_max
            """)
            atraksi_list = [
                {
                    'nama': row[0],
                    'jadwal': row[1].strftime("%Y-%m-%d"),
                    'jam': row[1].strftime("%H:%M"),
                    'lokasi': row[2],
                    'kapasitas_max': row[3],
                    'total_tiket_terpesan': row[4],
                    'kapasitas_tersisa': row[3] - row[4]
                }
                for row in cur.fetchall()
            ]

            # Ambil semua wahana
            cur.execute("""
                SELECT f.nama, w.peraturan, f.kapasitas_max, 
                       COALESCE(SUM(r.jumlah_tiket), 0) AS total_tiket_terpesan
                FROM FASILITAS f
                JOIN WAHANA w ON f.nama = w.nama_wahana
                LEFT JOIN RESERVASI r ON f.nama = r.nama_fasilitas
                GROUP BY f.nama, w.peraturan, f.kapasitas_max
            """)
            wahana_list = [
                {
                    'nama': row[0],
                    'peraturan': row[1],
                    'kapasitas_max': row[2],
                    'total_tiket_terpesan': row[3],
                    'kapasitas_tersisa': row[2] - row[3]
                }
                for row in cur.fetchall()
            ]

            # Ambil reservasi pengguna
            cur.execute("""
                SELECT r.nama_fasilitas, r.tanggal_kunjungan, r.jumlah_tiket, r.status
                FROM RESERVASI r
                WHERE r.username_p = %s
            """, (request.session.get('user')['username'],))
            user_reservasi = [
                {
                    'nama_fasilitas': row[0],
                    'tanggal_kunjungan': row[1].strftime("%Y-%m-%d"),
                    'jumlah_tiket': row[2],
                    'status': row[3],
                    'lokasi_peraturan': next(
                        (atraksi['lokasi'] for atraksi in atraksi_list if atraksi['nama'] == row[0]),
                        next((wahana['peraturan'] for wahana in wahana_list if wahana['nama'] == row[0]), None)
                    )
                }
                for row in cur.fetchall()
            ]
    finally:
        release_db_connection(conn)

    context = {
        'atraksi_list': atraksi_list,
        'wahana_list': wahana_list,
        'user_reservasi': user_reservasi
    }
    return render(request, 'reservasi.html', context)
def manajemen_data_reservasi(request):
    if not check_role(request, ['staf_admin']):
        return HttpResponseForbidden("You do not have permission to access this page.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.username_p, r.nama_fasilitas, r.tanggal_kunjungan, r.jumlah_tiket, r.status
                FROM RESERVASI r
            """)
            reservasi_list = [
                {
                    'username': row[0],
                    'nama_atraksi': row[1],
                    'tanggal': row[2].strftime("%Y-%m-%d"),
                    'jumlah_tiket': row[3],
                    'status': row[4]
                }
                for row in cur.fetchall()
            ]
    finally:
        release_db_connection(conn)

    context = {
        'reservasi_list': reservasi_list
    }
    return render(request, 'manajemen_data_reservasi.html', context)

def create_reservasi(request):
    if not check_role(request, ['pengunjung']):
        return HttpResponseForbidden("You do not have permission to access this page.")

    if request.method == 'GET':
        nama_fasilitas = request.GET.get('nama', '')
        lokasi_peraturan = request.GET.get('lokasi', '') or request.GET.get('peraturan', '')
        kategori = request.GET.get('kategori', '')

        context = {
            'nama_fasilitas': nama_fasilitas,
            'lokasi_peraturan': lokasi_peraturan,
            'kategori': kategori,
        }
        return render(request, 'create_reservasi.html', context)

    elif request.method == 'POST':
        username = request.session.get('user')['username']
        nama_fasilitas = request.POST.get('nama_fasilitas')
        tanggal_kunjungan = request.POST.get('tanggal_kunjungan')
        jumlah_tiket = request.POST.get('jumlah_tiket')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO RESERVASI (username_p, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, "Terjadwal"))
                conn.commit()
        finally:
            release_db_connection(conn)

        return redirect('booking_tiket:reservasi')

    return HttpResponseForbidden("Invalid request method.")

def edit_reservasi(request):
    if not check_role(request, ['pengunjung', 'staf_admin']):
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    if request.method == 'GET':
        user_role = request.session.get('role')
        if user_role == 'staf_admin':
            username = request.GET.get('username', '')
        else:
            username = request.session.get('user')['username']
        nama_fasilitas = request.GET.get('nama', '')
        lokasi_peraturan = request.GET.get('lokasi_peraturan', '')
        tanggal_kunjungan = request.GET.get('tanggal_kunjungan')
        jumlah_tiket = request.GET.get('jumlah_tiket')

        context = {
            'username': username,
            'nama_fasilitas': nama_fasilitas,
            'lokasi_peraturan': lokasi_peraturan,
            'tanggal_kunjungan': tanggal_kunjungan,
            'jumlah_tiket': jumlah_tiket,
        }
        return render(request, 'edit_reservasi.html', context)

    elif request.method == 'POST':
        username = request.POST.get('username')
        nama_fasilitas = request.POST.get('nama_fasilitas')
        tanggal_kunjungan = request.POST.get('tanggal_kunjungan')
        jumlah_tiket = request.POST.get('jumlah_tiket')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE RESERVASI
                    SET tanggal_kunjungan = %s, jumlah_tiket = %s
                    WHERE username_p = %s AND nama_fasilitas = %s
                """, (tanggal_kunjungan, jumlah_tiket, username, nama_fasilitas))
                conn.commit()
        finally:
            release_db_connection(conn)

        user_role = request.session.get('role')
        if user_role == 'staf_admin':
            return redirect('booking_tiket:manajemen_data_reservasi')
        elif user_role == 'pengunjung':
            return redirect('booking_tiket:reservasi')
    return HttpResponseForbidden("Invalid request method.")

def cancel_reservasi(request):
    if not check_role(request, ['pengunjung', 'staf_admin']):
        return HttpResponseForbidden("You do not have permission to access this page.")

    if request.method == 'POST':
        username = request.POST.get('username')
        nama_fasilitas = request.POST.get('nama_fasilitas')
        tanggal_kunjungan = request.POST.get('tanggal_kunjungan')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE RESERVASI
                    SET status = 'Dibatalkan'
                    WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s
                """, (username, nama_fasilitas, tanggal_kunjungan))
                conn.commit()
        finally:
            release_db_connection(conn)

        user_role = request.session.get('role')
        if user_role == 'staf_admin':
            return redirect('booking_tiket:manajemen_data_reservasi')
        elif user_role == 'pengunjung':
            return redirect('booking_tiket:reservasi')

    return HttpResponseForbidden("Invalid request method.")