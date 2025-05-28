import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def set_schema(cur, schema='sizopi'):
    cur.execute(f"SET search_path TO {schema}")


def dictfetchall(cursor):
    "Helper: ambil hasil cursor sebagai list of dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class DaftarHewanPakanView(View):
    template_name = 'daftar_hewan_pakan.html'
    
    def get(self, request):
        try:
            cur = connection.cursor()
            set_schema(cur)

            user_data = request.session.get('user', {})
            username_current = user_data.get('username')
            user_penjaga_id = None
                        
            if username_current:
                cur.execute("""
                    SELECT username_jh FROM penjaga_hewan 
                    WHERE username_jh = %s
                """, (username_current,))
                penjaga_result = cur.fetchone()
                user_penjaga_id = penjaga_result[0] if penjaga_result else None
            
            if not user_penjaga_id:
                user_penjaga_id = username_current

            cur.execute("""
                SELECT
                    id,
                    nama AS nama_individu,
                    spesies,
                    asal_hewan,
                    tanggal_lahir,
                    status_kesehatan,
                    nama_habitat AS habitat,
                    url_foto
                FROM hewan
                ORDER BY nama
            """)
            
            data = dictfetchall(cur)
            cur.close()

            for i, hewan in enumerate(data):
                print(f"Row {i}: ID = {hewan.get('id')} (type: {type(hewan.get('id'))}), Nama = {hewan.get('nama_individu')}")

            context = {
                'data': data,
                'user_penjaga_id': user_penjaga_id  
            }
            
            return render(request, self.template_name, context)
            
        except Exception as e:
            print(f"ERROR in DaftarHewanPakanView: {str(e)}")
            return JsonResponse({'error': str(e)})


def get_pakan_url(id_hewan):
    """
    Returns the URL to the pakan list page for a given id_hewan.
    """
    return f'/pakan_hewan/list/{id_hewan}/'


