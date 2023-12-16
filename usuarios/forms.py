from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator

from .models import CustomUser, Seccion

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'seccion',)  # Incluye aquí otros campos que quieras en el formulario

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'seccion',) 

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto', 'foto_ine_frontal', 'foto_ine_reverso']

class CustomUserCreationFormTemplate(UserCreationForm):
    
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento:",
        widget=forms.DateInput(attrs={'type': 'text', 'id': 'date', 'placeholder': "DD/MM/YYYY"}),
        input_formats=['%d/%m/%Y'],
    )

    def clean_fechaNacimiento(self):
        data = self.cleaned_data['fecha_nacimiento']
        today = datetime.date.today()
        age = today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        if age < 18:
            raise ValidationError('Debe de ser mayor de 18 años.')        
        if age > 110:
            raise ValidationError('La edad ingresada no es válida. Por favor, verifica la fecha de nacimiento.')
        return data
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'foto', 'foto_ine_frontal', 'foto_ine_reverso', 
                 'apellido_materno', 'direccion', 'colonia', 'localidad', 'ocupacion', 'celular', 'telefono_fijo', 
                 'sexo', 'fecha_nacimiento')  
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'placeholder': 'Seleccione la fecha de nacimiento', 'type': 'date'}),
            }
             
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationFormTemplate, self).__init__(*args, **kwargs)

       
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
        self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
        self.fields['last_name'].label = 'Apellido Paterno'
        self.fields['apellido_materno'].label = 'Apellido Materno'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
        self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
        self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
        self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
        self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
        self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'
        
        self.fields['sexo'].widget.attrs['placeholder'] = 'Sexo'
        self.fields['sexo'].label = 'Sexo'


        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field and isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})

class CustomCoordinatorCreationFormTemplate(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupo"
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','group','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo')

    def __init__(self, *args, **kwargs):
        super(CustomCoordinatorCreationFormTemplate, self).__init__(*args, **kwargs)

        for group_name in ['Coordinador General', ]:
                    Group.objects.get_or_create(name=group_name)
        self.fields['group'] = forms.ModelChoiceField(
                    queryset=Group.objects.filter(name__in=['Coordinador General']),
                    required=True,
                    label="Perfil"
                )
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
        self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
        self.fields['last_name'].label = 'Apellido Paterno'
        self.fields['apellido_materno'].label = 'Apellido Materno'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
        self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
        self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
        self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
        self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
        self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'


        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field and isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})

class CustomCoordinatorResCreationFormTemplate(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupo"
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','group','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo','created_by')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        super(CustomCoordinatorResCreationFormTemplate, self).__init__(*args, **kwargs)

        for group_name in ['Coordinador Responsable']:
                    Group.objects.get_or_create(name=group_name)
        self.fields['group'] = forms.ModelChoiceField(
                    queryset=Group.objects.filter(name__in=['Coordinador Responsable']),
                    required=True,
                    label="Perfil"
                )
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
        self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
        self.fields['last_name'].label = 'Apellido Paterno'
        self.fields['apellido_materno'].label = 'Apellido Materno'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
        self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
        self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
        self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
        self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
        self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'


        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field and isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
        
        if self.request and self.request.user.groups.filter(name__in=['Candidato', 'Administrador']).exists():
            Group.objects.get_or_create(name='Coordinador General')
            self.fields['created_by'] = forms.ModelChoiceField(
                queryset=CustomUser.objects.filter(groups__name='Coordinador General'),
                required=False,
                label="Asignar a:"
            )
        else:
            # Oculta el campo si el usuario no es Candidato o Administrador
            self.fields['created_by'].widget = forms.HiddenInput()

class CustomPromotorCreationFormTemplate(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Grupo"
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','group','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo')

    def __init__(self, *args, **kwargs):
        super(CustomPromotorCreationFormTemplate, self).__init__(*args, **kwargs)

        for group_name in ['Promotor General', 'Promotor Responsable']:
                    Group.objects.get_or_create(name=group_name)
        self.fields['group'] = forms.ModelChoiceField(
                    queryset=Group.objects.filter(name__in=['Promotor General', 'Promotor Responsable']),
                    required=True,
                    label="Perfil"
                )
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
        self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
        self.fields['last_name'].label = 'Apellido Paterno'
        self.fields['apellido_materno'].label = 'Apellido Materno'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
        self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
        self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
        self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
        self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
        self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'


        for field_name in self.fields:
            field = self.fields.get(field_name)  
            if field and isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})

# CREAR COORDINADOR 

class CustomUserCreationFormTemplateCordiArea(UserCreationForm):
   
     seccion = forms.ModelMultipleChoiceField(
         queryset=Seccion.objects.all(),
         required=True,
         label="Secciones",
     )

     class Meta:
         model = CustomUser
         fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo')

     def __init__(self, *args, **kwargs):
         super(CustomUserCreationFormTemplateCordiArea, self).__init__(*args, **kwargs)
         self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
         self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
         self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
         self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
         self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
         self.fields['last_name'].label = 'Apellido Paterno'
         self.fields['apellido_materno'].label = 'Apellido Materno'
         self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
         self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
         self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
         self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
         self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
         self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'
         self.fields['seccion'].widget.attrs['class'] = 'select2'
         self.fields['seccion'].widget.attrs['style'] = 'width: 100%;'


         for field_name in self.fields:
             field = self.fields.get(field_name)  
             if field and isinstance(field.widget, forms.TextInput):
                 field.widget.attrs.update({'class': 'form-control'})


