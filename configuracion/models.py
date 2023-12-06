from django.db import models

class CandidatoConfig(models.Model):
    nombre_candidato = models.CharField(max_length=100)
    color_primario = models.CharField(max_length=7)  # Guarda colores en formato HEX
    color_secundario = models.CharField(max_length=7)
    meta_promovidos = models.IntegerField()
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre_candidato