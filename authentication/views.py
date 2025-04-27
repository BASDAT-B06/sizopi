from django.shortcuts import render

# Create your views here.
def login_view(request):
    return render(request, 'login.html')

def register_dokter_view(request):
    return render(request, 'register_dokter_hewan.html')

def register_pengunjung_view(request):
    return render(request, 'register_pengunjung.html')

def register_staf_view(request):
    return render(request, 'register_staff.html')