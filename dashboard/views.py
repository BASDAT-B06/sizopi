from django.shortcuts import render

def dash_dokter_hewan(request):
    return render(request, 'dash_dokter_hewan.html')

def dash_pelatih(request):
    return render(request, 'dash_pelatih.html')

def dash_pengunjung(request):
    return render(request, 'dash_pengunjung.html')

def dash_penjaga_hewan(request):
    return render(request, 'dash_penjaga_hewan.html')

def dash_staf_admin(request):
    return render(request, 'dash_staf_admin.html')