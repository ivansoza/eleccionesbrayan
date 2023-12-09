from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, ListView, UpdateView

from catalogos.models import Calle
from .models import Promovido, Ubicacion, prospecto
from .forms import PromovidoForm, ProspectoForm, ProspectoFormNuevo, ProspectoFormNuevoUpdate,PromovidoFormNuevo
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

from django.views.decorators.csrf import csrf_exempt

class createPromovido(CreateView):
    template_name='crearPromovido.html'
    form_class= PromovidoForm
    model= Promovido
    def get_success_url(self):
        # Obtén el ID del promovido recién creado
        promovido_id = self.object.id
        messages.success(self.request, 'Promovido creado con éxito.')
        success_url = reverse('crearUbicacionPro', kwargs={'promovido_id': promovido_id})
        return success_url
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            usuario_data = self.request.user  # El usuario logeado
            initial['usuario'] = usuario_data.pk
            initial['status']='Promovido'

            # Agrega más campos según sea necesario
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_promovidos'  # Cambia esto según la página activa
        return context
class createProspecto(CreateView):
    template_name='crearProspecto.html'
    form_class=ProspectoForm
    model=Promovido
    def get_success_url(self):
        messages.success(self.request, 'Prospecto creado con éxito.')

        success_url = reverse('lista_prospectos')
        return success_url
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            usuario_data = self.request.user  # El usuario logeado
            initial['usuario'] = usuario_data.pk
            initial['status']='Prospecto'
            # Agrega más campos según sea necesario
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_prospectos'  # Cambia esto según la página activa
        return context
class updateProspecto(UpdateView):
    template_name='promoverProspecto.html'
    form_class= PromovidoForm
    model= Promovido
    def get_success_url(self):
        messages.success(self.request, 'Promovido creado con éxito.')
        promovido_id = self.object.id
        # Genera la URL de la vista 'crearUbicacionPro' con el ID como argumento
        success_url = reverse('crearUbicacionPro', kwargs={'promovido_id': promovido_id})
        return success_url
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Convierte la fecha de nacimiento a un formato aceptado por el widget DateInput
        form.fields['fechaNacimiento'].widget.format = '%Y-%m-%d'
        return form
    def get_initial(self):
        initial = super().get_initial()
       
        initial['status']='Promovido'

            # Agrega más campos según sea necesario
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_prospectos'  # Cambia esto según la página activa
        return context

class ListaPromovidos(ListView):
    template_name='listaPromovidos.html'
    context_object_name = 'promovidos'
    model = Promovido
    def get_queryset(self):
        return Promovido.objects.filter(usuario=self.request.user, status='Promovido')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()

        # Contador global de todos los promovidos
        context['contador_global'] = queryset.count()
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_promovidos'  # Cambia esto según la página activa
        return context

class ListaProspectos(ListView):
    template_name='listaProspectos.html'
    context_object_name = 'promovidos'
    model = Promovido
    def get_queryset(self):

        return Promovido.objects.filter(usuario=self.request.user, status='Prospecto')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()

        # Contador global de todos los promovidos
        context['contador_global'] = queryset.count()       
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_prospectos'  # Cambia esto según la página activa
        return context

   
class createUbicacion(TemplateView):
    template_name='crearUbicacion.html'
    def get_initial(self):
        initial = super().get_initial()
        promovido_id = self.kwargs['promovido_id']
        pro = Promovido.objects.get(id=promovido_id)
        initial['promovido']=pro
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        promovido_id = self.kwargs.get('promovido_id')
        promovido = Promovido.objects.get(id=promovido_id)
        context['promovido'] = promovido
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_promovidos'
        return context
    
def guardar_ubicacion(request):
    if request.method == 'POST':
        try:
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            promovido_id = request.POST.get('promovido')

            # Buscar el objeto Promovido por ID
            promovido = get_object_or_404(Promovido, id=promovido_id)

            # Crea una instancia de Ubicacion y guárdala en la base de datos
            ubicacion = Ubicacion(
                promovido=promovido,
                latitud=latitud,
                longitud=longitud
            )
            ubicacion.save()

            return JsonResponse({'mensaje': 'Datos guardados exitosamente'})
        except Exception as e:
            return JsonResponse({'mensaje': f'Error al guardar los datos: {str(e)}'}, status=400)
    else:
        return JsonResponse({'mensaje': 'Error en la solicitud'}, status=400)
    

