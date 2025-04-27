from django.shortcuts import render

def create_pemberian_pakan(request):
    return render(request, 'create_pemberian_pakan.html')

def edit_pemberian_pakan(request):
    return render(request, 'edit_pemberian_pakan.html')

def pakan_per_hewan(request):
    return render(request, 'pakan_per_hewan.html')

def riwayat_pakan_penjaga(request):
    return render(request, 'riwayat_pakan_penjaga.html')