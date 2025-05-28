from django import forms
from django.core.validators import RegexValidator

class AddAttractionForm(forms.Form):
    nama = forms.CharField(
        max_length=150, 
        label='Nama Atraksi',
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Name must contain only letters and spaces.')]
    )
    lokasi = forms.CharField(
        max_length=150, 
        label='Lokasi Atraksi',
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Location must contain only letters and spaces.')]
    )
    kapasitas = forms.IntegerField(
        label='Kapasitas',
        min_value=1,
        error_messages={
            'min_value': 'Kapasitas harus lebih dari 0.'
        }
    )
    jadwal = forms.TimeField(
        label='Jadwal'
    )
    pelatih = forms.CharField(required=False)
    hewan = forms.MultipleChoiceField(required=False)
    
class AddWahanaForm(forms.Form):
    nama = forms.CharField(
        max_length=150, 
        label='Nama Wahana',
        validators=[RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Name must contain only letters and spaces.')]
    )
    kapasitas = forms.IntegerField(
        label='Kapasitas',
        min_value=1,
        error_messages={
            'min_value': 'Kapasitas harus lebih dari 0.'
        }
    )
    jadwal = forms.TimeField(
        label='Jadwal'
    )
    peraturan = forms.CharField(
        max_length=150, 
        label='Peraturan',
        required=False,
    )