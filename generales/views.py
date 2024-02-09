from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from catalogos.models import Calle
from promovido.models import prospecto
from django.http import JsonResponse
from promovido.models import prospecto
from usuarios.models import Seccion
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from configuracion.models import CandidatoConfig
# Create your views here.
from django.http import HttpResponse
from django.db.models import Sum

def home(request):
    return render(request,'home.html')



class MenuView(LoginRequiredMixin, ListView):
    template_name = "menu.html"
    context_object_name = 'prospectos'
    model = prospecto  # Asegúrate de que 'prospecto' es el nombre correcto del modelo

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            return prospecto.objects.all()
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(calle__seccion__in=secciones_usuario)
        elif user.groups.filter(name='Promotor').exists():
            return prospecto.objects.filter(usuario=user)
        else:
            return prospecto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        prospectos_filtrados = self.get_queryset()

        context['total_prospectos_no_verificado'] = prospectos_filtrados.exclude(status="Rechazado").count()

        # Añadir contadores y otros datos al contexto
        context['prospectos_promovidos'] = prospectos_filtrados.filter(status="Promovido").count()
        context['total_prospectos'] = prospectos_filtrados.filter(status="Prospecto").count()
        context['total_prospectos_verificado'] = prospectos_filtrados.filter(status="Verificado").count()
        context['total_prospectos_seguros'] = prospectos_filtrados.filter(votoSeguro=True).count()

        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            # Contar todas las secciones y calles para usuarios con acceso especial
            context['total_secciones'] = Seccion.objects.all().count()
            context['total_calles'] = Calle.objects.all().count()
        else:
            # Contar solo las secciones y calles relacionadas con el usuario para otros grupos
            secciones_usuario = user.seccion.all()
            context['total_secciones'] = secciones_usuario.count()
            context['total_calles'] = Calle.objects.filter(seccion__in=secciones_usuario).count()

        try:
            config = CandidatoConfig.objects.first()
            context['meta_promovidos'] = config.meta_promovidos if config else 0
        except CandidatoConfig.DoesNotExist:
            context['meta_promovidos'] = 0
            
        total_meta_promovidos = Calle.objects.aggregate(Sum('meta_promovidos'))['meta_promovidos__sum'] or 0
        context['total_meta_promovidos'] = total_meta_promovidos
        context['porcentaje_alcanzado'] = (context['prospectos_promovidos'] / total_meta_promovidos * 100) if total_meta_promovidos else 0
        context['porcentaje_alcanzado'] = min(context['porcentaje_alcanzado'], 100)  # Asegurar que no exceda el 100%
        context['porcentaje_total'] = (context['total_prospectos_no_verificado'] / total_meta_promovidos * 100) if total_meta_promovidos else 0
        context['porcentaje_total'] = min(context['porcentaje_total'], 100)  # Asegurar que no exceda el 100%
        
        context['porcentaje_prospecto'] = (context['total_prospectos'] / total_meta_promovidos * 100) if total_meta_promovidos else 0
        context['porcentaje_prospecto'] = min(context['porcentaje_prospecto'], 100)  # Asegurar que no exceda el 100%

        context['porcentaje_verificado'] = (context['total_prospectos_verificado'] / total_meta_promovidos * 100) if total_meta_promovidos else 0
        context['porcentaje_verificado'] = min(context['porcentaje_verificado'], 100)  # Asegurar que no exceda el 100%

        context['porcentaje_seguro'] = (context['total_prospectos_seguros'] / total_meta_promovidos * 100) if total_meta_promovidos else 0
        context['porcentaje_seguro'] = min(context['porcentaje_seguro'], 100)  # Asegurar que no exceda el 100%

        context['navbar'] = "home"

        return context

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('menu')  # Redirige al menú si el usuario ya está autenticado
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('menu')  # Asegúrate de que 'menu' es el nombre de tu URL para el menú

    def form_invalid(self, form):
        mostrarAlerta = True
        # Asegúrate de que siempre devuelve una respuesta renderizada
        return render(self.request, self.template_name, {'form': form, 'mostrarAlerta': mostrarAlerta})

