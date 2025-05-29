import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse


def set_schema(cur, schema='sizopi'):
    cur.execute(f"SET search_path TO {schema}")


def dictfetchall(cursor):
    "Helper: ambil hasil cursor sebagai list of dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class DaftarHewanView(View):
    template_name = 'daftar_hewan.html'
    
    def get(self, request):
        try:
            cur = connection.cursor()
            set_schema(cur)

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

            return render(request, self.template_name, {'data': data})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class RekamMedisListView(View):
    template_name = 'list_rekam_medis.html'
    
    def get(self, request, id_hewan):
        try:
            cur = connection.cursor()
            set_schema(cur)

            cur.execute("""
                SELECT 
                    cm.tanggal_pemeriksaan, 
                    p.nama_depan,
                    p.nama_tengah,
                    p.nama_belakang,
                    cm.status_kesehatan,
                    cm.diagnosis, 
                    cm.pengobatan, 
                    cm.catatan_tindak_lanjut
                FROM catatan_medis cm
                JOIN dokter_hewan dh ON cm.username_dh = dh.username_dh
                JOIN pengguna p ON dh.username_dh = p.username
                WHERE cm.id_hewan = %s
                ORDER BY cm.tanggal_pemeriksaan DESC
            """, (str(id_hewan),))
            
            raw_records = cur.fetchall()
            
            cur.execute("""
                SELECT nama, spesies
                FROM hewan
                WHERE id = %s
            """, (str(id_hewan),))
            
            hewan_detail = cur.fetchone()
            nama_hewan = hewan_detail[0] if hewan_detail else "Unknown"
            jenis_hewan = hewan_detail[1] if hewan_detail else "Unknown"
            
            cur.close()
            
            records = []
            for record in raw_records:
                records.append({
                    'tanggal_pemeriksaan': record[0],
                    'nama_depan': record[1] or "",
                    'nama_tengah': record[2] or "",  # Handle null nama_tengah
                    'nama_belakang': record[3] or "",
                    'status_kesehatan': record[4],
                    'diagnosis': record[5] or "",
                    'pengobatan': record[6] or "",
                    'catatan_tindak_lanjut': record[7] or ""
                })
            
            return render(request, self.template_name, {
                'records': records,
                'id_hewan': id_hewan,
                'nama_hewan': nama_hewan,
                'jenis_hewan': jenis_hewan
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class CreateRekamMedisView(View):
    def post(self, request, id_hewan):
        data = request.POST

        user_data = request.session.get('user', {})
        username_dh = user_data.get('username')
        
        if not username_dh:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
        
        user_role = request.session.get('role')
        
        if user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Only dokter hewan can create medical records'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                SELECT COUNT(*) FROM catatan_medis 
                WHERE id_hewan = %s AND tanggal_pemeriksaan = %s
            """, (str(id_hewan), data.get('tanggal')))
            
            existing_count = cur.fetchone()[0]
            
            if existing_count > 0:
                cur.close()
                return JsonResponse({
                    'success': False, 
                    'error': f'Rekam medis untuk tanggal {data.get("tanggal")} sudah ada. Gunakan fitur edit untuk mengubah data existing.'
                })
            
            cur.execute("""
                INSERT INTO catatan_medis (
                    id_hewan, 
                    username_dh, 
                    tanggal_pemeriksaan,
                    status_kesehatan, 
                    diagnosis, 
                    pengobatan
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(id_hewan), 
                username_dh, 
                data.get('tanggal'),
                data.get('status'), 
                data.get('diagnosa', ''),
                data.get('pengobatan', '') 
            ))
            
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:list_rekam_medis', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
class EditRekamMedisView(View):
    def post(self, request, id_hewan, tanggal):
        data = request.POST
        
        user_data = request.session.get('user', {})
        username_dh = user_data.get('username')
        user_role = request.session.get('role')
                
        if not username_dh or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)

            cur.execute("""
                SELECT COUNT(*) FROM catatan_medis
                WHERE id_hewan = %s AND tanggal_pemeriksaan = %s
            """, (str(id_hewan), tanggal))
            
            if cur.fetchone()[0] == 0:
                cur.close()
                return JsonResponse({'success': False, 'error': 'Record not found'})
            
            cur.execute("""
                UPDATE catatan_medis
                SET 
                    diagnosis = %s, 
                    pengobatan = %s, 
                    catatan_tindak_lanjut = %s
                WHERE id_hewan = %s AND tanggal_pemeriksaan = %s
            """, (
                data.get('diagnosa', ''),
                data.get('pengobatan', ''),
                data.get('catatan', ''),
                str(id_hewan),
                tanggal
            ))
            
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:list_rekam_medis', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
@method_decorator(csrf_exempt, name='dispatch')
class DeleteRekamMedisView(View):
    def post(self, request, id_hewan, tanggal):
        user_data = request.session.get('user', {})
        username_dh = user_data.get('username')
        user_role = request.session.get('role')

        if not username_dh or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'}, status=403)

        try:
            cur = connection.cursor()
            set_schema(cur)

            cur.execute("""
                SELECT COUNT(*) FROM catatan_medis
                WHERE id_hewan = %s AND tanggal_pemeriksaan = %s
            """, (str(id_hewan), tanggal))

            if cur.fetchone()[0] == 0:
                cur.close()
                return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)

            cur.execute("""
                DELETE FROM catatan_medis
                WHERE id_hewan = %s AND tanggal_pemeriksaan = %s
            """, (str(id_hewan), tanggal))

            connection.commit()
            cur.close()

            return redirect('kesehatan_hewan:list_rekam_medis', id_hewan=id_hewan)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class JadwalPemeriksaanView(View):
    template_name = 'jadwal_pemeriksaan.html'
    
    def get(self, request, id_hewan):
        try:
            cur = connection.cursor()
            set_schema(cur)

            cur.execute("""
                SELECT tgl_pemeriksaan_selanjutnya 
                FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s
                ORDER BY tgl_pemeriksaan_selanjutnya DESC
            """, (str(id_hewan),))
            
            raw_jadwal = cur.fetchall()
            
            cur.execute("""
                SELECT freq_pemeriksaan_rutin
                FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s
                LIMIT 1
            """, (str(id_hewan),))
            
            result = cur.fetchone()
            frekuensi = result[0] if result else 3 
            
            cur.execute("""
                SELECT nama, spesies
                FROM hewan
                WHERE id = %s
            """, (str(id_hewan),))
            
            hewan_detail = cur.fetchone()
            nama_hewan = hewan_detail[0] if hewan_detail else "Unknown"
            jenis_hewan = hewan_detail[1] if hewan_detail else "Unknown"
            
            cur.close()
            
            jadwal = [{'tanggal_pemeriksaan': date[0]} for date in raw_jadwal]

            return render(request, self.template_name, {
                'jadwal': jadwal,
                'frekuensi': frekuensi,
                'id_hewan': id_hewan,
                'nama_hewan': nama_hewan,
                'jenis_hewan': jenis_hewan
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class CreateJadwalView(View):
    def post(self, request, id_hewan):
        tanggal = request.POST.get('tanggal')
        
        user_data = request.session.get('user', {})
        username = user_data.get('username')
        user_role = request.session.get('role')
                
        if not username or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                SELECT COUNT(*) FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s
            """, (str(id_hewan), tanggal))
            
            if cur.fetchone()[0] > 0:
                cur.close()
                return JsonResponse({'success': False, 'error': f'Jadwal untuk tanggal {tanggal} sudah ada'})

            cur.execute("""
                SELECT freq_pemeriksaan_rutin
                FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s
                LIMIT 1
            """, (str(id_hewan),))
            
            result = cur.fetchone()
            freq_rutin = result[0] if result else 3 
            
            cur.execute("""
                INSERT INTO jadwal_pemeriksaan_kesehatan (id_hewan, tgl_pemeriksaan_selanjutnya, freq_pemeriksaan_rutin)
                VALUES (%s, %s, %s)
            """, (str(id_hewan), tanggal, freq_rutin))
            
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:jadwal_pemeriksaan', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class EditJadwalView(View):
    def post(self, request, id_hewan):
        tanggal_lama = request.POST.get('tanggal_lama')
        tanggal_baru = request.POST.get('tanggal_baru')
        
        user_data = request.session.get('user', {})
        username = user_data.get('username')
        user_role = request.session.get('role')
                
        if not username or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)

            cur.execute("""
                SELECT COUNT(*) FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s AND tgl_pemeriksaan_selanjutnya != %s
            """, (str(id_hewan), tanggal_baru, tanggal_lama))
            
            if cur.fetchone()[0] > 0:
                cur.close()
                return JsonResponse({'success': False, 'error': f'Jadwal untuk tanggal {tanggal_baru} sudah ada'})

            cur.execute("""
                UPDATE jadwal_pemeriksaan_kesehatan
                SET tgl_pemeriksaan_selanjutnya = %s
                WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s
            """, (tanggal_baru, str(id_hewan), tanggal_lama))
            
            rows_affected = cur.rowcount
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:jadwal_pemeriksaan', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteJadwalView(View):
    def post(self, request, id_hewan):
        tanggal = request.POST.get('tanggal')
        
        user_data = request.session.get('user', {})
        username = user_data.get('username')
        user_role = request.session.get('role')
        
        
        if not username or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)
            
            cur.execute("""
                SELECT COUNT(*) FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s
            """, (str(id_hewan), tanggal))
            
            if cur.fetchone()[0] == 0:
                cur.close()
                return JsonResponse({'success': False, 'error': 'Jadwal tidak ditemukan'})

            cur.execute("""
                DELETE FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s
            """, (str(id_hewan), tanggal))
            
            rows_affected = cur.rowcount
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:jadwal_pemeriksaan', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
class EditFrekuensiView(View):
    def post(self, request, id_hewan):
        frekuensi = request.POST.get('frekuensi')
        
        user_data = request.session.get('user', {})
        username = user_data.get('username')
        user_role = request.session.get('role')
                
        if not username or user_role != 'dokter_hewan':
            return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
        try:
            cur = connection.cursor()
            set_schema(cur)
                        
            cur.execute("""
                SELECT COUNT(*) FROM jadwal_pemeriksaan_kesehatan
                WHERE id_hewan = %s
            """, (str(id_hewan),))
            
            count = cur.fetchone()[0]
            
            if count > 0:
                cur.execute("""
                    UPDATE jadwal_pemeriksaan_kesehatan
                    SET freq_pemeriksaan_rutin = %s
                    WHERE id_hewan = %s
                """, (frekuensi, str(id_hewan)))
            else:
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                cur.execute("""
                    INSERT INTO jadwal_pemeriksaan_kesehatan (id_hewan, tgl_pemeriksaan_selanjutnya, freq_pemeriksaan_rutin)
                    VALUES (%s, %s, %s)
                """, (str(id_hewan), today, frekuensi))
            
            connection.commit()
            cur.close()
            
            return redirect('kesehatan_hewan:jadwal_pemeriksaan', id_hewan=id_hewan)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})