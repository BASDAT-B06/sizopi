from django.db import connection
from datetime import datetime, timedelta
import uuid
from .utils import dictfetchall

class AdopsiService:
    
    @staticmethod
    def get_all_animals_with_adoption_status():
        """Business logic untuk mengambil semua hewan dengan status adopsi"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    h.id,
                    h.nama,
                    h.spesies as type,
                    h.status_kesehatan as condition,
                    h.url_foto as image,
                    hab.nama as habitat,
                    CASE 
                        WHEN a.id_hewan IS NOT NULL AND a.tgl_berhenti_adopsi > CURRENT_DATE 
                        THEN true 
                        ELSE false 
                    END as is_adopted,
                    CASE 
                        WHEN ind.nama IS NOT NULL THEN ind.nama
                        WHEN org.nama_organisasi IS NOT NULL THEN org.nama_organisasi
                        ELSE NULL
                    END as adopter,
                    a.tgl_mulai_adopsi as start_date,
                    a.tgl_berhenti_adopsi as end_date,
                    a.kontribusi_finansial as contribution,
                    a.status_pembayaran as payment_status
                FROM HEWAN h
                LEFT JOIN HABITAT hab ON h.nama_habitat = hab.nama
                LEFT JOIN ADOPSI a ON h.id = a.id_hewan 
                    AND a.tgl_berhenti_adopsi > CURRENT_DATE
                LEFT JOIN ADOPTER ad ON a.id_adopter = ad.id_adopter
                LEFT JOIN INDIVIDU ind ON ad.id_adopter = ind.id_adopter
                LEFT JOIN ORGANISASI org ON ad.id_adopter = org.id_adopter
                ORDER BY h.nama
            """)
            return dictfetchall(cursor)
    
    @staticmethod
    def get_top_adopters():
        """Mengambil 5 adopter dengan kontribusi tertinggi dalam setahun terakhir"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    COALESCE(ind.nama, org.nama_organisasi) as name,
                    SUM(a.kontribusi_finansial) as total_contribution
                FROM ADOPTER ad
                LEFT JOIN INDIVIDU ind ON ad.id_adopter = ind.id_adopter
                LEFT JOIN ORGANISASI org ON ad.id_adopter = org.id_adopter
                JOIN ADOPSI a ON ad.id_adopter = a.id_adopter
                WHERE a.status_pembayaran = 'Lunas' 
                    AND a.tgl_mulai_adopsi >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY ad.id_adopter, ind.nama, org.nama_organisasi
                ORDER BY total_contribution DESC
                LIMIT 5
            """)
            return dictfetchall(cursor)
    
    @staticmethod
    def get_individual_adopters():
        """Mengambil semua adopter individu"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    ad.id_adopter,
                    ind.nama as name,
                    'individual' as type,
                    ind.nik as identifier,
                    pg.alamat as address,
                    p.no_telepon as phone,
                    COALESCE(SUM(CASE WHEN a.status_pembayaran = 'Lunas' THEN a.kontribusi_finansial ELSE 0 END), 0) as total_contribution,
                    COUNT(CASE WHEN a.tgl_berhenti_adopsi > CURRENT_DATE THEN 1 END) as active_adoptions
                FROM ADOPTER ad
                JOIN INDIVIDU ind ON ad.id_adopter = ind.id_adopter
                LEFT JOIN PENGUNJUNG pg ON ad.username_adopter = pg.username_p
                LEFT JOIN PENGGUNA p ON ad.username_adopter = p.username
                LEFT JOIN ADOPSI a ON ad.id_adopter = a.id_adopter
                GROUP BY ad.id_adopter, ind.nama, ind.nik, pg.alamat, p.no_telepon
                ORDER BY total_contribution DESC
            """)
            return dictfetchall(cursor)
    
    @staticmethod
    def get_organization_adopters():
        """Mengambil semua adopter organisasi"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    ad.id_adopter,
                    org.nama_organisasi as name,
                    'organization' as type,
                    org.npp as identifier,
                    pg.alamat as address,
                    p.no_telepon as phone,
                    COALESCE(SUM(CASE WHEN a.status_pembayaran = 'Lunas' THEN a.kontribusi_finansial ELSE 0 END), 0) as total_contribution,
                    COUNT(CASE WHEN a.tgl_berhenti_adopsi > CURRENT_DATE THEN 1 END) as active_adoptions
                FROM ADOPTER ad
                JOIN ORGANISASI org ON ad.id_adopter = org.id_adopter
                LEFT JOIN PENGUNJUNG pg ON ad.username_adopter = pg.username_p
                LEFT JOIN PENGGUNA p ON ad.username_adopter = p.username
                LEFT JOIN ADOPSI a ON ad.id_adopter = a.id_adopter
                GROUP BY ad.id_adopter, org.nama_organisasi, org.npp, pg.alamat, p.no_telepon
                ORDER BY total_contribution DESC
            """)
            return dictfetchall(cursor)
    
    @staticmethod
    def get_adopter_by_id(adopter_id):
        """Mengambil data adopter berdasarkan ID"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    ad.id_adopter,
                    COALESCE(ind.nama, org.nama_organisasi) as name,
                    CASE 
                        WHEN ind.nama IS NOT NULL THEN 'individual'
                        ELSE 'organization'
                    END as type,
                    COALESCE(ind.nik, org.npp) as identifier,
                    pg.alamat as address,
                    p.no_telepon as phone
                FROM ADOPTER ad
                LEFT JOIN INDIVIDU ind ON ad.id_adopter = ind.id_adopter
                LEFT JOIN ORGANISASI org ON ad.id_adopter = org.id_adopter
                LEFT JOIN PENGUNJUNG pg ON ad.username_adopter = pg.username_p
                LEFT JOIN PENGGUNA p ON ad.username_adopter = p.username
                WHERE ad.id_adopter = %s
            """, [adopter_id])
            result = dictfetchall(cursor)
            return result[0] if result else None
    
    @staticmethod
    def get_adopter_history(adopter_id):
        """Mengambil riwayat adopsi adopter"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    a.id_hewan,
                    h.nama as animal_name,
                    h.spesies as animal_type,
                    a.tgl_mulai_adopsi as start_date,
                    a.tgl_berhenti_adopsi as end_date,
                    a.kontribusi_finansial as contribution,
                    a.status_pembayaran,
                    CASE 
                        WHEN a.tgl_berhenti_adopsi > CURRENT_DATE THEN 'ongoing'
                        ELSE 'completed'
                    END as status
                FROM ADOPSI a
                JOIN HEWAN h ON a.id_hewan = h.id
                WHERE a.id_adopter = %s AND a.status_pembayaran = 'Lunas'
                ORDER BY a.tgl_mulai_adopsi DESC
            """, [adopter_id])
            return dictfetchall(cursor)
    
    @staticmethod
    def get_user_active_adoptions(username):
        """Mengambil adopsi aktif user"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    h.id,
                    h.nama,
                    h.spesies as type,
                    h.status_kesehatan as condition,
                    h.url_foto as image,
                    hab.nama as habitat,
                    a.tgl_mulai_adopsi as start_date,
                    a.tgl_berhenti_adopsi as end_date,
                    a.kontribusi_finansial as contribution,
                    a.status_pembayaran as payment_status
                FROM ADOPSI a
                JOIN HEWAN h ON a.id_hewan = h.id
                JOIN HABITAT hab ON h.nama_habitat = hab.nama
                JOIN ADOPTER ad ON a.id_adopter = ad.id_adopter
                WHERE ad.username_adopter = %s 
                    AND a.tgl_berhenti_adopsi > CURRENT_DATE
                ORDER BY a.tgl_mulai_adopsi DESC
            """, [username])
            return dictfetchall(cursor)
    
    @staticmethod
    def get_animal_adoption_info(animal_id, username):
        """Mengambil info adopsi hewan untuk user tertentu"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    h.id,
                    h.nama,
                    h.spesies as type,
                    h.url_foto as image,
                    hab.nama as habitat,
                    a.tgl_mulai_adopsi as start_date,
                    a.tgl_berhenti_adopsi as end_date
                FROM HEWAN h
                JOIN HABITAT hab ON h.nama_habitat = hab.nama
                JOIN ADOPSI a ON h.id = a.id_hewan
                JOIN ADOPTER ad ON a.id_adopter = ad.id_adopter
                WHERE h.id = %s AND ad.username_adopter = %s
                    AND a.tgl_berhenti_adopsi > CURRENT_DATE
            """, [animal_id, username])
            result = dictfetchall(cursor)
            return result[0] if result else None
    
    @staticmethod
    def get_medical_records(animal_id, start_date):
        """Mengambil rekam medis hewan setelah tanggal mulai adopsi"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    cm.tanggal_pemeriksaan as date,
                    CONCAT(p.nama_depan, ' ', p.nama_belakang) as doctor,
                    cm.status_kesehatan as health_status,
                    cm.diagnosis as diagnosis,
                    cm.pengobatan as treatment,
                    cm.catatan_tindak_lanjut as notes
                FROM CATATAN_MEDIS cm
                JOIN DOKTER_HEWAN dh ON cm.username_dh = dh.username_DH
                JOIN PENGGUNA p ON dh.username_DH = p.username
                WHERE cm.id_hewan = %s AND cm.tanggal_pemeriksaan >= %s
                ORDER BY cm.tanggal_pemeriksaan DESC
            """, [animal_id, start_date])
            return dictfetchall(cursor)
    
    @staticmethod
    def verify_user_account(username):
        """Verifikasi akun pengunjung"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT p.username, p.nama_depan, p.nama_belakang, p.no_telepon, 
                       pg.alamat
                FROM PENGGUNA p
                JOIN PENGUNJUNG pg ON p.username = pg.username_p
                WHERE p.username = %s
            """, [username])
            result = dictfetchall(cursor)
            return result[0] if result else None
    
    @staticmethod
    def get_user_info(username):
        """Mengambil info user untuk sertifikat"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT p.nama_depan, p.nama_belakang
                FROM PENGGUNA p
                WHERE p.username = %s
            """, [username])
            result = dictfetchall(cursor)
            return result[0] if result else None
    
    @staticmethod
    def create_individual_adoption(username, animal_id, nik, nama, alamat, 
                                no_telepon, nominal, periode):
        """Membuat adopsi baru untuk individu"""
        try:
            # Validasi nominal dan periode
            if nominal <= 0:
                raise ValueError("Nominal kontribusi harus lebih dari 0")
            if periode not in [3, 6, 12]:
                raise ValueError("Periode adopsi harus 3, 6, atau 12 bulan")
            
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=periode * 30)
            
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                
                # Cek apakah user sudah pernah jadi adopter
                cursor.execute("""
                    SELECT id_adopter FROM ADOPTER 
                    WHERE username_adopter = %s
                """, [username])
                existing_adopter = cursor.fetchone()
                
                if existing_adopter:
                    adopter_id = existing_adopter[0]
                    print(f"Using existing adopter: {adopter_id}")
                    
                    # Cek apakah sudah ada record individu
                    cursor.execute("""
                        SELECT COUNT(*) FROM INDIVIDU 
                        WHERE id_adopter = %s
                    """, [adopter_id])
                    individu_count = cursor.fetchone()[0]
                    
                    if individu_count > 0:
                        # Cek apakah NIK sama dengan yang sudah ada
                        cursor.execute("""
                            SELECT nik FROM INDIVIDU 
                            WHERE id_adopter = %s
                        """, [adopter_id])
                        existing_nik = cursor.fetchone()[0]
                        
                        if existing_nik != nik:
                            raise ValueError("User sudah terdaftar sebagai adopter individu dengan NIK berbeda. Tidak dapat menggunakan NIK yang berbeda.")
                    
                    # Cek apakah sudah ada record organisasi
                    cursor.execute("""
                        SELECT COUNT(*) FROM ORGANISASI 
                        WHERE id_adopter = %s
                    """, [adopter_id])
                    organisasi_count = cursor.fetchone()[0]
                    
                    if organisasi_count > 0:
                        raise ValueError("User sudah terdaftar sebagai adopter organisasi. Tidak dapat mendaftar sebagai individu.")
                    
                    # Jika belum ada record individu, insert baru
                    if individu_count == 0:
                        cursor.execute("""
                            INSERT INTO INDIVIDU (nik, nama, id_adopter)
                            VALUES (%s, %s, %s)
                        """, [nik, nama, adopter_id])
                    
                else:
                    # Buat adopter baru
                    adopter_id = str(uuid.uuid4())
                    print(f"Creating new adopter: {adopter_id}")
                    
                    # Insert ke tabel ADOPTER dengan total_kontribusi = 0
                    cursor.execute("""
                        INSERT INTO ADOPTER (id_adopter, username_adopter, total_kontribusi)
                        VALUES (%s, %s, %s)
                    """, [adopter_id, username, 0])  # Set 0, akan diupdate oleh trigger
                    
                    # Insert ke tabel INDIVIDU
                    cursor.execute("""
                        INSERT INTO INDIVIDU (nik, nama, id_adopter)
                        VALUES (%s, %s, %s)
                    """, [nik, nama, adopter_id])
                
                # Cek apakah hewan sudah diadopsi saat ini
                cursor.execute("""
                    SELECT COUNT(*) FROM ADOPSI 
                    WHERE id_hewan = %s AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [animal_id])
                active_adoption = cursor.fetchone()
                
                if active_adoption[0] > 0:
                    raise ValueError("Hewan ini sedang diadopsi oleh adopter lain")
                
                # Insert ke tabel ADOPSI 
                cursor.execute("""
                    INSERT INTO ADOPSI (id_adopter, id_hewan, status_pembayaran, 
                                    tgl_mulai_adopsi, tgl_berhenti_adopsi, kontribusi_finansial)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [adopter_id, animal_id, 'Tertunda', start_date, end_date, nominal])
            
            return True
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error creating individual adoption: {e}")
            return False

    @staticmethod
    def create_organization_adoption(username, animal_id, npp, nama_organisasi, 
                                alamat, kontak, nominal, periode):
        """Membuat adopsi baru untuk organisasi - STRICT: Satu identity per adopter"""
        try:
            # Validasi nominal dan periode
            if nominal <= 0:
                raise ValueError("Nominal kontribusi harus lebih dari 0")
            if periode not in [3, 6, 12]:
                raise ValueError("Periode adopsi harus 3, 6, atau 12 bulan")
            
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=periode * 30)
            
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                
                # Cek apakah user sudah pernah jadi adopter
                cursor.execute("""
                    SELECT id_adopter FROM ADOPTER 
                    WHERE username_adopter = %s
                """, [username])
                existing_adopter = cursor.fetchone()
                
                if existing_adopter:
                    adopter_id = existing_adopter[0]
                    print(f"Using existing adopter: {adopter_id}")
                    
                    # Cek apakah sudah ada record organisasi
                    cursor.execute("""
                        SELECT COUNT(*) FROM ORGANISASI 
                        WHERE id_adopter = %s
                    """, [adopter_id])
                    organisasi_count = cursor.fetchone()[0]
                    
                    if organisasi_count > 0:
                        # Cek apakah NPP sama dengan yang sudah ada
                        cursor.execute("""
                            SELECT npp FROM ORGANISASI 
                            WHERE id_adopter = %s
                        """, [adopter_id])
                        existing_npp = cursor.fetchone()[0]
                        
                        if existing_npp != npp:
                            raise ValueError("User sudah terdaftar sebagai adopter organisasi dengan NPP berbeda. Tidak dapat menggunakan NPP yang berbeda.")
                    
                    # Cek apakah sudah ada record individu
                    cursor.execute("""
                        SELECT COUNT(*) FROM INDIVIDU 
                        WHERE id_adopter = %s
                    """, [adopter_id])
                    individu_count = cursor.fetchone()[0]
                    
                    if individu_count > 0:
                        raise ValueError("User sudah terdaftar sebagai adopter individu. Tidak dapat mendaftar sebagai organisasi.")
                    
                    # Jika belum ada record organisasi, insert baru
                    if organisasi_count == 0:
                        cursor.execute("""
                            INSERT INTO ORGANISASI (npp, nama_organisasi, id_adopter)
                            VALUES (%s, %s, %s)
                        """, [npp, nama_organisasi, adopter_id])
                    
                else:
                    # Buat adopter baru
                    adopter_id = str(uuid.uuid4())
                    print(f"Creating new adopter: {adopter_id}")
                    
                    # Insert ke tabel ADOPTER dengan total_kontribusi = 0
                    cursor.execute("""
                        INSERT INTO ADOPTER (id_adopter, username_adopter, total_kontribusi)
                        VALUES (%s, %s, %s)
                    """, [adopter_id, username, 0])  # Set 0, akan diupdate oleh trigger
                    
                    # Insert ke tabel ORGANISASI
                    cursor.execute("""
                        INSERT INTO ORGANISASI (npp, nama_organisasi, id_adopter)
                        VALUES (%s, %s, %s)
                    """, [npp, nama_organisasi, adopter_id])
                
                # Cek apakah hewan sudah diadopsi saat ini
                cursor.execute("""
                    SELECT COUNT(*) FROM ADOPSI 
                    WHERE id_hewan = %s AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [animal_id])
                active_adoption = cursor.fetchone()
                
                if active_adoption[0] > 0:
                    raise ValueError("Hewan ini sedang diadopsi oleh adopter lain")
                
                # Insert ke tabel ADOPSI
                cursor.execute("""
                    INSERT INTO ADOPSI (id_adopter, id_hewan, status_pembayaran, 
                                    tgl_mulai_adopsi, tgl_berhenti_adopsi, kontribusi_finansial)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [adopter_id, animal_id, 'Tertunda', start_date, end_date, nominal])
            
            return True
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error creating organization adoption: {e}")
            return False

    @staticmethod
    def update_payment_status(animal_id, status):
        """Update status pembayaran adopsi"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                cursor.execute("""
                    UPDATE ADOPSI 
                    SET status_pembayaran = %s
                    WHERE id_hewan = %s AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [status, animal_id])
                    
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return False
    
    @staticmethod
    def stop_adoption(animal_id):
        """Menghentikan adopsi dengan mengubah tanggal berakhir"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                cursor.execute("""
                    UPDATE ADOPSI 
                    SET tgl_berhenti_adopsi = CURRENT_DATE
                    WHERE id_hewan = %s AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [animal_id])
            return True
        except Exception as e:
            print(f"Error stopping adoption: {e}")
            return False
    
    @staticmethod
    def get_adopter_type_and_info(username, animal_id):
        """Mengambil tipe adopter dan info untuk form perpanjang adopsi"""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO SIZOPI")
            cursor.execute("""
                SELECT 
                    h.id,
                    h.nama as animal_name,
                    h.spesies as animal_type,
                    a.status_pembayaran,
                    a.tgl_berhenti_adopsi,
                    CASE 
                        WHEN ind.nama IS NOT NULL THEN 'individual'
                        WHEN org.nama_organisasi IS NOT NULL THEN 'organization'
                        ELSE NULL
                    END as adopter_type,
                    ind.nama as individual_name,
                    ind.nik as individual_nik,
                    org.nama_organisasi as organization_name,
                    org.npp as organization_npp,
                    pg.alamat as address,
                    p.no_telepon as phone
                FROM ADOPSI a
                JOIN HEWAN h ON a.id_hewan = h.id
                JOIN ADOPTER ad ON a.id_adopter = ad.id_adopter
                LEFT JOIN INDIVIDU ind ON ad.id_adopter = ind.id_adopter
                LEFT JOIN ORGANISASI org ON ad.id_adopter = org.id_adopter
                LEFT JOIN PENGUNJUNG pg ON ad.username_adopter = pg.username_p
                LEFT JOIN PENGGUNA p ON ad.username_adopter = p.username
                WHERE ad.username_adopter = %s AND a.id_hewan = %s
                    AND a.tgl_berhenti_adopsi > CURRENT_DATE
            """, [username, animal_id])
            result = dictfetchall(cursor)
            return result[0] if result else None

    @staticmethod
    def extend_adoption(username, animal_id, nominal, periode):
        """Perpanjang periode adopsi - DIPERBAIKI untuk UPDATE bukan INSERT"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                
                # Cek status pembayaran adopsi saat ini
                cursor.execute("""
                    SELECT a.status_pembayaran, a.tgl_berhenti_adopsi, a.kontribusi_finansial
                    FROM ADOPSI a
                    JOIN ADOPTER ad ON a.id_adopter = ad.id_adopter
                    WHERE a.id_hewan = %s AND ad.username_adopter = %s
                        AND a.tgl_berhenti_adopsi > CURRENT_DATE
                """, [animal_id, username])
                result = dictfetchall(cursor)
                
                if not result:
                    return False, 'Adopsi tidak ditemukan'
                
                current_adoption = result[0]
                
                if current_adoption['status_pembayaran'] != 'Lunas':
                    return False, 'Harap lunasi pembayaran adopsi saat ini terlebih dahulu'
                
                # Hitung tanggal baru dan kontribusi total
                current_end_date = current_adoption['tgl_berhenti_adopsi']
                new_end_date = current_end_date + timedelta(days=periode * 30)
                total_contribution = current_adoption['kontribusi_finansial'] + nominal
                
                # UPDATE record yang sudah ada
                cursor.execute("""
                    UPDATE ADOPSI 
                    SET tgl_berhenti_adopsi = %s,
                        kontribusi_finansial = %s,
                        status_pembayaran = 'Tertunda'
                    WHERE id_hewan = %s 
                        AND id_adopter = (
                            SELECT id_adopter FROM ADOPTER 
                            WHERE username_adopter = %s
                        )
                        AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [new_end_date, total_contribution, animal_id, username])
                
                # Cek apakah update berhasil
                if cursor.rowcount == 0:
                    return False, 'Gagal mengupdate adopsi'
            
            return True, 'Adopsi berhasil diperpanjang'
        except Exception as e:
            return False, f'Error: {str(e)}'
    
    @staticmethod
    def delete_adopter(adopter_id):
        """Menghapus data adopter"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                
                # Cek apakah adopter masih aktif
                cursor.execute("""
                    SELECT COUNT(*) as active_count
                    FROM ADOPSI 
                    WHERE id_adopter = %s AND tgl_berhenti_adopsi > CURRENT_DATE
                """, [adopter_id])
                result = dictfetchall(cursor)
                
                if result and result[0]['active_count'] > 0:
                    return False, "Adopter masih aktif berpartisipasi dalam program adopsi"
                
                # Hapus data adopsi
                cursor.execute("DELETE FROM ADOPSI WHERE id_adopter = %s", [adopter_id])
                
                # Hapus data individu/organisasi
                cursor.execute("DELETE FROM INDIVIDU WHERE id_adopter = %s", [adopter_id])
                cursor.execute("DELETE FROM ORGANISASI WHERE id_adopter = %s", [adopter_id])
                
                # Hapus data adopter
                cursor.execute("DELETE FROM ADOPTER WHERE id_adopter = %s", [adopter_id])
            
            return True, "Data adopter berhasil dihapus"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def delete_adoption_history(adopter_id, animal_id, start_date):
        """Menghapus riwayat adopsi yang sudah berakhir"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO SIZOPI")
                cursor.execute("""
                    DELETE FROM ADOPSI 
                    WHERE id_adopter = %s AND id_hewan = %s AND tgl_mulai_adopsi = %s 
                        AND tgl_berhenti_adopsi <= CURRENT_DATE
                """, [adopter_id, animal_id, start_date])
            return True
        except Exception as e:
            print(f"Error deleting adoption history: {e}")
            return False
