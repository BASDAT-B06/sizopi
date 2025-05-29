from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from datetime import datetime, timedelta
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2 import pool
from urllib.parse import urlparse, parse_qs



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
    """Check role dan set is_adopter status"""
    user_role = request.session.get('role')
    if user_role not in allowed_roles:
        return False
    
    if user_role == 'pengunjung':
        username = request.session.get('user', {}).get('username', '')
        if username:
            is_adopter = check_is_adopter(username)
            # Update session dengan status adopter
            user_data = request.session.get('user', {})
            user_data['is_adopter'] = is_adopter
            request.session['user'] = user_data
            request.session.modified = True
    
    return True

def check_is_adopter(username):
    """Cek apakah user adalah adopter dengan query database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM ADOPTER 
                WHERE username_adopter = %s
            """, (username,))
            result = cur.fetchone()
            return result[0] > 0 if result else False
    except Exception as e:
        print(f"Error checking adopter status: {e}")
        return False
    finally:
        release_db_connection(conn)

def reservasi(request):
    if not check_role(request, ['pengunjung', 'staf_admin']):
        return HttpResponseForbidden("You do not have permission to access this page.")

    user = request.session.get("user", {})
    is_adopter = user.get("is_adopter", False)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT f.nama, f.jadwal, a.lokasi, f.kapasitas_max
                FROM FASILITAS f
                JOIN ATRAKSI a ON f.nama = a.nama_atraksi
                ORDER BY f.nama
            """)
            atraksi_list = [
                {
                    'nama': row[0],
                    'jadwal': row[1].strftime("%Y-%m-%d") if row[1] else '',
                    'jam': row[1].strftime("%H:%M") if row[1] else '',
                    'lokasi': row[2],
                    'kapasitas_max': row[3],
                    'total_tiket_terpesan': 0,
                    'kapasitas_tersisa': row[3]
                }
                for row in cur.fetchall()
            ]

            cur.execute("""
                SELECT f.nama, w.peraturan, f.kapasitas_max
                FROM FASILITAS f
                JOIN WAHANA w ON f.nama = w.nama_wahana
                ORDER BY f.nama
            """)
            wahana_list = [
                {
                    'nama': row[0],
                    'peraturan': row[1],
                    'kapasitas_max': row[2],
                    'total_tiket_terpesan': 0,
                    'kapasitas_tersisa': row[2]
                }
                for row in cur.fetchall()
            ]

            cur.execute("""
                SELECT r.nama_fasilitas, r.tanggal_kunjungan, r.jumlah_tiket, r.status
                FROM RESERVASI r
                WHERE r.username_p = %s
                ORDER BY r.tanggal_kunjungan DESC
            """, (request.session.get('user')['username'],))
            
            user_reservasi = [
                {
                    'nama_fasilitas': row[0],
                    'tanggal_kunjungan': row[1].strftime("%Y-%m-%d"),
                    'jumlah_tiket': row[2],
                    'status': row[3],
                    'username': request.session.get('user')['username'],  # Tambahkan username
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
        'user_reservasi': user_reservasi,
        'is_adopter': is_adopter
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
                # Cek apakah reservasi sudah ada untuk tanggal yang sama
                cur.execute("""
                    SELECT COUNT(*) FROM RESERVASI 
                    WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s
                """, (username, nama_fasilitas, tanggal_kunjungan))
                
                existing_count = cur.fetchone()[0]
                
                if existing_count > 0:
                    # Jika sudah ada reservasi untuk tanggal yang sama, tampilkan error
                    lokasi_peraturan = request.POST.get('lokasi_peraturan', '')
                    kategori = request.POST.get('kategori', '')
                    
                    context = {
                        'nama_fasilitas': nama_fasilitas,
                        'lokasi_peraturan': lokasi_peraturan,
                        'kategori': kategori,
                        'error_message': f'Anda sudah memiliki reservasi untuk {nama_fasilitas} pada tanggal {tanggal_kunjungan}. Harap pilih tanggal yang berbeda.',
                        'tanggal_kunjungan': tanggal_kunjungan,
                        'jumlah_tiket': jumlah_tiket
                    }
                    return render(request, 'create_reservasi.html', context)
                
                # Jika belum ada, insert reservasi baru
                cur.execute("""
                    INSERT INTO RESERVASI (username_p, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, "Terjadwal"))
                conn.commit()
                
        except psycopg2.Error as e:
            conn.rollback()
            error_message = str(e)
            print(f"Database error: {error_message}")
            
            # Tangkap pesan error dari trigger
            if "ERROR: Kapasitas tersisa" in error_message:
                # Extract pesan error dari trigger
                trigger_error = error_message.split("ERROR: ")[1].split("\n")[0]
                display_error = f"ERROR: {trigger_error}"
            else:
                display_error = 'Terjadi kesalahan saat membuat reservasi. Silakan coba lagi.'
            
            # Tampilkan error dari trigger atau error umum
            lokasi_peraturan = request.POST.get('lokasi_peraturan', '')
            kategori = request.POST.get('kategori', '')
            
            context = {
                'nama_fasilitas': nama_fasilitas,
                'lokasi_peraturan': lokasi_peraturan,
                'kategori': kategori,
                'error_message': display_error,
                'tanggal_kunjungan': tanggal_kunjungan,
                'jumlah_tiket': jumlah_tiket
            }
            return render(request, 'create_reservasi.html', context)
            
        except Exception as e:
            conn.rollback()
            print(f"General error: {e}")
            
            # Tampilkan error umum jika ada masalah lain
            lokasi_peraturan = request.POST.get('lokasi_peraturan', '')
            kategori = request.POST.get('kategori', '')
            
            context = {
                'nama_fasilitas': nama_fasilitas,
                'lokasi_peraturan': lokasi_peraturan,
                'kategori': kategori,
                'error_message': 'Terjadi kesalahan saat membuat reservasi. Silakan coba lagi.',
                'tanggal_kunjungan': tanggal_kunjungan,
                'jumlah_tiket': jumlah_tiket
            }
            return render(request, 'create_reservasi.html', context)
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
            'tanggal_kunjungan_lama': tanggal_kunjungan,  # Simpan tanggal lama
            'jumlah_tiket': jumlah_tiket,
        }
        return render(request, 'edit_reservasi.html', context)

    elif request.method == 'POST':
        username = request.POST.get('username')
        nama_fasilitas = request.POST.get('nama_fasilitas')
        tanggal_kunjungan_baru = request.POST.get('tanggal_kunjungan')
        tanggal_kunjungan_lama = request.POST.get('tanggal_kunjungan_lama')
        jumlah_tiket = request.POST.get('jumlah_tiket')
        lokasi_peraturan = request.POST.get('lokasi_peraturan', '')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Jika tanggal berubah, cek apakah tanggal baru sudah ada
                if tanggal_kunjungan_baru != tanggal_kunjungan_lama:
                    cur.execute("""
                        SELECT COUNT(*) FROM RESERVASI 
                        WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s AND status != 'Dibatalkan'
                    """, (username, nama_fasilitas, tanggal_kunjungan_baru))
                    
                    existing_count = cur.fetchone()[0]
                    
                    if existing_count > 0:
                        # Jika sudah ada reservasi untuk tanggal baru, tampilkan error
                        context = {
                            'username': username,
                            'nama_fasilitas': nama_fasilitas,
                            'lokasi_peraturan': lokasi_peraturan,
                            'tanggal_kunjungan': tanggal_kunjungan_baru,
                            'tanggal_kunjungan_lama': tanggal_kunjungan_lama,
                            'jumlah_tiket': jumlah_tiket,
                            'error_message': f'Anda sudah memiliki reservasi untuk {nama_fasilitas} pada tanggal {tanggal_kunjungan_baru}. Harap pilih tanggal yang berbeda.'
                        }
                        return render(request, 'edit_reservasi.html', context)
                
                # Update reservasi dengan WHERE clause yang lengkap (username, nama_fasilitas, tanggal_lama)
                cur.execute("""
                    UPDATE RESERVASI
                    SET tanggal_kunjungan = %s, jumlah_tiket = %s
                    WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s
                """, (tanggal_kunjungan_baru, jumlah_tiket, username, nama_fasilitas, tanggal_kunjungan_lama))
                
                if cur.rowcount == 0:
                    # Jika tidak ada row yang ter-update
                    context = {
                        'username': username,
                        'nama_fasilitas': nama_fasilitas,
                        'lokasi_peraturan': lokasi_peraturan,
                        'tanggal_kunjungan': tanggal_kunjungan_baru,
                        'tanggal_kunjungan_lama': tanggal_kunjungan_lama,
                        'jumlah_tiket': jumlah_tiket,
                        'error_message': 'Reservasi tidak ditemukan atau sudah berubah. Silakan coba lagi.'
                    }
                    return render(request, 'edit_reservasi.html', context)
                
                conn.commit()
                
        except psycopg2.Error as e:
            conn.rollback()
            error_message = str(e)
            print(f"Database error: {error_message}")
            
            # Tangkap pesan error dari trigger
            if "ERROR: Kapasitas tersisa" in error_message:
                # Extract pesan error dari trigger
                trigger_error = error_message.split("ERROR: ")[1].split("\n")[0]
                display_error = f"ERROR: {trigger_error}"
            else:
                display_error = f'Terjadi kesalahan saat mengupdate reservasi: {str(e)}. Silakan coba lagi.'
            
            context = {
                'username': username,
                'nama_fasilitas': nama_fasilitas,
                'lokasi_peraturan': lokasi_peraturan,
                'tanggal_kunjungan': tanggal_kunjungan_baru,
                'tanggal_kunjungan_lama': tanggal_kunjungan_lama,
                'jumlah_tiket': jumlah_tiket,
                'error_message': display_error
            }
            return render(request, 'edit_reservasi.html', context)
            
        except Exception as e:
            conn.rollback()
            print(f"General error: {e}")
            
            context = {
                'username': username,
                'nama_fasilitas': nama_fasilitas,
                'lokasi_peraturan': lokasi_peraturan,
                'tanggal_kunjungan': tanggal_kunjungan_baru,
                'tanggal_kunjungan_lama': tanggal_kunjungan_lama,
                'jumlah_tiket': jumlah_tiket,
                'error_message': 'Terjadi kesalahan saat mengupdate reservasi. Silakan coba lagi.'
            }
            return render(request, 'edit_reservasi.html', context)
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
        user_role = request.session.get('role')
        if user_role == 'staf_admin':
            username = request.POST.get('username', '')
        else:
            username = request.session.get('user')['username']
        nama_fasilitas = request.POST.get('nama_fasilitas')
        tanggal_kunjungan = request.POST.get('tanggal_kunjungan')
        print(f"Canceling reservation for {username} on {nama_fasilitas} for {tanggal_kunjungan}")

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

        
        if user_role == 'staf_admin':
            return redirect('booking_tiket:manajemen_data_reservasi')
        elif user_role == 'pengunjung':
            return redirect('booking_tiket:reservasi')

    return HttpResponseForbidden("Invalid request method.")