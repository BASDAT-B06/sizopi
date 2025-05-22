from django.shortcuts import render
import psycopg2
from psycopg2 import pool
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .form import LoginForm, BaseRegisterForm, RegisterDokterForm, RegisterPenggunjungForm, RegisterStaffForm
import uuid
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv(override=True) 

# For deployment
# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     dbname="railway",
#     user="postgres",
#     password="NtrtcaMLQLEEGnNopTYFXNJJOlbmMVYt",
#     host="postgres.railway.internal",
#     port="5432",
#     database="-c search_path=sizopi"
# )

# For development
DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    options="-c search_path=sizopi"
)

# For development
def get_db_connection():
    conn = DB_POOL.getconn()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sizopi")
    return conn

# For development
# def get_db_connection():
#     return DB_POOL.getconn()

def release_db_connection(conn):
    DB_POOL.putconn(conn)

# Create your views here.
def login_view(request):
    if request.session.get('is_authenticated', False):
        return redirect('main:main')

    if request.method == 'POST':
        email = request.POST.get('email')
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
                """, (email, email, password))
                
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
    if request.method == 'POST':
        form = RegisterDokterForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                # Pastikan search_path sudah diatur sebelum transaksi dimulai
                with conn.cursor() as cur:
                    # Check if username already exists
                    cur.execute('SELECT 1 FROM PENGGUNA WHERE username = %s OR email = %s', 
                            (form.cleaned_data['username'], form.cleaned_data['email']))
                    if cur.fetchone():
                        messages.error(request, 'Username or email already registered.')
                        return render(request, 'register_dokter_hewan.html', {'form': form})
                
                # Mulai transaksi setelah pengecekan
                conn.autocommit = False
                
                with conn.cursor() as cur:
                    # Insert into PENGGUNA table
                    cur.execute("""
                        INSERT INTO PENGGUNA (
                            username, email, password, nama_depan, 
                            nama_tengah, nama_belakang, no_telepon
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        form.cleaned_data['username'],
                        form.cleaned_data['email'],
                        form.cleaned_data['password1'],
                        form.cleaned_data['nama_depan'],
                        form.cleaned_data['nama_tengah'] if form.cleaned_data.get('nama_tengah') else None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))
                    no_str_formatted = f"STR-DOC-{form.cleaned_data['no_izin_praktek']}"
                    # Insert into DOKTER_HEWAN table
                    cur.execute("""
                        INSERT INTO DOKTER_HEWAN (username_DH, no_STR)
                        VALUES (%s, %s)
                    """, (
                        form.cleaned_data['username'],
                        no_str_formatted
                    ))
                    
                    # Insert specialization information
                    specialization = form.cleaned_data['spesialis']
                    if specialization == 'Lainnya':
                        specialization = form.cleaned_data['spesialis_lainnya']
                    
                    cur.execute("""
                        INSERT INTO SPESIALISASI (username_SH, nama_spesialisasi)
                        VALUES (%s, %s)
                    """, (
                        form.cleaned_data['username'],
                        specialization
                    ))
                
                # Commit transaction
                conn.commit()
                messages.success(request, 'Registration successful. Please login.')
                return redirect('authentication:login')
            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()
                messages.error(request, f'Registration failed: {str(e)}')
            finally:
                conn.autocommit = True
                release_db_connection(conn)
    else:
        form = RegisterDokterForm()
    
    return render(request, 'register_dokter_hewan.html', {'form': form})

