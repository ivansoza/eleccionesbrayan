from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from catalogos.models import Calle
from usuarios.models import Seccion
# Create your models here.
GENERO_CHOICES = [
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer'),
    ]
STATUS_CHOICES = [
        ('Prospecto', 'Prospecto'),
        ('Promovido', 'Promovido'),
        ('Verificado', 'Verificado'),
        ('Rechazado', 'Rechazado'),  # Nuevo estado para reflejar los rechazos
    ]
SOLICITUD_CHOICES = [
        ('Apoyo Económico', 'Apoyo Económico'),
        ('Mejora de Infraestructuras', 'Mejora de Infraestructuras'),
        ('Programas Sociales', 'Programas Sociales'),
        ('Educación', 'Educación'),
        ('Salud', 'Salud'),
        ('Otros', 'Otros'),
    ]
PROBLEMATICAS_CHOICES = [
        ('Seguridad', 'Seguridad'),
        ('Desempleo', 'Desempleo'),
        ('Educación', 'Educación'),
        ('Salud', 'Salud'),
        ('Medio Ambiente', 'Medio Ambiente'),
        ('Corrupción', 'Corrupción'),
        ('Otros', 'Otros'),
    ]


OCUPACIONES_CHOICES = [
    ('Agricultor', 'Agricultor'),
    ('Artista', 'Artista'),
    ('Comerciante', 'Comerciante'),
    ('Docente', 'Docente'),
    ('Enfermero/a', 'Enfermero/a'),
    ('Ingeniero', 'Ingeniero'),
    ('Médico', 'Médico'),
    ('Abogado', 'Abogado'),
    ('Arquitecto', 'Arquitecto'),
    ('Contador', 'Contador'),
    ('Estudiante', 'Estudiante'),
    ('Obrero', 'Obrero'),
    ('Empresario', 'Empresario'),
    ('Chofer', 'Chofer'),
    ('Cocinero', 'Cocinero'),
    ('Camarero', 'Camarero'),
    ('Ama de casa', 'Ama de casa'),
    ('Mecánico', 'Mecánico'),
    ('Electricista', 'Electricista'),
    ('Carpintero', 'Carpintero'),
    ('Plomero', 'Plomero'),
    ('Vendedor', 'Vendedor'),
    ('Empleado de oficina', 'Empleado de oficina'),
    ('Técnico', 'Técnico'),
    ('Científico', 'Científico'),
    ('Dentista', 'Dentista'),
    ('Fotógrafo', 'Fotógrafo'),
    ('Diseñador', 'Diseñador'),
    ('Musico', 'Musico'),
    ('Pintor', 'Pintor'),
    ('Escritor', 'Escritor'),
    ('Otros', 'Otros'),
]

class prospecto(models.Model):

    STATUS_CHOICES = [
        ('Prospecto', 'Prospecto'),
        ('Promovido', 'Promovido'),
        ('Verificado', 'Verificado'),
        ('Rechazado', 'Rechazado'),  # Nuevo estado para reflejar los rechazos
    ]
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='prospecto_creados',
        blank=True, null=True
    )
    usuario_promovido = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='promovidos_asociados',
        blank=True, null=True
    )
    usuario_verificador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        related_name='promovidos_verificados',
        blank=True, null=True,
        verbose_name='Usuario Verificador'
    )
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    genero = models.CharField(max_length=50, choices=GENERO_CHOICES)
    fechaNacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    numeroCasa = models.CharField(max_length=5, verbose_name="Número de Casa:")
    calle = models.ForeignKey(
            Calle, 
            on_delete=models.SET_NULL, 
            null=True, blank=True, 
            related_name='prospectos'
        )

    seccion = models.ForeignKey(Seccion, on_delete=models.SET_NULL, null=True, blank=True)
    ocupacion = models.CharField(max_length=100, choices=OCUPACIONES_CHOICES, blank=True)
    celular = models.CharField(max_length=15, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    tipo_solicitud = models.CharField(max_length=100, choices=SOLICITUD_CHOICES)
    detalle_solicitud = models.TextField(blank=True)
    problema_tipo = models.CharField(max_length=100, choices=PROBLEMATICAS_CHOICES)
    detalle_problema = models.TextField(blank=True)
    foto_promovido = models.ImageField(upload_to='fotos_promovidos/', blank=True)
    foto_ine_frontal = models.ImageField(upload_to='fotos_ine/', blank=True)
    foto_ine_reverso = models.ImageField(upload_to='fotos_ine/', blank=True)
    numeroINE = models.CharField(max_length=13, unique=True, null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    fecha_promovido = models.DateTimeField(blank=True, null=True)
    fecha_verificado = models.DateTimeField(blank=True, null=True)
    alias = models.CharField(max_length=100, null=True, blank=True)
    numeroINE = models.CharField(max_length=13, unique=True, null=True, blank=True)


    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"
    class Meta:
        unique_together = ('nombre', 'apellido_paterno', 'apellido_materno')
    
class Felicitacion(models.Model):     
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='prospecto_creado',
        blank=True, null=True
    )
    prospecto = models.ForeignKey(
        'prospecto', 
        on_delete=models.CASCADE,
        related_name='felicitaciones'
    )
    fecha_felicitacion = models.DateField(auto_now_add=True)
    felicitado = models.BooleanField(default=False)

    def _str_(self):
        return f"Felicitación para {self.prospecto} - {self.fecha_felicitacion}"

    class Meta:
        unique_together = ('prospecto', 'fecha_felicitacion',)