from django.shortcuts import render
import psycopg2
from psycopg2 import pool
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .form import LoginForm, BaseRegisterForm, RegisterDokterForm, RegisterPengunjungForm, RegisterStaffForm
import uuid
from datetime import datetime, date

DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname="railway",
    user="postgres",
    password="NtrtcaMLQLEEGnNopTYFXNJJOlbmMVYt",
    host="postgres.railway.internal",
    port="5432",
    database="-c search_path=sizopi"
)

def get_db_connection():
    return DB_POOL.getconn()

def release_db_connection(conn):
    DB_POOL.putconn(conn)

# Create your views here.
def login_view(request):
    if request.session.get('is_authenticated', False):
        return redirect('main:main')
    

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Check if input is email or username
                cur.execute("""
                    SELECT username, email, nama_depan, nama_tengah, nama_belakang, 
                           no_telepon, password
                    FROM PENGGUNA
                    WHERE (username = %s OR email = %s) AND password = %s
                """, (username_or_email, username_or_email, password))
                
                user = cur.fetchone()
                
                if user:
                    username = user[0]
                    user_dict = {
                        'username': username,
                        'email': user[1],
                        'nama_depan': user[2],
                        'nama_tengah': user[3] if user[3] else '',
                        'nama_belakang': user[4],
                        'no_telepon': user[5],
                        'role': None  # Will be determined below
                    }
                    
                    # Check user role by checking the extension tables
                    cur.execute("SELECT 1 FROM PENGUNJUNG WHERE username_P = %s", (username,))
                    if cur.fetchone():
                        user_dict['role'] = 'pengunjung'
                        cur.execute("SELECT alamat, tgl_lahir FROM PENGUNJUNG WHERE username_P = %s", (username,))
                        pengunjung_details = cur.fetchone()
                        if pengunjung_details:
                            user_dict.update({
                                'alamat': pengunjung_details[0],
                                'tgl_lahir': pengunjung_details[1].strftime('%Y-%m-%d')
                            })
                    
                    cur.execute("SELECT 1 FROM DOKTER_HEWAN WHERE username_DH = %s", (username,))
                    if cur.fetchone():
                        user_dict['role'] = 'dokter_hewan'
                        cur.execute("SELECT no_STR FROM DOKTER_HEWAN WHERE username_DH = %s", (username,))
                        dokter_details = cur.fetchone()
                        if dokter_details:
                            user_dict['no_str'] = dokter_details[0]
                            
                        # Get dokter specializations
                        cur.execute("""
                            SELECT nama_spesialisasi 
                            FROM SPESIALISASI
                            WHERE username_SH = %s
                        """, (username,))
                        spesialisasi_results = cur.fetchall()
                        user_dict['spesialisasi'] = [row[0] for row in spesialisasi_results] if spesialisasi_results else []
                    
                    cur.execute("SELECT 1 FROM PENJAGA_HEWAN WHERE username_jh = %s", (username,))
                    if cur.fetchone():
                        user_dict['role'] = 'penjaga_hewan'
                        cur.execute("SELECT id_staf FROM PENJAGA_HEWAN WHERE username_jh = %s", (username,))
                        penjaga_details = cur.fetchone()
                        if penjaga_details:
                            user_dict['id_staf'] = str(penjaga_details[0])
                    
                    cur.execute("SELECT 1 FROM PELATIH_HEWAN WHERE username_lh = %s", (username,))
                    if cur.fetchone():
                        user_dict['role'] = 'pelatih_hewan'
                        cur.execute("SELECT id_staf FROM PELATIH_HEWAN WHERE username_lh = %s", (username,))
                        pelatih_details = cur.fetchone()
                        if pelatih_details:
                            user_dict['id_staf'] = str(pelatih_details[0])
                    
                    cur.execute("SELECT 1 FROM STAF_ADMIN WHERE username_sa = %s", (username,))
                    if cur.fetchone():
                        user_dict['role'] = 'staf_admin'
                        cur.execute("SELECT id_staf FROM STAF_ADMIN WHERE username_sa = %s", (username,))
                        admin_details = cur.fetchone()
                        if admin_details:
                            user_dict['id_staf'] = str(admin_details[0])
                    
                    request.session['user'] = user_dict
                    request.session['is_authenticated'] = True
                    request.session['role'] = user_dict['role']
                    return redirect('main:main')
                else:
                    messages.error(request, 'Invalid username/email or password.')
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')
        finally:
            release_db_connection(conn)
    return render(request, 'login.html')

def register_dokter_view(request):
    return render(request, 'register_dokter_hewan.html')

def register_pengunjung_view(request):
    return render(request, 'register_pengunjung.html')

def register_staf_view(request):
    return render(request, 'register_staff.html')