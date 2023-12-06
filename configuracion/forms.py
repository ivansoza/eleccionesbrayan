from django import forms
from .models import CandidatoConfig
from django.core.validators import MinValueValidator

class CandidatoConfigForm(forms.ModelForm):
    meta_promovidos = forms.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        model = CandidatoConfig
        fields = ['nombre_candidato', 'color_primario', 'color_secundario', 'meta_promovidos', 'latitud', 'longitud']
        widgets = {
            'color_primario': forms.TextInput(attrs={'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'type': 'color'}),
            'latitud': forms.NumberInput(attrs={'placeholder': 'Ejemplo: 19.432608', 'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'placeholder': 'Ejemplo: -99.133209', 'step': 'any'}),
        }
        help_texts = {
            'latitud': 'Introduce la latitud en formato decimal.',
            'longitud': 'Introduce la longitud en formato decimal.',
        }