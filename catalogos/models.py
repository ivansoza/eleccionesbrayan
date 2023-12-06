from django.db import models
from django.conf import settings
from usuarios.models import Seccion
# Create your models here.
class TipoChoices(models.TextChoices):
    LONA = 'Lona', 'Lona'
    PARED = 'Pared', 'Pared'
    POSTE = 'Poste', 'Poste'
class Publicidad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seccion = models.ForeignKey(Seccion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Sección')
    tipo = models.CharField(max_length=100, choices=TipoChoices.choices)
    foto = models.ImageField(upload_to='fotos/')
    comentarios = models.TextField(blank=True, null=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    


    def _str_(self):
        return self.tipo