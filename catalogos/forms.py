from django import forms
from .models import Calle, Publicidad
from usuarios.models import Seccion

from django.core.validators import RegexValidator

class PublicidadForm(forms.ModelForm):
    seccion = forms.ModelChoiceField(
        queryset=Seccion.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select', 'placeholder': 'Seleccione la sección...'}),
        empty_label="Seleccione la sección..."
    )

    class Meta:
        model = Publicidad
        fields = ('seccion','tipo','foto','comentarios','latitud','longitud')
        widgets = {
            'tipo': forms.Select(attrs={'class': 'custom-select'}),
            'comentarios': forms.Textarea(attrs={'placeholder': 'Agregue comentarios...'}),
            'latitud': forms.NumberInput(attrs={'readonly': True, 'placeholder': '19.432608'}),
            'longitud': forms.NumberInput(attrs={'readonly': True, 'placeholder': '-99.133209'}),
            'foto': forms.FileInput(attrs={'placeholder': 'Suba una foto...'}),
        }
        help_texts = {
            'latitud': 'Puedes capturar la Latitud y Longitud con alguna de las opciones que se muestran en la parte inferior.',
            'longitud': 'Puedes capturar la Latitud y Longitud con alguna de las opciones que se muestran en la parte inferior.',
        }

    def __init__(self, *args, **kwargs):
        super(PublicidadForm, self).__init__(*args, **kwargs)
        # Asegúrate de que 'seccion' use el queryset correcto si necesitas filtrar las secciones disponibles
        self.fields['seccion'].queryset = Seccion.objects.all()
        # Otras inicializaciones si son necesarias


class CalleForm(forms.ModelForm):
    ruta = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Selecciona en el mapa para agregar la ruta',
            'readonly': 'readonly'
        })
    )

    # Validador para asegurarse de que solo se acepten números enteros positivos y no el número 0
    positive_integer_validator = RegexValidator(
        regex=r'^[1-9]\d*$',
        message="Por favor, ingresa un número entero positivo y no cero."
    )

    meta_promovidos = forms.CharField(
        validators=[positive_integer_validator],
        widget=forms.NumberInput(attrs={'placeholder': 'Meta de promovidos'})
    )

    class Meta:
        model = Calle
        fields = ['nombre', 'seccion', 'meta_promovidos', 'ruta']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la calle'}),
            'seccion': forms.Select(attrs={'placeholder': 'Sección'}),
        }