from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import psycopg2
from psycopg2 import pool, IntegrityError, errors
from dotenv import load_dotenv
from django.contrib import messages
import re

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

# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     dbname="railway",
#     user="postgres",
#     password="NtrtcaMLQLEEGnNopTYFXNJJOlbmMVYt",
#     host="postgres.railway.internal",
#     port="5432",
#     options="-c search_path=sizopi"
# )


# DB_POOL = psycopg2.pool.SimpleConnectionPool(
#     minconn=1,
#     maxconn=10,
#     user=os.getenv('DB_USER'),
#     password=os.getenv('DB_PASSWORD'),
#     host=os.getenv('DB_HOST'),
#     port=os.getenv('DB_PORT'),
#     database=os.getenv('DB_NAME')
# )

DB_POOL = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    options='-c search_path=sizopi'
)

def get_db_connection():
    return DB_POOL.getconn()

def release_db_connection(conn):
    DB_POOL.putconn(conn)


def pengaturan_profil(request):
    if not request.session.get("is_authenticated"):
        return redirect("authentication:login")

    user = request.session.get("user")
    username = user.get("username")
    role = user.get("role")
    is_adopter = user.get("is_adopter", False)

    conn = get_db_connection()
    try:
        if request.method == "POST":
            # Ambil input
            email = request.POST.get("email", "").strip()
            nama_depan = request.POST.get("nama_depan", "").strip()
            nama_tengah = request.POST.get("nama_tengah", "").strip() or None
            nama_belakang = request.POST.get("nama_belakang", "").strip()
            nomor_telepon = request.POST.get("nomor_telepon", "").strip()

            # Validasi input manual
            if not email or not nama_depan or not nama_belakang or not nomor_telepon:
                messages.error(request, "Field wajib tidak boleh kosong.")
                return redirect("profil:pengaturan_profil")

            with conn.cursor() as cursor:
                # Update data pengguna
                cursor.execute("""
                    UPDATE PENGGUNA SET
                        email = %s,
                        nama_depan = %s,
                        nama_tengah = %s,
                        nama_belakang = %s,
                        no_telepon = %s
                    WHERE username = %s
                """, (email, nama_depan, nama_tengah, nama_belakang, nomor_telepon, username))

                if role == "pengunjung":
                    alamat_lengkap = request.POST.get("alamat_lengkap")
                    tanggal_lahir = request.POST.get("tanggal_lahir")

                    if not alamat_lengkap or not tanggal_lahir:
                        messages.error(request, "Alamat dan tanggal lahir wajib diisi.")
                        return redirect("profil:pengaturan_profil")

                    cursor.execute("""
                        UPDATE PENGUNJUNG SET
                            alamat = %s,
                            tgl_lahir = %s
                        WHERE username_P = %s
                    """, (alamat_lengkap, tanggal_lahir, username))

                    user['alamat'] = alamat_lengkap
                    user['tgl_lahir'] = tanggal_lahir
                    request.session['user'] = user

                elif role == "dokter_hewan":
                    spesialisasi_baru = []
                    for item in ["Mamalia Besar", "Reptil", "Burung Eksotis", "Primata"]:
                        if request.POST.get(item.lower().replace(" ", "_")):
                            spesialisasi_baru.append(item)
                    spesialisasi_lain = request.POST.get("spesialisasi_lain")
                    if spesialisasi_lain:
                        spesialisasi_baru.append(spesialisasi_lain)

                    cursor.execute("DELETE FROM SPESIALISASI WHERE username_SH = %s", (username,))
                    for spesialisasi in spesialisasi_baru:
                        cursor.execute("""
                            INSERT INTO SPESIALISASI (username_SH, nama_spesialisasi)
                            VALUES (%s, %s)
                        """, (username, spesialisasi))


                conn.commit()
                messages.success(request, "Profil berhasil diperbarui.")
                return redirect("profil:pengaturan_profil")

        context = {
            "username": username,
            "user_role": role,
            "is_logged_in": request.session.get("is_authenticated", False),
            "is_adopter": is_adopter,
        }

        with conn.cursor() as cursor:
            cursor.execute("SELECT email, nama_depan, nama_tengah, nama_belakang, no_telepon FROM PENGGUNA WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            context.update({
                "email": user_data[0],
                "nama_depan": user_data[1],
                "nama_tengah": user_data[2] or "",
                "nama_belakang": user_data[3],
                "no_telepon": user_data[4],
            })

            if role == "pengunjung":
                cursor.execute("SELECT alamat, tgl_lahir FROM PENGUNJUNG WHERE username_P = %s", (username,))
                pengunjung = cursor.fetchone()
                context["pengunjung_data"] = {
                    "alamat": pengunjung[0] if pengunjung else "",
                    "tgl_lahir": pengunjung[1].strftime("%Y-%m-%d") if pengunjung and pengunjung[1] else ""
                }

            elif role == "dokter_hewan":
                cursor.execute("SELECT no_STR FROM DOKTER_HEWAN WHERE username_DH = %s", (username,))
                no_str = cursor.fetchone()
                context["no_str"] = no_str[0] if no_str else None

                cursor.execute("SELECT nama_spesialisasi FROM SPESIALISASI WHERE username_SH = %s", (username,))
                spesialisasi = [row[0] for row in cursor.fetchall()]
                context["spesialisasi"] = spesialisasi

                spesialisasi_default = ["Mamalia Besar", "Reptil", "Burung Eksotis", "Primata"]
                context["spesialisasi_lain"] = next((s for s in spesialisasi if s not in spesialisasi_default), "")

            elif role in ["penjaga_hewan", "pelatih_hewan", "staf_admin"]:
                role_key = {
                    "penjaga_hewan": "jh",
                    "pelatih_hewan": "lh",
                    "staf_admin": "sa",
                }[role]
                table = role.upper()
                cursor.execute(f"SELECT id_staf FROM {table} WHERE username_{role_key} = %s", (username,))
                result = cursor.fetchone()
                context["id_staf"] = result[0] if result else None

        return render(request, "pengaturan_profil.html", context)

    except IntegrityError as e:
        conn.rollback()
        if isinstance(e.__cause__, errors.UniqueViolation):
            messages.error(request, "Email sudah digunakan oleh pengguna lain.")
        else:
            messages.error(request, "Terjadi kesalahan pada data yang dimasukkan.")
        return redirect("profil:pengaturan_profil")

    except Exception as e:
        conn.rollback()
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect("profil:pengaturan_profil")

    finally:
        release_db_connection(conn)


