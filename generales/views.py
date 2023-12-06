from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from promovido.models import prospecto
from django.http import JsonResponse
from promovido.models import prospecto
from usuarios.models import Seccion
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from configuracion.models import CandidatoConfig
# Create your views here.


def home(request):
    return render(request,'home.html')



def menu(request):
    user = request.user
    special_groups = ['Administrador', 'Coordinador General', 'Candidato']
    is_special_user = user.groups.filter(name__in=special_groups).exists()

    # Si el usuario es especial, verá todos los prospectos; de lo contrario, solo los de sus secciones
    if is_special_user:
        # Usuarios con acceso a todos los prospectos
        prospectos_filtrados = prospecto.objects.all()
    else:
        # Usuarios con acceso limitado a sus secciones asignadas
        user_sections = user.seccion.all()
        prospectos_filtrados = prospecto.objects.filter(seccion__in=user_sections)

    # Contadores ajustados según el usuario y su grupo
    ProspectosPromovidos = prospectos_filtrados.filter(status="Promovido").count()
    TotalProspectos = prospectos_filtrados.filter(status="Prospecto").count()
    TotalSecciones = Seccion.objects.all().count()
    try:
        config = CandidatoConfig.objects.first()
        meta_promovidos = config.meta_promovidos if config else 0
    except CandidatoConfig.DoesNotExist:
        meta_promovidos = 0  # Define un valor por defecto si no hay configuración

    # Calcula el porcentaje de la meta alcanzada
    porcentaje_alcanzado = (ProspectosPromovidos / meta_promovidos * 100) if meta_promovidos else 0
    porcentaje_alcanzado = min(porcentaje_alcanzado, 100)  # Asegura que no exceda el 100%

    context = {
        'prospectos_promovidos': ProspectosPromovidos,
        'total_prospectos': TotalProspectos,
        'total_secciones': TotalSecciones,
        'meta_promovidos': meta_promovidos,
        'porcentaje_alcanzado': porcentaje_alcanzado,  # Añadir esta línea
    }


    return render(request, "menu.html", context)

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