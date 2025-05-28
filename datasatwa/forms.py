from django import forms

STATUS_CHOICES = [
    ("Sehat", "Sehat"),
    ("Sakit", "Sakit"),
    ("Dalam Pemantauan", "Dalam Pemantauan"),
    ("Lainnya", "Lainnya"),
]

class SatwaForm(forms.Form):
    nama_individu = forms.CharField(label="Nama Individu", required=False)
    spesies = forms.CharField(label="Spesies", required=True)
    asal_hewan = forms.CharField(label="Asal Hewan", required=True)
    tanggal_lahir = forms.DateField(
        label="Tanggal Lahir", required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    status_kesehatan = forms.ChoiceField(
        label="Status Kesehatan", choices=STATUS_CHOICES, required=True
    )
    habitat = forms.CharField(label="Habitat", required=True)
    url_foto = forms.URLField(label="URL Foto", required=False)
