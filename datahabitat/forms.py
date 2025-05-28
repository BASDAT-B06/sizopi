from django import forms

class HabitatForm(forms.Form):
    nama = forms.CharField(label="Nama Habitat", max_length=100, required=True)
    luas_area = forms.FloatField(label="Luas Area (m²)", required=True)
    kapasitas = forms.IntegerField(label="Kapasitas Maksimal", required=True)
    status = forms.CharField(
        label="Status Lingkungan",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )
