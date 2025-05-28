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
from django.db import DatabaseError


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

def get_db_connection():
    conn = DB_POOL.getconn()
    conn.autocommit = True  
    with conn.cursor() as cur:
        cur.execute("SET search_path TO sizopi")  
    return conn



def release_db_connection(conn):
    DB_POOL.putconn(conn)



def login_view(request):
    if request.session.get('is_authenticated', False):
        return redirect('main:main')

    if request.method == 'POST':
        email = request.POST.get('email')  
        password = request.POST.get('password')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:

                cur.execute("SELECT cek_login_pengguna(%s, %s)", (email, password))
                username = cur.fetchone()[0]  

                # Ambil info pengguna
                cur.execute("""
                    SELECT username, email, nama_depan, nama_tengah, nama_belakang, no_telepon
                    FROM pengguna
                    WHERE username = %s
                """, (username,))
                user = cur.fetchone()

                if not user:
                    messages.error(request, "User tidak ditemukan.")
                    return render(request, 'login.html')

                user_dict = {
                    'username': user[0],
                    'email': user[1],
                    'nama_depan': user[2],
                    'nama_tengah': user[3] or '',
                    'nama_belakang': user[4],
                    'no_telepon': user[5],
                    'role': None
                }

                # Cek role pengguna
                # Pengunjung
                cur.execute("SELECT 1 FROM pengunjung WHERE username_P = %s", (username,))
                if cur.fetchone():
                    user_dict['role'] = 'pengunjung'
                    cur.execute("SELECT alamat, tgl_lahir FROM pengunjung WHERE username_P = %s", (username,))
                    detail = cur.fetchone()
                    if detail:
                        user_dict.update({
                            'alamat': detail[0],
                            'tgl_lahir': detail[1].strftime('%Y-%m-%d') if detail[1] else None
                        })
                    cur.execute("SELECT 1 FROM adopter WHERE username_adopter = %s", (username,))
                    user_dict['is_adopter'] = cur.fetchone() is not None

                # Dokter
                cur.execute("SELECT 1 FROM dokter_hewan WHERE username_DH = %s", (username,))
                if cur.fetchone():
                    user_dict['role'] = 'dokter_hewan'
                    cur.execute("SELECT no_STR FROM dokter_hewan WHERE username_DH = %s", (username,))
                    detail = cur.fetchone()
                    if detail:
                        user_dict['no_str'] = detail[0]
                    cur.execute("SELECT nama_spesialisasi FROM spesialisasi WHERE username_SH = %s", (username,))
                    spesialis = cur.fetchall()
                    user_dict['spesialisasi'] = [row[0] for row in spesialis] if spesialis else []

                # Penjaga Hewan
                cur.execute("SELECT 1 FROM penjaga_hewan WHERE username_jh = %s", (username,))
                if cur.fetchone():
                    user_dict['role'] = 'penjaga_hewan'
                    cur.execute("SELECT id_staf FROM penjaga_hewan WHERE username_jh = %s", (username,))
                    detail = cur.fetchone()
                    if detail:
                        user_dict['id_staf'] = str(detail[0])

                # Pelatih
                cur.execute("SELECT 1 FROM pelatih_hewan WHERE username_lh = %s", (username,))
                if cur.fetchone():
                    user_dict['role'] = 'pelatih_hewan'
                    cur.execute("SELECT id_staf FROM pelatih_hewan WHERE username_lh = %s", (username,))
                    detail = cur.fetchone()
                    if detail:
                        user_dict['id_staf'] = str(detail[0])

                # Admin
                cur.execute("SELECT 1 FROM staf_admin WHERE username_sa = %s", (username,))
                if cur.fetchone():
                    user_dict['role'] = 'staf_admin'
                    cur.execute("SELECT id_staf FROM staf_admin WHERE username_sa = %s", (username,))
                    detail = cur.fetchone()
                    if detail:
                        user_dict['id_staf'] = str(detail[0])

                # Set session
                request.session['user'] = user_dict
                request.session['is_authenticated'] = True
                request.session['role'] = user_dict['role']
                return redirect('main:main')

        except Exception as e:
            messages.error(request, str(e).split('\n')[0])
        finally:
            release_db_connection(conn)

    return render(request, 'login.html')




