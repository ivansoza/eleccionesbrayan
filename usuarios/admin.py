from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Seccion

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'is_staff','created_by']  # Asegúrate de que 'seccion' es un campo en CustomUser

    # Añade 'seccion' a los fieldsets de UserAdmin para la edición de usuarios
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('seccion',)}),
    )
    
    # Añade 'seccion' a los add_fieldsets para la creación de usuarios
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('seccion',)}),
    )

# Registra tus modelos en el admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Seccion) 