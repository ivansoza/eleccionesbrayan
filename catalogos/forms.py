from django import forms
from .models import Calle, Publicidad
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


class CalleForm(forms.ModelForm):

    ruta = forms.CharField( required=False)

    latitud = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})
    )
    longitud = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Calle
        fields = ['nombre', 'seccion', 'meta_promovidos', 'latitud', 'longitud', 'ruta']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la calle'}),
            'seccion': forms.Select(attrs={'placeholder': 'Sección'}),
            'meta_promovidos': forms.NumberInput(attrs={'placeholder': 'Meta de promovidos'}),
        }