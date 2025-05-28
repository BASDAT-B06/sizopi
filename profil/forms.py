from django import forms

class PengunjungProfileForm(forms.Form):
    email = forms.EmailField(label='Email')
    nama_depan = forms.CharField(label='Nama Depan')
    nama_tengah = forms.CharField(label='Nama Tengah', required=False)
    nama_belakang = forms.CharField(label='Nama Belakang')
    no_telepon = forms.CharField(label='Nomor Telepon')
    alamat = forms.CharField(label='Alamat Lengkap')
    tgl_lahir = forms.DateField(label='Tanggal Lahir', widget=forms.DateInput(attrs={'type': 'date'}))

class DokterHewanProfileForm(forms.Form):
    email = forms.EmailField(label='Email')
    nama_depan = forms.CharField(label='Nama Depan')
    nama_tengah = forms.CharField(label='Nama Tengah', required=False)
    nama_belakang = forms.CharField(label='Nama Belakang')
    no_telepon = forms.CharField(label='Nomor Telepon')
    no_str = forms.CharField(label='No STR', disabled=True) 

    SPESIALISASI_CHOICES = [
        ('Mamalia Besar', 'Mamalia Besar'),
        ('Reptil', 'Reptil'),
        ('Burung Eksotis', 'Burung Eksotis'),
        ('Primata', 'Primata'),
        ('lainnya', 'Lainnya'),
    ]
    spesialisasi = forms.MultipleChoiceField(
        choices=SPESIALISASI_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    spesialisasi_lainnya = forms.CharField(label='Spesialisasi Lainnya', required=False)
