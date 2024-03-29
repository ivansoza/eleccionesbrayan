from django import forms

from .models import Calle, GENERO_CHOICES,prospecto, Felicitacion, STATUS_CHOICES
from django.core.exceptions import ValidationError
import datetime


class ProspectoFormNuevo(forms.ModelForm):

    fechaNacimiento = forms.DateField(
        label="Fecha de Nacimiento:",
        widget=forms.DateInput(attrs={'type': 'text', 'id': 'date', 'placeholder': "DD/MM/YYYY"}),
        input_formats=['%d/%m/%Y'],
    )

    def clean_fechaNacimiento(self):
        data = self.cleaned_data['fechaNacimiento']
        today = datetime.date.today()
        age = today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        if age < 18:
            raise ValidationError('Debe de ser mayor de 18 años.')        
        if age > 110:
            raise ValidationError('La edad ingresada no es válida. Por favor, verifica la fecha de nacimiento.')
        return data
    

    def __init__(self, *args, **kwargs):
        super(ProspectoFormNuevo, self).__init__(*args, **kwargs)
        self.fields['celular'].required = True
        self.fields['email'].required = True

    class Meta:
        model = prospecto
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno','alias', 'genero', 'fechaNacimiento', 'calle','numeroCasa', 'ocupacion', 'celular', 'telefono', 'email'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellido_paterno': forms.TextInput(attrs={'placeholder': 'Apellido Paterno'}),
            'apellido_materno': forms.TextInput(attrs={'placeholder': 'Apellido Materno'}),
            'alias': forms.TextInput(attrs={'placeholder': 'Alias de la persona'}),

            'genero': forms.Select(attrs={'placeholder': 'Selecciona un Género'}),
            'calle': forms.Select(attrs={'placeholder': 'Calle'}),
            'numeroCasa': forms.TextInput(attrs={'placeholder': 'Ej: 35 A'}),

            'ocupacion': forms.Select(attrs={'placeholder': 'Ocupación'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Número de Celular'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Número de Teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        }

class ProspectoFormNuevoUpdate(forms.ModelForm):
    # ... Definiciones existentes de latitud y longitud ...
    fechaNacimiento = forms.DateField(
        label="Fecha de Nacimiento:",
        widget=forms.DateInput(attrs={'type': 'text', 'id': 'date', 'placeholder': "DD/MM/YYYY"}),
        input_formats=['%d/%m/%Y'],
    )

    def clean_fechaNacimiento(self):
        data = self.cleaned_data['fechaNacimiento']
        today = datetime.date.today()
        age = today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        if age < 18:
            raise ValidationError('Debe de ser mayor de 18 años.')        
        if age > 110:
            raise ValidationError('La edad ingresada no es válida. Por favor, verifica la fecha de nacimiento.')
        return data
    
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


    class Meta:
        model = prospecto
        fields = [
            'numeroINE', 'nombre', 'apellido_paterno', 'apellido_materno','alias', 'genero', 'fechaNacimiento', 'calle', 'ocupacion', 'celular', 'telefono', 'email', 'tipo_solicitud', 
            'detalle_solicitud', 'problema_tipo', 'detalle_problema', 'foto_promovido', 'latitud', 'longitud','numeroCasa', 'foto_ine_frontal','foto_ine_reverso', 'votoSeguro',
        ]
        widgets = {
            'numeroINE': forms.TextInput(attrs={'placeholder': 'Numero del INE'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellido_paterno': forms.TextInput(attrs={'placeholder': 'Apellido Paterno'}),
            'apellido_materno': forms.TextInput(attrs={'placeholder': 'Apellido Materno'}),
            'alias': forms.TextInput(attrs={'placeholder': 'Alias de la persona'}),

            'genero': forms.Select(attrs={'placeholder': 'Selecciona un Género'}),
            'fechaNacimiento': forms.DateInput(attrs={'placeholder': 'Fecha de Nacimiento', 'type': 'date'}),
            'numeroCasa': forms.TextInput(attrs={'placeholder': 'Ej: 35 A'}),

            'ocupacion': forms.Select(attrs={'placeholder': 'Ocupación'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Número de Celular'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Número de Teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
            'tipo_solicitud': forms.Select(attrs={'placeholder': 'Tipo de Solicitud'}),
            'detalle_solicitud': forms.Textarea(attrs={'placeholder': 'Detalles de la Solicitud'}),
            'problema_tipo': forms.Select(attrs={'placeholder': 'Tipo de Problema'}),
            'detalle_problema': forms.Textarea(attrs={'placeholder': 'Detalles del Problema'}),
        }

    # Puedes agregar más configuraciones si es necesario

   
class PromovidoFormNuevo(forms.ModelForm):
    fechaNacimiento = forms.DateField(
        label="Fecha de Nacimiento:",
        widget=forms.DateInput(attrs={'type': 'text', 'id': 'date', 'placeholder': "DD/MM/YYYY"}),
        input_formats=['%d/%m/%Y'],
    )

    def clean_fechaNacimiento(self):
        data = self.cleaned_data['fechaNacimiento']
        today = datetime.date.today()
        age = today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        if age < 18:
            raise ValidationError('Debe de ser mayor de 18 años.')        
        if age > 110:
            raise ValidationError('La edad ingresada no es válida. Por favor, verifica la fecha de nacimiento.')
        return data
    


    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        apellido_paterno = cleaned_data.get("apellido_paterno")
        apellido_materno = cleaned_data.get("apellido_materno")

        # Verifica si existe un prospecto con el mismo nombre, apellido paterno y apellido materno
        if prospecto.objects.filter(nombre=nombre, apellido_paterno=apellido_paterno, apellido_materno=apellido_materno).exists():
            raise forms.ValidationError("Este usuario ya está registrado.")

        return cleaned_data


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
        required=True
    )

    class Meta:
        model = prospecto
        fields = [
           'numeroINE', 'nombre', 'apellido_paterno', 'apellido_materno','alias', 'genero', 'fechaNacimiento', 'calle', 'ocupacion', 'celular', 'telefono', 'email', 'tipo_solicitud', 
            'detalle_solicitud', 'problema_tipo', 'detalle_problema', 'foto_promovido', 
            'latitud', 'longitud','numeroCasa', 'foto_ine_frontal','foto_ine_reverso', 'votoSeguro',
        ]
        widgets = {
            'numeroINE': forms.TextInput(attrs={'placeholder': 'Numero del INE'}),

            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellido_paterno': forms.TextInput(attrs={'placeholder': 'Apellido Paterno'}),
            'apellido_materno': forms.TextInput(attrs={'placeholder': 'Apellido Materno'}),
            'alias': forms.TextInput(attrs={'placeholder': 'Alias de la persona'}),

            'genero': forms.Select(attrs={'placeholder': 'Selecciona un Género'}),
            'numeroCasa': forms.TextInput(attrs={'placeholder': 'Ej: 35 A'}),

            'ocupacion': forms.Select(attrs={'placeholder': 'Ocupación'}),
            'celular': forms.TextInput(attrs={'placeholder': 'Número de Celular'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Número de Teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
            'tipo_solicitud': forms.Select(attrs={'placeholder': 'Tipo de Solicitud'}),
            'detalle_solicitud': forms.Textarea(attrs={'placeholder': 'Detalles de la Solicitud'}),
            'problema_tipo': forms.Select(attrs={'placeholder': 'Tipo de Problema'}),
            'detalle_problema': forms.Textarea(attrs={'placeholder': 'Detalles del Problema'}),
        }


class CalleForm(forms.ModelForm):
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
        fields = ['nombre', 'seccion', 'meta_promovidos', 'latitud', 'longitud']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la calle'}),
            'seccion': forms.Select(attrs={'placeholder': 'Sección'}),
            'meta_promovidos': forms.NumberInput(attrs={'placeholder': 'Meta de promovidos'}),
        }

class felicitacionForms(forms.ModelForm):
     class Meta:
        model = Felicitacion
        fields = '__all__'



class StatusSelectWidget(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Filtra las opciones para mostrar solo 'Verificado' y 'Rechazado'
        if value not in ['Verificado', 'Rechazado']:
            option['attrs']['style'] = 'display:none;'
        return option
class verificarForms(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=StatusSelectWidget)
    class Meta:
        model = prospecto
        fields = ['usuario_verificador','status']