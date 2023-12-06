from django import forms
from .models import Publicidad
from usuarios.models import Seccion


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