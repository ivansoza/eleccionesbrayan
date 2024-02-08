from typing import Any
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, ListView, UpdateView
from datetime import datetime, date
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import DetailView
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
from catalogos.models import Calle
from .models import  prospecto, Felicitacion
from .forms import  ProspectoFormNuevo, ProspectoFormNuevoUpdate,PromovidoFormNuevo, felicitacionForms, verificarForms
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages
from usuarios.models import CustomUser
from django.db.models import Count, Case, When, IntegerField
from django.db import models 
from django.db.models import F

from django.db.models import Q 
from usuarios.models import Seccion
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.http import HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model

from django.views.generic.edit import DeleteView



#----------------------- ESTADISTICAS GENERALES--------------------
class estadisticasGenerales(LoginRequiredMixin,UserPassesTestMixin, ListView):
    template_name= 'estadisticas/estadisticasPromovidos.html'
    context_object_name = 'promovidos'
    model = prospecto
    def get_queryset(self):
        # Ajustamos la consulta para usar el related_name 'promovidos_asociados'
        queryset = CustomUser.objects.annotate(
            num_promovidos=Count('promovidos_asociados', filter=Q(promovidos_asociados__status='Promovido')),
            num_prospectos=Count('promovidos_asociados', filter=Q(promovidos_asociados__status='Prospecto')),
            hombres=Count(Case(When(promovidos_asociados__genero='Hombre', then=1), output_field=IntegerField())),
            mujeres=Count(Case(When(promovidos_asociados__genero='Mujer', then=1), output_field=IntegerField()))
        )
        return queryset

    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists()  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajustamos también aquí para la obtención de usuarios destacados
        usuarios_destacados = CustomUser.objects.annotate(
            num_promovidos=Count('promovidos_asociados', filter=Q(promovidos_asociados__status='Promovido')),
            num_prospectos=Count('promovidos_asociados', filter=Q(promovidos_asociados__status='Prospecto'))
        ).order_by(F('num_promovidos') + F('num_prospectos')).reverse()[:3]

        context['usuarios_destacados'] = usuarios_destacados
        context['navbar'] = 'estadisticas'  # Asegúrate de ajustar esto según corresponda
        context['seccion'] = 'esta_general'
        return context
    
    def handle_no_permission(self):
        return redirect('templeteDenegado')
    
#----------------------- FIN ESTADISTICAS GENERALES--------------------


# ------------------------ESTADISTICAS CALLE ----------------

class CalleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Calle
    template_name = 'estadisticas/calles.html'
    context_object_name = 'calles'

    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists() 
    def handle_no_permission(self):
        return redirect('templeteDenegado')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.status = self.request.GET.get('status')
        if self.status:
            queryset = queryset.filter(prospectos__status=self.status).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'estadisticas'
        context['seccion'] = 'calles-list'
        context['status_choices'] = [choice for choice in prospecto.STATUS_CHOICES if choice[0] != 'Rechazado']
        context['total_calles'] = context['calles'].count()
        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        total_prospectos = 0  # Inicializa el conteo total de prospectos

        for calle in context['calles']:
                    if self.status:
                        calle_prospectos = prospecto.objects.filter(calle=calle, status=self.status).count()
                    else:
                        calle_prospectos = prospecto.objects.filter(calle=calle).exclude(status='Rechazado').count()

                    porcentaje = (calle_prospectos / calle.meta_promovidos * 100) if calle.meta_promovidos > 0 else 0
                    calle.progreso = porcentaje
                    calle.prospectos_count = calle_prospectos
                    total_prospectos += calle_prospectos  # Suma al total de prospectos

        context['total_meta_promovidos'] = total_meta_promovidos
        context['total_prospectos'] = total_prospectos  
        context['calles'] = sorted(context['calles'], key=lambda x: x.progreso, reverse=True)
        context['status_actual'] = self.status

        return context
# ------------------------FIN ESTADISTICAS CALLE ----------------

# ---------------- VER DETALLES DE CALLE -----------------

class CalleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Calle
    template_name = 'estadisticas/detalle_calle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'estadisticas'
        context['seccion'] = 'calles-list'
        status = self.kwargs.get('status')

        if status:
            context['prospectos'] = self.object.prospectos.filter(status=status)
        else:
            context['prospectos'] = self.object.prospectos.exclude(status='Rechazado')

        solicitudes_por_tipo = context['prospectos'].values('tipo_solicitud').annotate(total=Count('tipo_solicitud')).order_by('tipo_solicitud')
        # Convertir a JSON
        problematicas_por_tipo = context['prospectos'].values('problema_tipo').annotate(total=Count('problema_tipo')).order_by('problema_tipo')

        context['solicitudes_por_tipo_json'] = json.dumps(list(solicitudes_por_tipo), cls=DjangoJSONEncoder)
        context['problematicas_por_tipo_json'] = json.dumps(list(problematicas_por_tipo), cls=DjangoJSONEncoder)

        total_promovidos = context['prospectos'].count()
        context['total_prospectos'] = total_promovidos
        context['status_actual'] = status or 'Todo'

        total_hombres = context['prospectos'].filter(genero='Hombre').count()
        total_mujeres = context['prospectos'].filter(genero='Mujer').count()
        context['total_hombres'] = total_hombres
        context['total_mujeres'] = total_mujeres
        if total_promovidos > 0:
            context['porcentaje_hombres'] = (total_hombres / total_promovidos) * 100
            context['porcentaje_mujeres'] = (total_mujeres / total_promovidos) * 100
        else:
            context['porcentaje_hombres'] = 0
            context['porcentaje_mujeres'] = 0
        meta_promovidos_calle = self.object.meta_promovidos
        context['porcentaje_promovidos_calle'] = (total_promovidos / meta_promovidos_calle * 100) if meta_promovidos_calle else 0
        context['meta_calle'] = meta_promovidos_calle

        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        context['total_meta_promovidos'] = total_meta_promovidos

        context['porcentaje_promovidos_todas_calles'] = (total_promovidos / total_meta_promovidos * 100) if total_meta_promovidos else 0
        return context

    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists() 
    def handle_no_permission(self):
        return redirect('templeteDenegado')
# ---------------- FIN DETALLES DE CALLE -----------------

# ---------------- VER LISTA DE SECCION  -----------------

class SeccionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Seccion
    template_name = 'estadisticas/secciones.html'  # Especifica la ubicación de tu template
    context_object_name = 'secciones'  # Opcional: este es el nombre del contexto en el template
    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists() 
    def handle_no_permission(self):
        return redirect('templeteDenegado')
    def get_queryset(self):
        queryset = super().get_queryset()
        self.status = self.request.GET.get('status')
        if self.status:
            queryset = queryset.filter(calles_catalogos__prospectos__status=self.status).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'estadisticas'
        context['seccion'] = 'seccion-list'
        context['status_choices'] = [choice for choice in prospecto.STATUS_CHOICES if choice[0] != 'Rechazado']

        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        context['total_meta_promovidos'] = total_meta_promovidos
        context['total_secciones'] = Seccion.objects.count()

        if self.status:
            total_prospectos_filtrados = prospecto.objects.filter(status=self.status).count()
            context['total_prospectos_filtrados'] = total_prospectos_filtrados
        else:
            total_prospectos_no_rechazados = prospecto.objects.exclude(status='Rechazado').count()
            context['total_prospectos_no_rechazados'] = total_prospectos_no_rechazados
            
        secciones_con_progreso = []

        for seccion in self.get_queryset():
            meta_total = seccion.calles_catalogos.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
            if self.status:
                prospectos_total = prospecto.objects.filter(calle__seccion=seccion, status=self.status).count()
            else:
                prospectos_total = prospecto.objects.filter(calle__seccion=seccion).exclude(status='Rechazado').count()
            porcentaje_progreso = (prospectos_total / meta_total * 100) if meta_total > 0 else 0

            secciones_con_progreso.append({
                'seccion': seccion,
                'meta_total': meta_total,
                'prospectos_total': prospectos_total,
                'porcentaje_progreso': porcentaje_progreso
            })

        context['secciones_con_progreso'] = secciones_con_progreso
        context['status_actual'] = self.status

        return context
# ---------------- FIN LISTA DE SECCION  -----------------

# ---------------- detalles   DE SECCION  -----------------


class SeccionDetailView(LoginRequiredMixin,  DetailView):

    model = Seccion
    template_name = 'estadisticas/detalle_seccion.html'
    context_object_name = 'secciones' 



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'estadisticas'
        context['seccion'] = 'seccion-list'

        status = self.kwargs.get('status')
        if status:
            context['prospectos'] = prospecto.objects.filter(calle__seccion=self.object, status=status)
        else:
            context['prospectos'] = prospecto.objects.filter(calle__seccion=self.object).exclude(status='Rechazado')
        meta_promovidos_seccion = self.object.calles_catalogos.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        context['meta_seccion'] = meta_promovidos_seccion
        total_promovidos = context['prospectos'].count()

        if meta_promovidos_seccion > 0:
            context['porcentaje_promovidos_seccion'] = (total_promovidos / meta_promovidos_seccion) * 100
        else:
            context['porcentaje_promovidos_seccion'] = 0

        solicitudes_por_tipo = context['prospectos'].values('tipo_solicitud').annotate(total=Count('tipo_solicitud')).order_by('tipo_solicitud')
        problematicas_por_tipo = context['prospectos'].values('problema_tipo').annotate(total=Count('problema_tipo')).order_by('problema_tipo')
        context['solicitudes_por_tipo_json'] = json.dumps(list(solicitudes_por_tipo), cls=DjangoJSONEncoder)
        context['problematicas_por_tipo_json'] = json.dumps(list(problematicas_por_tipo), cls=DjangoJSONEncoder)

        context['status_actual'] = status or 'Todo'
        context['total_prospectos'] = total_promovidos


        total_hombres = context['prospectos'].filter(genero='Hombre').count()
        total_mujeres = context['prospectos'].filter(genero='Mujer').count()

        context['total_hombres'] = total_hombres
        context['total_mujeres'] = total_mujeres
        
        if total_promovidos > 0:
            context['porcentaje_hombres'] = (total_hombres / total_promovidos) * 100
            context['porcentaje_mujeres'] = (total_mujeres / total_promovidos) * 100
        else:
            context['porcentaje_hombres'] = 0
            context['porcentaje_mujeres'] = 0

        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        context['total_meta_promovidos'] = total_meta_promovidos
        context['porcentaje_promovidos_todas_seccion'] = (total_promovidos / total_meta_promovidos * 100) if total_meta_promovidos else 0

        return context

# ---------------- FIN  DE SECCION  -----------------



class EstadisticasGeneralesView(TemplateView):
    template_name = 'estadisticas/estadisticasUsuario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos el ID del usuario desde los parámetros de la URL
        usuario_id = self.kwargs.get('pk')
        usuario = CustomUser.objects.get(id=usuario_id)
        nombre = usuario.first_name + " " + usuario.last_name

        # Consulta para obtener la cantidad de Promovidos y Prospectos del usuario específico
        promovidos_usuario = prospecto.objects.filter(
            usuario_promovido=usuario,
            status='Promovido'
        ).count()
        prospectos_usuario = prospecto.objects.filter(
            usuario_promovido=usuario,
            status='Prospecto'
        ).count()

        # Consulta para obtener la cantidad de Hombres y Mujeres del usuario específico
        hombres_usuario = prospecto.objects.filter(
            usuario_promovido=usuario,
            genero='Hombre'
        ).count()

        mujeres_usuario = prospecto.objects.filter(
            usuario_promovido=usuario,
            genero='Mujer'
        ).count()

        context['num_promovidos'] = promovidos_usuario
        context['num_prospectos'] = prospectos_usuario
        context['num_hombres'] = hombres_usuario
        context['num_mujeres'] = mujeres_usuario
        context['nombre'] = nombre
        context['navbar'] = 'estadisticas'  # Cambia esto según la página activa
        context['seccion'] = 'esta_general'
        return context