class BuscadorView(TemplateView):
    template_name = 'buscador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'buscador'
        context['seccion'] = 'buscador'
        return context



class ListaTodos(LoginRequiredMixin,ListView):
    template_name = 'buscador.html'
    context_object_name = 'prospectos'
    model = prospecto

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            # Usuarios con roles especiales, muestran todos los prospectos con status 'Promovido'
            return prospecto.objects.exclude(status='Rechazado')
        elif user.groups.filter(name__in=['Coordinador de Area', 'Coordinador Sección']).exists():
            # Usuarios Coordinadores de Área y Sección, filtran por sección a través de la calle
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(calle__seccion__in=secciones_usuario).exclude(status='Rechazado')
        elif user.groups.filter(name='Promotor').exists():
            # Usuarios Promotores, filtran por los usuarios que han agregado
            return prospecto.objects.filter(usuario=user).exclude(status='Rechazado')
        else:
            # Para otros usuarios, puedes definir un comportamiento por defecto
            return prospecto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['prospectos_promovidos'] = queryset.filter(status="Promovido").count()
        context['total_prospectos_verificado'] = queryset.filter(status="Verificado").count()
        context['total_prospectos'] = queryset.filter(status="Prospecto").count()

        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['contador_global'] = queryset.count()       
        context['navbar'] = 'buscador'
        context['seccion'] = 'buscador'
        return context
    



def exit(request):
    logout(request)
    return redirect('home')

class templeteDenegado(TemplateView):
    template_name = 'denied.html'



#mapa individual
# def datos_promovidos(request):
#     promovidos_usuario = Promovido.objects.filter(usuario=request.user)
#     ubicaciones = Ubicacion.objects.filter(promovido__in=promovidos_usuario).select_related('promovido')

#     data = list(ubicaciones.values('latitud', 'longitud', 'promovido__nombre', 'promovido__apellido_paterno', 'promovido__apellido_materno', 'promovido__foto_promovido'))
#     return JsonResponse(data, safe=False)

@login_required
def datos_promovidos(request):
    # Identificar al usuario y verificar sus grupos
    user = request.user
    special_groups = ['Administrador', 'Coordinador General', 'Candidato']
    is_special_user = user.groups.filter(name__in=special_groups).exists()

    # Filtrar los prospectos según el usuario
    if is_special_user:
        # Usuarios con acceso a todos los promovidos
        prospectos_promovidos = prospecto.objects.filter(status='Promovido')
    else:
        # Usuarios con acceso limitado a sus secciones asignadas
        user_sections = user.seccion.all()
        prospectos_promovidos = prospecto.objects.filter(seccion__in=user_sections, status='Promovido')

    # Preparar los datos para la respuesta JSON
    data = []
    for p in prospectos_promovidos:
        item = {
            'latitud': p.latitud,
            'longitud': p.longitud,
            'nombre': p.nombre,
            'apellido_paterno': p.apellido_paterno,
            'apellido_materno': p.apellido_materno,
            'foto_promovido': request.build_absolute_uri(p.foto_promovido.url) if p.foto_promovido else None
        }
        data.append(item)

    return JsonResponse(data, safe=False)

@login_required
def ubicacion_primera_seccion(request):
    user = request.user
    special_groups = ['Administrador', 'Coordinador General', 'Candidato']
    is_special_user = user.groups.filter(name__in=special_groups).exists()

    # Si el usuario no es especial, obtener la primera sección
    if not is_special_user:
        primera_seccion = user.seccion.first()
        if primera_seccion:
            data = {
                'latitud': primera_seccion.latitud,
                'longitud': primera_seccion.longitud,
                'zoom': 15  # Un zoom más grande, por ejemplo 15
            }
            return JsonResponse(data)
    
    return JsonResponse({'error': 'No sección disponible'}, status=404)



