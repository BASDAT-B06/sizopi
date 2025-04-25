from django.shortcuts import render, redirect, get_object_or_404

from datasatwa.forms import SatwaForm
from .models import Satwa, Habitat

def tambah_satwa(request):
    habitat_list = Habitat.objects.all()
    if request.method == 'POST':
        Satwa.objects.create(
            nama_individu=request.POST.get('nama_individu'),
            spesies=request.POST.get('spesies'),
            asal_hewan=request.POST.get('asal_hewan'),
            tanggal_lahir=request.POST.get('tanggal_lahir') or None,
            status_kesehatan=request.POST.get('status_kesehatan'),
            habitat_id=request.POST.get('habitat'),
            url_foto=request.POST.get('url_foto')
        )
        return redirect('datasatwa:daftar_satwa')
    return render(request, 'form_satwa.html', {'habitat_list': habitat_list})

def daftar_satwa(request):
    data = Satwa.objects.all()
    return render(request, 'daftar_satwa.html', {'data': data})

def hapus_satwa(request, id):
    satwa = get_object_or_404(Satwa, id=id)
    satwa.delete()
    return redirect('datasatwa:daftar_satwa')

def home(request):
    return render(request, 'home.html')  

def edit_satwa(request, id):
    satwa = get_object_or_404(Satwa, id=id)
    if request.method == 'POST':
        form = SatwaForm(request.POST, instance=satwa)
        if form.is_valid():
            form.save()
            return redirect('datasatwa:daftar_satwa')
    else:
        form = SatwaForm(instance=satwa)
    return render(request, 'edit_satwa.html', {'form': form})
