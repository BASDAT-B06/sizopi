from django.db import models

class Habitat(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Satwa(models.Model):
    STATUS_KESEHATAN_CHOICES = [
        ('Sehat', 'Sehat'),
        ('Sakit', 'Sakit'),
        ('Dalam Pemantauan', 'Dalam Pemantauan'),
        ('Lainnya', 'Lainnya'),
    ]

    nama_individu = models.CharField(max_length=100, blank=True, null=True)
    spesies = models.CharField(max_length=100)
    asal_hewan = models.CharField(max_length=100)
    tanggal_lahir = models.DateField(blank=True, null=True)
    status_kesehatan = models.CharField(max_length=30, choices=STATUS_KESEHATAN_CHOICES)
    habitat = models.ForeignKey(Habitat, on_delete=models.SET_NULL, null=True)
    url_foto = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('nama_individu', 'spesies', 'asal_hewan')

    def __str__(self):
        return self.nama_individu or self.spesies
