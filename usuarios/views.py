from django.shortcuts import render
from django.urls import reverse_lazy
from django.db.models import Q

# Create your views here.from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import CustomUserUpdateForm, CustomUserCreationFormTemplate, CustomCoordinatorCreationFormTemplate, CustomPromotorCreationFormTemplate,CustomCoordinatorResCreationFormTemplate,CustomUserCreationFormTemplateCordiArea,CustomUserCreationFormTemplateCordiSeccion,CustomUserCreationFormTemplatePromotor, SeccionForm, UserStatusForm, \
SeccionFormUpdate
from promovido.models import prospecto
from .models import CustomUser, Seccion
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from promovido.models import Calle
from django.db.models import Sum
from django.http import JsonResponse
import json

User = get_user_model()


class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'update_profile.html'

    def get_success_url(self):
        # Redirige a la URL deseada tras actualizar el perfil
        return reverse_lazy('menu')  # Asegúrate de que 'menu' es el nombre de la URL a la que deseas redirigir

    def get_object(self, queryset=None):
        # Retorna el objeto que la vista está mostrando (en este caso, el usuario actual).
        return self.request.user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        return context


# CREAR USUARIO DESDE GRUPO ADMINISTRADOR --------------
class UserCreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = CustomUser
    form_class = CustomUserCreationFormTemplate
    template_name = 'administradores/register_user.html'
    success_url = reverse_lazy('users_list')  # Asegúrate de definir esta URL en tu urls.py

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Administrador', 'Candidato']).exists()

    def form_valid(self, form):
        user = form.save(commit=False)
        user.created_by = self.request.user
        user.save()
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        user.groups.add(admin_group)
        messages.success(self.request, "Usuario creado con éxito.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'gestion_user'  # Cambia esto según la página activa
        context['seccion'] = 'ver_usuarios'  # Cambia esto según la página activa

        return context
    

    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')
    
    # ----------------------- FIN CREAR USUARIO DESDE GRUPO ADMINISTRADOR --------------

    # CREAR USUARIO DESDE GRUPO Coordinador General --------------
class UserCreateCordiGeneView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = CustomUser
    form_class = CustomUserCreationFormTemplate
    template_name = 'administradores/register_user_CoordinadorGeneral.html'
    success_url = reverse_lazy('users_list_cordi_gene')  # Asegúrate de definir esta URL en tu urls.py
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Administrador', 'Candidato']).exists()

    def form_valid(self, form):
        user = form.save(commit=False)
        user.created_by = self.request.user
        user.save()
        admin_group, created = Group.objects.get_or_create(name='Coordinador General')
        user.groups.add(admin_group)
        messages.success(self.request, "Usuario creado con éxito.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'gestion_user'  # Cambia esto según la página activa
        context['seccion'] = 'ver_coordinadores'  # Cambia esto según la página activa

        return context
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')
    

# -------------------CREACION DE UN USUARIO PROMOTOR READY------------------
class UserCreateViewPromotor(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = CustomUser
    form_class = CustomUserCreationFormTemplatePromotor
    template_name = 'promotores/register_user.html'
    success_url = reverse_lazy('UserListViewCordiPromo')  # Asegúrate de definir esta URL en tu urls.py
    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists()    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.created_by = self.request.user
        user.save()
        admin_group, created = Group.objects.get_or_create(name='Promotor')
        user.groups.add(admin_group)
        messages.success(self.request, "Usuario creado con éxito.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name='Coordinador General').exists():
            context['navbar'] = 'gestion_user' 
            context['seccion'] = 'ver_coordinadores_area1'  

        elif self.request.user.groups.filter(name='Administrador').exists():
            context['navbar'] = 'consulta_users'  # Cambia esto según la página activa
            context['seccion'] = 'ver_promotores'  
        elif self.request.user.groups.filter(name='Candidato').exists():
            context['navbar'] = 'consulta_users'  # Cambia esto según la página activa
            context['seccion'] = 'ver_promotores' 
        elif self.request.user.groups.filter(name='Coordinador Sección').exists():
            context['navbar'] = 'gestion_user'  
            context['seccion'] = 'ver_promotores' 

        return context
    def get_form_kwargs(self):
            kwargs = super(UserCreateViewPromotor, self).get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')

class UserListViewCordiPromo(LoginRequiredMixin, UserPassesTestMixin,ListView):
    model = CustomUser
    template_name = 'administradores/list_user_Promotor.html'
    context_object_name = 'users'
    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists()   
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')
    def get_queryset(self):
        user = self.request.user
        special_groups = ['Administrador', 'Candidato', 'Coordinador General']
        is_special_user = user.groups.filter(name__in=special_groups).exists()

        if is_special_user:
            # Estos grupos pueden ver a todos los 'Promotores'
            return CustomUser.objects.filter(groups__name='Promotor')
        else:
            # 'Coordinadores de Area' y 'Coordinadores de Sección' solo ven 'Promotores' en sus secciones
            allowed_groups = ['Coordinador de Area', 'Coordinador Sección']
            if user.groups.filter(name__in=allowed_groups).exists():
                user_sections = user.seccion.all()
                return CustomUser.objects.filter(
                    groups__name='Promotor', 
                    seccion__in=user_sections
                )
            return CustomUser.objects.none()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_cordi_promo'] = self.get_queryset().count()
        context['es_coordinador_seccion'] = self.request.user.groups.filter(name='Coordinador Sección').exists()
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(sexo='M').count()
        context['num_mujeres'] = queryset.filter(sexo='F').count()
        
        if self.request.user.groups.filter(name='Coordinador General').exists():
            context['navbar'] = 'consulta_users' 
            context['seccion'] = 'ver_promotores'  

        elif self.request.user.groups.filter(name='Administrador').exists():
            context['navbar'] = 'consulta_users'  
            context['seccion'] = 'ver_promotores'
        elif self.request.user.groups.filter(name='Coordinador de Area').exists():
            context['navbar'] = 'consulta_users'  
            context['seccion'] = 'ver_promotores' 

        elif self.request.user.groups.filter(name='Coordinador Sección').exists():
            context['navbar'] = 'gestion_user'  
            context['seccion'] = 'ver_promotores' 
        return context

        
#------------------ FIN DE PROMOTOR READY -.-----------------------

class UserListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'administradores/list_user_Administrador.html'
    context_object_name = 'users'
    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
    def get_queryset(self):
        # Obtiene los grupos 'Administrador' y 'Capturista'
        groups = Group.objects.filter(name__in=['Administrador'])

        # Filtra los usuarios que fueron creados por el usuario logueado y que pertenecen a uno de los grupos especificados
        return CustomUser.objects.filter(
            groups__in=groups
        ).exclude(pk=self.request.user.pk)  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'gestion_user'  # Cambia esto según la página activa
        context['seccion'] = 'ver_usuarios'  # Cambia esto según la página activa
        context['num_administradores'] = self.get_queryset().count()
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(sexo='M').count()
        context['num_mujeres'] = queryset.filter(sexo='F').count()
        return context
    
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')

class UserListViewCordiGen(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'administradores/list_user_CoordinadorGeneral.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Obtiene los grupos 'Administrador' y 'Capturista'
        groups = Group.objects.filter(name__in=['Coordinador General'])
        return CustomUser.objects.filter(
            groups__in=groups
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'gestion_user'  # Cambia esto según la página activa
        context['seccion'] = 'ver_coordinadores'  # Cambia esto según la página activa
        context['num_cordi_gen'] = self.get_queryset().count()
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(sexo='M').count()
        context['num_mujeres'] = queryset.filter(sexo='F').count()
        context['es_administrador'] = self.request.user.groups.filter(name='Administrador').exists()

        return context





class seccionlist(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Seccion
    template_name = 'seccion/list_seccion.html'
    context_object_name = 'secciones'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Administrador', 'Candidato', 'Coordinador General']).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_secciones = Seccion.objects.count()  # Número total de secciones
        total_calles = Calle.objects.count() 
        # Añade el total de meta de promovidos a cada sección
        for seccion in context['secciones']:
            total_meta_promovidos = Calle.objects.filter(seccion=seccion).aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
            numero_de_calles = Calle.objects.filter(seccion=seccion).count()

            seccion.total_meta_promovidos = total_meta_promovidos
            seccion.numero_de_calles = numero_de_calles  # Añade el número de calles
        context['total_secciones'] = total_secciones
        context['total_calles'] = total_calles
        context['navbar'] = 'seccion'
        context['seccion'] = 'secciones'
        return context

    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templateDenegado')


    
class SeccionCreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Seccion
    form_class = SeccionForm
    template_name = 'seccion/create_seccion.html'
    success_url = reverse_lazy('seccion_list')

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Administrador', 'Candidato','Coordinador General']).exists()
    def form_valid(self, form):
        # Aquí se llama a la implementación del padre primero
        response = super().form_valid(form)
        # Agregar el mensaje de éxito
        messages.success(self.request, "Sección creada con éxito")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'seccion'
        context['seccion'] = 'secciones'
        return context
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')
class SeccionUpdateView(LoginRequiredMixin,UpdateView):
    model = Seccion
    form_class = SeccionFormUpdate
    template_name = 'seccion/update_seccion.html'
    success_url = reverse_lazy('seccion_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Sección actualizada con éxito")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'seccion'
        context['seccion'] = 'secciones'
        return context
    
class SeccionDetailView(DetailView):
    model = Seccion
    template_name = 'seccion/mostrar_seccion.html'
    context_object_name = 'secciones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seccion = self.get_object()

        # Obtiene todas las calles asociadas con la sección
        calles = Calle.objects.filter(seccion=seccion)

        # Calcula el total de calles
        total_calles = calles.count()

        rutas_con_nombre = []
        for calle in calles:
            if calle.ruta:
                ruta = json.loads(calle.ruta)
                rutas_con_nombre.append({
                    'nombre': calle.nombre,
                    'ruta': ruta
                })

        context['rutas'] = rutas_con_nombre
        context['total_calles'] = total_calles  # Agrega el total de calles al contexto
        context['navbar'] = 'seccion'
        context['seccion'] = 'secciones'
        return context
class callesList(LoginRequiredMixin, ListView):
    model = Calle
    template_name = 'calles/list_calles.html'
    context_object_name = 'calle'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        

        context['navbar'] = 'seccion'
        context['seccion'] = 'calle'
        return context
    
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')





# ACTUALIZAR ESTADO DEL USUARIO PARA EL LOGIN 

@login_required
def update_user_statusCordiGene(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserStatusForm(request.POST)
        if form.is_valid():
            user.is_active = not user.is_active  # Toggle the user's active status
            user.save()
            if user.is_active:
                messages.success(request, "Usuario activado con éxito.")
            else:
                messages.success(request, "Usuario desactivado con éxito.")
            return redirect('users_list_cordi_gene')  # Asegúrate de que esta es la URL correcta
    else:
        form = UserStatusForm(initial={'is_active': user.is_active})

    # Puedes redirigir o mostrar un mensaje si el método no es POST
    messages.error(request, "Método no permitido.")
    return redirect('users_list_cordi_gene')  # O re


@login_required
def update_user_statusPromotor(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserStatusForm(request.POST)
        if form.is_valid():
            user.is_active = not user.is_active  # Toggle the user's active status
            user.save()
            if user.is_active:
                messages.success(request, "Usuario activado con éxito.")
            else:
                messages.success(request, "Usuario desactivado con éxito.")
            return redirect('UserListViewCordiPromo')  # Asegúrate de que esta es la URL correcta
    else:
        form = UserStatusForm(initial={'is_active': user.is_active})

    # Puedes redirigir o mostrar un mensaje si el método no es POST
    messages.error(request, "Método no permitido.")
    return redirect('UserListViewCordiPromo')  # O re

