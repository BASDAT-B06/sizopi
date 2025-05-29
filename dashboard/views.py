from datetime import date
from django.shortcuts import render, redirect
from django.db import connection

def set_schema(cursor):
    cursor.execute("SET search_path TO sizopi")

def dash_dokter_hewan(request):
    user_data = request.session.get('user', {})
    username_dh = user_data.get('username')
    user_role = request.session.get('role')
    
    if user_role != 'dokter_hewan':
        return redirect('authentication:login')
    
    try:
        cur = connection.cursor()
        set_schema(cur)
        
        cur.execute("""
            SELECT 
                dh.username_dh,
                p.email,
                p.no_telepon,
                p.nama_depan,
                p.nama_tengah,
                p.nama_belakang,
                dh.no_str
            FROM dokter_hewan dh
            JOIN pengguna p ON dh.username_dh = p.username
            WHERE dh.username_dh = %s
        """, [username_dh])
        
        dokter_data = cur.fetchone()
        
        if dokter_data:
            nama_parts = []
            if dokter_data[3]:
                nama_parts.append(dokter_data[3])
            if dokter_data[4]:
                nama_parts.append(dokter_data[4])
            if dokter_data[5]:
                nama_parts.append(dokter_data[5])
            
            nama_lengkap = ' '.join(nama_parts) if nama_parts else username_dh
            
            cur.execute("""
                SELECT nama_spesialisasi
                FROM spesialisasi
                WHERE username_sh = %s
            """, [username_dh])
            
            spesialisasis = [row[0] for row in cur.fetchall()]
            
            cur.execute("""
                SELECT COUNT(DISTINCT id_hewan)
                FROM catatan_medis
                WHERE username_dh = %s
            """, [username_dh])
            
            total_hewan_result = cur.fetchone()
            total_hewan = total_hewan_result[0] if total_hewan_result else 0
            
            context = {
                'nama_lengkap': nama_lengkap,
                'username': dokter_data[0],
                'email': dokter_data[1],
                'nomor_telepon': dokter_data[2], 
                'no_str': dokter_data[6],
                'spesialisasis': spesialisasis,
                'total_hewan': total_hewan
            }
        else:
            context = {
                'nama_lengkap': username_dh,
                'username': username_dh,
                'email': None,
                'nomor_telepon': None,
                'no_str': None,
                'spesialisasis': [],
                'total_hewan': 0
            }
        
        cur.close()
        return render(request, 'dash_dokter_hewan.html', context)
        
    except Exception as e:
        print(f"Database Error: {e}")
        context = {
            'nama_lengkap': username_dh,
            'username': username_dh,
            'email': None,
            'nomor_telepon': None,
            'no_str': None,
            'spesialisasis': [],
            'total_hewan': 0
        }
        return render(request, 'dash_dokter_hewan.html', context)
    
