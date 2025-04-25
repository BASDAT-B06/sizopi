from django.db import models

class Habitat(models.Model):
    nama = models.CharField(max_length=100)
    luas_area = models.IntegerField()  
    kapasitas_maksimal = models.IntegerField()  
    status_lingkungan = models.TextField()  

    def __str__(self):
        return self.nama
