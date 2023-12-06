from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import CandidatoConfig
from .forms import CandidatoConfigForm
from django.shortcuts import redirect

class ConfiguracionView(CreateView):
    model = CandidatoConfig
    form_class = CandidatoConfigForm
    template_name = 'configuracionInicial.html'
    success_url = reverse_lazy('menu')  # Reemplaza con la URL a la que redirigir después del éxito

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'configuracion'
        context['seccion'] = 'ver_configuracion'
        return context
    
class ConfiguracionUpdateView(UpdateView):
    model = CandidatoConfig
    form_class = CandidatoConfigForm
    template_name = 'configuracionUpdate.html'
    success_url = reverse_lazy('menu')  # Reemplaza con la URL a la que redirigir después del éxito

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'configuracion'
        context['seccion'] = 'ver_configuracion'
        return context
    
def check_config_and_redirect(request):
    try:
        config = CandidatoConfig.objects.get(pk=1)
        return redirect('ruta_update_view', pk=config.pk)  # Cambia 'ruta_update_view' por la ruta de tu UpdateView
    except CandidatoConfig.DoesNotExist:
        return redirect('ruta_create_view')  # 