def dash_pelatih(request):
    user_data = request.session.get('user', {})
    username_lh = user_data.get('username')
    user_role = request.session.get('role')
    
    if user_role != 'pelatih_hewan':
        return redirect('authentication:login')
    
    try:
        cur = connection.cursor()
        set_schema(cur)
        
        cur.execute("""
            SELECT 
                lh.username_lh,
                lh.id_staf,
                p.email,
                p.no_telepon,
                p.nama_depan,
                p.nama_tengah,
                p.nama_belakang
            FROM pelatih_hewan lh
            JOIN pengguna p ON lh.username_lh = p.username
            WHERE lh.username_lh = %s
        """, [username_lh])
        
        pelatih_data = cur.fetchone()
        
        if pelatih_data:
            nama_parts = []
            if pelatih_data[4]: 
                nama_parts.append(pelatih_data[4])
            if pelatih_data[5]: 
                nama_parts.append(pelatih_data[5])
            if pelatih_data[6]:
                nama_parts.append(pelatih_data[6])
            
            nama_lengkap = ' '.join(nama_parts) if nama_parts else username_lh
            
            today = date.today()
            cur.execute("""
                SELECT 
                    jp.nama_atraksi,
                    a.lokasi,
                    jp.tgl_penugasan
                FROM jadwal_penugasan jp
                JOIN atraksi a ON jp.nama_atraksi = a.nama_atraksi
                WHERE jp.username_lh = %s AND DATE(jp.tgl_penugasan) = %s
                ORDER BY jp.tgl_penugasan
            """, [username_lh, today])
            
            atraksi_list = []
            for row in cur.fetchall():
                atraksi_list.append({
                    'nama_atraksi': row[0],
                    'lokasi': row[1],
                    'jadwal': row[2]
                })
            
            cur.execute("""
                SELECT DISTINCT
                    h.nama,
                    h.spesies,
                    h.status_kesehatan
                FROM hewan h
                JOIN berpartisipasi b ON h.id = b.id_hewan
                JOIN jadwal_penugasan jp ON b.nama_fasilitas = jp.nama_atraksi
                WHERE jp.username_lh = %s
            """, [username_lh])
            
            hewan_list = []
            for row in cur.fetchall():
                hewan_list.append({
                    'nama': row[0],
                    'spesies': row[1],
                    'status_kesehatan': row[2]
                })
            
            cur.execute("""
                SELECT COUNT(DISTINCT jp.nama_atraksi)
                FROM jadwal_penugasan jp
                WHERE jp.username_lh = %s
            """, [username_lh])
            total_atraksi = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(DISTINCT h.id)
                FROM hewan h
                JOIN berpartisipasi b ON h.id = b.id_hewan
                JOIN jadwal_penugasan jp ON b.nama_fasilitas = jp.nama_atraksi
                WHERE jp.username_lh = %s
            """, [username_lh])
            total_hewan_dilatih = cur.fetchone()[0]
            
            context = {
                'nama_lengkap': nama_lengkap,
                'username': pelatih_data[0],
                'email': pelatih_data[2],
                'nomor_telepon': pelatih_data[3],
                'id_staf': pelatih_data[1],
                'atraksi_list': atraksi_list,
                'hewan_list': hewan_list,
                'total_atraksi': total_atraksi,
                'total_hewan_dilatih': total_hewan_dilatih
            }
        else:
            context = {
                'nama_lengkap': username_lh,
                'username': username_lh,
                'email': None,
                'nomor_telepon': None,
                'id_staf': None,
                'atraksi_list': [],
                'hewan_list': [],
                'total_atraksi': 0,
                'total_hewan_dilatih': 0
            }
        
        cur.close()
        return render(request, 'dash_pelatih.html', context)
        
    except Exception as e:
        print(f"Database Error: {e}")
        context = {
            'nama_lengkap': username_lh,
            'username': username_lh,
            'email': None,
            'nomor_telepon': None,
            'id_staf': None,
            'atraksi_list': [],
            'hewan_list': [],
            'total_atraksi': 0,
            'total_hewan_dilatih': 0
        }
        return render(request, 'dash_pelatih.html', context)
    
def dash_pengunjung(request):
    user_data = request.session.get('user', {})
    username_p = user_data.get('username')
    user_role = request.session.get('role')
    
    if user_role != 'pengunjung':
        return redirect('authentication:login')
    
    try:
        cur = connection.cursor()
        set_schema(cur)

        # Cek apakah pengunjung adalah adopter
        cur.execute("""
            SELECT COUNT(*) FROM adopter 
            WHERE username_adopter = %s
        """, [username_p])
        is_adopter = cur.fetchone()[0] > 0
        
        # Update session dengan status adopter
        user_data['is_adopter'] = is_adopter
        request.session['user'] = user_data
        request.session.modified = True
        
        cur.execute("""
            SELECT 
                p.username,
                p.email,
                p.no_telepon,
                p.nama_depan,
                p.nama_tengah,
                p.nama_belakang
            FROM pengguna p
            WHERE p.username = %s
        """, [username_p])
        
        pengunjung_data = cur.fetchone()
        
        if pengunjung_data:
            nama_parts = []
            if pengunjung_data[3]:
                nama_parts.append(pengunjung_data[3])
            if pengunjung_data[4]: 
                nama_parts.append(pengunjung_data[4])
            if pengunjung_data[5]:
                nama_parts.append(pengunjung_data[5])
            
            nama_lengkap = ' '.join(nama_parts) if nama_parts else username_p
            
            today = date.today()
            cur.execute("""
                SELECT 
                    r.tanggal_kunjungan,
                    r.nama_fasilitas,
                    r.jumlah_tiket,
                    r.status
                FROM reservasi r
                WHERE r.username_p = %s AND r.tanggal_kunjungan < %s
                ORDER BY r.tanggal_kunjungan DESC
            """, [username_p, today])
            
            riwayat_kunjungan = []
            for row in cur.fetchall():
                riwayat_kunjungan.append({
                    'tanggal_kunjungan': row[0],
                    'nama_fasilitas': row[1], 
                    'jumlah_tiket': row[2],
                    'status': row[3]
                })
            
            cur.execute("""
                SELECT 
                    r.tanggal_kunjungan,
                    r.nama_fasilitas,
                    r.jumlah_tiket,
                    r.status
                FROM reservasi r
                WHERE r.username_p = %s AND r.status = 'Terjadwal'
                ORDER BY r.tanggal_kunjungan ASC
            """, [username_p])
            
            tiket_dibeli = []
            for row in cur.fetchall():
                tiket_dibeli.append({
                    'tanggal_kunjungan': row[0],
                    'nama_fasilitas': row[1], 
                    'jumlah_tiket': row[2],
                    'status': row[3]
                })
                        
            email = pengunjung_data[1] or user_data.get('email')
            no_telepon = pengunjung_data[2] or user_data.get('no_telepon')
            
            context = {
                'nama_lengkap': nama_lengkap,
                'username': pengunjung_data[0],
                'email': email,
                'nomor_telepon': no_telepon,
                'riwayat_kunjungan': riwayat_kunjungan,
                'tiket_dibeli': tiket_dibeli,
                'is_adopter': is_adopter
            }
        else:
            context = {
                'nama_lengkap': user_data.get('nama_lengkap', username_p),
                'username': username_p,
                'email': user_data.get('email'),
                'nomor_telepon': user_data.get('no_telepon'),
                'riwayat_kunjungan': [],
                'tiket_dibeli': [],
                'is_adopter': is_adopter
            }
        
        cur.close()
        return render(request, 'dash_pengunjung.html', context)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        context = {
            'nama_lengkap': user_data.get('nama_lengkap', username_p),
            'username': username_p,
            'email': user_data.get('email'),
            'nomor_telepon': user_data.get('no_telepon'),
            'riwayat_kunjungan': [],
            'tiket_dibeli': [],
            'is_adopter': False
        }
        return render(request, 'dash_pengunjung.html', context)

def dash_penjaga_hewan(request):
    user_data = request.session.get('user', {})
    username_jh = user_data.get('username')
    user_role = request.session.get('role')
    
    if user_role != 'penjaga_hewan':
        return redirect('authentication:login')
    
    try:
        cur = connection.cursor()
        set_schema(cur)
        
        cur.execute("""
            SELECT 
                jh.username_jh,
                jh.id_staf,
                p.email,
                p.no_telepon,
                p.nama_depan,
                p.nama_tengah,
                p.nama_belakang
            FROM penjaga_hewan jh
            JOIN pengguna p ON jh.username_jh = p.username
            WHERE jh.username_jh = %s
        """, [username_jh])
        
        penjaga_data = cur.fetchone()
        
        if penjaga_data:
            nama_parts = []
            if penjaga_data[4]:
                nama_parts.append(penjaga_data[4])
            if penjaga_data[5]: 
                nama_parts.append(penjaga_data[5])
            if penjaga_data[6]:
                nama_parts.append(penjaga_data[6])
            
            nama_lengkap = ' '.join(nama_parts) if nama_parts else username_jh
            
            cur.execute("""
                SELECT COUNT(DISTINCT m.id_hewan)
                FROM memberi m
                WHERE m.username_jh = %s
            """, [username_jh])
            
            total_hewan_diberi_pakan = cur.fetchone()[0]
            
            context = {
                'nama_lengkap': nama_lengkap,
                'username': penjaga_data[0],
                'email': penjaga_data[2],
                'nomor_telepon': penjaga_data[3],
                'id_staf': penjaga_data[1],
                'total_hewan_diberi_pakan': total_hewan_diberi_pakan
            }
        else:
            context = {
                'nama_lengkap': username_jh,
                'username': username_jh,
                'email': None,
                'nomor_telepon': None,
                'id_staf': None,
                'total_hewan_diberi_pakan': 0
            }
        
        cur.close()
        return render(request, 'dash_penjaga_hewan.html', context)
        
    except Exception as e:
        print(f"Database Error: {e}")
        context = {
            'nama_lengkap': username_jh,
            'username': username_jh,
            'email': None,
            'nomor_telepon': None,
            'id_staf': None,
            'total_hewan_diberi_pakan': 0
        }
        return render(request, 'dash_penjaga_hewan.html', context)
    
def dash_staf_admin(request):
    user_data = request.session.get('user', {})
    username_sa = user_data.get('username')
    user_role = request.session.get('role')
    
    if user_role != 'staf_admin':
        return redirect('authentication:login')
    
    try:
        cur = connection.cursor()
        set_schema(cur)
        
        cur.execute("""
            SELECT 
                sa.username_sa,
                sa.id_staf,
                p.email,
                p.no_telepon,
                p.nama_depan,
                p.nama_tengah,
                p.nama_belakang
            FROM staf_admin sa
            JOIN pengguna p ON sa.username_sa = p.username
            WHERE sa.username_sa = %s
        """, [username_sa])
        
        staf_data = cur.fetchone()
        
        if staf_data:
            nama_parts = []
            if staf_data[4]:
                nama_parts.append(staf_data[4])
            if staf_data[5]:  
                nama_parts.append(staf_data[5])
            if staf_data[6]: 
                nama_parts.append(staf_data[6])
            
            nama_lengkap = ' '.join(nama_parts) if nama_parts else username_sa
            
            today = date.today()
            
            cur.execute("""
                SELECT COALESCE(SUM(jumlah_tiket), 0)
                FROM reservasi
                WHERE DATE(tanggal_kunjungan) = %s
            """, [today])
            total_tiket_hari_ini = cur.fetchone()[0]
            
            jumlah_pengunjung_hari_ini = total_tiket_hari_ini
            
            context = {
                'nama_lengkap': nama_lengkap,
                'username': staf_data[0],
                'email': staf_data[2],
                'nomor_telepon': staf_data[3],
                'id_staf': staf_data[1],
                'total_tiket_hari_ini': total_tiket_hari_ini,
                'jumlah_pengunjung_hari_ini': jumlah_pengunjung_hari_ini
            }
        else:
            context = {
                'nama_lengkap': username_sa,
                'username': username_sa,
                'email': None,
                'nomor_telepon': None,
                'id_staf': None,
                'total_tiket_hari_ini': 0,
                'jumlah_pengunjung_hari_ini': 0
            }
        
        cur.close()
        return render(request, 'dash_staf_admin.html', context)
        
    except Exception as e:
        print(f"Database Error: {e}")
        context = {
            'nama_lengkap': username_sa,
            'username': username_sa,
            'email': None,
            'nomor_telepon': None,
            'id_staf': None,
            'total_tiket_hari_ini': 0,
            'jumlah_pengunjung_hari_ini': 0
        }
        return render(request, 'dash_staf_admin.html', context)