from django.shortcuts import render, redirect
from django.http import HttpResponse



def pengunjung(request):
    return render(request, 'pengunjung.html')
def dokter_hewan(request):
    return render(request, 'dokter_hewan.html')
def petugas(request):
    return render(request, 'petugas.html')

def ubah_password(request):
    return render(request, 'ubah_password.html')

def pengaturan_profil(request):
    return render(request, 'pengaturan_profil.html')



