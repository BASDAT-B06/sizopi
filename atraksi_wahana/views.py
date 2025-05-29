from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
import json
import psycopg2
from django.shortcuts import render, redirect
from django.contrib import messages
import uuid
import datetime
import psycopg2.pool
import os
from dotenv import load_dotenv
from .form import AddAttractionForm, AddWahanaForm
from django.contrib.auth.decorators import login_required
import json

load_dotenv(override=True) 

# For deployment
DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname="railway",
    user="postgres",
    password="NtrtcaMLQLEEGnNopTYFXNJJOlbmMVYt",
    host="postgres.railway.internal",
    port="5432",
    database="-c search_path=sizopi"
)

# For development
# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     options="-c search_path=sizopi"
# )

def get_db_connection():
    conn = DB_POOL.getconn()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sizopi")
    return conn

def release_db_connection(conn):
    DB_POOL.putconn(conn)

def staff_admin_required(view_func):
    """
    Decorator to check if user is logged in and has staff_admin role
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated', False):
            messages.error(request, 'Login required to access this page.')
            return redirect('authentication:login')
        
        if request.session.get('role') != 'staf_admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('main:main')
            
        return view_func(request, *args, **kwargs)
    return wrapper

@staff_admin_required
def manajemen_data_atraksi(request):
    conn = get_db_connection()
    atraksis = []
    pelatih_list = []
    hewan_list = []
    
    try:
        with conn.cursor() as cur:
            # Fetch all trainers
            cur.execute("""
                SELECT p.username, p.nama_depan, p.nama_tengah, p.nama_belakang 
                FROM PELATIH_HEWAN ph
                JOIN PENGGUNA p ON ph.username_lh = p.username
            """)
            
            pelatih_rows = cur.fetchall()
            for row in pelatih_rows:
                full_name = f"{row[1]}"
                if row[2]:  # If middle name exists
                    full_name += f" {row[2]}"
                full_name += f" {row[3]}"
                
                pelatih_list.append({
                    'id': row[0],
                    'nama': full_name
                })
            
            # Fetch all animals
            cur.execute("""
                SELECT id, nama, spesies 
                FROM HEWAN
                ORDER BY nama
            """)
            
            hewan_rows = cur.fetchall()
            for row in hewan_rows:
                hewan_list.append({
                    'id': row[0],
                    'nama': row[1],
                    'jenis': row[2]
                })
            
            # Fetch all attractions with related information
            cur.execute("""
                SELECT 
                    a.nama_atraksi, 
                    a.lokasi, 
                    f.kapasitas_max, 
                    f.jadwal,
                    jp.username_lh
                FROM ATRAKSI a
                JOIN FASILITAS f ON a.nama_atraksi = f.nama
                LEFT JOIN JADWAL_PENUGASAN jp ON a.nama_atraksi = jp.nama_atraksi
            """)
            
            atraksi_rows = cur.fetchall()
            for row in atraksi_rows:
                nama_atraksi = row[0]
                pelatih_id = row[4]
                pelatih_name = ""
                
                # Get the trainer's full name if available
                if pelatih_id:
                    cur.execute("""
                        SELECT p.nama_depan, p.nama_tengah, p.nama_belakang 
                        FROM PENGGUNA p
                        WHERE p.username = %s
                    """, (pelatih_id,))
                    
                    pelatih_info = cur.fetchone()
                    if pelatih_info:
                        pelatih_name = f"{pelatih_info[0]}"
                        if pelatih_info[1]:  # If middle name exists
                            pelatih_name += f" {pelatih_info[1]}"
                        pelatih_name += f" {pelatih_info[2]}"
                
                # Get participating animals for this attraction
                cur.execute("""
                    SELECT h.id, h.nama, h.spesies
                    FROM BERPARTISIPASI bp
                    JOIN HEWAN h ON bp.id_hewan = h.id
                    WHERE bp.nama_fasilitas = %s
                """, (nama_atraksi,))
                
                hewan_rows = cur.fetchall()
                hewan_names = []
                hewan_ids = []
                
                for hewan in hewan_rows:
                    hewan_names.append(f"{hewan[1]} ({hewan[2]})")
                    hewan_ids.append(str(hewan[0]))
                
                # Format the time
                jadwal = row[3].strftime('%H:%M') if row[3] else ''
                
                atraksis.append({
                    'nama': nama_atraksi,
                    'lokasi': row[1],
                    'kapasitas': row[2],
                    'jadwal': jadwal,
                    'hewan': ', '.join(hewan_names) if hewan_names else 'Tidak ada',
                    'hewan_ids': hewan_ids,
                    'pelatih': pelatih_name if pelatih_name else 'Tidak ada',
                    'pelatih_id': pelatih_id if pelatih_id else ''
                })
                
    except Exception as e:
        messages.error(request, f"Error retrieving data: {str(e)}")
    finally:
        release_db_connection(conn)
        
    context = {
        'atraksis': atraksis,
        'pelatih_list': pelatih_list,
        'hewan_list': hewan_list
    }
    
    return render(request, 'manajemen_data_atraksi.html', context)

@staff_admin_required
def tambah_atraksi(request):
    if request.method == 'GET':
        conn = get_db_connection()
        pelatih_list = []
        hewan_list = []

        try:
            with conn.cursor() as cur:
                # Ambil data pelatih
                cur.execute("""
                    SELECT p.username, p.nama_depan, p.nama_tengah, p.nama_belakang
                    FROM PELATIH_HEWAN ph
                    JOIN PENGGUNA p ON ph.username_lh = p.username
                """)
                pelatih_rows = cur.fetchall()
                for row in pelatih_rows:
                    full_name = f"{row[1]}"
                    if row[2]:  # Jika ada nama tengah
                        full_name += f" {row[2]}"
                    full_name += f" {row[3]}"
                    pelatih_list.append({'id': row[0], 'nama': full_name})

                # Ambil data hewan
                cur.execute("""
                    SELECT id, nama, spesies
                    FROM HEWAN
                    ORDER BY nama
                """)
                hewan_rows = cur.fetchall()
                for row in hewan_rows:
                    hewan_list.append({'id': row[0], 'nama': row[1], 'jenis': row[2]})
        except Exception as e:
            messages.error(request, f"Error retrieving data: {str(e)}")
        finally:
            release_db_connection(conn)

        context = {
            'pelatih_list': pelatih_list,
            'hewan_list': hewan_list,
        }
        return render(request, 'tambah_atraksi.html', context)

    elif request.method == 'POST':
        nama = request.POST.get('nama')
        lokasi = request.POST.get('lokasi')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        jadwal_full = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(jadwal, '%H:%M').time())
        pelatih = request.POST.get('pelatih')
        hewan_ids = request.POST.getlist('hewan')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Periksa apakah nama atraksi sudah ada
                cur.execute("SELECT 1 FROM FASILITAS WHERE nama = %s", (nama,))
                if cur.fetchone():
                    messages.error(request, "Nama atraksi sudah digunakan.")
                    return redirect('atraksi_wahana:manajemen_data_atraksi')

                # Masukkan data ke tabel FASILITAS
                cur.execute("""
                    INSERT INTO FASILITAS (nama, jadwal, kapasitas_max)
                    VALUES (%s, %s, %s)
                """, (nama, jadwal_full, kapasitas))

                # Masukkan data ke tabel ATRAKSI
                cur.execute("""
                    INSERT INTO ATRAKSI (nama_atraksi, lokasi)
                    VALUES (%s, %s)
                """, (nama, lokasi))

                # Masukkan data pelatih jika ada
                if pelatih:
                    cur.execute("""
                        INSERT INTO JADWAL_PENUGASAN (username_lh, tgl_penugasan, nama_atraksi)
                        VALUES (%s, %s, %s)
                    """, (pelatih, datetime.date.today(), nama))

                # Masukkan data hewan yang berpartisipasi
                for hewan_id in hewan_ids:
                    cur.execute("""
                        INSERT INTO BERPARTISIPASI (nama_fasilitas, id_hewan)
                        VALUES (%s, %s)
                    """, (nama, hewan_id))

                conn.commit()
                messages.success(request, "Atraksi berhasil ditambahkan.")
        except Exception as e:
            conn.rollback()
            messages.error(request, f"Error menambahkan atraksi: {str(e)}")
        finally:
            release_db_connection(conn)

        return redirect('atraksi_wahana:manajemen_data_atraksi')

    return HttpResponseForbidden("Invalid request method.")

@staff_admin_required
def edit_atraksi(request):
    if request.method == 'GET':
        conn = get_db_connection()
        pelatih_list = []
        hewan_list = []
        nama = request.GET.get('nama', '')
        lokasi = request.GET.get('lokasi', '')
        kapasitas = request.GET.get('kapasitas', '')
        jadwal = request.GET.get('jadwal', '')
        pelatih_id = request.GET.get('pelatih', '')
        hewan_ids = request.GET.getlist('hewan[]')

        try:
            with conn.cursor() as cur:
                # Ambil data pelatih
                cur.execute("""
                    SELECT p.username, p.nama_depan, p.nama_tengah, p.nama_belakang
                    FROM PELATIH_HEWAN ph
                    JOIN PENGGUNA p ON ph.username_lh = p.username
                """)
                pelatih_rows = cur.fetchall()
                for row in pelatih_rows:
                    full_name = f"{row[1]}"
                    if row[2]:  # Jika ada nama tengah
                        full_name += f" {row[2]}"
                    full_name += f" {row[3]}"
                    pelatih_list.append({'id': row[0], 'nama': full_name})

                # Ambil data hewan
                cur.execute("""
                    SELECT id, nama, spesies
                    FROM HEWAN
                    ORDER BY nama
                """)
                hewan_rows = cur.fetchall()
                for row in hewan_rows:
                    hewan_list.append({'id': row[0], 'nama': row[1], 'jenis': row[2]})

                # Ambil data hewan yang berpartisipasi
                cur.execute("""
                    SELECT h.id
                    FROM BERPARTISIPASI bp
                    JOIN HEWAN h ON bp.id_hewan = h.id
                    WHERE bp.nama_fasilitas = %s
                """, (nama,))
                hewan_ids = [row[0] for row in cur.fetchall()]
        except Exception as e:
            messages.error(request, f"Error retrieving data: {str(e)}")
        finally:
            release_db_connection(conn)

        context = {
            'nama': nama,
            'lokasi': lokasi,
            'kapasitas': kapasitas,
            'jadwal': jadwal,
            'pelatih_id': pelatih_id,
            'hewan_ids': hewan_ids,
            'pelatih_list': pelatih_list,
            'hewan_list': hewan_list,
        }
        return render(request, 'edit_atraksi.html', context)

    elif request.method == 'POST':
        nama = request.POST.get('nama')
        lokasi = request.POST.get('lokasi')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        jadwal_full = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(jadwal, '%H:%M').time())
        pelatih = request.POST.get('pelatih')
        hewan_ids = request.POST.getlist('hewan')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Update data di tabel FASILITAS
                cur.execute("""
                    UPDATE FASILITAS
                    SET jadwal = %s, kapasitas_max = %s
                    WHERE nama = %s
                """, (jadwal_full, kapasitas, nama))

                # Update data di tabel ATRAKSI
                cur.execute("""
                    UPDATE ATRAKSI
                    SET lokasi = %s
                    WHERE nama_atraksi = %s
                """, (lokasi, nama))

                # Update data pelatih
                cur.execute("DELETE FROM JADWAL_PENUGASAN WHERE nama_atraksi = %s", (nama,))
                if pelatih:
                    cur.execute("""
                        INSERT INTO JADWAL_PENUGASAN (username_lh, tgl_penugasan, nama_atraksi)
                        VALUES (%s, %s, %s)
                    """, (pelatih, datetime.date.today(), nama))

                # Update data hewan yang berpartisipasi
                cur.execute("DELETE FROM BERPARTISIPASI WHERE nama_fasilitas = %s", (nama,))
                for hewan_id in hewan_ids:
                    cur.execute("""
                        INSERT INTO BERPARTISIPASI (nama_fasilitas, id_hewan)
                        VALUES (%s, %s)
                    """, (nama, hewan_id))

                conn.commit()
                messages.success(request, "Atraksi berhasil diperbarui.")
        except Exception as e:
            conn.rollback()
            messages.error(request, f"Error memperbarui atraksi: {str(e)}")
        finally:
            release_db_connection(conn)

        return redirect('atraksi_wahana:manajemen_data_atraksi')

    return HttpResponseForbidden("Invalid request method.")

@staff_admin_required
def manajemen_data_wahana(request):
    conn = get_db_connection()
    wahanas = []
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT w.nama_wahana, f.kapasitas_max, f.jadwal, w.peraturan
                FROM WAHANA w
                JOIN FASILITAS f ON w.nama_wahana = f.nama
            """)
            
            wahana_rows = cur.fetchall()
            for row in wahana_rows:
                # Parse peraturan from text to array
                peraturan_text = row[3]
                peraturan_array = [rule.strip('"') for rule in peraturan_text.strip('{}').split(',')]
                
                # Format the time
                jadwal = row[2].strftime('%H:%M') if row[2] else ''
                
                wahanas.append({
                    'nama': row[0],
                    'kapasitas': row[1],
                    'jadwal': jadwal,
                    'peraturan': peraturan_array,
                    'peraturan_json': json.dumps(peraturan_array)
                })
                
    except Exception as e:
        messages.error(request, f"Error retrieving data: {str(e)}")
    finally:
        release_db_connection(conn)
        
    context = {
        'wahanas': wahanas
    }
    
    return render(request, 'manajemen_data_wahana.html', context)

