from typing import Any
from .models import Publicidad
from .forms import PublicidadForm
from django.views.generic import CreateView, TemplateView
# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from usuarios.models import Seccion

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
        context['navbar'] = 'publicidad'  # Cambia esto según la página activa
        context['seccion'] = 'ver_publicidad'
        return context

class mapaPublicidad(TemplateView):
    template_name = 'mapaPublicidad.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_actual = self.request.user
        es_administrador = usuario_actual.groups.filter(name='Administrador').exists()

        # Obtener el queryset base
        if es_administrador:
            ubicaciones = Publicidad.objects.all()
        else:
            ubicaciones = Publicidad.objects.filter(usuario=usuario_actual)

        # Aplicar filtros adicionales si existen
        seccion_filtro = self.request.GET.get('seccion')
        tipo_filtro = self.request.GET.get('tipo')
        if seccion_filtro:
            ubicaciones = ubicaciones.filter(seccion_id=seccion_filtro)
        if tipo_filtro:
            ubicaciones = ubicaciones.filter(tipo=tipo_filtro)

        # Contadores de tipos de publicidad
        num_cordi_area = ubicaciones.filter(tipo='Lona').count()
        num_hombres = ubicaciones.filter(tipo='Pared').count()
        num_mujeres = ubicaciones.filter(tipo='Poste').count()
        num_total = ubicaciones.count()

        context.update({
            'num_cordi_area': num_cordi_area,
            'num_hombres': num_hombres,
            'num_mujeres': num_mujeres,
            'num_total': num_total,
            'ubicaciones': ubicaciones,
            'secciones': Seccion.objects.all(),
            'navbar': 'publicidad',
            'seccion': 'ver_publicidad',
        })
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