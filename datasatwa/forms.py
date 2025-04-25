from django import forms
from .models import Satwa

class SatwaForm(forms.ModelForm):
    class Meta:
        model = Satwa
        fields = ['nama_individu', 'spesies', 'asal_hewan', 'tanggal_lahir', 'status_kesehatan', 'habitat', 'url_foto']
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['habitat'].required = False