class EstadisticasSoliView(TemplateView):
    template_name = 'estadisticas/barrasSolicitud.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Consulta para contar la frecuencia de tipo_solicitud
        tipo_solicitud_data = prospecto.objects.values('tipo_solicitud').annotate(count=Count('tipo_solicitud'))

        # Consulta para contar la frecuencia de problema_tipo
        problema_tipo_data = prospecto.objects.values('problema_tipo').annotate(count=Count('problema_tipo'))

        context['tipo_solicitud_data'] = tipo_solicitud_data
        context['problema_tipo_data'] = problema_tipo_data
        context['navbar'] = 'estadisticas'  # Cambia esto según la página activa
        context['seccion'] = 'esta_soli'
        return context
    


# CREACION DE PROSPECTO NUEVO 
class CreateProspectoNuevo(LoginRequiredMixin,CreateView):
    template_name = 'prospecto/crearProspecto.html'
    form_class = ProspectoFormNuevo
    model = prospecto

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.status = 'Prospecto'
        return super(CreateProspectoNuevo, self).form_valid(form)
    def get_success_url(self):
        messages.success(self.request, 'Prospecto creado con éxito.')
        return reverse('lista_prospectos')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'
        context['seccion'] = 'ver_prospectos'
        return context
# FIN CREACION DE PROSPECTO NUEVO 


# LISTA DE PROSPECTO NUEVO 

class ListaProspectosNuevo(LoginRequiredMixin,ListView):
    template_name = 'prospecto/listaProspectos.html'
    context_object_name = 'prospectos'
    model = prospecto

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            # Usuarios con roles especiales, muestran todos los prospectos con status 'Promovido'
            return prospecto.objects.filter(status='Prospecto')
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            # Usuarios Coordinadores de Área y Sección, filtran por sección a través de la calle
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(calle__seccion__in=secciones_usuario, status='Prospecto')
        elif user.groups.filter(name='Promotor').exists():
            # Usuarios Promotores, filtran por los usuarios que han agregado
            return prospecto.objects.filter(usuario=user, status='Prospecto')
        else:
            # Para otros usuarios, puedes definir un comportamiento por defecto
            return prospecto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['contador_global'] = queryset.count()       
        context['navbar'] = 'promovidos'
        context['seccion'] = 'ver_prospectos'
        return context
# FIN  DE PROSPECTO NUEVO 

   
# LISTA DE ACTUALIZACION NUEVO 

class ProspectoUpdateView(LoginRequiredMixin,UpdateView):
    model = prospecto
    form_class = ProspectoFormNuevoUpdate
    template_name = 'prospecto/updateProspecto.html'  # Asegúrate de tener este template
    success_url = reverse_lazy('lista_prospectos')  # Cambia esto por tu URL

    def form_valid(self, form):
        # Asigna el usuario actual a usuario_promovido
        form.instance.usuario_promovido = self.request.user
        # Cambia el status a 'Promovido'
        form.instance.status = 'Promovido'
        form.instance.fecha_promovido = timezone.now()

        messages.success(self.request, 'Promovido con éxito.')

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        calles = Calle.objects.select_related('seccion').all()

        context['secciones_coords'] = {
            calle.id: {'lat': calle.seccion.latitud, 'lng': calle.seccion.longitud, 'ruta': calle.ruta}
            for calle in calles if calle.seccion
        }        
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_prospectos'  # Cambia esto según la página activa
        return context
    # FIN DE ACTUALIZACION NUEVO 


# LISTA DE PROMOVIDOS NUEVO 

class ListaPromovidosNuevo(LoginRequiredMixin, ListView):
    template_name='prospecto/listaPromovidos.html'
    context_object_name = 'promovidos'
    model = prospecto
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            # Usuarios con roles especiales, muestran todos los prospectos con status 'Promovido'
            return prospecto.objects.filter(status='Promovido')
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            # Usuarios Coordinadores de Área y Sección, filtran por sección a través de la calle
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(calle__seccion__in=secciones_usuario, status='Promovido')
        elif user.groups.filter(name='Promotor').exists():
            # Usuarios Promotores, filtran por los usuarios que han agregado
            return prospecto.objects.filter(usuario=user, status='Promovido')
        else:
            # Para otros usuarios, puedes definir un comportamiento por defecto
            return prospecto.objects.none()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['contador_global'] = queryset.count()
        context['navbar'] = 'promovidos'  
        context['seccion'] = 'ver_promovidos' 
        return context

