from django.shortcuts import render, redirect, get_object_or_404
from .models import Habitat
from .forms import HabitatForm
from datasatwa.models import Satwa 

def daftar_habitat(request):
    habitats = Habitat.objects.all()
    return render(request, 'daftar_habitat.html', {'habitats': habitats})

def tambah_habitat(request):
    if request.method == 'POST':
        form = HabitatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('datahabitat:daftar_habitat') 
    else:
        form = HabitatForm()
    return render(request, 'form_habitat.html', {'form': form})


def edit_habitat(request, pk):
    habitat = get_object_or_404(Habitat, pk=pk)
    if request.method == 'POST':
        form = HabitatForm(request.POST, instance=habitat)
        if form.is_valid():
            form.save()
            return redirect('datahabitat:daftar_habitat')
    else:
        form = HabitatForm(instance=habitat)
    return render(request, 'form_habitat.html', {'form': form})

# View for deleting a habitat
def hapus_habitat(request, pk):
    habitat = get_object_or_404(Habitat, pk=pk)
    habitat.delete()
    return redirect('datahabitat:daftar_habitat')



# View for habitat details
def detail_habitat(request, pk):
    habitat = get_object_or_404(Habitat, pk=pk)
    species_in_habitat = Satwa.objects.filter(habitat=habitat)  
    return render(request, 'datahabitat/detail_habitat.html', {
        'habitat': habitat,
        'species_in_habitat': species_in_habitat
    })