@staff_admin_required
def tambah_wahana(request):
    if request.method == 'GET':
        return render(request, 'tambah_wahana.html')
    elif request.method == 'POST':
        nama = request.POST.get('nama')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        jadwal_full = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(jadwal, '%H:%M').time())
        peraturan = request.POST.getlist('peraturan[]')
        peraturan_text = '{' + ','.join([f'"{rule}"' for rule in peraturan]) + '}'

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Periksa apakah nama wahana sudah ada
                cur.execute("SELECT 1 FROM FASILITAS WHERE nama = %s", (nama,))
                if cur.fetchone():
                    messages.error(request, "Nama wahana sudah digunakan.")
                    return redirect('atraksi_wahana:manajemen_data_wahana')

                # Masukkan data ke tabel FASILITAS
                cur.execute("""
                    INSERT INTO FASILITAS (nama, jadwal, kapasitas_max)
                    VALUES (%s, %s, %s)
                """, (nama, jadwal_full, kapasitas))

                # Masukkan data ke tabel ATRAKSI
                cur.execute("""
                    INSERT INTO WAHANA (nama_wahana, peraturan)
                    VALUES (%s, %s)
                """, (nama, peraturan_text))

                conn.commit()
                messages.success(request, "Wahana berhasil ditambahkan.")
        except Exception as e:
            conn.rollback()
            messages.error(request, f"Error menambahkan wahana: {str(e)}")
        finally:
            release_db_connection(conn)

        return redirect('atraksi_wahana:manajemen_data_wahana')

    return HttpResponseForbidden("Invalid request method.")