def register_dokter_view(request):
    if request.method == 'POST':
        form = RegisterDokterForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                conn.autocommit = False  

                with conn.cursor() as cur:
                    # Insert ke PENGGUNA
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
                        form.cleaned_data['nama_tengah'] or None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))

                    # Buat STR dan insert ke DOKTER_HEWAN
                    no_str = f"STR-DOC-{form.cleaned_data['no_izin_praktek']}"
                    cur.execute("""
                        INSERT INTO DOKTER_HEWAN (username_DH, no_STR)
                        VALUES (%s, %s)
                    """, (
                        form.cleaned_data['username'],
                        no_str
                    ))

                    # Spesialisasi
                    spesialis = form.cleaned_data['spesialis']
                    if spesialis == 'Lainnya':
                        spesialis = form.cleaned_data['spesialis_lainnya']

                    cur.execute("""
                        INSERT INTO SPESIALISASI (username_SH, nama_spesialisasi)
                        VALUES (%s, %s)
                    """, (
                        form.cleaned_data['username'],
                        spesialis
                    ))

                conn.commit()
                messages.success(request, 'Registrasi berhasil. Silakan login.')
                return redirect('authentication:login')

            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()

                conn.autocommit = True
                release_db_connection(conn)

                error_message = str(e).split('CONTEXT:')[0].strip()
                messages.error(request, error_message)

            finally:
                conn.autocommit = True
                release_db_connection(conn)

        else:
            messages.error(request, 'Form tidak valid. Periksa kembali input Anda.')
    else:
        form = RegisterDokterForm()

    return render(request, 'register_dokter_hewan.html', {'form': form})



def register_pengunjung_view(request):
    if request.method == 'POST':
        form = RegisterPenggunjungForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                conn.autocommit = False
                with conn.cursor() as cur:
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
                        form.cleaned_data.get('nama_tengah') or None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))

                    cur.execute("""
                        INSERT INTO PENGUNJUNG (username_P, alamat, tgl_lahir)
                        VALUES (%s, %s, %s)
                    """, (
                        form.cleaned_data['username'],
                        form.cleaned_data['alamat'],
                        form.cleaned_data['tgl_lahir']
                    ))

                conn.commit()
                conn.autocommit = True
                release_db_connection(conn)

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')

            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()

                conn.autocommit = True
                release_db_connection(conn)

                error_message = str(e).split('CONTEXT:')[0].strip()
                messages.error(request, error_message)

        else:
            messages.error(request, "Form tidak valid. Silakan periksa kembali.")
    else:
        form = RegisterPenggunjungForm()

    return render(request, 'register_pengunjung.html', {'form': form})



def register_staf_view(request):
    if request.method == 'POST':
        form = RegisterStaffForm(request.POST)
        if form.is_valid():
            conn = get_db_connection()
            try:
                conn.autocommit = False  # Start transaction

                with conn.cursor() as cur:
                    # Insert ke tabel PENGGUNA
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
                        form.cleaned_data.get('nama_tengah') or None,
                        form.cleaned_data['nama_belakang'],
                        form.cleaned_data['no_hp']
                    ))

                    # Generate UUID
                    id_staf = uuid.uuid4()
                    job_role = form.cleaned_data['job_role']

                    if job_role == 'Penjaga Hewan':
                        cur.execute("""
                            INSERT INTO PENJAGA_HEWAN (username_jh, id_staf)
                            VALUES (%s, %s)
                        """, (form.cleaned_data['username'], str(id_staf)))

                    elif job_role == 'Staff Administrasi':
                        cur.execute("""
                            INSERT INTO STAF_ADMIN (username_sa, id_staf)
                            VALUES (%s, %s)
                        """, (form.cleaned_data['username'], str(id_staf)))

                    elif job_role == 'Pelatih Pertunjukan':
                        cur.execute("""
                            INSERT INTO PELATIH_HEWAN (username_lh, id_staf)
                            VALUES (%s, %s)
                        """, (form.cleaned_data['username'], str(id_staf)))


                conn.commit()
                messages.success(request, 'Registrasi staf berhasil! Silakan login.')
                return redirect('authentication:login')

            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()

                conn.autocommit = True
                release_db_connection(conn)

                error_message = str(e).split('CONTEXT:')[0].strip()
                messages.error(request, error_message)

            finally:
                if conn:
                    try:
                        conn.autocommit = True
                        release_db_connection(conn)
                    except:
                        pass
        else:
            messages.error(request, "Form tidak valid. Cek kembali inputnya.")
    else:
        form = RegisterStaffForm()

    return render(request, 'register_staff.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect(reverse('main:main'))

def register_role_selection_view(request):
    return render(request, "register_role_selection.html")
