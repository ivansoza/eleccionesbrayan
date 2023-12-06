from django.db import models
from django.db import models
from django.contrib.auth.models import (AbstractUser)
from django.conf import settings

# Create your models here.




class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    latitud = models.FloatField()
    longitud = models.FloatField()
    meta_promovidos = models.IntegerField(default=0)  # Agregado con un valor predeterminado

    def __str__(self):
        return self.nombre
class CustomUser(AbstractUser):
    # Puedes agregar más campos si necesitas

    foto = models.ImageField(upload_to='fotos_usuarios/', blank=True, null=True)
    foto_ine_frontal = models.ImageField(upload_to='fotos_ine/', blank=True, null=True)
    foto_ine_reverso = models.ImageField(upload_to='fotos_ine/', blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    seccion = models.ManyToManyField(Seccion, blank=True)
    ocupacion = models.CharField(max_length=100, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    telefono_fijo = models.CharField(max_length=20, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='Creado por'
    )

    SEX_CHOICES = [
        ('M', 'Hombre'),
        ('F', 'Mujer'),
        # Puedes agregar más opciones si es necesario
    ]
    sexo = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    def profile_complete(self):
            # Reemplaza 'foto', 'foto_ine_frontal', y 'foto_ine_reverso' con los nombres reales de tus campos de imagen
            # Asegúrate de que estos campos existen en tu modelo CustomUser
            return all([self.foto, self.foto_ine_frontal, self.foto_ine_reverso])
    def __str__(self):
        # Regresa el nombre completo del usuario
        return f"{self.first_name} {self.last_name}"
    def is_in_special_groups(self):
        return self.groups.filter(name__in=["Administrador", "Coordinador General", "Candidato"]).exists()