@staff_admin_required
def edit_wahana(request):
    if request.method == 'GET':
        conn = get_db_connection()
        nama = request.GET.get('nama', '')
        kapasitas = request.GET.get('kapasitas', '')
        jadwal = request.GET.get('jadwal', '')
        peraturan_text = request.GET.get('peraturan', '')
        peraturan = peraturan_text.strip('{}').split(',')
        peraturan = [rule.strip('"') for rule in peraturan]
        print(f"Nama: {nama}, Kapasitas: {kapasitas}, Jadwal: {jadwal}, Peraturan: {peraturan}")

        context = {
            'nama': nama,
            'kapasitas': kapasitas,
            'jadwal': jadwal,
            'peraturan': peraturan,
        }
        return render(request, 'edit_wahana.html', context)

    elif request.method == 'POST':
        nama = request.POST.get('nama')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        jadwal_full = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(jadwal, '%H:%M').time())
        peraturan = request.POST.getlist('peraturan[]')
        peraturan_text = '{' + ','.join([f'"{rule}"' for rule in peraturan]) + '}'
        print(f"Nama: {nama}, Kapasitas: {kapasitas}, Jadwal: {jadwal}, Peraturan: {peraturan}")


        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Update data di tabel FASILITAS
                cur.execute("""
                    UPDATE FASILITAS
                    SET jadwal = %s, kapasitas_max = %s
                    WHERE nama = %s
                """, (jadwal_full, kapasitas, nama))

                # Update data di tabel WAHANA
                cur.execute("""
                    UPDATE WAHANA
                    SET peraturan = %s
                    WHERE nama_wahana = %s
                """, (peraturan_text, nama))

                conn.commit()
                messages.success(request, "WAHANA berhasil diperbarui.")
        except Exception as e:
            conn.rollback()
            messages.error(request, f"Error memperbarui wahana: {str(e)}")
        finally:
            release_db_connection(conn)

        return redirect('atraksi_wahana:manajemen_data_wahana')
    return HttpResponseForbidden("Invalid request method.")

