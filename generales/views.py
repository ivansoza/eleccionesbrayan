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
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

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


        # Añadir contadores y otros datos al contexto
        context['prospectos_promovidos'] = prospectos_filtrados.filter(status="Promovido").count()
        context['total_prospectos'] = prospectos_filtrados.count()
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

        context['porcentaje_alcanzado'] = min((context['prospectos_promovidos'] / context['meta_promovidos'] * 100) if context['meta_promovidos'] else 0, 100)
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



def send_sms_view(request):
    # La región debería coincidir con la configuración de tu cuenta SNS
    sns_client = boto3.client('sns', region_name='us-east-1')
    
    # Lista de números en formato E.164
    phone_numbers = ['+522461229984', '+522462087165']  # Agrega los números aquí
    message = 'Hola, feliz cumplaeaños mi estimado Antonio sois, espero que te la pases fantastico!'
    
    # Guardar los resultados de cada intento de envío en un diccionario
    results = {}

    for number in phone_numbers:
        try:
            response = sns_client.publish(
                PhoneNumber=number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'  # O 'Promotional' dependiendo del uso
                    }
                }
            )
            # Guardar el MessageId en el diccionario de resultados
            results[number] = f"Mensaje enviado exitosamente! ID: {response['MessageId']}"
        except NoCredentialsError:
            results[number] = "Error: No se encontraron credenciales de AWS."
        except ClientError as e:
            results[number] = f"Error al enviar mensaje: {e}"

    # Devolver una respuesta JSON con los resultados de cada número
    return JsonResponse(results)