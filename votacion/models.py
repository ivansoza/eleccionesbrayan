from django.db import models

from elecciones import settings

# Create your models here.
class Voto(models.Model):
    prospecto = models.ForeignKey(
        'Prospecto',  # Asegúrate de usar el nombre correcto de tu modelo Prospecto
        on_delete=models.CASCADE,
        related_name='votos'
    )
    fecha_hora_voto = models.DateTimeField(auto_now_add=True)
    usuario_registro_voto = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votos_registrados'
    )
    ESTADO_VOTO_CHOICES = [
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
        ('Pendiente', 'Pendiente'),
    ]
    estado_voto = models.CharField(max_length=10, choices=ESTADO_VOTO_CHOICES)

    def __str__(self):
        return f"Voto de {self.prospecto.nombre} {self.prospecto.apellido_paterno} - {self.estado_voto}"

    class Meta:
        unique_together = ('prospecto', 'fecha_hora_voto')