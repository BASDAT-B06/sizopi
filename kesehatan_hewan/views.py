from django.shortcuts import render

def list_rekam_medis(request):
    return render(request, 'list_rekam_medis.html')

def jadwal_pemeriksaan(request):
    return render(request, 'jadwal_pemeriksaan.html')

def create_jadwal_pemeriksaan(request):
    return render(request, 'create_jadwal_pemeriksaan.html')

def create_rekam_medis(request):
    return render(request, 'create_rekam_medis.html')

def edit_rekam_medis(request):
    return render(request, 'edit_rekam_medis.html')