def register_pengunjung_view(request):
    if request.method == 'POST':
        form = RegisterPenggunjungForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                # Pastikan search_path sudah diatur sebelum transaksi dimulai
                with conn.cursor() as cur:
                    # Check if username already exists
                    cur.execute('SELECT 1 FROM PENGGUNA WHERE username = %s OR email = %s', 
                             (form.cleaned_data['username'], form.cleaned_data['email']))
                    if cur.fetchone():
                        messages.error(request, 'Username or email already registered.')
                        return render(request, 'register_pengunjung.html', {'form': form})
                
                # Mulai transaksi setelah pengecekan
                conn.autocommit = False
                
                with conn.cursor() as cur:
                    # Insert into PENGGUNA table
                    cur.execute("""
                        INSERT INTO PENGGUNA (
                            username, email, password, nama_depan, 
                            nama_tengah, nama_belakang, no_telepon
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        form.cleaned_data['username'],
                        form.cleaned_data['email'],
                        form.cleaned_data['password1'],
                        form.cleaned_data['nama_depan'],
                        form.cleaned_data['nama_tengah'] if form.cleaned_data.get('nama_tengah') else None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))
                    
                    # Insert into PENGUNJUNG table
                    cur.execute("""
                        INSERT INTO PENGUNJUNG (username_P, alamat, tgl_lahir)
                        VALUES (%s, %s, %s)
                    """, (
                        form.cleaned_data['username'],
                        form.cleaned_data['alamat'],
                        form.cleaned_data['tgl_lahir']
                    ))
                
                # Commit transaction
                conn.commit()
                messages.success(request, 'Registration successful. Please login.')
                return redirect('authentication:login')
            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()
                messages.error(request, f'Registration failed: {str(e)}')
            finally:
                conn.autocommit = True
                release_db_connection(conn)
    else:
        form = RegisterPenggunjungForm()
    
    return render(request, 'register_pengunjung.html', {'form': form})

def register_staf_view(request):
    if request.method == 'POST':
        form = RegisterStaffForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                # Pastikan search_path sudah diatur sebelum transaksi dimulai
                with conn.cursor() as cur:
                    # Check if username already exists
                    cur.execute('SELECT 1 FROM PENGGUNA WHERE username = %s OR email = %s', 
                            (form.cleaned_data['username'], form.cleaned_data['email']))
                    if cur.fetchone():
                        messages.error(request, 'Username or email already registered.')
                        return render(request, 'register_staff.html', {'form': form})
                
                # Mulai transaksi setelah pengecekan
                conn.autocommit = False
                
                with conn.cursor() as cur:
                    # Insert into PENGGUNA table
                    cur.execute("""
                        INSERT INTO PENGGUNA (
                            username, email, password, nama_depan, 
                            nama_tengah, nama_belakang, no_telepon
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        form.cleaned_data['username'],
                        form.cleaned_data['email'],
                        form.cleaned_data['password1'],
                        form.cleaned_data['nama_depan'],
                        form.cleaned_data['nama_tengah'] if form.cleaned_data.get('nama_tengah') else None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))
                    
                    # Generate UUID untuk id_staf
                    id_staf = uuid.uuid4()
                    
                    # Insert ke tabel staff yang sesuai berdasarkan job_role
                    job_role = form.cleaned_data['job_role']
                    if job_role == 'Penjaga Hewan':
                        cur.execute("""
                            INSERT INTO PENJAGA_HEWAN (username_jh, id_staf)
                            VALUES (%s, %s)
                        """, (
                            form.cleaned_data['username'],
                            id_staf
                        ))
                    elif job_role == 'Staff Administrasi':
                        cur.execute("""
                            INSERT INTO STAF_ADMIN (username_sa, id_staf)
                            VALUES (%s, %s)
                        """, (
                            form.cleaned_data['username'],
                            id_staf
                        ))
                    elif job_role == 'Pelatih Pertunjukan':
                        cur.execute("""
                            INSERT INTO PELATIH_HEWAN (username_lh, id_staf)
                            VALUES (%s, %s)
                        """, (
                            form.cleaned_data['username'],
                            id_staf
                        ))
                
                # Commit transaction
                conn.commit()
                messages.success(request, 'Registration successful. Please login.')
                return redirect('authentication:login')
            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()
                messages.error(request, f'Registration failed: {str(e)}')
            finally:
                conn.autocommit = True
                release_db_connection(conn)
    else:
        form = RegisterStaffForm()
    
    return render(request, 'register_staff.html', {'form': form})

def logout_view(request):
    request.session.flush()
    return redirect(reverse('main:main'))