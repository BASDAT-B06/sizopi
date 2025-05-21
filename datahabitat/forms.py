from django import forms
from .models import Habitat

class HabitatForm(forms.ModelForm):
    class Meta:
        model = Habitat
        fields = ['nama', 'luas_area', 'kapasitas_maksimal', 'status_lingkungan']