class CustomUserCreationFormTemplateCordiSeccion(UserCreationForm):
   
     seccion = forms.ModelMultipleChoiceField(
         queryset=Seccion.objects.all(),
         required=True,
         label="Secciones",
     )

     class Meta:
         model = CustomUser
         fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo')

     def __init__(self, *args, **kwargs):
         user = kwargs.pop('user', None)

         super(CustomUserCreationFormTemplateCordiSeccion, self).__init__(*args, **kwargs)
         self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
         self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
         self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
         self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
         self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
         self.fields['last_name'].label = 'Apellido Paterno'
         self.fields['apellido_materno'].label = 'Apellido Materno'
         self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
         self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
         self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
         self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
         self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
         self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'
         self.fields['seccion'].widget.attrs['class'] = 'select2'
         self.fields['seccion'].widget.attrs['style'] = 'width: 100%;'

         if user is not None:
            # Filtra las secciones basándote en el usuario logueado
                self.fields['seccion'].queryset = Seccion.objects.filter(customuser=user)
        
         for field_name in self.fields:
             field = self.fields.get(field_name)  
             if field and isinstance(field.widget, forms.TextInput):
                 field.widget.attrs.update({'class': 'form-control'})


class CustomUserCreationFormTemplatePromotor(UserCreationForm):
   
     seccion = forms.ModelMultipleChoiceField(
         queryset=Seccion.objects.all(),
         required=True,
         label="Secciones",
     )

     class Meta:
         model = CustomUser
         fields = ('username', 'first_name', 'last_name', 'email', 'seccion', 'foto', 'foto_ine_frontal', 'foto_ine_reverso','apellido_materno','direccion','colonia','localidad','ocupacion','celular','telefono_fijo')

     def __init__(self, *args, **kwargs):
         user = kwargs.pop('user', None)

         super(CustomUserCreationFormTemplatePromotor, self).__init__(*args, **kwargs)
         self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
         self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
         self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido Paterno'
         self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'
         self.fields['apellido_materno'].widget.attrs['placeholder'] = 'Apellido Materno'
         self.fields['last_name'].label = 'Apellido Paterno'
         self.fields['apellido_materno'].label = 'Apellido Materno'
         self.fields['direccion'].widget.attrs['placeholder'] = 'Ej. Av Moctezuma'
         self.fields['colonia'].widget.attrs['placeholder'] = 'Ej. La Loma '
         self.fields['localidad'].widget.attrs['placeholder'] = 'Ej. Tlaxcala Centro '
         self.fields['ocupacion'].widget.attrs['placeholder'] = 'Ej. Docente '
         self.fields['celular'].widget.attrs['placeholder'] = 'Numero de Celular'
         self.fields['telefono_fijo'].widget.attrs['placeholder'] = 'Numero de Teléfono'
         self.fields['seccion'].widget.attrs['class'] = 'select2'
         self.fields['seccion'].widget.attrs['style'] = 'width: 100%;'

         for field_name in self.fields:
             field = self.fields.get(field_name)  
             if field and isinstance(field.widget, forms.TextInput):
                 field.widget.attrs.update({'class': 'form-control'})

class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'descripcion', 'latitud', 'longitud']
        help_texts = {
            'longitud': 'Puedes capturar la Longitud con alguna de las opciones que se muestran en la parte inferior.',
            'latitud': 'Puedes capturar la Latitud con alguna de las opciones que se muestran en la parte inferior.',
        }
    
    def __init__(self, *args, **kwargs):
        super(SeccionForm, self).__init__(*args, **kwargs)
        # Establecer los campos latitud y longitud como solo lectura
        self.fields['latitud'].widget.attrs['readonly'] = True
        self.fields['longitud'].widget.attrs['readonly'] = True
        # Agregar placeholders
        self.fields['nombre'].widget.attrs['placeholder'] = 'Nombre de la sección'
        self.fields['descripcion'].widget.attrs['placeholder'] = 'Descripción breve de la sección'
        self.fields['latitud'].widget.attrs['placeholder'] = 'Ej: 19.432608'
        self.fields['longitud'].widget.attrs['placeholder'] = 'Ej: -99.133209'
class SeccionFormUpdate(forms.ModelForm):

    class Meta:
        model = Seccion
        fields = ['latitud', 'longitud']
        help_texts = {
        'longitud': 'Puedes capturar la Longitud con alguna de las opciones que se muestran en la parte inferior.',
        'latitud': 'Puedes capturar la Latitud  con alguna de las opciones que se muestran en la parte inferior.',

        }
    def __init__(self, *args, **kwargs):
        super(SeccionFormUpdate, self).__init__(*args, **kwargs)
        self.fields['latitud'].widget.attrs['readonly'] = True
        self.fields['longitud'].widget.attrs['readonly'] = True
        

    
class UserStatusForm(forms.Form):
    # El campo no necesita ser visible, ya que solo se utilizará para cambiar el estado
    is_active = forms.BooleanField(widget=forms.HiddenInput(), required=False)