@staff_admin_required
def hapus_atraksi(request):
    nama = request.GET.get('nama')  # Ambil nama atraksi dari query parameter
    if not nama:
        messages.error(request, "Nama atraksi tidak ditemukan.")
        return redirect('atraksi_wahana:manajemen_data_atraksi')

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Hapus data dari tabel FASILITAS (akan cascade ke tabel ATRAKSI, BERPARTISIPASI, dan JADWAL_PENUGASAN)
            cur.execute("DELETE FROM FASILITAS WHERE nama = %s", (nama,))
        conn.commit()
        messages.success(request, f"Atraksi '{nama}' berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        messages.error(request, f"Error menghapus atraksi: {str(e)}")
    finally:
        release_db_connection(conn)

    return redirect('atraksi_wahana:manajemen_data_atraksi')

@staff_admin_required
def hapus_wahana(request):
    nama = request.GET.get('nama')  # Ambil nama atraksi dari query parameter
    if not nama:
        messages.error(request, "Nama wahana tidak ditemukan.")
        return redirect('atraksi_wahana:manajemen_data_wahana')

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Hapus data dari tabel FASILITAS (akan cascade ke tabel WAHANA, BERPARTISIPASI, dan JADWAL_PENUGASAN)
            cur.execute("DELETE FROM FASILITAS WHERE nama = %s", (nama,))
        conn.commit()
        messages.success(request, f"Wahana '{nama}' berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        messages.error(request, f"Error menghapus wahana: {str(e)}")
    finally:
        release_db_connection(conn)

    return redirect('atraksi_wahana:manajemen_data_wahana')