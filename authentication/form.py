from django import forms
from django.core.validators import RegexValidator

POSISI_CHOICES = [
    ('Penjaga Hewan', 'Penjaga Hewan'),
    ('Staff Administrasi', 'Staff Administrasi'),
    ('Pelatih Pertujukan', 'Pelatih Pertujukan'),
    ]

SPESIALIS_CHOICES = [
    ('Mamalia Besar', 'Mamalia Besar'),
    ('Reptil', 'Reptil'),
    ('Burung Eksotis', 'Burung Eksotis'),
    ('PRIMATA', 'PRIMATA'),
    ('Lainnya', 'Lainnya'),
]

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class BaseRegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label='Username',
        validators=[RegexValidator(r'^[a-zA-Z0-9_]+$', 'Username must contain only letters, numbers, and underscores.')]
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput, 
        label='Password',
        min_length=8
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, 
        label='Konfirmasi Password',
        min_length=8
    )
    nama_depan = forms.CharField(
        max_length=150, 
        label='Nama Depan',
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Name must contain only letters and spaces.')]
    )
    nama_tengah = forms.CharField(
        max_length=150, 
        label='Nama Tengah',
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Name must contain only letters and spaces.')]
    )
    nama_belakang = forms.CharField(
        max_length=150, 
        label='Nama Belakang',
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Name must contain only letters and spaces.')]
    )
    no_hp = forms.CharField(
        max_length=15, 
        label='No HP',
        validators=[RegexValidator(r'^\d+$', 'Phone number must contain only numbers.')]
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class RegisterPenggunjungForm(BaseRegisterForm):
    tgl_lahir = forms.DateField(
        label='Tanggal Lahir', 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    alamat = forms.CharField(
        widget=forms.Textarea, 
        label='Alamat'
    )

class RegisterStaffForm(BaseRegisterForm):
    posisi = forms.CharField(
        choices=POSISI_CHOICES,
        label='Posisi',
    )

class RegisterDokterForm(BaseRegisterForm):
    spesialis = forms.ChoiceField(
        choices=SPESIALIS_CHOICES,
        label='Spesialis',
    )
    spesialis_lainnya = forms.CharField(
        max_length=150,
        label='Spesifikasi Spesialis Lainnya',
        required=False,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Specialization must contain only letters and spaces.')]
    )
    no_izin_praktek = forms.CharField(
        max_length=15, 
        label='No Izin Praktek',
        validators=[RegexValidator(r'^\d+$', 'License number must contain only numbers.')]
    )

    def clean(self):
        cleaned_data = super().clean()
        spesialis = cleaned_data.get('spesialis')
        spesialis_lainnya = cleaned_data.get('spesialis_lainnya')

        if spesialis == 'Lainnya' and not spesialis_lainnya:
            raise forms.ValidationError(
                "Harap tentukan spesialis lainnya."
            )
        
        return cleaned_data