@method_decorator(csrf_exempt, name='dispatch')
class PakanPerHewanView(View):
    template_name = 'pakan_per_hewan.html'
    
    def get(self, request, id_hewan):
        try:
            cur = connection.cursor()
            set_schema(cur)

            # Ambil data user dari session
            user_data = request.session.get('user', {})
            username_current = user_data.get('username')
            user_penjaga_id = None
                        
            # Cek apakah user adalah penjaga hewan
            if username_current:
                cur.execute("""
                    SELECT username_jh FROM penjaga_hewan 
                    WHERE username_jh = %s
                """, (username_current,))
                penjaga_result = cur.fetchone()
                user_penjaga_id = penjaga_result[0] if penjaga_result else None
            
            # Fallback jika tidak ditemukan di tabel penjaga_hewan
            if not user_penjaga_id:
                user_penjaga_id = username_current

            # Query data pakan untuk hewan tertentu
            cur.execute("""
                SELECT 
                    p.jadwal,
                    p.jenis,
                    p.jumlah,
                    p.status
                FROM pakan p
                WHERE p.id_hewan = %s
                ORDER BY p.jadwal DESC
            """, (str(id_hewan),))
            
            raw_pakan = cur.fetchall()
            
            # Query detail hewan
            cur.execute("""
                SELECT nama, spesies
                FROM hewan
                WHERE id = %s
            """, (str(id_hewan),))
            
            hewan_detail = cur.fetchone()
            nama_hewan = hewan_detail[0] if hewan_detail else "Unknown"
            jenis_hewan = hewan_detail[1] if hewan_detail else "Unknown"
            
            cur.close()
            
            # Format data pakan
            pakan_list = []
            for item in raw_pakan:
                pakan_list.append({
                    'jadwal': item[0],
                    'jenis': item[1],
                    'jumlah': item[2],
                    'status': item[3]
                })

            return render(request, self.template_name, {
                'pakan_list': pakan_list,
                'id_hewan': id_hewan,
                'nama_hewan': nama_hewan,
                'jenis_hewan': jenis_hewan,
                'user_penjaga_id': user_penjaga_id  # Tambahkan ini untuk navbar
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class CreatePakanView(View):
    def post(self, request, id_hewan):
        data = request.POST
        try:
            user_data = request.session.get('user', {})
            username_jh = user_data.get('username')
            
            if not username_jh:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})
            
            user_role = request.session.get('role')
            if user_role != 'penjaga_hewan':
                return JsonResponse({'success': False, 'error': 'Only penjaga hewan can create pakan records'})
            
            jenis = data.get('jenis')
            jumlah = data.get('jumlah')
            jadwal = data.get('jadwal')
            status = "Menunggu Pemberian" 
            
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                INSERT INTO pakan (id_hewan, jadwal, jenis, jumlah, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (str(id_hewan), jadwal, jenis, jumlah, status))
            
            connection.commit()
            cur.close()
            
            return redirect('pakan_hewan:pakan_per_hewan', id_hewan=id_hewan)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class EditPakanView(View):
    def post(self, request, id_hewan):
        data = request.POST
        try:
            user_data = request.session.get('user', {})
            username_jh = user_data.get('username')
            user_role = request.session.get('role')
            
            if not username_jh or user_role != 'penjaga_hewan':
                return JsonResponse({'success': False, 'error': 'Unauthorized access'})
            
            jadwal_lama = data.get('jadwal_lama')
            jenis = data.get('jenis')
            jumlah = data.get('jumlah')
            jadwal = data.get('jadwal')
            
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                UPDATE pakan
                SET jenis = %s, jumlah = %s, jadwal = %s
                WHERE id_hewan = %s AND jadwal = %s
            """, (jenis, jumlah, jadwal, str(id_hewan), jadwal_lama))
            
            connection.commit()
            cur.close()
            
            return redirect('pakan_hewan:pakan_per_hewan', id_hewan=id_hewan)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class DeletePakanView(View):
    def post(self, request, id_hewan):
        data = request.POST
        try:
            user_data = request.session.get('user', {})
            username_jh = user_data.get('username')
            user_role = request.session.get('role')
            
            if not username_jh or user_role != 'penjaga_hewan':
                return JsonResponse({'success': False, 'error': 'Unauthorized access'})
            
            jadwal = data.get('jadwal')
            
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                DELETE FROM pakan
                WHERE id_hewan = %s AND jadwal = %s
            """, (str(id_hewan), jadwal))
            
            connection.commit()
            cur.close()
            
            return redirect('pakan_hewan:pakan_per_hewan', id_hewan=id_hewan)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusPakanView(View):
    def post(self, request, id_hewan):
        data = request.POST
        try:
            user_data = request.session.get('user', {})
            username_jh = user_data.get('username')
            user_role = request.session.get('role')
            
            if not username_jh or user_role != 'penjaga_hewan':
                return JsonResponse({'success': False, 'error': 'Unauthorized access'})
            
            jadwal = data.get('jadwal')
            status = "Selesai Diberikan"
            
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                UPDATE pakan
                SET status = "Selesai Diberikan"
                WHERE id_hewan = %s AND jadwal = %s
            """, (str(id_hewan), jadwal))
            
            cur.execute("""
                INSERT INTO memberi (username_jh, id_hewan, jadwal)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM memberi 
                    WHERE username_jh = %s AND id_hewan = %s AND jadwal = %s
                )
            """, (username_jh, str(id_hewan), jadwal, username_jh, str(id_hewan), jadwal))
            
            connection.commit()
            cur.close()
            
            return redirect('pakan_hewan:pakan_per_hewan', id_hewan=id_hewan)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class RiwayatPakanPenjagaView(View):
    template_name = 'riwayat_pakan_penjaga.html'
    
    def get(self, request, username_penjaga=None):
        try:
            if not username_penjaga or username_penjaga == 'None':
                user_data = request.session.get('user', {})
                username_penjaga = user_data.get('username')
                
            if not username_penjaga:
                return JsonResponse({'error': 'Username penjaga tidak ditemukan'})
                
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                SELECT 
                    ph.username_jh,
                    pg.nama_depan || ' ' || COALESCE(pg.nama_tengah, '') || ' ' || pg.nama_belakang as nama_lengkap
                FROM penjaga_hewan ph
                JOIN pengguna pg ON ph.username_jh = pg.username
                WHERE ph.username_jh = %s
            """, (username_penjaga,))
            
            penjaga_data = cur.fetchone()
            if not penjaga_data:
                return JsonResponse({'error': 'Penjaga hewan tidak ditemukan'})
                
            nama_penjaga = penjaga_data[1] if penjaga_data else "Unknown"
            
            cur.execute("""
                SELECT 
                    p.jadwal,
                    h.nama AS nama_hewan,
                    p.jenis,
                    p.jumlah,
                    p.status
                FROM memberi m
                JOIN pakan p ON m.id_hewan = p.id_hewan AND m.jadwal = p.jadwal
                JOIN hewan h ON m.id_hewan = h.id
                WHERE m.username_jh = %s
                ORDER BY p.jadwal DESC
            """, (username_penjaga,))
            
            raw_records = cur.fetchall()
            
            records = []
            for record in raw_records:
                records.append({
                    'jadwal': record[0],
                    'nama_hewan': record[1],
                    'jenis_pakan': record[2],
                    'jumlah_pakan': record[3],
                    'status_pemberian': record[4]
                })
            
            cur.close()
            
            return render(request, self.template_name, {
                'records': records,
                'username_penjaga': username_penjaga,
                'nama_penjaga': nama_penjaga
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})