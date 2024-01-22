from django import forms
from .models import Calle, Publicidad
from usuarios.models import Seccion

from django.core.validators import RegexValidator

class PublicidadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicidadForm, self).__init__(*args, **kwargs)
        # Agregar una opción predeterminada al inicio de las opciones para 'tipo'
        self.fields['tipo'].choices = [('','Seleccione un tipo de publicidad')] + list(self.fields['tipo'].choices)[1:]

    latitud = forms.FloatField(
        required=True, 
        help_text='Puedes capturar la Latitud con alguna de las opciones que se muestran en la parte inferior.',
        widget=forms.NumberInput(attrs={'placeholder': 'Ejemplo: 19.432608', 'readonly': 'readonly'})
    ) 
    longitud = forms.FloatField(
        required=True, 
        help_text='Puedes capturar la Longitud con alguna de las opciones que se muestran en la parte inferior.',
        widget=forms.NumberInput(attrs={'placeholder': 'Ejemplo: -99.133209', 'readonly': 'readonly'})
    )
    calle = forms.ModelChoiceField(
        queryset=Calle.objects.all(),
        label='Calle',
        widget=forms.Select(attrs={'id': 'id_calle'}),  # Asegúrate de que el id sea único y correcto
        required=True,
        empty_label="Selecciona una calle",  # Esta es la opción que se mostrará inicialmente

    )

    class Meta:
        model = Publicidad
        fields = ('calle','tipo','foto','comentarios','latitud','longitud')
        widgets = {
            'tipo': forms.Select(attrs={'class': 'custom-select'}),
            'comentarios': forms.Textarea(attrs={'placeholder': 'Agregue comentarios...'}),
            'latitud': forms.NumberInput(attrs={'readonly': True, 'placeholder': '19.432608'}),
            'longitud': forms.NumberInput(attrs={'readonly': True, 'placeholder': '-99.133209'}),
            'foto': forms.FileInput(attrs={'placeholder': 'Suba una foto...'}),
        }
  



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