class mapas(ListView):
    template_name='mapaPromovidos.html'
    context_object_name='ubicaciones'
    def get_queryset(self):
     promovidos_usuario = Promovido.objects.filter(usuario=self.request.user)
    # Obtener las ubicaciones asociadas a esos promovidos
     ubicaciones = Ubicacion.objects.filter(promovido__in=promovidos_usuario)
     return ubicaciones
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'mapa_promovidos'
        promovidos_usuario = Promovido.objects.filter(usuario=self.request.user)

        # Conteo de géneros basado en Promovido
        context['num_hombres'] = promovidos_usuario.filter(genero='Hombre').count()
        context['num_mujeres'] = promovidos_usuario.filter(genero='Mujer').count()

        # Contador global de todos los promovidos
        context['contador_global'] = promovidos_usuario.count()
        return context

class estadisticasGenerales(ListView):
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
    
class CreateProspectoNuevo(CreateView):
    template_name = 'prospecto/crearProspecto.html'
    form_class = ProspectoFormNuevo
    model = prospecto

    def form_valid(self, form):
        # Establecer el usuario actual como usuario del prospecto
        form.instance.usuario = self.request.user
        # Establecer el estado a 'Promovido'
        form.instance.status = 'Prospecto'
        # Guardar el formulario
        return super(CreateProspectoNuevo, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Prospecto creado con éxito.')
        return reverse('lista_prospectos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'
        context['seccion'] = 'ver_prospectos'
        return context
    
class ListaProspectosNuevo(ListView):
    template_name = 'prospecto/listaProspectos.html'
    context_object_name = 'prospectos'
    model = prospecto

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General']).exists():
            # El usuario es Administrador o Coordinador General, puede ver todos los prospectos con status 'Prospecto'
            return prospecto.objects.filter(status='Prospecto')
        else:
            # El usuario no es Administrador o Coordinador General, filtra por secciones
            secciones_usuario = Seccion.objects.filter(customuser=user)
            return prospecto.objects.filter(seccion__in=secciones_usuario, status='Prospecto')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        context['contador_global'] = queryset.count()       
        context['navbar'] = 'promovidos'
        context['seccion'] = 'ver_prospectos'
        return context

   

class ProspectoUpdateView(UpdateView):
    model = prospecto
    form_class = ProspectoFormNuevoUpdate
    template_name = 'prospecto/updateProspecto.html'  # Asegúrate de tener este template
    success_url = reverse_lazy('lista_prospectos')  # Cambia esto por tu URL

    def form_valid(self, form):
        # Asigna el usuario actual a usuario_promovido
        form.instance.usuario_promovido = self.request.user
        # Cambia el status a 'Promovido'
        form.instance.status = 'Promovido'
        messages.success(self.request, 'Promovido con éxito.')

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_prospectos'  # Cambia esto según la página activa
        return context
    
class ListaPromovidosNuevo(ListView):
    template_name='prospecto/listaPromovidos.html'
    context_object_name = 'promovidos'
    model = prospecto
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Administrador', 'Coordinador General', 'Candidato']).exists():
            # El usuario pertenece a uno de los grupos especiales, muestra todos los prospectos con status 'Promovido'
            return prospecto.objects.filter(status='Promovido')
        else:
            # El usuario no pertenece a los grupos especiales, filtra por las secciones del usuario
            secciones_usuario = user.seccion.all()
            return prospecto.objects.filter(seccion__in=secciones_usuario, status='Promovido')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()

        # Contador global de todos los promovidos
        context['contador_global'] = queryset.count()
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'ver_promovidos'  # Cambia esto según la página activa
        return context



class MapaProspectosPromovidosView(ListView):
    template_name = 'mapa/mapaPromovidos.html'
    context_object_name = 'prospectos'

    def get_queryset(self):
        # Filtrar los prospectos con estado "Promovido"
        return prospecto.objects.filter(status='Promovido')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'promovidos'  # Cambia esto según la página activa
        context['seccion'] = 'mapa_promovidos'
        queryset = self.get_queryset()
        context['num_hombres'] = queryset.filter(genero='Hombre').count()
        context['num_mujeres'] = queryset.filter(genero='Mujer').count()
        # Puedes agregar más contexto según sea necesario
        context['contador_global'] = queryset.count()
        return context
    
class CreatePromovidoNuevo(CreateView):
    template_name = 'prospecto/crearPromovido.html'
    form_class = PromovidoFormNuevo
    model = prospecto
    
    def form_valid(self, form):
        # Asigna el usuario actual a usuario_promovido
        form.instance.usuario_promovido = self.request.user
        # Cambia el status a 'Promovido'
        form.instance.status = 'Promovido'
        messages.success(self.request, 'Promovido con éxito.')

        return super().form_valid(form)

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
    
@csrf_exempt
def verificar_numero_ine(request):
    if request.method == 'POST':
        numero_ine = request.POST.get('numeroINE', '')

        # Verifica si ya existe un registro con el número de INE
        existe = prospecto.objects.filter(numeroINE=numero_ine).exists()

        return JsonResponse({'existe': existe})

    return JsonResponse({'existe': False})