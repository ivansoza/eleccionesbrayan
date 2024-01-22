from django.db import models
from django.conf import settings
from usuarios.models import Seccion
# Create your models here.


class Calle(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='calles_catalogos')
    meta_promovidos = models.IntegerField(default=0)
    ruta = models.TextField(blank=True, null=True)  # Almacenar la ruta en formato JSON


    def __str__(self):
        return f"{self.nombre} - {self.seccion.nombre}"
    

class TipoChoices(models.TextChoices):
    LONA = 'Lona', 'Lona'
    PARED = 'Pared', 'Pared'
    POSTE = 'Poste', 'Poste'
class Publicidad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calle = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Calle')
    tipo = models.CharField(max_length=100, choices=TipoChoices.choices)
    foto = models.ImageField(upload_to='fotos/')
    comentarios = models.TextField(blank=True, null=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    


    def _str_(self):
        return self.tipo
    