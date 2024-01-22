from typing import Any
from .models import Calle, Publicidad
from .forms import CalleForm, PublicidadForm
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView
# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from usuarios.models import Seccion
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import json
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from django.db.models import Sum

class crearPublicidad(CreateView):
    template_name = 'crearPublicidad.html'
    model = Publicidad
    form_class = PublicidadForm
    success_url = reverse_lazy('mapapublicidad')

    def form_valid(self, form):
        # Aquí se establece el usuario antes de guardar el objeto Publicidad
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        calles = Calle.objects.select_related('seccion').all()
        context['secciones_coords'] = {
            calle.id: {'lat': calle.seccion.latitud, 'lng': calle.seccion.longitud, 'ruta': calle.ruta}
            for calle in calles if calle.seccion
        }        
        context['navbar'] = 'publicidad'  # Cambia esto según la página activa
        context['seccion'] = 'ver_publicidad'
        return context

class mapaPublicidad(TemplateView):
    template_name = 'mapaPublicidad.html'
    context_object_name = 'publicidad'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset=Publicidad.objects.all()

        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            queryset=Publicidad.objects.filter(usuario=user)

        elif user.groups.filter(name='Promotor').exists():
            queryset=Publicidad.objects.filter(usuario=user)

        else:
            queryset=Publicidad.objects.none()

        calle_filtro = self.request.GET.get('calle')
        if calle_filtro:
            queryset = queryset.filter(calle_id=calle_filtro)

        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_actual = self.request.user

        # Filtrar calles según el grupo de usuarios
        if usuario_actual.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            calles = Calle.objects.all()
        elif usuario_actual.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            calles = Calle.objects.filter(seccion__usuario=usuario_actual)
        elif usuario_actual.groups.filter(name='Promotor').exists():
            calles = Calle.objects.filter(publicidad__usuario=usuario_actual).distinct()
        else:
            calles = Calle.objects.none()

        ubicaciones = self.get_queryset()
        num_cordi_area = ubicaciones.filter(tipo='Lona').count()
        num_hombres = ubicaciones.filter(tipo='Pared').count()
        num_mujeres = ubicaciones.filter(tipo='Poste').count()
        num_total = ubicaciones.count()
        context.update({
            'ubicaciones': ubicaciones,
            'num_cordi_area': num_cordi_area,

            'num_hombres': num_hombres,
            'calles': calles,
            'navbar': 'publicidad',
            'seccion': 'ver_publicidad',
            'num_mujeres': num_mujeres,
            'num_total': num_total,        })
        return context

from django_postalcodes_mexico.models import PostalCode
from django.shortcuts import render


C_ESTADO_CHOICES = {
        "26": "Sonora",
        "10": "Durango",
        "03": "Baja California Sur",
        "04": "Campeche",
        "16": "Michoacán de Ocampo",
        "31": "Yucatán",
        "19": "Nuevo León",
        "12": "Guerrero",
        "11": "Guanajuato",
        "25": "Sinaloa",
        "15": "Ciudad de México",
        "29": "Tlaxcala",
        "13": "Hidalgo",
        "08": "Chihuahua",
        "24": "San Luis Potosí",
        "27": "Tabasco",
        "23": "Quintana Roo",
        "28": "Tamaulipas",
        "14": "Jalisco",
        "05": "Coahuila de Zaragoza",
        "09": "Ciudad de México",
        "21": "Puebla",
        "06": "Colima",
        "02": "Baja California",
        "32": "Zacatecas",
        "01": "Aguascalientes",
        "22": "Querétaro",
        "30": "Veracruz de Ignacio de la Llave",
        "20": "Oaxaca",
        "17": "Morelos",
        "18": "Nayarit",
        "07": "Chiapas",
}

def postal_code_view(request, postal_code):
    colonias_info = PostalCode.objects.filter(d_codigo=postal_code)

    # Convertir los códigos de estado a nombres
    for colonia in colonias_info:
        colonia.nombre_estado = C_ESTADO_CHOICES.get(colonia.c_estado, 'Desconocido')

    context = {'colonias_info': colonias_info, 'codigo_postal': postal_code}
    return render(request, 'postal.html', context)

from django.http import JsonResponse
from django_postalcodes_mexico.models import PostalCode

def postal_code_view_test(request, postal_code):
    colonias_info = PostalCode.objects.filter(d_codigo=postal_code)

    # Preparar los datos para la respuesta JSON
    data = {
        'colonias': [
            {
                'd_asenta': colonia.d_asenta,
                'd_tipo_asenta': colonia.d_tipo_asenta,
                'D_mnpio': colonia.D_mnpio,
                'd_estado': colonia.d_estado,
            }
            for colonia in colonias_info
        ]
    }

    return JsonResponse(data)


def pruebacp(request):
    return render(request,"formpostal.html")


class callesList(LoginRequiredMixin, ListView):
    model = Calle
    template_name = 'calles/list_calles.html'
    context_object_name = 'calle'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
   # Estadísticas
        total_calles = Calle.objects.count()
        calles_por_seccion = Calle.objects.values('seccion__nombre').annotate(total=Count('id'))
        calles_con_ruta = Calle.objects.exclude(ruta='').count()
        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))

        context['total_calles'] = total_calles
        context['total_meta_promovidos'] = total_meta_promovidos['meta_promovidos__sum']
        context['calles_por_seccion'] = calles_por_seccion
        context['calles_con_ruta'] = calles_con_ruta

        context['navbar'] = 'seccion'
        context['seccion'] = 'calle'
        return context
    
    def handle_no_permission(self):
        # Redirigir a alguna página de error o inicio si el usuario no cumple el test
        return redirect('templeteDenegado')
    

    
class CalleCreateView(CreateView):
    model = Calle
    form_class = CalleForm
    template_name = 'calles/calle_create.html'
    success_url = reverse_lazy('calle_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'seccion'
        context['seccion'] = 'calle'
        return context

class CalleUpdateView(UpdateView):
    model = Calle
    form_class = CalleForm
    template_name = 'calles/calle_update.html'  # Debes crear este template
    success_url = reverse_lazy('calle_list')  # Asegúrate de que esta URL exista

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'seccion'
        context['seccion'] = 'calle'
        return context

def mostrar_mapa(request, calle_id):
    calle = get_object_or_404(Calle, pk=calle_id)

    context = {
        'calle': calle,
        'navbar': 'seccion',  # Cambia esto según la página activa
        'seccion': 'calle'
    }
    
    return render(request, 'calles/mostrar_mapa.html', context)