def ubah_password(request):
    if not request.session.get("is_authenticated"):
        return redirect("authentication:login")

    username = request.session.get("user", {}).get("username")


    conn = get_db_connection()

    try:
        if request.method == "POST":
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not old_password or not new_password or not confirm_password:
                messages.error(request, "Semua field wajib diisi.")
                return redirect("profil:ubah_password")

            if new_password != confirm_password:
                messages.error(request, "Konfirmasi password tidak cocok.")
                return redirect("profil:ubah_password")

            with conn.cursor() as cursor:
                # Ambil password lama dari database
                cursor.execute("SELECT password FROM PENGGUNA WHERE username = %s", (username,))
                result = cursor.fetchone()

                if not result:
                    messages.error(request, "Data pengguna tidak ditemukan.")
                    return redirect("profil:ubah_password")

                if old_password != result[0]:
                    messages.error(request, "Password lama salah.")
                    return redirect("profil:ubah_password")

                # Update password baru
                cursor.execute("UPDATE PENGGUNA SET password = %s WHERE username = %s", (new_password, username))
                conn.commit()

                messages.success(request, "Password berhasil diperbarui.")
                return redirect("profil:pengaturan_profil")

        context = {
            "username": username,
            "user_role": request.session.get("user", {}).get("role"),
            "is_logged_in": True,
            "is_adopter": request.session.get("user", {}).get("is_adopter", False),
        }
        return render(request, "ubah_password.html", context)


    except Exception as e:
        conn.rollback()
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect("profil:ubah_password")

    finally:
        release_db_connection(conn)
