from django import forms
from django.core.validators import RegexValidator
from django.forms import CheckboxSelectMultiple



POSISI_CHOICES = [
    ('Penjaga Hewan', 'Penjaga Hewan'),
    ('Staff Administrasi', 'Staff Administrasi'),
    ('Pelatih Pertujukan', 'Pelatih Pertujukan'),
]

SPESIALIS_CHOICES = [
    ('Mamalia Besar', 'Mamalia Besar'),
    ('Reptil', 'Reptil'),
    ('Burung Eksotis', 'Burung Eksotis'),
    ('Primata', 'Primata'),
    ('Lainnya', 'Lainnya'),
]
class LoginForm(forms.Form):
    email = forms.CharField(label='Email') 
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class BaseRegisterForm(forms.Form):
    username = forms.CharField(label='Username')
    email = forms.CharField(label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Konfirmasi Password')
    nama_depan = forms.CharField(label='Nama Depan')
    nama_tengah = forms.CharField(label='Nama Tengah', required=False)
    nama_belakang = forms.CharField(label='Nama Belakang')
    no_hp = forms.CharField(label='No HP')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class RegisterPenggunjungForm(BaseRegisterForm):
    tgl_lahir = forms.CharField(label='Tanggal Lahir')  # Bisa diolah manual di views kalau perlu
    alamat = forms.CharField(widget=forms.Textarea, label='Alamat')

class RegisterStaffForm(BaseRegisterForm):
    job_role = forms.ChoiceField(choices=POSISI_CHOICES, label='Posisi')



# class RegisterDokterForm(BaseRegisterForm):
#     spesialis = forms.ChoiceField(
#         choices=SPESIALIS_CHOICES,
#         label='Spesialis',
#     )
#     spesialis_lainnya = forms.CharField(
#         label='Spesifikasi Spesialis Lainnya',
#         required=False,
#     )
#     no_izin_praktek = forms.CharField(
#         label='No Izin Praktek',
        
#     )

#     def clean(self):
#         cleaned_data = super().clean()
#         spesialis = cleaned_data.get('spesialis')
#         spesialis_lainnya = cleaned_data.get('spesialis_lainnya')

#         if spesialis == 'Lainnya' and not spesialis_lainnya:
#             raise forms.ValidationError(
#                 "Harap tentukan spesialis lainnya."
#             )
        
#         return cleaned_data

class RegisterDokterForm(BaseRegisterForm):
    spesialis = forms.MultipleChoiceField(
        choices=SPESIALIS_CHOICES,
        label='Spesialis',
        widget=forms.CheckboxSelectMultiple
    )
    spesialis_lainnya = forms.CharField(
        label='Spesifikasi Spesialis Lainnya',
        required=False,
    )
    no_izin_praktek = forms.CharField(
        label='No Izin Praktek',
    )

    def clean(self):
        cleaned_data = super().clean()
        spesialis_list = cleaned_data.get('spesialis') or []
        spesialis_lainnya = cleaned_data.get('spesialis_lainnya')

        if 'Lainnya' in spesialis_list and not spesialis_lainnya:
            raise forms.ValidationError("Jika memilih 'Lainnya', kolom spesialisasi lainnya wajib diisi.")

        return cleaned_data