# FIN  DE PROMOVIDOS NUEVO 
    

# INICIO DE VOTO SEGURO
class ListaVotoSeguro(LoginRequiredMixin, ListView):
    template_name='votoduro/listaVotoSeguro.html'
    context_object_name = 'promovidos'
    model = prospecto
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            return prospecto.objects.filter(status='Promovido', votoSeguro=True)
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(calle__seccion__in=secciones_usuario, status='Promovido')
        elif user.groups.filter(name='Promotor').exists():
            return prospecto.objects.filter(Q(usuario=user) | Q(usuario_promovido=user), status='Promovido', votoSeguro=True)
        else:
            return prospecto.objects.none()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['contador_global'] = queryset.count()
        context['navbar'] = 'promovidos'  
        context['seccion'] = 'ver_votos_seguro' 
        return context

#FIN DE VOTO SEGURO


class MapaProspectosPromovidosView(LoginRequiredMixin,ListView):
    template_name = 'mapa/mapaPromovidos.html'
    context_object_name = 'prospectos'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset = prospecto.objects.filter(status='Promovido')
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            queryset = prospecto.objects.filter(calle__seccion__in=secciones_usuario, status='Promovido')
        elif user.groups.filter(name='Promotor').exists():
            queryset = prospecto.objects.filter(usuario=user, status='Promovido')
        else:
            return prospecto.objects.none()

        # Aplica filtros adicionales si están presentes
        calle_filtro = self.request.GET.get('calle')
        genero_filtro = self.request.GET.get('genero')

        if calle_filtro:
            queryset = queryset.filter(calle_id=calle_filtro)
        if genero_filtro:
            queryset = queryset.filter(genero=genero_filtro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            calles = Calle.objects.all()
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            calles = Calle.objects.filter(seccion__in=secciones_usuario)
        elif user.groups.filter(name='Promotor').exists():
            # Si un Promotor solo debería ver las calles relacionadas con los prospectos que ha agregado, ajusta esta consulta
            calles = Calle.objects.filter(prospectos__usuario=user).distinct()
        else:
            calles = Calle.objects.none()

        context['navbar'] = 'mapa'
        context['seccion'] = 'mapa_promo'
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['calles'] = calles
        context['contador_global'] = queryset.count()
        return context
    
class MapaVotosSegurosView(LoginRequiredMixin,ListView):
    template_name = 'mapa/mapaVotosSeguros.html'
    context_object_name = 'prospectos'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset = prospecto.objects.filter(votoSeguro=True)
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            queryset = prospecto.objects.filter(calle__seccion__in=secciones_usuario, votoSeguro=True)
        elif user.groups.filter(name='Promotor').exists():
            queryset = prospecto.objects.filter(usuario=user, votoSeguro=True)
        else:
            return prospecto.objects.none()

        # Aplica filtros adicionales si están presentes
        calle_filtro = self.request.GET.get('calle')
        genero_filtro = self.request.GET.get('genero')

        if calle_filtro:
            queryset = queryset.filter(calle_id=calle_filtro)
        if genero_filtro:
            queryset = queryset.filter(genero=genero_filtro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            calles = Calle.objects.all()
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            calles = Calle.objects.filter(seccion__in=secciones_usuario)
        elif user.groups.filter(name='Promotor').exists():
            # Si un Promotor solo debería ver las calles relacionadas con los prospectos que ha agregado, ajusta esta consulta
            calles = Calle.objects.filter(prospectos__usuario=user).distinct()
        else:
            calles = Calle.objects.none()

        context['navbar'] = 'mapa'
        context['seccion'] = 'mapa_segu'
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['calles'] = calles
        context['contador_global'] = queryset.count()
        return context
    

class MapaVerificadosView(LoginRequiredMixin,ListView):
    template_name = 'mapa/mapaVerificados.html'
    context_object_name = 'prospectos'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset = prospecto.objects.filter(status='Verificado')
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            queryset = prospecto.objects.filter(calle__seccion__in=secciones_usuario, status='Verificado')
        elif user.groups.filter(name='Promotor').exists():
            queryset = prospecto.objects.filter(usuario=user, status='Verificado')
        else:
            return prospecto.objects.none()

        # Aplica filtros adicionales si están presentes
        calle_filtro = self.request.GET.get('calle')
        genero_filtro = self.request.GET.get('genero')

        if calle_filtro:
            queryset = queryset.filter(calle_id=calle_filtro)
        if genero_filtro:
            queryset = queryset.filter(genero=genero_filtro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            calles = Calle.objects.all()
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            calles = Calle.objects.filter(seccion__in=secciones_usuario)
        elif user.groups.filter(name='Promotor').exists():
            # Si un Promotor solo debería ver las calles relacionadas con los prospectos que ha agregado, ajusta esta consulta
            calles = Calle.objects.filter(prospectos__usuario=user).distinct()
        else:
            calles = Calle.objects.none()

        context['navbar'] = 'mapa'
        context['seccion'] = 'mapa_verifi'
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['calles'] = calles
        context['contador_global'] = queryset.count()
        return context

class CreatePromovidoNuevo(LoginRequiredMixin,CreateView):
    template_name = 'prospecto/crearPromovido.html'
    form_class = PromovidoFormNuevo
    model = prospecto
    
    def form_valid(self, form):
        # Intenta guardar el formulario
        form.instance.usuario = self.request.user
        form.instance.usuario_promovido = self.request.user
        form.instance.status = 'Promovido'
        form.instance.fecha_promovido = timezone.now()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Aquí puedes manejar el caso de formulario no válido
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Promovido creado con éxito.')
        return reverse('lista_promovidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        calles = Calle.objects.select_related('seccion').all()

        context['secciones_coords'] = {
            calle.id: {'lat': calle.seccion.latitud, 'lng': calle.seccion.longitud, 'ruta': calle.ruta}
            for calle in calles if calle.seccion
        }        
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_promovidos' 
        return context
    

class UpdatePromovidoNuevo(LoginRequiredMixin, UpdateView):
    template_name = 'prospecto/crearPromovido.html'
    form_class = PromovidoFormNuevo
    model = prospecto  # Asegúrate de que el nombre del modelo esté correctamente capitalizado

    def form_invalid(self, form):
        # Maneja el caso de formulario no válido
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Promovido actualizado con éxito.')
        return reverse('lista_promovidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Asume que Calle y las relaciones están definidas similar a la CreateView
        calles = Calle.objects.select_related('seccion').all()
        context['secciones_coords'] = {
            calle.id: {'lat': calle.seccion.latitud, 'lng': calle.seccion.longitud, 'ruta': calle.ruta}
            for calle in calles if calle.seccion
        }
        context['navbar'] = 'promovidos'  # Esto se mantiene igual
        context['seccion'] = 'ver_promovidos'  # Esto también se mantiene igual
        return context
    
class EliminarPromovido(LoginRequiredMixin, DeleteView):
    model = prospecto
    template_name = 'modals/confirmar_eliminacion.html'
    def get_success_url(self):
        extranjero_id = self.object.id  # Obtén el ID del extranjero del objeto biometrico
        extranjero = prospecto.objects.get(id=extranjero_id)
        messages.success(self.request, 'Promovido Eliminado con Éxito.')
        return reverse_lazy('lista_promovidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        promovido_id = self.kwargs.get('pk')  # Cambia 'extranjero_id' a 'pk'
        promovido = prospecto.objects.get(id=promovido_id)


        return context

@csrf_exempt
def verificar_numero_ine(request):
    if request.method == 'POST':
        numero_ine = request.POST.get('numeroINE', '')

        # Verifica si ya existe un registro con el número de INE
        existe = prospecto.objects.filter(numeroINE=numero_ine).exists()

        return JsonResponse({'existe': existe})

    return JsonResponse({'existe': False})


class ListCumple(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'estadisticas/cumple.html'
    model = prospecto
    context_object_name = 'promovidos'

    def test_func(self):
        return self.request.user.groups.filter(
                    Q(name='Administrador') |
                    Q(name='Candidato') |
                    Q(name='Coordinador General') 
                ).exists()  
   
    def get_queryset(self):
        today = datetime.now().date()
        estado_defensoria = self.request.GET.get('estado_defensoria', None)

        if estado_defensoria == 'ya_notificado':
            # Filtra a los que ya han sido felicitados este mes
            start_of_month = today.replace(day=1)
            end_of_month = today.replace(day=28) + relativedelta(days=4)
            end_of_month = end_of_month - relativedelta(days=end_of_month.day - 1)
            felicitados_este_mes = Felicitacion.objects.filter(
                felicitado=True,
                fecha_felicitacion__range=(start_of_month, end_of_month)
            ).select_related('prospecto')

            # Agregar la edad y el estado de felicitación a cada prospecto en felicitaciones
            for felicitacion in felicitados_este_mes:
                cumpleanos = felicitacion.prospecto.fechaNacimiento.replace(year=today.year)
                edad = today.year - felicitacion.prospecto.fechaNacimiento.year - ((today.month, today.day) < (felicitacion.prospecto.fechaNacimiento.month, felicitacion.prospecto.fechaNacimiento.day))
                setattr(felicitacion.prospecto, 'edad', edad)
                setattr(felicitacion.prospecto, 'ya_felicitado', True)

            return felicitados_este_mes
        else:
                queryset = prospecto.objects.all()

                promovidos_cumplen_hoy = []
                promovidos_cumplen_proximamente = []

                for promovido in queryset:
                    cumpleanos = promovido.fechaNacimiento.replace(year=today.year)
                    edad = today.year - promovido.fechaNacimiento.year - ((today.month, today.day) < (promovido.fechaNacimiento.month, promovido.fechaNacimiento.day))
                    dias_restantes = (cumpleanos - today).days

                    setattr(promovido, 'edad', edad)
                    setattr(promovido, 'dias_restantes_cumple', dias_restantes)

                    if dias_restantes == 0:
                        promovidos_cumplen_hoy.append(promovido)
                    elif cumpleanos > today:
                        promovidos_cumplen_proximamente.append(promovido)

                return {
                    'cumplen_hoy': sorted(promovidos_cumplen_hoy, key=lambda x: x.apellido_paterno),
                    'cumplen_proximamente': sorted(promovidos_cumplen_proximamente, key=lambda x: x.dias_restantes_cumple)
                }
        
    def handle_no_permission(self):
        return redirect('templeteDenegado')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        estado_defensoria = self.request.GET.get('estado_defensoria', None)

        today = datetime.now().date()
        mes_actual = today.month
        anio_actual = today.year

        # Calcular y agregar el total de promovidos que cumplen años hoy y en este mes
        total_cumplen_hoy = sum(
            promovido.fechaNacimiento.replace(year=anio_actual) == today
            for promovido in prospecto.objects.all()
        )
        total_cumplen_este_mes = sum(
            promovido.fechaNacimiento.month == mes_actual
            for promovido in prospecto.objects.all()
        )

        context['total_cumplen_hoy'] = total_cumplen_hoy
        context['total_cumplen_este_mes'] = total_cumplen_este_mes

        if estado_defensoria == 'ya_notificado':
            context['felicitaciones_este_mes'] = self.get_queryset()
        else:
            context['promovidos_cumplen_hoy'] = queryset.get('cumplen_hoy', [])
            context['promovidos_cumplen_proximamente'] = queryset.get('cumplen_proximamente', [])

        # Agregar ya_felicitados_ids y el resto del contexto necesario
        ya_felicitados_ids = Felicitacion.objects.filter(
            felicitado=True,
            fecha_felicitacion__year=anio_actual
        ).values_list('prospecto', flat=True)
        context['ya_felicitados_ids'] = ya_felicitados_ids

        context['navbar'] = 'estadisticas'
        context['seccion'] = 'cumple'

        return context


    
class Felicitar(CreateView):
    template_name='estadisticas/modalFelicitacion.html'
    model = Felicitacion
    form_class = felicitacionForms
    def get_success_url(self):
        messages.success(self.request, 'Felicitación exitosamente')

        return reverse_lazy('lista-cumple')
    def get_initial(self):
        initial = super().get_initial()
        usuario = self.request.user
        initial['usuario']=usuario
        prospecto_id = self.kwargs.get('pk')
        prospetos= prospecto.objects.get(pk=prospecto_id)
        initial['prospecto']=prospetos
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prospecto_id = self.kwargs.get('pk')
        prospetos= prospecto.objects.get(pk=prospecto_id)
        context['prospecto']=prospetos
      
        return context

def obtener_calles(request):
    seccion_id = request.GET.get('seccion')
    print(f"Sección ID recibida: {seccion_id}")

    calles = Calle.objects.filter(seccion_id=seccion_id).values('pk', 'nombre')
    calles_list = list(calles)
    print(f"Calles encontradas: {calles_list}")

    return JsonResponse({'calles': calles_list})


class PromovidosLista(ListView):
    template_name = 'verificar/listaPromovidos.html'
    context_object_name = 'prospectos'
    model = prospecto

    def get_queryset(self):
        today = datetime.now().date()
        user = self.request.user
        estado_promovidos = self.request.GET.get('estado_promovidos', 'promovidos')

        # Determinar el estado de los prospectos a filtrar
        if estado_promovidos == 'verificados':
            estado_filtro = 'Verificado'
        elif estado_promovidos == 'rechazados':
            estado_filtro = 'Rechazado'
        else:
            estado_filtro = 'Promovido'

        # Filtrar los prospectos según el grupo y el estado
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset = prospecto.objects.filter(status=estado_filtro)
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            queryset = prospecto.objects.filter(calle__seccion__in=secciones_usuario, status=estado_filtro)
        elif user.groups.filter(name='Promotor').exists():
            queryset = prospecto.objects.filter(usuario=user, status=estado_filtro)
        else:
            queryset = prospecto.objects.none()

        # Calcular la edad para cada promovido
        for promovido in queryset:
            edad = today.year - promovido.fechaNacimiento.year - (
                (today.month, today.day) < (promovido.fechaNacimiento.month, promovido.fechaNacimiento.day)
            )
            setattr(promovido, 'edad', edad)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determinar qué prospectos contar según el grupo del usuario
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            queryset = prospecto.objects.all()
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            queryset = prospecto.objects.filter(calle__seccion__in=secciones_usuario)
        elif user.groups.filter(name='Promotor').exists():
            queryset = prospecto.objects.filter(usuario=user)
        else:
            queryset = prospecto.objects.none()

        # Contar el número de prospectos por estado
        context['num_promovidos'] = queryset.filter(status='Promovido').count()
        context['num_verificados'] = queryset.filter(status='Verificado').count()
        context['num_rechazados'] = queryset.filter(status='Rechazado').count()
        context['navbar'] = 'promovidos'
        context['seccion'] = 'veri_promovidos'

        return context

class verificarPromovidos(UpdateView):
    template_name ='verificar/verificarPromovido.html'
    model = prospecto
    form_class = verificarForms
    def get_success_url(self):
        messages.success(self.request, 'Verificación exitosa.')
        return reverse('lista-promovidos-verificar')

    def get_initial(self):
        initial = super().get_initial()
        usuario = self.request.user
        initial['usuario_verificador']=usuario
        initial['status']='Verificado'
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prospecto_id = self.kwargs.get('pk')
        prospetos= prospecto.objects.get(pk=prospecto_id)
        context['prospecto']=prospetos
        context['navbar'] = 'promovidos'  
        context['seccion'] = 'veri_promovidos'
        return context

class votosSeguros(TemplateView):
    template_name = 'estadisticas/votoSeguro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtiene la cantidad de registros con votoSeguro=True
        votos_seguros_count = prospecto.objects.filter(votoSeguro=True).count()
        tipos_status = ['Promovido', 'Verificado']
        promovidos = prospecto.objects.filter(status__in=tipos_status).count
        context['votos_seguros_count'] = votos_seguros_count
        context['promovidos_count'] = promovidos
        porcentaje_progreso = (votos_seguros_count / promovidos() * 100) if promovidos() > 0 else 0
        context['porcentaje_votos_seguros'] = porcentaje_progreso
        context['navbar'] = 'estadisticas'  
        context['seccion'] = 'voto'

        return context
    